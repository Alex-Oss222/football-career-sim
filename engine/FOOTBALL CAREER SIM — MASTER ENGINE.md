# FOOTBALL CAREER SIM — MASTER ENGINE

> This document governs all modules. Player Module, Coaching Module, Interview Module, and State Block all defer to the rules defined here. If a module-level rule conflicts with the Master Engine, the Master Engine wins.

---

## 1. SIMULATION MODE

**REALISTIC ONLY.**

There are no difficulty settings. There are no buffs, nerfs, pity mechanics, or user-selected consequence scaling. All outcomes derive from ratings, opponent quality, context factors, league environment, and variance.

---

## 2. REALISM RULES

### 2.1 Anti-Softening (Always Active)
- No sugarcoating poor performance.
- No participation trophies. No "great effort despite the result."
- Success does not erase future risk.
- One good game does not guarantee the next.
- Praise must be earned and is always temporary.
- No protagonist immunity. The player character is subject to the same probabilities as every other entity in the simulation.

### 2.2 Anti-Scripted-Misery (Always Active)
- Criticism must be proportional to role, expectation, and result.
- Coaches, media, and teammates are self-interested and outcome-sensitive — not uniformly hostile.
- Earned praise is allowed when the state supports it.
- Careers are shaped by cumulative probability, not scripted drama beats.
- There is no checklist of mandatory adversity events. Setbacks emerge from the simulation state, not from a quota.
- Reality includes success, not just failure. A player who performs at a 92 in a must-win game should feel that — briefly — before the next challenge arrives.

### 2.3 Proportional Tone Rule
The simulation's tone is calibrated to the gap between **expectation** and **result**:

| Result vs Expectation | Tone |
|---|---|
| Far exceeded | Earned praise + immediate pivot to next challenge |
| Met | Acknowledged, not celebrated. "That's the job." |
| Slightly below | Direct criticism, no consolation |
| Far below | Consequences: benchings, demotions, lost trust, media heat |
| Catastrophic | Career-altering fallout proportional to the failure |

### 2.4 NPC Behavior Rules
- Coaches have personalities generated at creation. They are consistent with those personalities, not generically harsh or generically kind.
- Media coverage reflects market size, program profile, and recent results — not a fixed negativity percentage.
- Teammates respond to your play, your personality, and shared history. Respect is earned and lost dynamically.
- No NPC exists solely to validate or solely to antagonize the player character.

---

## 3. RANDOMNESS POLICY

### 3.1 Tape System (Optional)
The simulation supports two variance modes:

**MODE A — User-Supplied Tape (Default if tape is provided)**
- User pastes a block of random integers (0–99) at any time.
- The engine consumes values sequentially from the tape for all rolls.
- Tape position is tracked in the State Block.
- When tape is exhausted, the engine notifies the user and requests more.
- Tape values are never skipped, reused, or reordered.

**MODE B — Engine-Generated Variance (Default if no tape is provided)**
- The LLM generates contextually appropriate outcomes using internal variance.
- Outcomes must still respect all probability distributions defined in the modules (injury rates, development curves, performance formulas).
- The engine logs what each "roll" produced and what it was used for.
- Command: `"Show rolls"` displays the roll log for the current turn.
- Command: `"Audit on"` displays rolls, formulas, and outcome math for every turn going forward.
- Command: `"Audit off"` returns to standard output.

**MODE SWITCHING:**
- User can switch modes at any time by pasting tape (enters Mode A) or saying `"No tape"` (enters Mode B).
- When switching from A to B mid-session, unused tape is discarded.
- When switching from B to A, the user supplies fresh tape and the cursor resets.

### 3.2 Variance Integrity Rules
Regardless of mode:
- Outcomes must be consistent with the probability distributions defined in the active module.
- The engine must not adjust outcomes to fit a narrative arc, reward persistence, punish success, or create artificial drama.
- Streaks (good and bad) are allowed to occur naturally. The engine does not force regression or force continuation.
- Variance is not storytelling. It is input. The narrative is built around whatever the variance produces.

---

## 4. ANTI-PROTAGONIST SYSTEM

### 4.1 Core Principle
The player character receives no narrative privilege. They exist inside the simulation on the same terms as every other entity.

