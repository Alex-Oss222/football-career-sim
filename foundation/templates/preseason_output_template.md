# Preseason output template

**Status:** Complete preseason version of the user's original game-output layout. It preserves all eight sections and places the full coaching report beneath each game narrative in section 4.
**Authority:** Required coach-facing preseason format under Document 7 §§5.1 and 5.2. The existing bulk-turn process and material-decision pauses still govern execution.
**When used:** A requested individual preseason game report or the consolidated preseason turn. Use the [regular-season output template](regular_season_output_template.md) for regular-season and postseason turns. A camp practice uses the [camp report](training_camp_and_preseason/training_camp_report.md). An unplayed game receives preparation only, never filled results or invented performances.

## Storage and bulk-report rule

Each played preseason game's complete output remains in its existing game folder. For 2014 onward, use `career/[year]/04_Training_Camp_and_Preseason/Preseason_Games/Game_NN/output.md`; preserve the existing named game folders for 2013. The game output owns preparation, recorded media, the game narrative, the coaching report, full generated box score, consequential decisions and subsequent work. Keep receipt/provenance, medical changes and personnel decisions in their existing supporting owners.

Use all eight sections below for the consolidated preseason turn. Show period-level coach status and preparation once, and repeat the complete section 4 game block for each played game, with the correct opponent/date and its own report and box score. Keep each game's recorded media clearly dated in sections 3 and 5. Section 6 draws together the findings across games and camp; section 7 shows the current personnel at the report's cutoff; section 8 closes the period actually reached. The [consolidated review guide](training_camp_and_preseason/preseason_review.md) supplies section 6's football substance, not a replacement layout.

Save the new cross-game assessment as a dated **Preseason review through [cutoff]** subsection of section 6 in the latest completed game's `output.md` at that cutoff. That section is its single saved owner; link earlier game reports and preserve earlier dated reviews rather than replacing their judgments. Render it in section 6 of the consolidated chat output. If the period stops before any game, keep the camp assessment in `Training_Camp/training_report.md`; an unplayed game does not receive a review to provide a storage location.

Follow the existing bulk preseason workflow. Stop at an uncovered consequential Stone decision when required; report only the completed work. Do not run a game to fill a template, award a role from a heading, or turn a planned opportunity into recorded participation. Routine practice reports do not acquire these game-output tables.

## Preseason-stat persistence rule

Preserve every played game's own public result, receipt and full generated box score. For 2014 onward, preseason statistics belong under `career/[year]/04_Training_Camp_and_Preseason/Preseason_Games/statistics/`, with the game output in its own game folder. Use the season's supported preseason receipt/rendering path. Do not write preseason results into regular-season or postseason receipts, standings, player totals or career win-loss totals.

All displayed counts come from the resolved game. Keep a row for every player the generated box score requires, and preserve any unattributed totals honestly. A missing statistic remains missing. Do not import the real historical game's numbers or type plausible values to complete a table. If the supported preseason path cannot produce the required record, identify the specific blocker; this template does not authorize using a regular-season statbook as a workaround.

## Structured game call-sheet rule

Use the authorized game process and released kernel for the season. The prepared executable offensive menu is carried in the supported structured `TeamInput.offensive_call_sheet` data; do not infer it afterward from the story. This is the machine-readable version of the call sheet Stone and staff already approved during preparation.

A call entry may contain:

- `name` — human-readable call label for the snap ledger;
- `family` — stable concept identity, such as `Mesh`, `Power`, or `Y-Cross`;
- `type` — `run`, `pass`, `any`, or `mixed`;
- `personnel`;
- `formation`;
- `motion`;
- `protection`;
- `tags`.

Do not invent structure that was not actually prepared. If only the family is established, supply only the family/name/type. Human display aliases do not determine the result; football substance is canonicalized in the frozen game packet. A named-call preseason total may be reported only from the generated snap ledger, never inferred afterward from the prose recap.

## Depth and word-count rule

