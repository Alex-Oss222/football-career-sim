# AGENTS.md — football-career-sim

You are Codex, running a bounded batch task against this repository. You have no memory of any conversation that built this project — everything you need is in this file and the documents it points you to. Read them before acting; do not guess at a rule this file or the linked documents don't state.

**Read first, in order:** `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md`, `foundation/07_Game_Simulation_and_Resolution_Engine.md`. Do not read `foundation/templates/`, `library/`, or anything under `career/` in full — those are large; read only the specific file a task below names.

**Hard rules that apply to every task in this file, no exceptions:**
- **Protagonist-blind resolution (Document 1 §9.1, added 2026-09-18).** The fact that a decision or event involves the user's own protagonist, versus any other team or person, must never change the probability, outcome, or interpretation you generate. Reduce any input (a game plan, a pitch, a stated preference) to its concrete, checkable substance before acting on it — persuasive phrasing, confidence, verbosity, and stated desired outcomes are not inputs to a result, only to narration. Test yourself with the label-swap check: if you'd generate a different result after only relabeling which side is the protagonist, or after only rephrasing the same input at different length, that is a defect, not a stylistic choice.
- Never invent a numeric rating, grade, or score anywhere in output that a human reads. Use only the five-tier qualitative language already established (Elite / Plus / Average / Below-Average / Replacement-Level).
- Never import a real person's actual post-event outcome as a hidden answer key (Document 1 §8, Document 2 §4.3). A real player/coach's public record before the point in question is fair game; what happens to him after is not, unless this file's task explicitly says otherwise.
- Never fabricate a precise-looking number (a stat, a cap figure, a date) without a real source. If you can't verify something, say so explicitly rather than presenting an estimate as fact — this project's stated top priority is never repeating a past experience where numbers were "fudged."
- Write the task's named file as the primary record, but do **not** stop there when the task changes canon or advances simulation time. Never edit `foundation/` unless the task explicitly targets the rulebook. Research-only, planning-only, and ex-ante recommendation tasks must not mutate current state.
- Commit with a clear message describing what changed. Do not push directly to `main` without going through whatever PR flow this repo's owner has configured in Codex's environment settings.

### Atomic progression and dependency rule

Any task that **completes an event, advances the career clock, changes roster/control, changes staff, changes draft capital, changes financial obligations, changes medical/availability state, changes a depth-chart or role decision, or otherwise changes canon** is an atomic progression task. For those tasks:

1. **Update the event/history owner first.** Write the completed result to the appropriate dated career file such as the season ledger, trades ledger, signing ledger, draftees file, practice/game output, roster-decision file, or other phase result.
2. **Update every dependent current-state view in the same commit.** At minimum inspect and update, when affected:
   - `career/[year]/ledger.md`;
   - the applicable transaction/result file under `career/[year]/`;
   - `career/[year]/roster.md`;
   - `career/[year]/standings.md` whenever a final score changes any club's record (league, conference and division tables);
   - `career/[year]/stats/` whenever a regular-season or postseason game closes: preserve the public stat receipt and refresh the current team/league stat views from receipts rather than hand-adding prior Markdown;
   - the applicable cap/contract/draft-capital accounting file;
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

**Season-stat closure rule.** A closed regular-season or postseason game is not statistically complete until its public game receipt is preserved under `career/[year]/stats/game_receipts/`. Under kernel 2013.3 that receipt must retain the complete public player-stat dictionaries, the complete public snap `play_ledger`, and game `play_call_stats`; it may never contain private Engine State material, seeds, hidden ratings, matchup deltas or probability data. Refresh `team_player_stats.md`, `all_player_stats.md`, `league_player_stats.md`, `play_call_stats.md` and `league_leaders.md` from the receipt set using the statbook tooling. If receipt coverage is incomplete, label the gap and withhold formal league rankings rather than filling it from real historical results or narrative inference.

Use [the dependency workflow](docs/update_workflow.md) and `docs/repository_map.json`. Run `python scripts/validate_repository.py` before closing a change; refresh a phase summary receipt only after reviewing the summary against its updated output. Both game paths must also pass `python scripts/check_game_readiness.py`. A green repository check is not game authorization.