### 4.2 Structural Rules

**Independent Outcomes:**
- Player performance and team outcome are generated independently.
- A player can have a great game and the team can still lose.
- A player can have a bad game and the team can still win.
- The player's decision quality influences their personal output. It does not determine the final score.

**No Plot Armor:**
- Injuries follow position-specific base rates modified by fatigue, age, wear, and situation. Being the protagonist does not reduce injury probability.
- Opponents are generated with realistic ratings for their level. They are not weakened to create heroic moments or strengthened to create artificial adversity.
- Depth chart decisions are made by the coach NPC based on performance, not based on the player being the main character.

**Decision Influence, Not Decision Control:**
- Player decisions (training focus, play style, off-field choices) influence probability distributions.
- They do not guarantee outcomes.
- A good decision can still produce a bad result. A bad decision can still produce a good result. Over time, good decisions win — but "over time" can mean seasons, not turns.

### 4.3 Season Expectation Anchoring
At the start of each season, the engine calculates a **Season Expectation Band** based on:
- Team roster quality (average OVR of starters)
- Coaching quality
- Conference/division strength
- Schedule difficulty
- Returning production percentage

The band is a win-loss range (e.g., 7-10 wins to 4-7 wins). The team's actual season result will fall within or near this band unless specific in-sim events (injuries, chemistry collapse, breakout performances) push it outside. The player character's individual brilliance cannot single-handedly move the band by more than ±2 wins.

### 4.4 Upset and Variance Distribution
- At least 15% of games in any season should produce results that defy pre-game probability (upsets in either direction).
- Slumps (3+ game stretches of below-expectation play) should occur naturally when variance clusters. They are not forced, but they are not prevented.
- Breakout stretches are also allowed to occur naturally.

---

## 5. TURN STRUCTURE

### 5.1 Role-Variable Turn Length

Turn length depends on BOTH phase and current role.

#### A. PLAYER CAREER

| Phase | Turn Length |
|---|---|
| Offseason (post-season through spring) | 2 weeks |
| Summer / Camp | 2 weeks |
| Regular Season | 1 week |
| Playoffs / Postseason | 1 game |
| Combine / Pro Day / Draft Week | Event-based |
| Bye Week | 1 week (recovery/development focus) |

#### B. COACHING CAREER — ENTRY & ROOM LEVEL
Applies to: GA / QC / Position Coach

| Phase | Turn Length |
|---|---|
| Staff Building / Hiring Cycle | Event-based |
| Offseason / Spring / Summer | 1 month |
| Camp | 1 month |
| Regular Season | 1 month |
| Playoffs / Bowl Prep / Postseason | 1 round / 1 game block |
| Emergency / high-stakes situation | Zoom-in turn if triggered |

**Design rule:**
These roles advance in larger time blocks because their authority is limited and their work is repetitive by week. The engine summarizes the month through assignments, learning, room development, trust shifts, player progress, and any standout events.

The engine may temporarily zoom in to a shorter turn when:
- A promotion race intensifies
- A firing/hiring event happens
- A conflict erupts
- A major game creates direct pressure on the character
- The user explicitly requests a closer view

#### C. COACHING CAREER — UNIT / ORGANIZATION LEVEL
Applies to: Coordinator / Head Coach

| Phase | Turn Length |
|---|---|
| Offseason | 2 weeks |
| Camp | 2 weeks |
| Regular Season | 1 week |
| Playoffs | 1 game |
| Job Search / Interview | Event-based |

**Design rule:**
These roles stay on normal football time because they own weekly planning, game adjustments, and public accountability.

### 5.2 Role Compression Rule

For GA / QC / Position Coach monthly turns:
- The engine summarizes 3–5 meaningful work blocks within the month.
- Game outcomes are aggregated, not narrated week-by-week.
- Player stats shown for the role must be month-to-date or season-to-date.
- Only one or two standout weekly incidents are surfaced in prose.
- The engine does not write with weekly granularity when the clock is monthly.

### 5.3 Turn Processing Order
Every turn is processed in this order, regardless of module:

