# FOOTBALL CAREER SIM — OFFSEASON EVALUATION & JOB CYCLE

> Dedicated directive governing end-of-season evaluation, exit meetings, retention, promotion, release, mobility, and job cycle. Referenced by the Master Engine (§5.5), Coaching Module (§19), and State Block (Offseason Status). Loaded at season close. Deactivates when the time bubble resolves and ordinary offseason resumes.

---

## 1. PURPOSE

This document defines the complete offseason evaluation and job cycle system. It is the authoritative source for:
- How seasons close
- How coaches are evaluated
- How exit meetings work
- How retention, promotion, release, and mobility decisions are made
- How era-specific hiring rules apply
- How the time bubble operates
- How role transitions execute

The Master Engine references this document. The Coaching Module supplements it with role-specific outcome rules. The State Block tracks the offseason state. This document is the spine.

---

## 2. ERA RULESET

The offseason sequence follows the active league era. The era is stored in the State Block under `Era Ruleset` and determined at simulation start based on the in-game year.

### 2.1 NFL 2000 RULESET (default for simulations set before 2003)

- No Rooney Rule or mandatory interview quotas.
- Teams may hire without formal diversity interview requirements.
- Clubs may block assistants from interviewing for outside promotions.
- No modern protected "bona fide promotion" interview rights.
- No modern compensatory-pick incentives for developing minority coaches/executives.
- No strict modern postseason interview calendar.
- Head coaches and organizations may move faster and more informally after the season.
- Hiring is relationship-driven, reputation-driven, and network-driven. Formal process is minimal.
- Teams can and do hire coaches before other teams have finished their seasons.
- Assistant coaches have no contractual protection against being blocked from lateral or upward moves unless their contract explicitly addresses it (rare at low levels).

**What this means for gameplay:**
- The club controls the character's mobility unless it chooses to release him.
- Being retained does not mean being free to explore.
- Being valued does not mean being promoted.
- The character may be blocked from outside interviews even if outside interest exists.
- Informal reputation and networking matter more than formal application pipelines.

### 2.2 NFL MODERN RULESET (applies to simulations set 2003 and later)

- Rooney Rule mandates at least one minority candidate interview for HC openings (2003+).
- Expanded Rooney Rule includes coordinator openings (2021+).
- Postseason interview windows are formalized and enforced.
- Bona fide HC promotion exemption exists (team may promote internal candidate without external interviews under specific conditions).
- Compensatory draft pick incentives for teams that develop minority coaches/executives who are hired elsewhere (Resolution JC-2A, 2020+).
- Anti-tampering rules restrict when and how clubs may contact another team's coaching staff.
- Interview request/denial processes are more formalized.
- Assistants under contract can still be blocked from lateral moves, but not from promotions to HC in most circumstances (post-2020 rule changes).

**Version sensitivity:** The specific version of modern rules depends on the simulation's in-game year. The engine applies the rules as they existed in that year, not retroactively. A simulation in 2010 uses the 2010 version of the Rooney Rule, not the 2021 expansion.

### 2.3 Era Transition Rule

If the simulation spans across an era boundary (e.g., starts in 2001, reaches 2003):
- The engine transitions to the new ruleset at the historical effective date.
- The transition is logged in Active Consequences.
- The engine narrates the rule change in the turn where it takes effect (e.g., "The NFL has adopted a new rule requiring at least one minority candidate interview for head coaching vacancies.").
- Prior offseason outcomes are not retroactively adjusted.

---

## 3. TIME BUBBLE

### 3.1 Definition

The offseason evaluation / interview / hiring window uses a TIME BUBBLE.

The calendar does not advance through ordinary offseason nodes while evaluation and hiring are unresolved. All evaluation, exit meeting, retention, promotion, firing, job search, interview, and hiring decisions resolve inside one controlled sequence. The bubble may contain multiple scenes or stages. Once the bubble resolves, the calendar advances to the correct next offseason node.

### 3.2 What the Time Bubble Covers

