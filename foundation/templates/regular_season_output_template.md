# Regular-season output template

**Status:** The user's original `Season Output.txt` layout, refined September 19, 2026 and renamed at the user's request. The complete coaching report now sits beneath the game narrative in section 4.
**Authority:** Required coach-facing regular-season and postseason format under Document 7 §5.2. Document 7 governs simulation; this template governs presentation.
**When used:** Regular-season game weeks, byes and postseason turns. Use the complete [preseason output template](preseason_output_template.md) for preseason and the [offseason output template](offseason_output_template.md) for offseason turns.

## Storage rule

For a regular-season or postseason week, the complete protagonist-team turn is stored in that week's existing:

`career/[year]/regular_season/week_NN_<away>_at_<home>/output.md`

or the equivalent postseason `output.md`.

That single `output.md` owns the week's coach-facing package:

- opponent/week setup;
- Stone's game preparation;
- pregame media Q&A;
- the simulated game result;
- selected narrated highlight sequences;
- box score and standout performances;
- material head-coach game-management decisions;
- postgame media Q&A;
- coaching corrections and carry-forward priorities;
- material roster and availability changes.

Do **not** create separate `prep.md`, `pregame_press.md`, `game_recap.md`, `highlights.md`, or `postgame_press.md` files. Supporting evidence remains in its existing canonical owners: ledger, roster, standings, medical/current-state files, playbook, game-event ledger, and league-results files.

Background games remain in `career/[year]/league_results/week_NN.md`; they are not expanded into this protagonist-team format.

## Season-stat persistence rule

Every closed regular-season or postseason game produces a **public stat receipt** under:

`career/[year]/stats/game_receipts/`

The receipt is downstream of the already-resolved game. It names the home and away clubs, the final score and team statistics, and a player row for every player on each club's game-day active list. Protagonist receipts also keep the complete public snap `play_ledger` and named `play_call_stats`. A receipt never contains private Engine State material, hidden ratings, matchup deltas, probabilities or seeds.

Everything statistical is generated from the receipts, never added by hand:

- the week's box score in `output.md` (`scripts/render_box_score.py`);
- `career/[year]/standings.md`: records, division order, seeding and tiebreakers (`scripts/render_standings.py`);
- `career/[year]/stats/`: player views by position, leaders, team statistics and named-call statistics (`scripts/render_season_stats.py`).

A missing attribution stays missing; never import the real historical game's statistic to fill it.

## Structured weekly call-sheet rule

Before a protagonist game is closed under kernel 2013.4, the executable offensive menu used by the simulator must be passed as structured `TeamInput.offensive_call_sheet` data. This is the machine-readable version of the call sheet Stone and staff already approved during preparation.

A call entry may contain:

- `name` — human-readable call label for the snap ledger;
- `family` — stable concept identity, such as `Mesh`, `Power`, or `Y-Cross`;
- `type` — `run`, `pass`, `any`, or `mixed`;
- `personnel`;
- `formation`;
- `motion`;
- `protection`;
- `tags`.

Do not invent structure that was not actually prepared. If only the family is established, supply only the family/name/type. Human display aliases do not determine the result; football substance is canonicalized in the frozen game packet. A named-call season total may be reported only from the generated snap ledger, never inferred afterward from the prose recap.

## Depth and word-count rule

Word counts are planning bands for the existing weekly prose, not quotas. Allow additional space for the substantive coaching report beneath the game narrative; avoid repeating its findings in later sections. Do not pad a quiet game and do not compress a genuinely major one. High stakes should increase useful evidence and decision context, not adjective density.

### Routine regular-season game week

Target roughly **700-1,100 words of prose**, plus tables:

- Week setup / opponent context: **75-125 words**
- Weekly game preparation: **125-200 words**
- Pregame media Q&A: **75-125 words**
- Game narrative / highlight plays: **300-450 words**
- Postgame media Q&A: **125-200 words**
- Coaching takeaways / next-week carry-forward: **75-125 words**

### High-stakes game week

For postseason, rivalry, elimination, dramatic finish, signature result, major job-security consequence, or another legitimately high-stakes game, expand naturally to roughly **1,200-1,600 words of prose**.

Typical bands:

- Week setup / preparation: **200-300 words**
- Pregame Q&A: **125-200 words**
- Game narrative / highlight plays: **500-750 words**
- Postgame Q&A: **200-300 words**
- Coaching takeaways: **100-175 words**

### Bye / no-game week

Use a compressed format. Preparation, roster/medical developments, self-scout, and next-opponent work should normally fit in **150-300 words total**, unless something material actually happens.

## Coaching report beneath the game summary