```
1. ADVANCE CLOCK — Update date, phase, turn counter.
2. CONTEXT CHECK — Determine active phase, upcoming events, open consequence chains.
3. RANDOM EVENTS — Roll for non-player-driven events (injuries to others, coaching changes, weather, off-field news). These happen TO the world, not just to the player.
4. PLAYER/COACH ACTIONS — Resolve the decisions submitted last turn. Apply skill checks, training, game prep, recruiting calls, etc.
5. PERFORMANCE — If a game occurs this turn, simulate it. Player performance and team outcome generated independently per §4.2.
6. CONSEQUENCES — Update state based on results: depth chart, chemistry, trust, fatigue, wear, media, finances, draft stock, job security.
7. STATE UPDATE — Write all numeric changes to the State Block.
8. NARRATIVE — Generate the turn's written output based on what actually happened in steps 1–7.
9. DECISIONS — Present the decisions for next turn.
```

**Critical rule:** Step 8 (Narrative) must never influence Steps 1–7 (Mechanics). The story follows the math. The math does not follow the story.

### 5.4 Turn Counter
```
Career Turn: Cumulative count from simulation start. Never resets.
Season Turn: Resets each year. Count within current season.
Phase Turn: Resets each phase. Count within current phase (e.g., "Week 3 of regular season").
```

---

### 5.5 OFFSEASON EVALUATION, EXIT MEETINGS, AND JOB CYCLE

At the end of every season, the simulation enters a controlled offseason sequence before the next season begins.

This sequence determines:
- retention
- non-renewal / release
- promotion
- internal reassignment
- contract extension
- external interview access
- external hiring
- blocked mobility when era rules allow it

The offseason sequence happens before normal offseason turns resume.

The full offseason evaluation and job cycle system is defined in the dedicated document: `offseason_evaluation_and_job_cycle.md`. The Master Engine references that document and enforces its rules. What follows here is the structural summary that governs how the offseason integrates with the turn system.

---

#### 5.5.1 ERA RULESET

The offseason sequence follows the active league era. The era is stored in the State Block under `Era Ruleset`.

**NFL 2000 RULESET (default for any simulation set before 2003)**
- No Rooney Rule or mandatory interview quotas.
- Teams may hire without formal diversity interview requirements.
- Clubs may block assistants from interviewing for outside promotions.
- No modern protected "bona fide promotion" interview rights.
- No modern compensatory-pick incentives for developing minority coaches/executives.
- No strict modern postseason interview calendar.
- Head coaches and organizations may move faster and more informally after the season.

**NFL MODERN RULESET (applies to simulations set 2003 and later)**
- Rooney Rule mandates at least one minority candidate interview for HC openings (2003+).
- Expanded Rooney Rule includes coordinator openings (2021+).
- Postseason interview windows are formalized and enforced.
- Bona fide HC promotion exemption exists (team may promote internal candidate without external interviews under specific conditions).
- Compensatory draft pick incentives for teams that develop minority coaches/executives who are hired elsewhere (Resolution JC-2A, 2020+).
- Anti-tampering rules restrict when and how clubs may contact another team's coaching staff.
- The specific version of modern rules depends on the simulation's in-game year. The engine applies the rules as they existed in that year, not retroactively.

**Era Selection Rule:**
- The era is locked at simulation start based on the in-game starting year.
- If the simulation spans across an era boundary (e.g., starts in 2001, reaches 2003), the engine transitions to the new ruleset at the historical effective date and logs the change in Active Consequences.
- The user may override era selection at simulation start with explicit instruction. Otherwise, the engine auto-selects based on the in-game year.

---

#### 5.5.2 OFFSEASON TIME BUBBLE RULE

The offseason evaluation / interview / hiring window uses a TIME BUBBLE.

Meaning:
- Calendar does not advance through ordinary offseason nodes while evaluation and hiring are unresolved.
- Exit meetings, internal evaluations, extension talks, firing decisions, promotion decisions, external job search, and hiring decisions all resolve inside one controlled bubble.
- The bubble may contain multiple scenes or stages.
- Once the bubble resolves, the calendar advances to the correct next offseason node.

This prevents:
- losing calendar coherence
- overlapping contradictory events
- promotion and job-search logic bleeding into ordinary offseason turns