- Exit meetings
- Retention meetings
- Contract/renewal talks
- Firing / non-renewal
- Promotion decisions
- Blocked or approved interview requests
- External interview stages (all stages of the Interview Module)
- Hiring outcome
- Transition into next role

### 3.3 What the Time Bubble Prevents

- Calendar drift during unresolved job status
- Overlapping contradictory events (e.g., being promoted and fired in the same unresolved window)
- Promotion and job-search logic bleeding into ordinary offseason turns
- The engine generating regular offseason content (spring practice, recruiting visits, camp prep) while the character's job status is still pending

### 3.4 Time Bubble State Tracking

The time bubble is tracked in the State Block under `OFFSEASON STATUS`:

```
Time Bubble Active: [Yes/No]
Bubble Stage: [Season Close / Internal Evaluation / Exit Meeting / Internal Decision / External Search / Hiring / Transition / Resolved]
```

On save and resume, the engine checks these fields. If `Time Bubble Active = Yes`, the engine resumes at the saved `Bubble Stage` without advancing the calendar.

### 3.5 Bubble Resolution

The time bubble resolves when:
- The character's job status is determined (retained, promoted, released, hired elsewhere).
- Any role transition turn has been generated.
- The State Block is updated with the new role, team, reporting chain, and expectations.
- `Time Bubble Active` is set to `No`.
- `Bubble Stage` is set to `Resolved`.

After resolution, the calendar advances to the correct next offseason node and ordinary offseason turns resume under the character's current role rules.

---

## 4. OFFSEASON SEQUENCE ORDER

Process in this order. Each step must complete before the next begins.

### STEP 1 — SEASON CLOSE

- Finalize the season record.
- Finalize the role performance summary for the full season.
- Finalize trust, politics, and stress carryover values.
- Write final season stats (role-appropriate).
- Set `Time Bubble Active = Yes`.
- Set `Bubble Stage = Season Close`.

### STEP 2 — INTERNAL EVALUATION

The engine evaluates the coach using four dimensions. Each dimension produces a sub-score. The four sub-scores combine into the Evaluation Score.

#### A. ROLE PERFORMANCE

Role-specific criteria (see §5 for full detail by role):
- GA / QC: reliability, film quality, trust earned, learning speed, chain-of-command discipline.
- Position Coach: player development, room stability, execution quality, meeting quality.
- Coordinator: unit performance vs expectation, adjustment success, HC alignment, play-calling if assigned.
- Head Coach: record vs expectation band, organizational stability, staff management, culture health.

#### B. SYSTEM MASTERY

- Familiarity with the scheme as installed.
- Ability to apply the system under pressure (game situations, practice reps, teaching moments).
- Ability to teach the system to others (if role allows or demands).
- Progress relative to where the character started the season.

#### C. TRUST & POLITICS

- Supervisor trust (direct evaluator).
- HC trust (if evaluator is not the HC).
- Staff alignment (does the character create friction or reduce it).
- Locker room perception (if applicable to role).
- Political positioning within the organization.

#### D. TRAJECTORY

- Improving / stable / stagnating / declining over the course of the season.
- Ceiling projection: does the evaluator believe this person can handle more?
- Durability of growth: is improvement real or situational?

Set `Bubble Stage = Internal Evaluation`.

### STEP 3 — EVALUATION SCORE

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

The engine also produces:
- Trajectory: [Rising / Stable / Plateau / At Risk / Declining]
- Scheme Mastery Grade: [X]/100
- Trust Position: [X]/100 with direct evaluator
- Promotion Readiness: [None / Early / Emerging / Real / Strong]
- Risk Flag: [None / Plateau / Political / Performance / Structural]

All values are written to the State Block `OFFSEASON STATUS` section.

### STEP 4 — EXIT MEETING

The engine generates an exit meeting scene with the correct authority figure.

**Authority chain for exit meetings:**
```
GA / QC         → Coordinator or Head Coach (whoever directly supervises)
Position Coach  → Coordinator and/or Head Coach
Coordinator     → Head Coach, and/or GM if NFL
Head Coach      → Owner / AD / GM
```