Section 4 keeps the established game header and selected narrative. Immediately below the narrative, render **Report to render** and every subsection through the full box score. This incorporates the former separate game-report material into the original output layout. The date and final score remain in the game header; do not add a second game title or result. Preserve sections 1 through 8, including both media sessions, coach status, the personnel snapshot and closure.

Read the prepared menu, actual participation/substitutions, public receipt/play record, medical instructions and dated coaching observations before filling the report. Use the relevant active playbook entries and the [player-assessment method](training_camp_and_preseason/player_assessment.md). A concept's presence in the book does not establish that it was taught or called. Distinguish an immediate impression from a completed staff review. Do not invent film viewing, a spoken check, effort, a missed assignment or a technical cause from a statistic alone.

Assess the actual starters, reserves and mixed groups with their supporting players, opposition, assignment and opportunity. A quarterback change does not establish that the entire unit changed. Keep recognition, technique, physical execution and decisions distinct. Give supported strengths and failures their proper weight without requiring equal praise and criticism or a note on every player. The [preseason research](../../docs/preseason_game_reports.md) supplies coaching examples; outside player results do not become branch evidence.

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

Before the week closes, perform this pass:

1. **Evidence:** every score, stat, injury, play, decision, and technical detail traces to generated/canonical evidence.
2. **Causality:** the prose distinguishes what happened from why it plausibly happened. It does not claim a cause the evidence cannot support.
3. **Specificity:** vague praise/blame is replaced by assignment, technique, communication, physical result, processing, field position, or decision evidence when available.
4. **Repetition:** repeated transitions, repeated adjectives, repeated sentence shapes, and duplicate box-score facts are cut.
5. **Voice:** narration sounds like a football report; Stone sounds like Stone; reporters do not all sound like the same writer.
6. **Compression:** remove any sentence whose only job is to announce that the previous sentence mattered.

## Box-score presentation rule

Every played game gets a **full statistical box score for both teams**, generated from the game's receipt. Never type or edit box-score numbers by hand.

Place this block where the box score belongs, then fill it:

```
<!-- box-score event=EVENT_ID team=[Your team] -->
<!-- /box-score -->
```

`python scripts/render_box_score.py --season YEAR --write career/[year]/regular_season/week_NN_<away>_at_<home>/output.md`

The generated box score follows the standard NFL layout: a team comparison, then each club in turn (your team first) with Passing, Rushing, Receiving, Fumbles, Defense, Kicking, Punting and Returns. Every player with a generated statistic in a category appears in it; Passing, Rushing, Receiving and Defense end with a **Team total** row. A line whose player attribution could not be preserved appears as **Team / unattributed**.

The box score shows only statistics the engine generates. Derived columns are arithmetic on those counts: completion percentage, averages and the official NFL passer rating (RTG) from completions, attempts, yards, touchdowns and interceptions. The engine does not generate red-zone or down-and-distance data, so neither appears. `scripts/validate_repository.py` fails if a filled box score differs from its receipt.

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

---

~~~
**[Coach Name] ([age]) | [Title] | [Team] ([W]-[L])**
**[Season Year] | [Phase label] | [Date range] | [Result/current game context]**
**Next:** [Week N+1 vs Opponent / Postseason round / Offseason begins]  |  **Days since career start:** [X]

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

## 2. Week setup and game preparation

**Opponent context:** [What the staff sees on film, current opponent strengths/problems, and relevant public availability/context. State specific evidence. Do not manufacture a storyline.]

**Stone's priorities:** [Specific offensive, defensive, situational, and team-wide goals Stone establishes for the week.]

**Practice / teaching emphasis:** [What is drilled, corrected, simplified, or expanded. Include protection, communication, situational work, film cutups, and teaching changes only when relevant.]

**Workload / recovery:** [Any meaningful practice-load, travel, recovery, or medical constraint that changes preparation. Do not dump routine logistics.]

## 3. Pregame media Q&A

**Reporter:** [Question grounded in public context.]