Length follows the actual football evidence. A complete individual game package will often need 1,100 to 1,600 words of prose plus tables and the generated box score, with less for a thin record. The selected game narrative usually needs 300 to 450 words; leave enough room afterward for the coaching report. These are planning bands, not quotas.

In a bulk turn, give each game the space needed to explain its actual action, unit execution, communication and consequential players. Keep the cross-game review concise by discussing what changed instead of repeating the individual reports. Do not compress the whole preseason into a score table or a few star statistics. An unfinished period remains unfinished.

## Coaching report beneath the game summary

Section 4 keeps the established game header and selected narrative. Immediately below the narrative, render **Report to render** and every subsection through the full box score. This incorporates the former separate game-report material into the original output layout. The date and final score remain in the game header; do not add a second game title or result. Preserve sections 1 through 8, including both media sessions, coach status, the personnel snapshot and closure.

Read the prepared menu, actual participation/substitutions, public receipt/play record, medical instructions and dated coaching observations before filling the report. Use the relevant active playbook entries and the [player-assessment method](training_camp_and_preseason/player_assessment.md). A concept's presence in the book does not establish that it was taught or called. Distinguish an immediate impression from a completed staff review. Do not invent film viewing, a spoken check, effort, a missed assignment or a technical cause from a statistic alone.

Assess the actual starters, reserves and mixed groups with their supporting players, opposition, assignment and opportunity. A quarterback change does not establish that the entire unit changed. Keep recognition, technique, physical execution and decisions distinct. Give supported strengths and failures their proper weight without requiring equal praise and criticism or a note on every player. The [preseason research](../../docs/preseason_game_reports.md) supplies coaching examples; outside player results do not become branch evidence.

A game is valuable evidence when its actual task and opposition test the question. Compare it with the player's practice work rather than automatically putting every exhibition snap above every camp rep. Identify different menus, surrounding personnel, workload or contact limits that affect a comparison. Use recorded snap/series counts when they help; do not manufacture equal opportunities or turn missing participation detail into zero work. Repetition supports a conclusion only when the later opportunity tested the relevant responsibility again.

Use connected prose in the filled report. The game narrative tells what happened; the report develops the football judgments. Sections 5 through 8 retain their original purposes. Mention a fact again only when it answers a different question, and keep section 6 focused on the resulting work. The full template below is an authoring scaffold: render its filled Markdown normally in chat, without the outer fence or bracketed instructions.

## Game-narrative rule

The game section is a **selective game story**, not play-by-play, a drive log, broadcast commentary, or a novelized scene.

The final score is already visible before the prose. The narrative's job is to let the coach understand **how the result happened**, which football problems or advantages actually drove it, and which in-game decisions or adjustments materially changed the available choices. Do not invent Stone's private thoughts, feelings, motives, or lessons. If Stone did not publicly say it or make a recorded decision, describe the football evidence rather than narrating an interior reaction.

### Select the game before writing it

For a routine game, narrate roughly **6-10 meaningful sequences** when the generated evidence supports that many. Use fewer when the game is quiet or the evidence is sparse. A sequence can be a full drive, a short cluster of plays, or one spotlight play when Document 7 §3.5 legitimately escalates the detail.

Possible sequences include:

- an opening scripted possession that actually reveals something;
- a protection, communication, run-fit, coverage, or field-position problem;
- a turnover and the possession it changed;
- an explosive play;
- a red-zone sequence;
- a major third- or fourth-down stop;
- a special-teams swing;
- an adjustment that is visible in later generated evidence;
- an injury generated by the runtime;
- a fourth-quarter turning point;
- the final meaningful possession.

Do not narrate a sequence merely because it happened. Select it because it changed score, field position, possession, tactical options, personnel, clock leverage, or the coach's decision context.

If the game has a clear governing football thread, let that thread organize the recap. Examples might be pass protection failing against a four-man rush, Jacksonville living in third-and-long, red-zone efficiency separating otherwise even teams, or a special-teams error creating short fields. Do not manufacture a theme when the evidence is mixed. A messy game may remain a messy game.