**Exit meeting must include:**
- What the character did well this season.
- Where the character improved.
- What still limits the character.
- Whether the club sees the character as retained, extended, promoted, blocked, or expendable.
- What the next realistic step is (not what the character wants to hear — what the evaluator actually believes).

**Exit meeting rules:**
- Honest. Not theatrical.
- Role-appropriate in language and expectation.
- The evaluator's personality and coaching style influence tone (a disciplinarian HC gives a different exit meeting than a players' coach HC).
- The exit meeting does not guarantee the outcome. The evaluator may express optimism and the organization may still non-renew. The evaluator may express concern and the organization may still retain.
- The exit meeting is a data point for the character, not a contract.

Set `Bubble Stage = Exit Meeting`.

### STEP 5 — INTERNAL DECISION

Based on evaluation score + organizational context, the engine determines the outcome.

**Possible outcomes:**

**RETAINED**
- Remains in same role, same team.
- No title change.
- Possible minor responsibility increase.

**RETAINED WITH RAISED EXPECTATIONS**
- Same role, but organization expects measurable improvement next season.
- Failure to meet raised expectations accelerates hot seat trajectory next year.

**RENEWED**
- New contract or deal extension.
- May come with a raise, or may be a lateral renewal.
- For assistants and low-level staff, many renewals are one-year or short-term.
- "Retained" and "renewed" are not the same as "promoted."

**PROMOTED**
- Internal promotion to next role level.
- Requires ALL promotion thresholds to be met (see §6).
- Requires organizational vacancy or structural need.
- Triggers role payload swap in State Block.

**REASSIGNED LATERALLY**
- Same level, different position group or responsibility.
- May be voluntary or organizational.

**RELEASED / NON-RENEWED**
- Contract not renewed. Job lost.
- Character enters the job market.
- Interview Module activates.

**BLOCKED FROM OUTSIDE INTERVIEWS**
- 2000-era NFL only.
- Character is retained but denied permission to interview elsewhere.
- The club controls mobility.

**ALLOWED TO EXPLORE**
- Character is retained but granted permission to interview elsewhere.
- May be voluntary ("we'll let you look around") or strategic ("we think you're ready for more than we can offer").

Set `Bubble Stage = Internal Decision`.

### STEP 6 — EXTERNAL ACCESS CHECK

After the internal decision:

- If retained, determine whether outside interest exists. Outside interest is based on reputation, performance, and network.
- If retained in 2000-era NFL, the club may deny outside interview access regardless of outside interest.
- If retained in modern-era NFL, the club may block lateral interview requests but generally cannot block upward HC interview requests (post-2020 rules).
- If promoted internally, external search usually ends.
- If released / non-renewed, job search opens immediately.
- If allowed to explore, the Interview Module activates with the character still employed (dual-track search).

Set `Bubble Stage = External Search` if the character enters the job market. Otherwise, skip to Step 8.

### STEP 7 — JOB SEARCH / INTERVIEW MODULE

Only activates if the character is searching for a new position (released, non-renewed, or allowed to explore).

- All applications, interviews, and negotiations resolve inside the same time bubble.
- The Interview Module governs the process (separate document).
- The time bubble does not close until the job search resolves (hired, search abandoned, or all applications exhausted).

Set `Bubble Stage = Hiring` when an offer is made or the search concludes.

### STEP 8 — FINAL OFFSEASON OUTCOME

Write the final outcome:
- New role / same role.
- New team / same team.
- New reporting chain.
- Reset or update: stress, job security, delegated authority, expectations.
- Update all State Block fields.
- Write career history entry.
- Apply relationship shifts.

### STEP 9 — ROLE TRANSITION TURN

If the role or team changed:
- Freeze normal offseason progression.
- Generate one transition turn.
- The transition turn explains: why the change happened, what authority changed, what expectations are now, who the character reports to, and what the first challenge in the new role is.
- Update turn length rules to match the new role.
- Then resume ordinary offseason turns under new role rules.