Time Bubble applies to:
- exit meetings
- retention meetings
- contract/renewal talks
- firing / non-renewal
- promotion decisions
- blocked or approved interview requests
- external interview stages
- hiring outcome
- transition into next role

The Time Bubble is tracked in the State Block under `Time Bubble Active` and `Bubble Stage`.

---

#### 5.5.3 OFFSEASON SEQUENCE ORDER

Process in this order:

```
1. SEASON CLOSE
   - Finalize record.
   - Finalize role performance summary.
   - Finalize trust / politics / stress carryover.

2. INTERNAL EVALUATION
   - Role-specific review (see offseason_evaluation_and_job_cycle.md §4).
   - Trajectory review.
   - Scheme mastery review.
   - Organizational need review.

3. EXIT MEETING
   - Honest feedback from proper authority (see offseason_evaluation_and_job_cycle.md §6).
   - Role outlook stated clearly.
   - Strengths / weaknesses / projection.

4. INTERNAL DECISION
   - Retained.
   - Retained with raised expectations.
   - Extended.
   - Promoted.
   - Reassigned laterally.
   - Released / non-renewed.

5. EXTERNAL ACCESS CHECK
   - If retained, determine whether outside interest exists.
   - If retained in 2000-era NFL, club may deny outside interview access.
   - If promoted internally, external search usually ends.
   - If released / non-renewed, job search opens immediately.

6. JOB SEARCH / INTERVIEW MODULE
   - Only if active after internal decision.
   - All applications, interviews, and negotiations resolve inside same time bubble.

7. FINAL OFFSEASON OUTCOME
   - Write new role / team / reporting chain.
   - Reset or update stress, job security, delegated authority, and expectations.

8. ROLE TRANSITION TURN
   - If role or team changes, generate one transition turn before ordinary offseason continues.
```

---

#### 5.5.4 ROLE-SPECIFIC EVALUATION

**GA / QC:**
- Reliability of deliverables
- Film accuracy
- Scout-team execution
- System language fluency
- Chain-of-command discipline
- Anticipation of coach needs
- Whether football intelligence became usable staff work

**Position Coach:**
- Room development
- Meeting quality
- Player trust
- Technical improvement of room
- Room stability / politics
- Quality of input to coordinator / HC

**Coordinator:**
- Unit performance vs expectation
- Install quality
- Adjustment quality
- Play-calling if assigned
- HC alignment
- Media / pressure handling

**Head Coach:**
- Record vs expectation band
- Staff management
- Organizational stability
- Culture health
- Ownership / AD / GM trust
- Playoff / postseason outcome

---

#### 5.5.5 EVALUATION SCORE

The engine produces:

```
Evaluation Score: [0–100]

Bands:
  90–100 → elite trajectory
  80–89  → strong upward trajectory
  70–79  → solid / stable
  60–69  → borderline
  50–59  → at risk
  <50    → failure
```

Every offseason evaluation must also produce:
- Trajectory: [Rising / Stable / Plateau / At Risk / Declining]
- Scheme Mastery Grade
- Trust Position with direct evaluator
- Promotion Readiness: [None / Early / Emerging / Real / Strong]
- Risk Flag: [None / Plateau / Political / Performance / Structural]

---

#### 5.5.6 EXIT MEETING RULE

Exit meeting must be generated with the correct authority:

```
QC / GA         → Coordinator or Head Coach
Position Coach  → Coordinator and/or Head Coach
Coordinator     → Head Coach / GM / Owner equivalent
Head Coach      → Owner / AD / GM equivalent
```

Exit meeting must include:
- What you did well
- Where you improved
- What still limits you
- Whether the club sees you as retained, extended, promoted, blocked, or expendable
- What the next realistic step is

Exit meeting is honest, role-appropriate, and non-theatrical.

---

#### 5.5.7 DECISION OUTCOME

Based on evaluation score + context:

**RETAINED**
- Remains in same role.
- Possible responsibility increase.

**RETAINED WITH RAISED EXPECTATIONS**
- Same role, but organization expects measurable improvement next season.
- Failure to meet raised expectations accelerates hot seat.

**PROMOTION**
- Internal promotion.
- Role payload changes per State Block §6.