Every narrated event must come from the simulated game's generated result or another canonical in-world record. Never import the real historical game's plays, score, injuries, statistics, or outcome.

### Football specificity without fake precision

Prefer concrete football cause over generic evaluation.

A useful highlight usually contains two or three of these:

1. **Situation:** score/clock, field position, down-and-distance, personnel, or game state.
2. **Action:** what the offense, defense, special-teams unit, or coach actually did.
3. **Consequence:** yardage, score, field-position change, turnover, lost opportunity, personnel change, or altered decision.
4. **Response:** a later adjustment or counter only when the generated evidence supports it.

Use exact clock, down-and-distance, route, protection, front, coverage, pressure, personnel grouping, or play-call terminology only when that precision exists in the generated evidence and reconciles with the game ledger. Never add technical detail to make the prose sound expert.

When the evidence only establishes a broad fact, stay broad. "Pressure forced an early throw" is better than inventing a nickel pressure, protection slide, route conversion, or defender responsibility that the engine never generated.

Use terminology from the active, legally available playbook iteration only when the concept was actually installed/available and relevant to the sequence. Do not pull future playbook language backward into an earlier season.

Statistics belong in the prose when they explain the game. Do not restate the box score sentence by sentence.

### Narrative voice and rhythm

Write like a sharp coach-facing game story.

- Use active verbs and concrete football nouns.
- Keep most sentences direct, but vary length naturally. Do not make every highlight a matching three-sentence unit.
- Vary paragraph length. Some sequences need one sentence; some need a short paragraph.
- Do not start every paragraph with the quarter, "on the next drive," or another repeated transition.
- Prefer names, assignments, field position, and consequences over adjectives.
- Keep analysis close to observable evidence. One precise explanation is better than three sentences telling the reader a moment was important.
- Do not invent crowd emotion, sideline body language, locker-room mood, weather drama, or cinematic atmosphere unless it exists in the generated/public evidence and matters to football.
- Do not turn ordinary competence into heroism. A routine punt, tackle, conversion, or completed assignment can remain routine.
- Do not force a comeback arc, redemption arc, rivalry arc, "statement" result, or lesson because the score shape resembles one.
- Do not close the game story with an inspirational moral, slogan, or summary of what the game "meant." End on the last material football consequence, unresolved correction, or result context that actually belongs there.

### Anti-slop guardrails

Before finalizing the narrative, cut or rewrite any sentence that would still fit after changing only the team and player names. Generic prose is not made specific by inserting a proper noun.

Watch for repeated AI-style rhetorical scaffolding. Do not lean on:

- "not just X, but Y" or "more than just";
- "served as a reminder," "a testament to," "underscored," "highlighted," "showcased," or similar significance filler;
- "set the tone," "shifted the momentum," "when it mattered most," "the stage was set," or "statement win/loss" when the sentence does not explain a concrete football cause;
- generic virtue labels such as "resilience," "grit," "heart," "composure," or "determination" as substitutes for what a player or unit actually did;
- repetitive sentence tails such as "highlighting...", "demonstrating...", or "underscoring..." that only restate the previous clause;
- a forced three-part list every time a point needs emphasis;
- one mini-conclusion after every highlight paragraph.

These are not banned words. Use one only when it is the most precise description of established evidence. Do not mechanically replace a cliché with a synonym.

A reliable edit test is: **if a sentence declares significance but contains no new football fact or causal explanation, cut it or replace it with the fact.**

### Silent final edit pass

Before the period closes, perform this pass:

1. **Evidence:** every score, stat, injury, play, decision, and technical detail traces to generated/canonical evidence.
2. **Causality:** the prose distinguishes what happened from why it plausibly happened. It does not claim a cause the evidence cannot support.
3. **Specificity:** vague praise/blame is replaced by assignment, technique, communication, physical result, processing, field position, or decision evidence when available.
4. **Repetition:** repeated transitions, repeated adjectives, repeated sentence shapes, and duplicate box-score facts are cut.
5. **Voice:** narration sounds like a football report; Stone sounds like Stone; reporters do not all sound like the same writer.
6. **Compression:** remove any sentence whose only job is to announce that the previous sentence mattered.