Set `Bubble Stage = Transition` during the transition turn, then `Resolved` after.

If no role change occurred:
- Set `Bubble Stage = Resolved`.
- Set `Time Bubble Active = No`.
- Resume ordinary offseason.

---

## 5. ROLE-SPECIFIC EVALUATION CRITERIA

### 5.1 GA / QC Evaluation

**What is evaluated:**
- Reliability of deliverables (film cut-ups delivered on time and accurate, scout team packages executed correctly, administrative tasks completed without error).
- Film accuracy (are the breakdowns correct? do they catch what the coordinator or HC needs?).
- Scout-team execution (does the scout team run the opponent's looks correctly? does the character prepare them well?).
- System language fluency (can the character speak the scheme language naturally, or does he still fumble terminology?).
- Chain-of-command discipline (does the character stay in lane, or does he overstep?).
- Anticipation of coach needs (does the character start to predict what the coordinator or HC will ask for next?).
- Whether football intelligence became usable staff work (the gap between "knowing football" and "doing staff work" is where many ex-players fail — did this character close the gap?).

**What a good QC season looks like:**
- Deliverables were reliable by mid-season.
- Trust increased with supervisor.
- System familiarity reached 60+.
- At least one moment where the character's football eye contributed to a win or a better practice.
- No chain-of-command violations.
- Staff trust footprint grew naturally.

**What a bad QC season looks like:**
- Deliverables were inconsistent or late.
- Trust stalled or declined.
- System familiarity plateaued below 50.
- Character overstepped role boundaries or created friction.
- Football intelligence did not translate into useful work product.

### 5.2 Position Coach Evaluation

**What is evaluated:**
- Room development (did the players in the room improve? measurable stat and OVR changes).
- Meeting quality (are meetings productive? do players leave meetings better prepared?).
- Player trust (do the players in the room trust the coach? is the room unified or fractured?).
- Technical improvement (did specific technique work produce results? blocking, route-running, footwork, hand placement — whatever the room demands).
- Room stability / politics (is the room a source of calm or chaos within the larger staff?).
- Quality of input to coordinator / HC (does the position coach provide useful upward input, or is he invisible in staff meetings?).

### 5.3 Coordinator Evaluation

**What is evaluated:**
- Unit performance vs expectation (points/game, yards/game, efficiency, third down, red zone, turnovers — relative to the talent on the roster and the strength of opponents).
- Install quality (was the scheme installed cleanly? did players understand their assignments?).
- Adjustment quality (did the coordinator make effective halftime and in-game adjustments?).
- Play-calling if assigned (was play-calling situationally appropriate? did it put players in good positions?).
- HC alignment (does the coordinator work within the HC's framework, or is there friction?).
- Media / pressure handling (did the coordinator handle public scrutiny well?).

### 5.4 Head Coach Evaluation

**What is evaluated:**
- Record vs expectation band (did the team meet, exceed, or fall below the pre-season expectation?).
- Staff management (is the staff stable, effective, and aligned?).
- Organizational stability (is the program/franchise in better shape than it was a year ago?).
- Culture health (is the locker room healthy? are players buying in?).
- Ownership / AD / GM trust (does the organization still believe in the HC?).
- Playoff / postseason outcome (if applicable — did the team perform in the postseason?).

---

## 6. PROMOTION THRESHOLDS

Promotion is possible only if ALL of the following are true:

```
1. Evaluation score ≥ 75
2. Trajectory is Rising or Strong
3. Direct evaluator trust ≥ 70
4. System mastery is high enough for the next role level
5. Organizational opening or structural reason exists (vacancy, restructure, expansion)
```

Meeting the thresholds does not guarantee promotion. It makes promotion possible. The organization must also want it. Promotion without all five conditions met is a system violation.

### 6.1 QC → Position Coach

Additional requirements beyond the general thresholds:
- Teaching ≥ 50
- Administrative ≥ 45
- At least one position-specific knowledge area ≥ 60
- 15+ successful task completions logged
- Recommendation from superior (relationship > 70)
- Demonstrated direct teaching readiness (not just football knowledge — the ability to run a room)
- Role vacancy or organizational need (if no position coach job is open, no promotion happens)

### 6.2 Position Coach → Coordinator

Additional requirements:
- Scheme Design > 65
- Staff Management > 60
- Game Management > 55
- Proven development of 3+ players (documented improvement)
- Unit consistently performs at or above expectation
- HC willingness to restructure or fill a coordinator vacancy with the character

### 6.3 Coordinator → Head Coach

Additional requirements:
- Leadership > 75
- Media Relations > 60
- Recruiting > 70 (college) or Player Evaluation > 70 (NFL)
- Administrative > 65
- Successful track record (unit rankings or win contribution)
- HC opening exists (internal or external)

---

## 7. RETENTION AND NON-RENEWAL THRESHOLDS

### 7.1 Retention

```
≥ 80 = valued retainable (extension conversations likely)
≥ 70 = positive retainable (organization is happy, no urgency)
≥ 60 = retainable (adequate, no immediate threat)
```

Retention may still come with no promotion. A coach can be valued, kept, and blocked from upward mobility indefinitely. This is the most common outcome, especially at QC and position coach levels.

### 7.2 Non-Renewal / Release

```
50–59 = at risk (organization considers alternatives, may retain if no better option)
<50   = near-certain non-renewal unless extraordinary mitigating circumstances
```

Mitigating circumstances that might prevent non-renewal below 50:
- No replacement available
- Political protection from a powerful ally inside the organization
- Mid-contract with expensive buyout (rare at low levels)
- Organization in crisis and cannot afford staff turnover

These are exceptions, not expectations.

---

## 8. 2000-ERA NFL MOBILITY RULES

### 8.1 Core Rule

In the 2000 NFL ruleset, assistants do NOT have protected upward-mobility rights. The club controls access to outside interviews.

### 8.2 What the Club Can Do

- Retain the character and block all outside interview requests.
- Retain the character and selectively approve some interview requests.
- Retain the character and quietly allow exploration without formal approval.
- Promote the character internally.
- Release the character into the open market.

### 8.3 What Determines Club Behavior

The club's decision to block or allow is based on:
- How much it values the character (evaluation score, trust).
- Whether losing the character would hurt the organization.
- The HC's personal relationship with the character.
- Organizational politics (does the HC want to keep a loyal ally? does the HC want to get rid of a potential rival?).
- Whether the outside opportunity is a promotion (some clubs block lateral moves but allow promotions out of goodwill).

### 8.4 Informal Reputation Channel

Even when blocked, informal reputation still operates:
- Other coaches in the league talk.
- A well-regarded assistant's name circulates even without formal interviews.
- Reputation from playing career provides visibility.
- This does not override a block, but it means that when the character is eventually free, opportunities may already be warm.

---

## 9. CONTRACT AND RENEWAL SPECIFICS

### 9.1 Assistant-Level Contracts

For GA, QC, and most position coaches:
- Contracts are typically one-year deals.
- "Renewed" means a new one-year deal, not long-term security.
- Raises are small and incremental unless the character is being promoted.
- There is no guaranteed multi-year deal at these levels unless the organization is making an unusual investment.

### 9.2 Coordinator-Level Contracts

- Contracts are typically two to three years.
- Buyout clauses begin to matter.
- Renewal may include meaningful salary increases.
- Extension conversations happen when the organization wants to prevent poaching.

### 9.3 Head Coach Contracts

- Contracts are typically three to five years.
- Buyout clauses are significant.
- Extension conversations are driven by record, stability, and organizational confidence.
- Firing mid-contract triggers buyout obligations.

### 9.4 Era-Adjusted Compensation

All salary figures in the Coaching Module are approximate 2024–2025 benchmarks. The engine adjusts all coaching compensation to match the simulation's current in-game year using historical coaching salary growth trends. A QC in 1999 does not earn a 2024 QC salary.

---

## 10. ROLE TRANSITION EXECUTION

### 10.1 When Role Changes

If the offseason sequence produces a role change (promotion, lateral move, new team, demotion):

```
1. Remove the old role payload from the State Block entirely.
2. Initialize the new role payload with appropriate defaults.
3. Update Current Role and Position Detail in the Identity section.
4. Update Reports To in Reporting Structure.
5. Reset Delegated Authority to None unless the hiring context specifies otherwise.
6. Carry forward all universal shell data unchanged.
7. Log the change in Active Consequences if it creates new expectations or deadlines.
8. Update Offseason Status fields:
   - Club Decision = [Promoted / Lateral / Released / Hired]
   - Transition Pending = Yes
9. Generate one transition turn before ordinary offseason continues.
10. After the transition turn, set Transition Pending = No.
11. Resume ordinary offseason under new role rules.
```

### 10.2 Transition Turn Content

The transition turn is a special turn that covers:
- Why the change happened (evaluation result, organizational need, external hire).
- What authority changed (new reporting chain, new responsibilities, new restrictions).
- What expectations are now (what the new evaluator or organization expects in the first season).
- Who the character's key relationships are in the new context.
- What the first concrete challenge is in the new role.

The transition turn uses the standard turn structure but adapts the content to the transition context. It is not a regular offseason turn and it is not an exit meeting — it is the bridge between the old role and the new one.

### 10.3 No Payload Blending

The engine does not blend payloads. The character is either a QC or a Position Coach — never a hybrid. The old payload is removed completely. The new payload is initialized fresh. Data that belongs in the universal shell (trust, relationships, finances, legacy) carries forward. Data that belongs in the role payload (room roster, unit stats, coordinator alignment) starts fresh for the new role.

---

## 11. INTEGRATION WITH OTHER DOCUMENTS

### 11.1 Master Engine

The Master Engine (§5.5) provides the structural framework for the offseason sequence. This document provides the detailed rules, criteria, and logic that execute within that framework.

### 11.2 Coaching Module

The Coaching Module (§19) provides role-specific outcome rules and promotion/retention thresholds. This document provides the evaluation criteria, exit meeting rules, and mobility rules that feed into those outcomes.

### 11.3 State Block

The State Block tracks the offseason state in the `OFFSEASON STATUS` section. This document defines what each field means and when each field updates.

### 11.4 Interview Module

The Interview Module governs the job search process when it activates during Step 7 of the offseason sequence. This document defines when and why the Interview Module activates, but the Interview Module governs the process itself.

### 11.5 End-of-Season Output Format

The end-of-season output format (`end_of_season_output_format.md`) defines how the offseason evaluation sequence is presented to the user. This document defines the logic. That document defines the output.

---

## 12. DESIGN PRINCIPLES

- **Earned, not automatic.** No retention, promotion, or renewal happens without evaluation and justification.
- **Era-accurate.** The mobility and hiring rules match the in-game era, not the most convenient or most modern version.
- **Time-bubbled.** The offseason sequence resolves inside a controlled bubble. The calendar does not drift. Contradictory events cannot overlap.
- **State-driven.** Every offseason decision writes to the State Block. Every resume reads from the State Block. The offseason is fully persistent.
- **Role-specific.** Evaluation criteria, exit meeting authority, and outcome possibilities differ by role. A QC evaluation is not a HC evaluation with smaller numbers.
- **Promotion-safe.** Promotion requires all thresholds AND organizational need. Good performance does not automatically produce promotion. This is the most important design constraint in the system.
- **One role at a time.** The State Block never contains more than one role payload. Promotion replaces the payload cleanly.
- **Honest exits.** Exit meetings are honest, not theatrical. The evaluator says what they think. The organization may act differently than the evaluator suggests. This gap is realistic and intentional.

---

*Offseason Evaluation & Job Cycle — Complete. Referenced by Master Engine §5.5, Coaching Module §19, and State Block Offseason Status section. Loaded at season close. Deactivates when the time bubble resolves.*