**EXTENSION**
- Contract extended (if applicable).

**LATERAL**
- Same level, different team or role.

**RELEASED / NON-RENEWED**
- Contract not renewed / job lost.

**EXTERNAL INTEREST**
- New job opportunities open.
- Interview Module activates.

---

#### 5.5.8 STATE UPDATE AFTER OFFSEASON

The following MUST update:
- current_role
- current_team
- reports_to
- delegated_authority
- job_security reset
- stress adjusted
- career_history entry added
- relationship shifts applied
- Offseason Status fields in the State Block

---

#### 5.5.9 ROLE TRANSITION TURN

If role changes:
- One transition turn is generated.
- Explains why the change happened, what authority changed, and what expectations are now.
- Next turn uses new role rules.

---

#### 5.5.10 2000-ERA NFL MOBILITY RULE

In the 2000 NFL ruleset:
- Assistants do NOT have protected upward-mobility rights.
- The club may block interview requests for outside roles, including promotions.
- Internal retention may coexist with blocked outside mobility.
- Informal reputation still matters: a well-regarded assistant may quietly attract interest, but the current club controls access.

This means the character can:
- Be retained and blocked from outside interviews.
- Be retained and quietly allowed to explore.
- Be promoted internally.
- Be released into the open market.

...depending on trust, politics, and organizational need.

---

#### 5.5.11 CONTRACT / RENEWAL RULE

For assistants and low-level staff:
- Extension does not have to mean long-term security.
- Many renewals are one-year or short-term.
- "Retained" and "renewed" are not the same as "promoted."

Possible outcomes:
- Retained on same deal
- Renewed on new 1-year deal
- Renewed with small raise
- Promoted with title change
- Non-renewed
- Allowed to explore outside jobs
- Blocked from outside jobs

---

#### 5.5.12 ROLE TRANSITION RULE

If role changes, title changes, or team changes:
- Freeze normal offseason progression.
- Generate one transition turn.
- Update reporting chain, authority, expectations, visible data, and turn length.
- Then resume ordinary offseason turns under new role rules.

---

## 6. OUTPUT MODES

### 6.1 Standard Turn (Default)
The default output for every turn. Compact, playable, focused on what matters this turn.

**Structure:**
1. **State Snapshot** — Date, phase, role, record, health, key metrics. 3–5 lines max.
2. **This Period's Football** — What happened on the field or in the building. The core content of the turn.
3. **Body & Availability** — Health, fatigue, injury status. Only if something changed or is relevant.
4. **Depth Chart & Relationships** — Position, competition, chemistry, trust. Only notable changes.
5. **External World** — Media, recruiting, NIL/contract, draft stock. Only active threads.
6. **What Changed** — Numeric summary of attribute/stat/state changes. Compact table or list.
7. **Decision(s)** — What the player/coach must decide before next turn. 2–4 decisions typical. Max 5.

**Rules:**
- Sections with nothing notable to report are omitted, not filled with filler.
- Narrative is integrated into Section 2, not isolated in its own block.
- No section exceeds what is needed to convey the information.

### 6.2 Audit Turn
Command: `"Audit turn"` or `"Audit on"` (persistent)

Adds to Standard Turn:
- All roll values and what they were used for
- Formula inputs and outputs for every calculation
- Probability distributions consulted
- Skill check thresholds and results
- Tape position or engine-generated roll log

### 6.3 Full Report
Command: `"Full report"`

Expands the current turn into the long-form dossier:
- Complete stat lines (season and career)
- Full scouting / draft / NIL / contract breakdown
- All relationship statuses
- Financial detail
- Historical context and trajectory analysis
- Full narrative section

This is the equivalent of the v3.0 integrated turn template — available on demand, not forced every turn.

### 6.4 Quick Turn
Command: `"Quick"`

Compresses the turn to: state snapshot + key result + decisions. No narrative. Used for low-leverage periods.

### 6.5 Sim Forward
Command: `"Sim X"` (where X = number of turns)

Fast-forwards X turns using auto-decisions (per §8). Outputs a summary covering:
- Win/loss results
- Major events only (injuries, benchings, milestones, draft stock shifts)
- Attribute changes (net)
- Any decisions that could not be auto-resolved (pauses sim)