## Box-score presentation rule

Every played game receives the full generated statistical box score for both teams, directly after the coaching report where section 4 places it. Preserve the result and receipt provenance. The display covers the available team comparison and each club's generated Passing, Rushing, Receiving, Fumbles, Defense, Kicking, Punting and Returns categories, with team totals and unattributed production where the receipt requires them. Show only supported statistics and arithmetic derived from them.

Insert the complete output of the season's supported preseason renderer in the marked place below. Do not copy a regular-season renderer command or receipt marker into a preseason file unless that path explicitly supports preseason records. Missing production support is a blocker to a complete box score, not permission to hand-fill one or mix competition totals.

## Media rule

Pregame and postgame media are actual **question-and-answer texture**, not press-release summaries and not the game recap rewritten inside quotation marks.

Questions must arise from plausible public context available at that point. The reporter may press a follow-up when the first answer leaves a real public football question unresolved, but do not manufacture hostility or controversy to create drama.

Reporter questions should vary in length and construction. Avoid a row of polished, two-part questions that all ask Stone to summarize the same issue. Ask about concrete choices, availability, matchup problems, game management, role changes, or public consequences.

Stone's established media voice from `career/2013/offseason/the_prowl_program_identity.md` controls:

- understated;
- specific;
- dry when appropriate;
- football first;
- answers what he can answer;
- protects what should remain private;
- does not treat every question as disrespectful;
- does not use the podium to coach through a player.

Stone does not repeatedly sell "The Prowl" as branding. After a loss, he owns his approved plan and his game-management decisions before shifting blame. After a win, he can credit the team plainly while still identifying correctable football. A player's costly mistake may be identified as a football mistake, but the podium does not become a character judgment. Internal discipline stays private except for material football availability.

Routine answers should usually be **1-4 sentences**. Longer answers need a real football reason. Stone may say he needs the tape, medical information, or staff review when that is genuinely true, but do not use uncertainty as a canned answer to every difficult question.

Do not invent direct quotes from a named real reporter or media member unless that person and quote are already part of the canonical event. Use **Reporter:** generically otherwise.

A routine pregame session normally uses **2-3 substantive questions**. A routine postgame session normally uses **3-5 substantive questions**. High-stakes sessions may run longer where the result genuinely creates more to address.

**Answer method.** Both sessions follow the [head-coach media method](../../docs/head_coach_media_method.md): how real sessions run, the catalogue of real answers, the anti-slop rules, Stone's voice sheet and a worked postgame example. Its key rules, carried here:

- Questions are taken from real transcripts in the reporter's wording and length (clipped, two-in-one, statement-questions and the reporter's own count included); only the branch's names and details change. Run them in a real session's order: the largest thing first, plays and players in the middle, the wide questions last. End each media section with a **Question sources** line per question: the coach asked, the club, the date and the transcript link.
- Stone's answers open on the substance, never by restating the question. No lists of three built for rhythm, no "at the end of the day", no sermon, no explaining the plan's rationale unprompted, no coach-speak the real transcripts do not show. The tape deferral and "I'll have to look at it" each appear at most once per session and carry a specific observation.
- Give a one-sentence answer where a real coach would give one; a third of a postgame session after a loss runs that short. Numbers only as the coach would hold them at the podium.
- Injury answers give what the medical record holds and stop; the roster is Caldwell's; a competition is not decided from the podium after one game; blame is Stone's first and in one sentence; credit is named and specific.

---

~~~
**[Coach Name] ([age]) | [Title] | [Team] (preseason [W]-[L]-[T])**
**[Season Year] | Preseason | [Date range] | [Completed game/period context]**
**Next:** [Next actual camp/preseason event / Regular-season opener]  |  **Days since career start:** [X]