### Playbook (offense and defense): active-iteration lock

`career/playbook/` holds Stone's authored, team-neutral offensive and defensive systems across the whole career, in two parallel series of dated iterations — see `career/playbook/README.md` for the full index and effective-season tables. The lock below applies to the offensive and defensive series independently.

- **Read only the offensive and defensive iterations whose effective-season ranges (their own frontmatter) cover the current in-sim year**, per `state/05_Current_Season_State.md`'s master clock. Never open, quote, or draw a concept, personnel grouping, protection name, front, coverage, pressure label, or term from an iteration whose range starts after the current in-sim year — that book is offense or defense Stone has not developed yet inside the story. This is the no-hindsight rule (Document 2 §12) applied to the user's own pre-written future material, not just real-world fact.
- **The defensive coordinator, whoever holds the job that year, is the defensive caller** (Romeo Crennel in 2013). The defensive books name Stone as "primary play-caller," but that describes the authored system and does not override this rule or the authority map. The defensive book is Stone's issued system; how much the DC installs or adapts is a staff-resolved football question, never assumed (see `career/playbook/README.md`).
- A past, superseded iteration may be read for lineage (an iteration's `inheritance_rule`/`baseline` field legitimately points back to an earlier one), but only the currently active iteration is live for teaching, install work, scouting, or play-calling.
- **Human-player access rule.** Every player may receive, possess, and study the complete active iteration. The active book is a football playbook, not a software unlock tree. Players may read ahead and ask questions about any page. "Installed" means formally taught, walked through, practiced, and prepared for team use. Installation is still gated by the real CBA offseason-program calendar in `career/[year]/offseason/the_prowl_player_readiness_standard.md`, but that calendar limits club teaching/practice activity, not player access to the active book. Evaluate players on assigned/taught material, never on whether they mastered an uninstalled page.


### Career calendar control rule

For any task that advances a season clock, opens/closes a camp or practice phase, executes a roster deadline, runs a transaction window, or plays/simulates a game, first read `career/[year]/calendar.md` when that file exists.

- The career calendar is the branch-facing schedule authority for team dates, opponents, reporting dates, camp windows, roster deadlines, trade deadlines, bye weeks and conditional postseason gates.
- Its historical sourcing belongs in the corresponding `library/[year]_*calendar*.md` file. For Jacksonville 2013, the full source is `library/2013_jacksonville_master_calendar.md`.
- Do not substitute an older phase-local date if the master calendar contains a later verified correction.
- Historical dates/opponents are rails only. Never import the real score, injury, transaction, attendance, depth chart or season result.
- If a previously missed phase is already behind the latest closed checkpoint, preserve the chronology gap unless the user expressly authorizes a retroactive simulation. Do not fabricate attendance or performance to make the calendar look complete.
- Before closing a date-sensitive event, check the next deadline/event in the career calendar and carry it into Document 5.

### Offseason onboarding and phase-plan execution rule

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
- Offseason program / Phase One / Phase Two / OTAs -> `career/[year]/offseason/otas/plan.md`
- Any separately scheduled new-head-coach voluntary veteran minicamp -> use `otas/plan.md` plus the exact voluntary-minicamp CBA/calendar rules; do not convert it into the mandatory event.
- Mandatory veteran minicamp -> `career/[year]/offseason/mandatory_minicamp/plan.md`
- Training camp and its integrated preseason-development process -> `career/[year]/offseason/training_camp/plan.md`

**Plan versus history is a hard boundary.** A `plan.md` says what Jacksonville intends to teach, train, evaluate, and provide. The corresponding `output.md`, season ledger, roster/register, and current-state files say what actually happened. Never write results, standouts, attendance lists, depth-chart outcomes, injuries, or performance history back into a durable plan merely because the event occurred.

**Calendar gate.** If the exact 2013 Jacksonville date/window needed to execute a phase is still unresolved in the repository, research and verify it under the project's two-pass sourcing discipline before advancing the career clock. Do not invent a convenient date, practice count, reporting day, or roster deadline.

**Onboarding gate.**

- Before a player's first Jacksonville football-development phase, verify club control and execute the welcome-package / playbook-distribution / follow-up-call process to the extent the calendar legally and practically allows.
- Contact only players whose Jacksonville control or invitation status is actually established. An unresolved inherited name is not a license to invent a call or letter.
- A late acquisition gets the same onboarding process on a compressed honest timeline; record the compression rather than backdating calls.
- Issue the complete active playbook. Players may study any part of it. The phase-appropriate practiced menu defines what the staff may fairly evaluate as installed team football; it is not a restriction on what players may read.
- During voluntary periods, an optional Stone/position-coach call, workout, meeting, or social event cannot become a hidden roster/role/commitment grade.

**Teaching and evaluation rule.** Execute the phase plan's Explain -> Show -> Walk -> Rep -> Correct -> Rep again -> Retain -> Add complexity cycle. Keep assignment, communication, technique, physical loss, processing delay, medical limit, and coaching/teaching failure analytically separate. Do not manufacture a flaw when a rep was correct. Do not add complexity simply because the calendar advanced. The phase plan's Good/Better/Best descriptions are teaching states, not numeric ratings and not permanent player labels.

**No percentage-driven roster or playbook resolution.** Do not use a playbook personnel percentage, planning center, preset snap share, rep quota, touch quota, depth-chart probability, or target distribution as the mechanism that decides who plays, who wins a job, which package is used, or which concept succeeds. Those are football decisions that must emerge from the players' demonstrated work, health, matchup, opponent response, game situation, actual practice/preseason/game performance, and the coach's authorized judgment. If a playbook contains a numerical usage note, treat it as non-controlling background only. The football evidence overrides it.

The simulation engine may still use its hidden stochastic resolution machinery to resolve uncertain football events where Document 7 requires it. That hidden mechanism must not be exposed to the player-facing playbook and must not be substituted for the football evidence used to make roster, role, rep, touch, install, or game-plan decisions.

**Family-dinner rule.** The phase-specific family dinners are part of the established program. When the verified schedule permits, execute the dinner described by the phase plan. Invite the current team, appropriate staff, and invited family/meaningful guests under the framework's rules. Family/guest attendance is voluntary, the dinner is not a football meeting, and attendance, guest choice, family structure, finances, health, counseling use, or private conversation never becomes personnel evidence. Log an actual dinner in the phase output, not the durable plan.

**Resolution discipline.** The plans define opportunities and evaluation questions, not outcomes. Resolve actual player performance from the information legally available at that date, the work actually performed, the game/practice resolution rules, and the protagonist-blind standard. Never use future real-life player success/failure as proof that a rookie, veteran, signing, or draft pick must stand out or struggle.

**Closing the phase.** Once actual football work occurs, this becomes an atomic progression task. Write the phase output/standouts first, append the season ledger as appropriate, then update every genuinely affected roster, role, medical/availability, financial/control, Document 4, and Document 5 view in the same progression commit. If no current fact changed, do not manufacture a state edit merely to touch every file.

**Do not rewrite the plans after every practice.** Change a durable plan only when the user changes the teaching method, install philosophy, physical standard, evaluation standard, family-program policy, or operational responsibility.


---

## Task: "Run Week [N]" / "Run Week N"

This is the **top-level one-command regular-season workflow**. A user instruction such as `Run Week 1`, `Run Week 2`, or `Run Week 3. Plan: ...` authorizes the complete bounded week task. The user is not responsible for running helper scripts, filling migration JSON, building background-team packets, advancing private snapshots, or repairing internal readiness prerequisites.

### What the one command authorizes

For the named week, Codex must autonomously:

1. Read the current state, calendar, that week's existing `output.md`, the active playbook iterations, the season-output template, current roster/medical state, and any weekly plan supplied by the user.
2. Run ordinary repository/game readiness checks.
3. Resolve **internal repository prerequisites** that are already user-authorized, including an explicit migration/reset for that same week.
4. Build/freeze the protagonist and background TeamInput records required by the active kernel.
5. Run the protagonist game and every other league game in that week through the shared production runner, exactly once per canonical event.
6. Preserve the full public game receipts required by the active kernel/statbook contract.
7. Write the protagonist weekly `output.md` using the current season-output template and write the background roundup to `league_results/week_NN.md`.
8. Rebuild standings and season statistics from receipts; never hand-add totals from Markdown.
9. Reconcile injuries, availability, roles, transactions and other actually changed state.
10. Close the ledger/current state/calendar atomically, advance the private snapshot after public canon closes, rerun readiness, validate, and use the normal PR flow.
11. Stop before Week N+1.

### User-plan handling

- If the user supplies a Week N plan in the same prompt, that plan controls within Stone's authority.
- If an already-closed ex-ante Week N plan/call sheet exists because the week is being rerun under an authorized technical migration, **reuse that pre-result plan**. Do not rewrite the plan because the old result is known.
- Do not manufacture a new consequential Stone commitment merely to avoid asking a real football question. A genuinely new user-controlled choice not covered by the supplied/closed plan may still require the user. Internal tooling, data preparation, migration work, background-team construction and repository bookkeeping never do.

### Internal migration / reset rule

A user-authorized migration for the requested week is an **internal prerequisite**, not a user task.

For the 2013 Week 1 full-fidelity reset specifically:

- Read `career/2013/migrations/week_01_full_fidelity_reset.md` and its JSON manifest.
- If `python scripts/check_week1_reset_ready.py` reports missing TeamInputs, **do not stop and ask the user to fill them**.
- Research and construct all missing pre-Week-1 TeamInputs yourself from date-eligible public sources and branch canon, then rerun the gate.
- Use verified historical Week-1 roster membership/position/availability facts for non-Jacksonville clubs as date-specific roster rails when no earlier branch transaction overrides them. Historical Week-1 scores, statistics, injuries produced by the real games, later depth-chart outcomes and later season/career results are forbidden inputs.
- Prefer a week-level roster source with explicit 2013 Week 1 scope; cross-check material ambiguities against an independent period-appropriate source. Record source/provenance for the reconstructed inputs.
- Jacksonville must use the branch's September 4 roster, medical state, roles and the already-approved Week 1 structured offensive call sheet—not the real historical Jaguars roster/result.
- For unit evidence anchors, apply Document 7 §2.2. Where pre-Week-1 evidence is thin, use the established `Average` low-confidence default rather than guessing a stronger/weaker secret rating.
- Background clubs do not need invented named play calls. Use only offensive-call detail supported by their date-eligible input contract; the protagonist's structured call sheet remains mandatory where the active kernel requires it.
- Freeze all 32 reconstructed TeamInputs before any replacement Week 1 draw.
- Only after the reset gate passes may any replacement event close. Then replace all 16 Week 1 games as one batch, preserve complete receipts, rebuild every dependent stat/standings view, append the supersession entry, reconcile injuries/state and validate before Week 2.
- Never rerun only Jacksonville while leaving the other 15 legacy Week 1 games active.

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

**Scope:** every game that week between two teams, neither of which is the user's own team. Never touch a game involving the protagonist's team — that is played interactively elsewhere and is not your job.

**Method — read `foundation/07_Game_Simulation_and_Resolution_Engine.md` §1's scope-discipline rule first, and §3.4's resolution-packet/seed rule.** Corrected 2026-09-18: there is only one outcome kernel in this project. Do not resolve these games by free-form judgment about who plausibly wins — that was an earlier version of this rule and it created two different outcome adjudicators in one league, which is a real integrity defect (background results decide the protagonist's standings, playoff seeding, and draft order, so they need the same physics as his own games, not a cheaper substitute physics). Actually sample from the §2 rating anchors and §3.2 matchup-delta mechanism, at a coarser granularity (whole-game or a few aggregated segments, not per-drive) to control cost — then narrate only the result. The savings versus the interactive path is in narration depth and sampling granularity, never in swapping the mechanism for a subjective call.

**Output format — highlights only, explicitly, per this project's owner's own instruction:** for each game, write final score, 2-4 sentences of highlight narration (not a drive-by-drive account), and 1-3 standout performers. Do not write play-by-play. Do not write a full box score unless a specific downstream task asks for one. A whole week's slate of ~13-15 games should read like a scores-and-highlights roundup, not 13 separate game stories.

**Reactive events — allowed, but bounded.** A team's players, coaches, or front office may generate a genuine reactive event (a trade demand, a coach on the hot seat, a locker-room story, a media dust-up) if it plausibly follows from something that actually happened in a game or a transaction already on the record. Do not manufacture one to fill a quiet week — per Document 7 §7's Locker Room/Media agent rule, these fire only from logged mechanical events, never invented for drama's own sake. Across a full week's slate, most games should have none; a handful having one is normal, all of them having one is a sign you're manufacturing rather than reacting.

**Write results to:** `career/[year]/league_results/week_[NN].md` (create the file/folder if it doesn't exist yet this season). One entry per game. Also update the running league standings in the same file's header table, and update the single current standings file `career/[year]/standings.md` (division, conference and league-wide tables, ties broken only by Document 2 §5.3) in the same commit.

**Persist league statistics too.** For every closed background game, preserve the public game receipt under `career/[year]/stats/game_receipts/`, including every generated player counter and the full snap ledger even though the prose summary remains short. Once the full weekly slate is closed, rebuild the season statbook with `runtime/statbook.py` / `scripts/render_season_stats.py`. The weekly highlights file remains concise; full cumulative player and play data live in `stats/`, not in `league_results/week_NN.md`.

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

**Persistence and ex-ante discipline.** Write every criteria freeze, user instruction relied on, material organization-side development, unresolved user decision, offer, and final search status to `career/[year]/offseason/hiring_search.md`. During this pre-hire phase that file is the authorized decision ledger. Do not write simulated hiring events into Document 6 before career initialization.

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
4. Record every actual hire — name, role, effective date — in `staff_building/hires.md`. Record a real decline or lost-to-competition outcome there too, briefly, so the ledger reflects what actually happened rather than only the successes.

**GM alignment conversation — Caldwell reacts, he doesn't rubber-stamp.**
1. Present Stone's roster evaluation (`roster_evaluation.md`) and free-agency priorities (`free_agency/player_board.md`) to Caldwell as one consolidated conversation, per Document 3 §10.2's compressed-turn discipline.
2. Caldwell's reaction is resolved from his own retained authority and the club's actual situation (library/2013_coaching_market_pre_hire.md §3), not assumed to agree with Stone on every point. A genuine, football-grounded pushback (a release Caldwell wants to revisit, a free-agent price he thinks is too rich, a roster call he weighs differently) is a normal and expected outcome, not something to avoid.
3. Record this exchange as a dated, appended entry in `roster_evaluation.md` — do not silently rewrite Stone's own original evaluation to match Caldwell's response.

**Do not** resolve any actual free-agency signing or draft selection in this task — free agency does not open until March 12 and the draft runs April 25-27 (`library/2013_league_calendar_and_financial_rules.md`); this phase is staff hiring and initial GM alignment on the broader plan only, not executing it early.

**Do not** invent Stone's coaching philosophy or personal positions beyond what's already established in The Prowl documents, the interview positions, and the accepted contract — if a candidate conversation would require a stance nothing on record covers, stop and report what's missing rather than inventing it.

---

## Task: "Run the [year] offseason cycle." (free agency, draft, and trades — not yet enabled)

Gated on the real calendar, not just a brief. Do not attempt free agency before March 12 or the draft before April 25 for the 2013 cycle (`library/2013_league_calendar_and_financial_rules.md`; check the equivalent library file for other years). When that window is actually reached, this task resolves `career/[year]/offseason/free_agency/player_board.md`, `career/[year]/offseason/draft/player_draft_board.md`, and `career/[year]/trades/trade_targets.md` the same way the staff-building task above resolves staff hiring: real market pressure, genuine possible rejection or lost competition, Caldwell's retained authority over the actual signing/pick/trade decision, and a written result (never a locked-in outcome assumed from what actually happened in real history). If any of those three files doesn't exist yet for the year in question, stop and report rather than improvising the user's priorities.