**Stone:** [Direct answer in Stone's established voice. Specific football when possible, private matters protected.]

[Repeat only for the number of questions justified by the week.]

## 4. Game

### Week [N]: [Opponent] at [Location]

**Final:** [Team] [Score], [Opponent] [Score] | [W/L]
**Location:** [Stadium] | [conditions only if established and material]

### Game narrative: selected highlights

[Routine target: 300-450 words. High-stakes target: 500-750 words. Follow a selected chronology, not a possession log. Use only meaningful generated sequences. Paragraphs do not need to map one-to-one to drives. Explain concrete football cause and consequence. Include Stone's in-game management only where he actually made or approved a recorded decision. Do not invent interiority, fake technical precision, atmosphere, or a moral at the end.]

### Report to render

**Review:** [Immediate postgame assessment, or completed staff review with its actual evidence-through date.]

#### What the staff wanted to see

[Briefly identify the questions from preparation the game was meant to test, the prepared menu, personnel opportunities and material workload limits. Explain why a player or combination received that work when the reason is recorded. Distinguish the plan from who actually played. The recorded pregame exchange belongs in section 3; do not repeat it here.]

#### How the game unfolded

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

[Use named paragraphs with the [player-assessment method](training_camp_and_preseason/player_assessment.md). State what the player did well, what he did poorly where supported, and what that means for his particular job. Include meaningful contrary evidence in the same assessment. Connect the game to the question from preparation or earlier games: was it answered, partly answered, contradicted or never tested? Show how an error or successful technique held up on another opportunity when recorded. Do not merely repeat the scoring plays or the unit section.]

[Give the reader the distinction that matters: dependable work, a useful performance earning another look, a recurring limitation, or an unresolved comparison. Those are judgments to express in normal prose, not mandatory labels or grades. A receiver can help through spacing or blocking without a catch; a defensive back can execute his coverage without a target. Credit those jobs only with actual evidence. A productive reserve with a narrower menu has established something useful within that menu, not mastery of the entire offense. Playing little, being medically limited or never encountering the planned test is not failure.]

#### Stone's decisions and the next practice

[Record consequential choices Stone actually made, why the recorded football problem prompted them and what happened afterward. Separate the choice from its execution. Consider the staff's teaching, call, personnel support and sideline operation alongside the players. Do not rewrite Stone's intentions from the final score or invent a private reaction.]

[Give each material correction its responsible coach and next useful opportunity: film/meeting clarification, a technique period, a combination rep, a situation or a later game exposure as appropriate. Explain what would count as improvement in that job. Use that season's actual staff; a proposed correction is not a delivered lesson, and a planned retest is not a successful rep. Distinguish a recommendation for different work from Stone's actual role decision. Link any actual role or availability change to its owner. Keep recorded postgame media in section 5, in Stone's established voice; do not manufacture quotes in a retrospective rewrite. Identify the next work or consequential choice; section 6 carries those priorities forward without repeating the assessment.]

#### Box score

<!-- box-score event=[EVENT_ID] team=[Your team] -->
<!-- /box-score -->

[Filled by `scripts/render_box_score.py --season YEAR --write`; see the box-score presentation rule.]

**Standout performances**
- [Player]: [Specific football evidence and relevant statistics.]
- [Player]: [Specific football evidence and relevant statistics.]
[Use 2-4 only when earned by the generated game.]

**Material game-management decisions:** [Only consequential fourth-down, clock, challenge, timeout, personnel, tempo, or other head-coach decisions actually made. Separate the quality of the decision from whether the result worked. Omit if none.]

**Injuries / availability from the game:** [Only generated/medically established changes. Omit if none.]

## 5. Postgame media Q&A

**Reporter:** [Question arising from what actually happened.]

**Stone:** [Answer in Stone's established voice. Do not restate the recap. Address the football question.]

[Use 3-5 substantive questions for a routine game; more only when the stakes/result justify it.]

## 6. Coaching takeaways and next-week carry-forward

**What held up:** [Execution, communication, preparation, or unit strengths actually supported by the week.]

**What must be corrected:** [Specific football problems. Distinguish assignment, communication, technique, physical loss, processing, medical limitation, and teaching failure.]

**Next-week carry-forward:** [What Stone/staff will retain, reduce, correct, or investigate. Do not pre-resolve next week's outcome.]

## 7. Weekly personnel and availability snapshot

This is a **complete unit-level weekly view**, not a second copy of the full roster. Every functional position group gets a current line, but name only the starters, primary rotational players, specialists, and anyone whose role or availability is material to the week.

Keep four different questions separate:

1. **Role:** what the player is currently being asked to do.
2. **Availability:** whether and how the player can participate, using only the canonical medical/game-status information actually established.
3. **Evaluation:** the staff's current qualitative football read, using the established five-tier language only where it adds value.
4. **This week's evidence:** what changed, held up, or became a concern in this specific week.

A strong game does not automatically raise a player's underlying tier, and a bad game does not automatically lower it. Weekly production is evidence. Role, health, matchup, assignment quality, and the broader body of work still control the current evaluation.

### Offense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
|---|---|---|---|---|
| QB | QB1: [Name] ([tier if useful]); QB2: [Name only when role/availability is material] | [Canonical status / limitation] | [Processing, accuracy, ball security, pocket management, movement, command, or other supported read] | [What the week actually showed; distinguish player execution from protection, receiver, play-call, or teaching issues] |
| RB / FB | [Lead runner, third-down back, short-yardage back, FB or other materially used roles] | [Status] | [Vision, contact balance, pass protection, receiving, ball security, short-yardage value, etc.] | [Role change, workload issue, protection result, explosive runs, missed assignment, or no material change] |
| WR | [Primary outside receivers, slot, and any material rotational/return role] | [Status] | [Separation, releases, route detail, catch-point work, blocking, communication, etc.] | [Who actually affected the week and how; do not rank the whole room from raw receiving totals] |
| TE | [Inline, move, receiving, blocking, or hybrid roles actually in use] | [Status] | [Blocking, route value, hands, assignment reliability, versatility, etc.] | [Material contribution/problem, role change, or no material change] |
| OL | LT: [Name]; LG: [Name]; C: [Name]; RG: [Name]; RT: [Name] | [Any individual limitation or lineup contingency] | [Run blocking, pass protection, communication, stunt/pickup handling, short-yardage movement, overall cohesion] | [Identify the exact edge/interior issue, pressure source, communication problem, lineup change, or strength when supported] |

**Offensive role changes:** [New starter, rotation change, package change, reduced/increased responsibility, backup promotion, or "none." Do not manufacture a change because one player had a productive game.]

### Defense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
|---|---|---|---|---|
| Interior DL | [Primary interior starters/rotation and role if material] | [Status] | [Run fits, anchor, penetration, gap discipline, rush contribution, rotation quality] | [What held up or failed this week] |
| Edge | [Primary edge defenders / rush or contain roles] | [Status] | [Pressure quality, edge setting, rush plan, finish, discipline] | [Pressure source, lost edge, containment issue, matchup win, or no material change] |
| LB | [Primary off-ball linebackers and subpackage roles] | [Status] | [Run fits, coverage, communication, tackling, pressure responsibility] | [Assignment/communication/physical result from the week] |
| CB | [Outside corners and any material matchup assignment] | [Status] | [Coverage, leverage, ball production, tackling, penalty/technique issues] | [Targeted matchup result, role change, or no material change] |
| Nickel / dime | [Primary slot/subpackage defenders if used] | [Status] | [Coverage, pressure, fit, communication, versatility] | [Subpackage-specific evidence or issue] |
| S | [Primary safeties and deep/box/matchup roles] | [Status] | [Range, angles, tackling, communication, coverage responsibility] | [Material play, bust, support strength, rotation change, or no material change] |

**Defensive role changes:** [New starter, package/rotation change, matchup role, reduced/increased responsibility, or "none."]

### Special teams

| Unit | Primary personnel / role | Availability | Current qualitative read | This week's evidence / issue |
|---|---|---|---|---|
| K | [Name] | [Status] | [Range/consistency only from established evidence; do not invent precision] | [Makes/misses or operation issue that mattered] |
| P | [Name] | [Status] | [Placement, hang-time/field-position value only when supported] | [Material punt/field-position evidence] |
| LS / operation | [Name(s) only if material] | [Status] | [Snap/hold/operation reliability if evidenced] | [Only note when the operation materially affected a play or availability] |
| Kick return | [Primary returner(s)] | [Status] | [Decision-making, ball security, field-position value] | [Material return or decision] |
| Punt return | [Primary returner(s)] | [Status] | [Decision-making, security, return value] | [Material return/fair-catch/ball-security issue] |
| Coverage units | [Core coverage players only when material] | [Status] | [Lane integrity, leverage, tackling, discipline] | [Breakdown, strong field-position work, penalty, or no material change] |

### Material personnel changes this week

- **Injuries / limitations:** [New injury, worsening/improving limitation, return, or no material change.]
- **Activations / elevations / transactions:** [Only changes that actually occurred.]
- **Depth-chart / rotation changes:** [Only decisions actually made. An open competition remains open until Stone/staff resolve it.]
- **Role consequences for next week:** [Who may need a larger/smaller role, what remains unresolved, or no material change. Do not pre-resolve the next game.]

Do not repeat the entire roster or every unchanged backup. `career/[year]/roster.md` and Document 4 remain authoritative for full personnel ownership and status. This section exists to show the coach the **current functional shape of the team** entering the next football decision.

## 8. Week closure

**Record after game:** [W-L-T]
**Division / conference position:** [From `career/[year]/standings.md`: division place and current seed, when useful.]
**Statbook:** [Through week and coverage status of the regenerated `career/[year]/stats/` views; leaders complete or withheld.]
**Ledger entry:** [Entry N]
**Next event:** [Exact next football/calendar event]
~~~

Coach-facing evaluation uses the established qualitative language only: **Elite / Plus / Average / Below-Average / Replacement-Level** where a tier is actually useful. Never expose hidden numeric ratings, probabilities, grades, or roster-survival percentages.