## 1. Coach status

| Field | Value |
|---|---|
| Full name | [Full legal name] |
| Date of birth | [Month Day, Year] |
| Age on period end date | [Derived from DOB and current date] |
| Position | [Title] |
| Team | [Team] ([Conference/Division]) |
| Reports to | [Superior name, title] |
| Contract | Year [X] of [Y] @ $[salary] |
| Current-team HC record | [W-L] ([win %]) |
| NFL regular-season HC record | [W-L] |
| NFL postseason HC record | [W-L] |
| NFL overall HC record | [W-L, regular + postseason] |

[These career records retain their established regular-season/postseason scope. Preseason results appear separately in the header and section 8.]

## 2. Preseason setup and game preparation

**Opponent context:** [What the staff sees on film, current opponent strengths/problems, and relevant public availability/context. State specific evidence. Do not manufacture a storyline.]

**Stone's priorities:** [Actual camp questions, prepared menu, personnel opportunities and offensive, defensive, situational and team-wide goals. Distinguish planned exposure from who actually played.]

**Practice / teaching emphasis:** [What is drilled, corrected, simplified, or expanded. Include protection, communication, situational work, film cutups, and teaching changes only when relevant.]

**Workload / recovery:** [Any meaningful practice-load, travel, recovery, or medical constraint that changes preparation. Do not dump routine logistics.]

## 3. Pregame media Q&A

**Reporter:** [Question grounded in public context.]