### 6.6 End-of-Season Evaluation Turn
Command: Automatically generated at season close. Can also be triggered with `"Season eval"`.

Uses the dedicated end-of-season output format defined in `end_of_season_output_format.md`. This is distinct from the ordinary weekly/monthly turn and from the Full Report. It covers the offseason evaluation sequence (§5.5) in a structured, role-specific format.

---

## 7. CONTEXT FACTORS

These are **not** difficulty modifiers. They are state-derived inputs that affect performance and outcome calculations. They exist because football outcomes are context-dependent.

### 7.1 Performance Context Factors
| Factor | Source | Effect |
|---|---|---|
| Chemistry | Team chemistry rating | Execution quality modifier |
| Fatigue | Accumulated fatigue | Physical performance, injury risk |
| Health | Current health % | All physical attributes scaled |
| Matchup | Player OVR vs opponent OVR | Positional advantage/disadvantage |
| Weather | Generated per game | Position-specific effects |
| Crowd/Venue | Home/away, rivalry, stakes | Composure check modifier |
| Scheme Fit | Player skills vs team scheme | Role effectiveness |

### 7.2 Development Context Factors
| Factor | Source | Effect |
|---|---|---|
| Age | Current age | Development rate multiplier |
| Coach Quality | Coaching staff rating | Training effectiveness |
| Facilities | Program tier | Recovery, development ceiling |
| Scheme Fit | Skills vs system | Which skills develop faster |
| Playing Time | Starter/backup/reserve | Experience-based growth rate |

### 7.3 Career Context Factors
| Factor | Source | Effect |
|---|---|---|
| Market Size | Team location | Media exposure, NIL/endorsement value |
| Program Prestige | Historical program strength | Recruiting, draft visibility |
| Conference Strength | Conference quality | Strength of schedule, draft evaluation |
| Coaching Stability | Staff tenure | Chemistry continuity, scheme mastery |

---

## 8. AUTO-DECISION DEFAULTS

When the user does not respond within 3 turns, or during `Sim X` fast-forward, decisions are resolved automatically based on the character's personality and state:

| Decision Type | Auto-Resolution Logic |
|---|---|
| Training Focus | Lowest critical skill for current position and role |
| School Choice | Highest-ranked school offering playing time |
| Injury Management | Sit if health < 70%. Play if Warrior > 60 AND health > 55% |
| Contract Offer | Accept if ≥ 85% of market value |
| Transfer | Stay unless depth chart ≥ 4th AND better offer exists |
| Draft Declaration | Declare if projected Round 1–3. Return if Round 5+ |
| Academic | Maintain minimum eligibility effort (Scholar-weighted) |
| NIL Deal | Accept highest offer requiring < 10 hrs/month |
| Retirement | Continue if starting. Retire if 3rd string+ AND age > 35 |
| Coaching Decisions | Delegate to strongest available subordinate |

Auto-decisions are noted in the turn output so the user knows what was chosen on their behalf.

---

## 9. MODULE LOADING

### 9.1 Active Modules
Only relevant modules are active at any time:

| Career Phase | Active Modules |
|---|---|
| Player (HS / College / NFL) | Master Engine + Player Module + State Block |
| Coaching Transition | Master Engine + Player Module (closing) + Coaching Module (opening) + State Block |
| Coaching Career | Master Engine + Coaching Module + State Block |
| Job Search / Interview | Master Engine + Coaching Module + Interview Module + State Block |
| Offseason Evaluation | Master Engine + Coaching Module + Offseason Evaluation & Job Cycle + State Block |

### 9.2 Module Activation
- **Player Module** activates at simulation start. Deactivates at retirement or coaching transition.
- **Coaching Module** activates when the player enters coaching. Does not load during player career.
- **Interview Module** activates during active job searches. Deactivates when hired or search abandoned.
- **Offseason Evaluation & Job Cycle** activates at season close. Deactivates when the time bubble resolves and ordinary offseason resumes.
- **State Block** is always active.

---

## 10. COMMANDS

### Universal Commands (All Modules)
```
"Next"           — Process next turn (Standard output)
"Quick"          — Process next turn (compressed)
"Sim X"          — Fast-forward X turns
"Audit on/off"   — Toggle audit output
"Audit turn"     — One-time audit for this turn only
"Full report"    — Long-form dossier for current state
"Stats"          — Display all current attributes
"State"          — Display compact State Block
"Save"           — Export full State Block for continuation
"Show rolls"     — Display roll log for current turn
"Help"           — List all available commands
"Season eval"    — Trigger end-of-season evaluation turn manually
```

### Module-Specific Commands
Defined within each module document. The Master Engine does not restrict what commands a module can define, but all module commands must respect the turn processing order (§5.3) and realism rules (§2).

---

## 11. INITIALIZATION

### 11.1 New Simulation Start
When the user says `"Start simulation"` or equivalent:

1. **Module Selection:** Default is Player Module. User can specify `"Start as coach"` to begin with Coaching Module.
2. **Character Creation:** User provides details or accepts defaults (defined in active module).
3. **Tape Decision:** User pastes tape (Mode A) or proceeds without (Mode B auto-activates).
4. **Era Determination:** Engine determines era ruleset based on in-game starting year. User may override.
5. **Season Expectation Band:** Calculated for Year 1 based on team context.
6. **Turn 1 begins.**

### 11.2 Continuation from Save
When the user pastes a State Block:
1. Engine validates the state (including Offseason Status fields and Era Ruleset).
2. Loads appropriate modules based on career phase.
3. If Time Bubble Active = Yes, resumes offseason sequence at the saved Bubble Stage.
4. Resumes from the saved turn.

---

## 12. INTEGRITY RULES

These override everything else in the simulation:

1. **Math before narrative.** Outcomes are calculated first. The story wraps around them. Never reverse.
2. **State is truth.** If the State Block says health is 62%, the narrative cannot describe the player as fully healthy.
3. **No retroactive adjustment.** Once a turn's outcomes are generated, they are final. They cannot be softened, rerolled, or revised in the same turn.
4. **Consistency across turns.** An injury in Turn 5 still affects Turn 6. A promise made in Turn 8 is remembered in Turn 12. Consequence chains do not evaporate.
5. **Module boundaries are enforced.** Coaching Module systems do not bleed into Player Module turns and vice versa.
6. **Caps are absolute.** Attribute caps defined in the active module are enforced every turn. No attribute may exceed its current cap for any reason.
7. **No invisible buffs.** Every factor affecting an outcome must be traceable to a state value, context factor, or roll. Nothing is applied "because it would make a better story."
8. **Offseason outcomes are earned.** No auto-promotion, no auto-retention. Every year-end role outcome must pass through the evaluation sequence (§5.5) and be justified by performance, trust, and organizational context.
9. **Era rules are binding.** The engine applies the mobility, hiring, and interview rules of the active era, not the most convenient or most modern version.

---

## 12A. ROLE AUTHORITY & CHAIN OF COMMAND

The character acts only within the authority of the current role unless temporary or permanent extra authority is explicitly granted in the State Block.

### Authority Bands

| Role | Authority Scope |
|---|---|
| GA / QC | Support work, film, scout team, errands, learning, internal observations |
| Position Coach | Room teaching, drills, room evaluation, player development, limited input upward |
| Coordinator | Unit installation, game plan, adjustment recommendations, play-calling if assigned |
| Head Coach | Full staff direction, roster authority within org structure, public accountability |

### Chain of Command
The engine must track:
- Who the character reports to
- Whose system the character is serving
- Whether the character has delegated authority beyond the base role

### Hard Boundary Rule
The character does not:
- Make decisions above role level
- Speak with authority above role level
- Receive media/platform power above role level
- Change scheme above role level

...unless the State Block explicitly says extra authority has been granted.

### Delegated Authority Rule
If extra authority is granted, it must appear in the State Block under:

```
Delegated Authority: [specific area]
Source: [who granted it]
Duration: [turn-limited / ongoing]
```

This field is blank by default. Extra authority is the exception, not the norm.

---

*Master Engine — Complete. Governs Player Module, Coaching Module, Interview Module, Offseason Evaluation & Job Cycle, and State Block.*