**Stone:** [Direct answer in Stone's established voice. Specific football when possible, private matters protected.]

[Repeat only for the number of questions justified by the period.]

## 4. Game

### Preseason game [N]: [Opponent] at [Location] | [Date]

**Final:** [Team] [Score], [Opponent] [Score] | [W/L/T]
**Location:** [Stadium] | [conditions only if established and material]

### Game narrative: selected highlights

[Usual target: 300-450 words; expand or shorten with the actual game evidence. Follow a selected chronology, not a possession log. Use only meaningful generated sequences. Paragraphs do not need to map one-to-one to drives. Explain concrete football cause and consequence. Include Stone's in-game management only where he actually made or approved a recorded decision. Do not invent interiority, fake technical precision, atmosphere, or a moral at the end.]

### Report to render

**Review:** [Immediate postgame assessment, or completed staff review with its actual evidence-through date.]

#### What the staff wanted to see

[Briefly identify the camp questions the game was meant to test, the prepared menu, personnel opportunities and material workload limits. Explain why a player or combination received that work when the reason is recorded. Distinguish the plan from who actually played. Do not assume every starter plays the same number of series or that game three always has a fixed rehearsal role. The recorded pregame exchange belongs in section 3; do not repeat it here.]

#### What the game established

[Use the game summary directly above as the account of what happened. Explain what those sequences establish about the team's play as a whole and what changed with the actual personnel. Connect offense, defense and special teams through possession, field position and the situations they left each other. Include the opponent's contribution. Develop the coaching assessment here without retelling the chronology.]

#### How the units played

##### Offense

[Explain which parts of the prepared offense functioned and which broke down, with named players and representative evidence. Assess the actual opening, relief and mixed combinations. Could they line up, handle a changed defensive picture and run the intended call? Did the run blocks and back's track fit together? Did the quarterback, protection and routes provide the same answer at the same time? Describe drive sustainability and the relevant third-down, red-zone or clock situations, including failures that did not become turnovers. Use game statistics to explain the finding, not to replace it.]

[Separate recognition, technique, matchup and decision errors. A sack can involve the protection call, a lost block, the back, the route answer or the quarterback's timing. Attribute the cause only where the evidence supports it. A designed unblocked edge is not automatically a bust. A completion does not clear a late read or wrong route; an incompletion can include a correct decision. Explain what support made a combination work and what that support cost the rest of the call.]

##### Defense

[Explain the defense's collective play and the changes with its actual personnel. Connect front and gap control to linebacker fits and the force/support defender; connect rush lanes and pressure to coverage and help. Assess block defeat, tackling and pursuit where observed, along with motion/bunch exchanges, leverage and the response to changed formations. Explain whether an explosive play was an isolated loss or part of a repeated problem only when the wider record supports that distinction. A tackle total, sack or interception cannot stand in for the whole assignment. Credit the defender whose sound job allowed someone else to make the play.]

##### Special teams

[Assess the kicking units as football units: snap/hold/protection, kick instruction and placement, releases, coverage lanes, blocks, return decisions and the resulting field position. Distinguish specialist execution from the protection or coverage around him. Name reserves whose work mattered. Include actual substitution or emergency-operation findings. A made kick does not prove protection was sound; participation alone does not earn coverage credit.]

#### Communication and game operation

[Explain whether the team could get the call from the sideline into the huddle, make its shared declarations and get the correct people aligned before the snap. Use specific recorded examples of protection agreement, coverage exchanges, substitutions, tempo, clock handling or a replacement taking over communication. Describe what held together and what needed rescue, including timeout or play-menu costs when established. Account for coach-to-player communication as well as player-to-player communication.]

[Do not label every bust a communication problem. Distinguish a call not received, conflicting instructions, a correctly understood job executed poorly and a cause that is still unclear. A clean penalty line or a win does not establish clean communication. If only one unit has usable evidence, state that limit once and assess that unit without awarding the whole team a communication verdict.]

#### Players who stood out and questions still open

[Use named paragraphs with the [player-assessment method](training_camp_and_preseason/player_assessment.md). State what the player did well, what he did poorly where supported, and what that means for his particular job. Include meaningful contrary evidence in the same assessment. Connect the game to the previous camp question: was it answered, partly answered, contradicted or never tested? Show how an error or successful technique held up on another opportunity when recorded. Do not merely repeat the scoring plays or the unit section.]

[Give the reader the distinction that matters: dependable work, a useful performance earning another look, a recurring limitation, or an unresolved comparison. Those are judgments to express in normal prose, not mandatory labels or grades. A receiver can help through spacing or blocking without a catch; a defensive back can execute his coverage without a target. Credit those jobs only with actual evidence. A productive reserve with a narrower menu has established something useful within that menu, not mastery of the entire offense. Playing little, being medically limited or never encountering the planned test is not failure.]

[For an existing position battle, state what this game adds to the particular job comparison and link its card. Do not create a battle from a vacancy, cross-training rep or good highlight. Evaluate what moving a candidate changes for the surrounding unit and other duties, including special teams. A recorded role decision belongs in roster decisions and the depth chart; this report supplies its football evidence.]

#### Stone's decisions and the next practice

[Record consequential choices Stone actually made, why the recorded football problem prompted them and what happened afterward. Separate the choice from its execution. Consider the staff's teaching, call, personnel support and sideline operation alongside the players. Do not rewrite Stone's intentions from the final score or invent a private reaction.]

[Give each material correction its responsible coach and next useful opportunity: film/meeting clarification, a technique period, a combination rep, a situation or a later game exposure as appropriate. Explain what would count as improvement in that job. Use that season's actual staff. The position coach addresses technique and recognition, the coordinator connects the unit's assignments, and the head coach evaluates the team consequence within his actual responsibilities; do not invent a second coach when duties overlap. A proposed correction is not a delivered lesson, and a planned retest is not a successful rep. Distinguish a recommendation for different work from Stone's actual role decision. Link any actual role or availability change to its owner. Keep recorded postgame media in section 5, in Stone's established voice; do not manufacture quotes in a retrospective rewrite. Identify the next work or consequential choice that pauses the bulk turn; section 6 carries those priorities forward without repeating the assessment.]

#### Box score

[Insert the full generated box score for this game and both teams using the supported preseason receipt/rendering path. Preserve provenance. Do not hand-fill statistics or put preseason production into the regular-season statbook. Identify a concrete production blocker if the required record is unavailable.]

**Standout performances**
- [Player]: [Specific football evidence and relevant statistics.]
- [Player]: [Specific football evidence and relevant statistics.]
[Use 2-4 only when earned by the generated game.]
[These are concise references to the developed player findings above, not another assessment or a second account of the same plays.]

**Material game-management decisions:** [Only consequential fourth-down, clock, challenge, timeout, personnel, tempo, or other head-coach decisions actually made. Separate the quality of the decision from whether the result worked. Omit if none.]

**Injuries / availability from the game:** [Only generated/medically established changes. Omit if none.]

## 5. Postgame media Q&A

**Reporter:** [Question arising from what actually happened.]

**Stone:** [Answer in Stone's established voice. Do not restate the recap. Address the football question.]

[Use 3-5 substantive questions for a routine game; more only when the stakes/result justify it.]

## 6. Coaching takeaways and preseason carry-forward

[For a bulk report, connect the games to the camp findings here using the consolidated review guide. Retain the three fields below; develop the changes in unit execution, communication and player assessment without replaying each game.]

**What held up:** [Execution, communication, preparation, or unit strengths actually supported by the period.]

**What must be corrected:** [Specific football problems. Distinguish assignment, communication, technique, physical loss, processing, medical limitation, and teaching failure.]

**Next-period carry-forward:** [What Stone/staff will retain, reduce, correct, or investigate. Do not pre-resolve the next period's outcome.]

## 7. Preseason personnel and availability snapshot

This is a **complete unit-level period view**, not a second copy of the full roster. Every functional position group gets a current line, but name only the starters, primary rotational players, specialists, and anyone whose role or availability is material to the period.

Use actual camp/game assignments and the current competition status. A first-group trial or a QB1 label for one exhibition does not award the regular-season job. Include material reserve and mixed-group findings; keep an unsettled position unsettled until Stone makes a decision.

Keep four different questions separate:

1. **Role:** what the player is currently being asked to do.
2. **Availability:** whether and how the player can participate, using only the canonical medical/game-status information actually established.
3. **Evaluation:** the staff's current qualitative football read, using the established five-tier language only where it adds value.
4. **This period's evidence:** what changed, held up, or became a concern during the reported period.

A strong game does not automatically raise a player's underlying tier, and a bad game does not automatically lower it. Preseason production is evidence. Role, health, matchup, assignment quality, and the broader body of work still control the current evaluation.

### Offense

| Group | Primary personnel / current role | Availability | Current qualitative read | This period's evidence / issue |
|---|---|---|---|---|
| QB | QB1: [Name] ([tier if useful]); QB2: [Name only when role/availability is material] | [Canonical status / limitation] | [Processing, accuracy, ball security, pocket management, movement, command, or other supported read] | [What the period actually showed; distinguish player execution from protection, receiver, play-call, or teaching issues] |
| RB / FB | [Lead runner, third-down back, short-yardage back, FB or other materially used roles] | [Status] | [Vision, contact balance, pass protection, receiving, ball security, short-yardage value, etc.] | [Role change, workload issue, protection result, explosive runs, missed assignment, or no material change] |
| WR | [Primary outside receivers, slot, and any material rotational/return role] | [Status] | [Separation, releases, route detail, catch-point work, blocking, communication, etc.] | [Who actually affected the period and how; do not rank the whole room from raw receiving totals] |
| TE | [Inline, move, receiving, blocking, or hybrid roles actually in use] | [Status] | [Blocking, route value, hands, assignment reliability, versatility, etc.] | [Material contribution/problem, role change, or no material change] |
| OL | LT: [Name]; LG: [Name]; C: [Name]; RG: [Name]; RT: [Name] | [Any individual limitation or lineup contingency] | [Run blocking, pass protection, communication, stunt/pickup handling, short-yardage movement, overall cohesion] | [Identify the exact edge/interior issue, pressure source, communication problem, lineup change, or strength when supported] |

**Offensive role changes:** [New starter, rotation change, package change, reduced/increased responsibility, backup promotion, or "none." Do not manufacture a change because one player had a productive game.]

### Defense

| Group | Primary personnel / current role | Availability | Current qualitative read | This period's evidence / issue |
|---|---|---|---|---|
| Interior DL | [Primary interior starters/rotation and role if material] | [Status] | [Run fits, anchor, penetration, gap discipline, rush contribution, rotation quality] | [What held up or failed this period] |
| Edge | [Primary edge defenders / rush or contain roles] | [Status] | [Pressure quality, edge setting, rush plan, finish, discipline] | [Pressure source, lost edge, containment issue, matchup win, or no material change] |
| LB | [Primary off-ball linebackers and subpackage roles] | [Status] | [Run fits, coverage, communication, tackling, pressure responsibility] | [Assignment/communication/physical result from the period] |
| CB | [Outside corners and any material matchup assignment] | [Status] | [Coverage, leverage, ball production, tackling, penalty/technique issues] | [Targeted matchup result, role change, or no material change] |
| Nickel / dime | [Primary slot/subpackage defenders if used] | [Status] | [Coverage, pressure, fit, communication, versatility] | [Subpackage-specific evidence or issue] |
| S | [Primary safeties and deep/box/matchup roles] | [Status] | [Range, angles, tackling, communication, coverage responsibility] | [Material play, bust, support strength, rotation change, or no material change] |

**Defensive role changes:** [New starter, package/rotation change, matchup role, reduced/increased responsibility, or "none."]

### Special teams

| Unit | Primary personnel / role | Availability | Current qualitative read | This period's evidence / issue |
|---|---|---|---|---|
| K | [Name] | [Status] | [Range/consistency only from established evidence; do not invent precision] | [Makes/misses or operation issue that mattered] |
| P | [Name] | [Status] | [Placement, hang-time/field-position value only when supported] | [Material punt/field-position evidence] |
| LS / operation | [Name(s) only if material] | [Status] | [Snap/hold/operation reliability if evidenced] | [Only note when the operation materially affected a play or availability] |
| Kick return | [Primary returner(s)] | [Status] | [Decision-making, ball security, field-position value] | [Material return or decision] |
| Punt return | [Primary returner(s)] | [Status] | [Decision-making, security, return value] | [Material return/fair-catch/ball-security issue] |
| Coverage units | [Core coverage players only when material] | [Status] | [Lane integrity, leverage, tackling, discipline] | [Breakdown, strong field-position work, penalty, or no material change] |

### Material personnel changes this period

- **Injuries / limitations:** [New injury, worsening/improving limitation, return, or no material change.]
- **Activations / elevations / transactions:** [Only changes that actually occurred.]
- **Depth-chart / rotation changes:** [Only decisions actually made. An open competition remains open until Stone/staff resolve it.]
- **Role consequences for the next period:** [Who may need a larger/smaller role, what remains unresolved, or no material change. Do not pre-resolve the next game.]

Do not repeat the entire roster or every unchanged backup. `career/[year]/roster.md` and Document 4 remain authoritative for full personnel ownership and status. This section exists to show the coach the **current functional shape of the team** entering the next football decision.

## 8. Preseason closure

**Preseason record:** [W-L-T from completed preseason receipts only]
**Roster decisions:** [Decisions actually made; identify unresolved choices and link the proper roster-decision owner]
**Preseason statistics:** [Completed-game coverage and the separate preseason statistics record; any specific missing receipt/box-score support]
**Dated record:** [Descriptive link to the actual game/period event owner and its annual Record.md index; retain the existing event for a presentation-only rewrite]
**Next event:** [Exact next football/calendar event]
~~~

Coach-facing evaluation uses the established qualitative language only: **Elite / Plus / Average / Below-Average / Replacement-Level** where a tier is actually useful. Never expose hidden numeric ratings, probabilities, grades, or roster-survival percentages.
