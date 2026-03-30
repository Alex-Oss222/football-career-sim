# FOOTBALL CAREER SIM — COACHING MODULE

> Governs coaching careers from entry through retirement or Hall of Fame. Defers to the Master Engine for realism rules, turn processing, randomness, and output modes. The Interview Module is loaded separately when actively job searching. The Offseason Evaluation & Job Cycle document is loaded at season close.

---

## 1. ENTRY PATHS

### 1.1 Post-Playing Career (Most Common)
Automatic eligibility check at player retirement:

```
Scholar > 70 AND Leadership > 75:  Start as Position Coach
Scholar 50–70 OR Leadership 60–75: Start as GA/QC
Scholar < 50:                      Must complete coaching certification (3 turns, $15K)

Playing Experience Bonus: +10 initial credibility with players
Starting Reputation = Legacy Points / 10 (max 50)
```

### 1.2 Direct-to-Coaching (No Playing Career)
```
Requirements:
- Age 22+ (college graduate)
- Start as Graduate Assistant only
- No credibility bonus (−20 with players initially)
- Must prove competence through results

Character Creation:
- User defines name, age, background
- Coaching attributes generated from scratch (see §2.2)
- No playing experience conversion
- Reputation starts at 0
```

---

## 2. COACHING ATTRIBUTES

### 2.1 Conversion from Player (Post-Retirement Entry)
One-time conversion at coaching career start:

```
CORE (Converted from Player Attributes):
Tactical Knowledge   = (Football IQ × 0.8) + (Work Ethic × 0.2)
Teaching             = (Coachability × 0.4) + (Football IQ × 0.3) + (Discipline × 0.3)
Leadership           = (Leadership × 0.8) + (Competitiveness × 0.2)
Recruiting           = (Composure × 0.4) + (Leadership × 0.3) + (Awareness × 0.3)
Man Management       = (Leadership × 0.7) + (Coachability × 0.3)
Motivation           = (Competitiveness × 0.5) + (Leadership × 0.5)

NEW (Start 30–50, seeded by player attributes):
Scheme Design        = 30 + (Football IQ × 0.2)
Game Management      = 35 + (Decision Making × 0.4)
Player Evaluation    = 40 + (Vision × 0.3)
Media Relations      = 30 + (Composure × 0.4)
Staff Management     = 35 + (Leadership × 0.2)
Administrative       = 30 + (Work Ethic × 0.3)
Playbook Innovation  = 30 + (Football IQ × 0.3)
Development Expertise= 35 + (Teaching × 0.5)
Contract Negotiation = 25 + (Leadership × 0.2)
Combine Evaluation   = 35 + (Player Evaluation × 0.2)
Trade Negotiation    = 30 + (Leadership × 0.3)
```

### 2.2 Direct-to-Coaching Starting Attributes
All coaching attributes start at 30–45 range. No conversion bonuses. User distributes 50 bonus points across any coaching attributes.

### 2.3 Coaching Traits (100 Points to Distribute)
```
Disciplinarian (0–50):  Strict rules, high standards, accountability
Players' Coach (0–50):  Relationship-focused, player development
Innovator (0–50):       Scheme creativity, willingness to experiment
Traditionalist (0–50):  Proven methods, conservative approach
Total must = 100
```

These traits influence how NPCs (players, staff, media, administration) respond to your coaching style and decisions.

---

## 3. CAREER LADDER

### 3.1 Positions & Requirements

Promotion is **skill-based, not time-based**. A GA with elite skills can advance faster than a mediocre position coach. Tenure alone does not earn promotion.

**LEVEL 0: GRADUATE ASSISTANT / QUALITY CONTROL**
```
Entry: Any (default for direct-to-coaching and low-skill retirees)
Salary: $0–35K (GA) / $30–60K (QC)
Attribute Cap: 60
Authority: None
Direct Reports: 0

Promotion Requirements (to Position Coach):
- Teaching >= 50
- Administrative >= 45
- At least one position-specific knowledge area >= 60 (position knowledge is exempt from the general attribute cap — see note below)
- 15+ successful task completions logged
- Recommendation from superior (relationship > 70)

Note: Position-specific knowledge (e.g., TE Knowledge, Route Craft, Offensive Structure) as defined in the character profile is NOT subject to the coaching level attribute cap. These represent football knowledge accumulated from playing and studying the game, not coaching skill. They can exceed the Level 0 cap of 60.
```

**LEVEL 1: POSITION COACH**
```
Positions: QB / RB / WR / TE / OL / DL / LB / DB / ST Assistant
Attribute Cap: 75

Salary Ranges (scaled by performance, not just level):
- High School:    $60–100K
- Small College:  $80–150K
- FBS:            $150–400K
- NFL:            $300–500K

Promotion Requirements (to Coordinator):
- Scheme Design > 65
- Staff Management > 60
- Game Management > 55
- Proven development of 3+ players (documented improvement)
- Unit consistently performs at or above expectation
```

**LEVEL 2: COORDINATOR (OC / DC / STC)**
```
Attribute Cap: 90

Salary Ranges:
- Small College:  $150–300K
- FBS:            $400K–$2M
- NFL:            $1–4M

Promotion Requirements (to Head Coach):
- Leadership > 75
- Media Relations > 60
- Recruiting > 70 (college) or Player Evaluation > 70 (NFL)
- Administrative > 65
- Successful track record (unit rankings or win contribution)
```

**LEVEL 3: HEAD COACH — HIGH SCHOOL**
```
Attribute Cap: 85
Salary: $70–150K
Focus: Player development, community, program building
Recruiting scope: Local/regional
```

**LEVEL 4: HEAD COACH — COLLEGE**
```
Attribute Cap: 95
Salary: $500K–$12M (program-dependent)
Focus: Recruiting, staff management, program identity, media
Recruiting scope: Regional/national
Additional: NIL coordination, portal management, booster relations
```

**LEVEL 5: HEAD COACH — NFL**
```
Attribute Cap: 99
Salary: $5–20M
Focus: Game management, roster construction, staff, media, ownership
Additional: Cap management, trade evaluation, draft strategy
Works with GM (NPC or delegated functions)
```

### 3.2 Lateral Moves
Coaches can move laterally at the same level:
- Position coach switching position groups
- Coordinator moving to a different school/team at the same level
- HC moving between programs at a similar tier

Lateral moves require a job search (Interview Module) but have lower skill thresholds than promotions.

### 3.3 Demotions
Demotions occur when:
- Fired for performance (job security hits 0)
- Scandal/violation forces resignation
- Coaching skills deteriorate below level minimum
- Voluntary step-down (to reduce stress or change environment)

After demotion, the coach must rebuild through the job market. Previous level experience provides a credibility bonus (+10 to applications at the lower level) but does not guarantee rehiring at the same tier.

---

## 4. COACHING TURN STRUCTURE

The Coaching Module uses a **coach-specific Standard Turn** that differs from the Player Module turn.

### 4.1 Turn Length by Phase
```
Regular Season:    1 week per turn
Playoffs:          1 game per turn
Offseason:         2 weeks per turn
Job Search:        Event-based (Interview Module takes over)
```

### 4.2 Coach Standard Turn (7 Sections)

**1. Date / Phase / Job State**
```
Date, phase, team, role, record, job security, stress. 3–5 lines.
```

**2. Facility Pulse**
```
The building temperature. What you're sensing from staff and players.
One important sidebar conversation or observation.
Short — this is atmosphere, not a report.
```

**3. What Happened This Turn**
```
Operational summary: practices, meetings, recruiting activity,
staff work, roster management, game result if applicable.
This is the core content of the turn.
```

**4. Football Operations**
```
Offense / defense / special teams status.
Playbook installation or weekly game plan.
Injuries, depth, practice performance.
Scheme fit or adaptation issues.
```

**5. People & Power**
```
Owner / AD / GM pressure and expectations.
Staff relationships and dynamics.
Locker room temperature.
Media narrative and public perception.
```

**6. What Changed**
```
Numeric summary:
- Coaching attribute changes
- Stress level
- Trust / job security movement
- Recruiting traction / cap / roster changes
- Player development progress under your watch
```

**7. Decisions**
```
3 major decisions (strategic, consequential)
3–5 secondary actions (operational, routine)
0–2 gates (only when a high-stakes event demands immediate response)
```

### 4.3 Section Omission Rule
Same as Master Engine §6.1: sections with nothing notable to report are omitted, not filled with filler.

---

## 5. SKILL-BASED TASK RESOLUTION

Every coaching action is resolved by a skill check against the task's difficulty. Your position title does not determine success — your attributes do.

### 5.1 Skill Check Formula
```
Result = Relevant Skill Total vs Difficulty Threshold

Outcome Tiers:
  Skill ≥ Threshold + 20:  Exceptional — exceeds expectations, reputation boost
  Skill ≥ Threshold + 10:  Strong — solid execution, positive outcome
  Skill ≥ Threshold:       Adequate — gets the job done, no special notice
  Skill < Threshold by 10: Subpar — noticeable shortcomings, minor consequences
  Skill < Threshold by 20: Failure — visible problems, trust/security impact
```

### 5.2 Task Types by Role

**Graduate Assistant / QC:**
```
Film Breakdown:       Tactical Knowledge + Administrative
Scout Team Prep:      Teaching + Leadership
Administrative Work:  Administrative + Work Ethic
Recruiting Support:   Recruiting + Administrative (if assigned)
```

**Position Coach:**
```
Player Development:   Teaching + Development Expertise
Game Preparation:     Tactical Knowledge + Teaching
Recruiting:           Recruiting + Player Evaluation
Practice Design:      Scheme Design + Teaching
```

**Coordinator:**
```
Scheme Installation:  Scheme Design + Teaching + Playbook Innovation
Play Calling:         Game Management + Tactical Knowledge + Composure
Staff Coordination:   Leadership + Staff Management
Game Planning:        Tactical Knowledge + Player Evaluation + Scheme Design
```

**Head Coach:**
```
Program Direction:    Leadership + Administrative + Vision
Staff Hiring/Firing:  Player Evaluation + Staff Management + Leadership
Media Handling:       Media Relations + Composure
Recruiting (College): Recruiting + Player Evaluation + Media Relations
Roster Decisions:     Player Evaluation + Game Management
Booster/Owner Mgmt:   Media Relations + Leadership + Administrative
```

### 5.3 Cross-Level Competence
A GA with Tactical Knowledge 80 makes better schematic observations than a coordinator with Tactical Knowledge 50. The engine respects this. Skill checks do not receive bonuses or penalties based on job title — only based on attribute values and task difficulty.

---

## 6. PLAYBOOK SYSTEM

### 6.1 Control Options
Based on your role and attributes:

```
FULL CONTROL (HC only):
  Requires: Scheme Design > 70, Administrative > 60
  You design both sides. +10 execution when you design. +5 stress/turn.

DELEGATE ONE SIDE (HC only):
  Requires: Trust > 70 with one coordinator
  You design offense OR defense. Coordinator handles the other using THEIR skills.

DELEGATE BOTH (HC only):
  Requires: Trust > 70 with both coordinators
  Success entirely dependent on coordinator attributes.
  You can override specific calls if Game Management > 75.

COLLABORATIVE (Any HC):
  You work with coordinators. Combined skill: (Yours + Theirs) / 2.
  +3 execution, +5 staff chemistry. Time cost: moderate.
```

### 6.2 Offensive Philosophies
```
Pro-Style:    Requires Tactical Knowledge > 70, Traditionalist > 30
Spread:       Requires Playbook Innovation > 30, Game Management > 60
Air Raid:     Requires Playbook Innovation > 40, Development Expertise > 70
Option:       Requires Teaching > 70, Traditionalist > 40
Power Run:    Requires Traditionalist > 35, Development Expertise > 65
RPO-Heavy:    Requires Scheme Design > 75, Playbook Innovation > 45
```

### 6.3 Defensive Philosophies
```
1. 4-3 DEFENSE
Best if: Tactical Knowledge > 65, Traditionalist > 30

2. 3-4 DEFENSE
Best if: Playbook Innovation > 35, Scheme Design > 60

3. 4-2-5 (Nickel)
Best if: Playbook Innovation > 40, Player Evaluation > 65

4. 3-3-5
Best if: Playbook Innovation > 45, Scheme Design > 65

5. Tampa 2
Best if: Tactical Knowledge > 60, Teaching > 65

6. Multiple
Best if: Scheme Design > 75, Staff Management > 65
```

### 6.4 Installation Success
```
Installation Quality = (Scheme Design × 0.4) + (Teaching × 0.3) + (Innovation × 0.3)

Complexity You Can Handle:
  90+:  NFL-level complexity (10/10)
  75–89: Advanced college (8–9/10)
  60–74: Standard college (6–7/10)
  45–59: Basic college (4–5/10)
  <45:  High school level (1–3/10)

Attempting complexity beyond your skill results in execution penalties.
```

---

## 7. GAME SIMULATION (COACHING)

### 7.1 Coaching Impact on Games
```
Coaching Game Score =
  (Scheme Advantage × 0.25) +
  (Play Call Quality × 0.25) +
  (Player Preparation × 0.20) +
  (In-Game Adjustments × 0.15) +
  (Motivation × 0.15)

Scheme Advantage = Your Scheme Design vs Opponent Coordinator Scheme Design
Play Call Quality = Game Management + Tactical Knowledge (skill check per drive)
Player Preparation = Teaching + Development Expertise (week's practice quality)
In-Game Adjustments = Tactical Knowledge + Game Management (halftime and situational)
Motivation = Motivation attribute + Chemistry
```

### 7.2 Critical Decisions During Games
```
4th Down:       Game Management + Tactical Knowledge check
Timeout Usage:  Game Management + Composure check
Challenge Flag: Tactical Knowledge + Player Evaluation check
Halftime Adj:   Tactical Knowledge + Scheme Design check
Personnel:      Player Evaluation + Game Management check

Each is a skill check. A GA with 80 Game Management makes a better 4th-down call than an HC with 50.
```

### 7.3 Team Performance
```
Team Game Quality =
  (Roster Talent × 0.40) +
  (Coaching Impact × 0.30) +
  (Chemistry × 0.15) +
  (Health/Depth × 0.15)

± Variance (roll-based)

Your coaching decisions influence the 30% coaching slice.
You do not control the other 70%.
```

---

## 8. RECRUITING (COLLEGE)

### 8.1 Recruiting Capability
```
Evaluation Accuracy = Player Evaluation + Combine Evaluation
  90+: See true ratings within ±2
  75–89: Within ±5
  60–74: Within ±8
  <60:  Within ±15 (may recruit busts or miss gems)

Recruiting Power = Recruiting + Media Relations + Program Prestige
  Determines what star level of recruit you can realistically attract.

Territory = Based on school location + reputation + personal connections
```

### 8.2 Recruiting Process
```
Each offseason recruiting cycle:

Identify Targets:    Player Evaluation check
Initial Contact:     Recruiting + Communication check
Campus Visit:        Recruiting + Program Prestige + Facilities
Closing:             Recruiting + Leadership + NIL Coordination

Competition: Rival coaches with their own Recruiting attributes compete for same players.
Higher combined score wins the recruit.
Ties broken by: program prestige > scheme fit > proximity.
```

### 8.3 Recruiting Class Quality
```
Class Rank = f(Average Recruit Rating, Number of Commits, Position Need Coverage)
Directly affects future team OVR and program trajectory.
```

---

## 9. STAFF MANAGEMENT

### 9.1 Hiring
```
Your Evaluation Accuracy for Staff:
  Player Evaluation + Staff Management combined:
  90+: See exact true ratings
  75–89: ±3 accuracy
  60–74: ±5 accuracy
  45–59: ±10 accuracy
  <45:  ±15 accuracy (risk hiring disasters)
```

### 9.2 Staff Performance Under You
```
Staff Effectiveness = Their Base Skill × Your Leadership Modifier

Your Leadership 80+:  Staff performs at 110%
Your Leadership 60–79: Staff at 100%
Your Leadership 40–59: Staff at 90%
Your Leadership <40:   Staff at 75%
```

### 9.3 Conflict Resolution
```
Resolution Quality = Staff Management + Leadership + Man Management

85+: Turn conflict into productive collaboration
70–84: Resolve with minimal disruption
55–69: Temporary fix, underlying tension remains
40–54: One party must leave
<40:  Both parties leave, program damaged
```

---

## 10. DELEGATION

### 10.1 Delegation Capacity
Based on Leadership + Staff Management, not position title:
```
Combined 90+:  Delegate 4 tasks effectively
Combined 75–89: 3 tasks
Combined 60–74: 2 tasks
Combined 45–59: 1 task
Combined <45:   Delegation likely to fail
```

### 10.2 Delegation Success
```
Outcome = Your Leadership + Their Competence + Trust Level

90+: Task exceeded expectations
75–89: Completed well
60–74: Adequate
45–59: Subpar results
<45:  Failure — must handle yourself, trust damaged
```

### 10.3 What Can Be Delegated (By Role)
```
GA (if skills warrant):
  Tactical Knowledge > 60: Suggest scheme adjustments
  Player Evaluation > 55: Identify recruiting targets
  Administrative > 70: Handle coordinator's paperwork

Position Coach:
  Teaching > 70: Run drills for other groups
  Recruiting > 65: Lead area recruiting
  Development > 70: Create individualized player plans

Coordinator:
  Staff Management > 75: Delegate to all position coaches
  Leadership > 70: Mentor younger coaches
  Scheme Design > 80: Have assistants install base packages

Head Coach:
  Delegation capacity determines what you can hand off
  Low-skill areas you can't delegate will suffer visibly
```

---

## 11. MEDIA & PUBLIC PERCEPTION

### 11.1 Media Handling
```
Press Conference Quality = Media Relations + Leadership + Tactical Knowledge

90+: Positive viral moment, quote of the week
75–89: Good headlines, controlled narrative
60–74: Neutral coverage
45–59: Negative spin, your words used against you
<45:  Disaster, becomes a meme

Question Difficulty Scales to Your Skill:
  Media Relations < 40: Every question is a trap
  40–60: Standard difficulty
  60–80: You can steer the narrative
  80+: Media becomes an asset
```

### 11.2 Media Coverage
Coverage intensity and tone based on:
- Market size (NFL big market vs small college town)
- Program profile (blue blood vs mid-major)
- Recent results vs expectations
- Your Media Relations skill (higher skill = better framing even in losses)
- Controversy status (active scandals amplify everything)

### 11.3 Social Media
```
Program Social Presence = Media Relations + Spotlight (coaching trait) + Win%
Recruiting impact: Social presence affects recruit interest
Controversy risk: Higher visibility = higher scrutiny
```

---

## 12. STRESS & BURNOUT

### 12.1 Stress Calculation
```
Weekly Stress Gain = (Job Difficulty − Your Average Relevant Skills) / 10

Minimum: 1 per turn (the job always costs something)
Maximum: 10 per turn (completely overwhelmed)

Additional Stress:
  Each loss: +5
  Each failed skill check: +2
  Media disaster: +10
  Staff conflict: +5
  Family/personal issues: +5
  Booster/owner confrontation: +7
  Job security below 30: +5 per turn
```

### 12.2 Stress Effects
```
0–30:   No effect
31–50:  All skills −5
51–70:  All skills −10, health warnings in narrative
71–90:  All skills −20, mandatory rest events triggered
91–100: Breakdown — forced leave, possible forced resignation
```

### 12.3 Stress Reduction
```
Win important game: −10
All skill checks passed in a turn: −5
Vacation (offseason only): −15
Exercise routine: −2 per turn
Family time: −3 per turn
Job security above 70: −2 per turn
Promotion or contract extension: −10
```

---

## 13. JOB SECURITY

### 13.1 Calculation
```
Job Security (0–100):

Base = 50 (neutral start)

Modifiers Per Turn:
  Win vs expectation: +3 per win above expected, −4 per win below
  Recruiting class quality: +5 (top 25), +2 (above avg), −3 (below avg), −7 (bottom tier)
  Player development: +2 per notable improvement, −2 per regression
  Scandal/violation: −15 to −30
  Media perception: ±5 based on coverage
  Booster/owner satisfaction: ±5
  Staff stability: +2 (stable) / −3 (high turnover)
```

### 13.2 Thresholds
```
80–100: Secure — extension conversations, program loyalty
60–79:  Stable — no immediate threat, but expectations exist
40–59:  Warm seat — AD/owner watching closely, media speculation
20–39:  Hot seat — buyout discussions, coaching search rumors
0–19:   Fired — termination within 1–2 turns unless dramatic reversal
```

### 13.3 Firing Consequences
- Buyout received (if contracted)
- Must enter job market (Interview Module activates)
- Reputation takes a hit (−10 to −25 based on circumstances)
- Can apply at same level or lower
- 1-year "cooling off" penalty to applications at fired school's conference

---

## 14. CONTRACTS & FINANCES (COACHING)

### 14.1 Salary Ranges by Level
```
GA/QC:              $0–60K
Position Coach HS:   $60–100K
Position Coach College: $80–400K
Position Coach NFL:  $300–500K
Coordinator College: $150K–$2M
Coordinator NFL:     $1–4M
HC High School:      $70–150K
HC College:          $500K–$12M
HC NFL:              $5–20M
```

### 14.2 Era Adjustment
All salary figures are approximate 2024–2025 benchmarks. The engine adjusts all coaching compensation to match the simulation's current in-game year, using historical coaching salary growth trends. Earlier eras pay less; future eras project forward.

### 14.3 Contract Negotiation
```
Negotiation Power = Contract Negotiation + Leadership + Leverage

Leverage Sources:
  Multiple offers: +15
  Recent championship: +20
  Hot coaching candidate: +10
  Fired/desperate: −15
  First HC job: −10

Negotiable Terms:
  Base salary, contract length, buyout clause,
  assistant coach salary pool (HC), performance bonuses,
  moving expenses, facilities commitments
```

### 14.4 Financial Tracking
```
Income: Salary + Bonuses + Speaking Fees + Media Appearances
Deductions: Taxes (federal + state) + Agent (if applicable) + Living Expenses
Net Worth: Cumulative savings + investments
Investment Returns: 5–8% if Scholar > 60, 2–4% otherwise
```

---

## 15. COACHING SKILL DEVELOPMENT

### 15.1 Growth Methods
Development is earned, not automatic:

```
1. Successful Task Completion:
   Each passed skill check: +0.1 to that skill
   Critical success (20+ over threshold): +0.3
   Failure: −0.1 (reinforces bad habits)

2. Learning from Superiors:
   Working under a coach whose skill > yours: +0.2 per turn in that skill
   Mentorship relationship (trust > 80): +0.5 per turn in specific skill

3. Education:
   Coaching clinic: +3 to +7 in specific skill (offseason only)
   Certification course: +3 to +5 in related skills
   Self-study: +0.1 per turn (requires Scholar equivalent > 60)

4. Experience Accumulation:
   10 successful recruiting closes: +1 Recruiting
   10 successful game plans: +1 Scheme Design
   10 players developed significantly: +1 Teaching
```

### 15.2 Skill Maintenance
Coaching skills do not automatically decay during active employment. Decay applies only during extended unemployment (6+ turns without a coaching position): −0.1 per turn to all coaching attributes after 6 turns unemployed.

---

## 16. RIVAL COACHES

### 16.1 Generation
Rival coaches are generated with comparable total skill points to yours (±50 total) but distributed differently:

```
Archetypes:
  The Specialist:  90+ in one area, weak elsewhere
  The Generalist:  Balanced across all skills
  The Mirror:      Similar distribution to yours
  The Opposite:    Strong where you're weak, weak where you're strong
```

### 16.2 Head-to-Head Competition
```
Recruiting Battle: Your (Recruiting + Evaluation + Prestige) vs Theirs
Game Day: Your (Scheme + Game Management + Adjustments) vs Theirs
Job Market: Your Interview Score vs Theirs (same job, best candidate wins)
```

Rivals persist across your career. They take jobs, get fired, get promoted. The coaching world is small.

---

## 17. COACHING RETIREMENT

### 17.1 Triggers
```
Forced:
  Age ≥ 70
  Stress hits 100 (breakdown)
  3+ consecutive years unemployed
  Health crisis event (random, age-scaled)

Voluntary Check (each offseason if age > 55):
  Retirement Score =
    (Age − 50) × 2 +
    (Stress / 3) +
    (100 − Job Security) / 4 +
    Financial Security bonus (Net Worth > $10M: +15)

  Score > 60: Retirement dialogue
  Score > 80: Strong lean
  Score > 95: Near-certain
```

### 17.2 Legacy & Hall of Fame
```
Legacy Points (cumulative career):
  Each player developed +10 OVR under your watch: 5 points
  Each game won above expectation: 2 points
  Each assistant who becomes HC: 15 points
  Each schematic innovation adopted widely: 20 points
  Each championship: 30 points
  Each Coach of Year award: 10 points

Hall of Fame Threshold: 200+ Legacy Points
Consideration requires:
  At least 3 coaching skills that reached 90+
  Measurable program impact at multiple stops
  Coaching tree quality
```

---

## 18. COMMANDS (COACHING-SPECIFIC)

```
"Begin coaching career"     — Start coaching (post-retirement or direct)
"Search coaching jobs"      — View open positions (activates Interview Module)
"Apply for [job]"           — Begin application process
"Check skill requirements"  — See what jobs you qualify for
"Evaluate my skills"        — Display all coaching attributes
"Skill development plan"    — Get recommendations for improvement
"Check delegation capacity" — See how many tasks you can delegate
"Delegate [task] to [name]" — Assign task to staff member
"Review delegated tasks"    — Check delegation outcomes
"Staff evaluation"          — Assess your staff's true ratings (accuracy limited by your skill)
"Attend clinic"             — Offseason skill improvement event
"Find mentor"               — Seek mentorship from superior coach
"Playbook review"           — Current scheme status and installation quality
"Job security"              — Detailed breakdown of your seat temperature
"Stress check"              — Current stress level and sources
"Rival coaches"             — See your coaching rivals and their status
"Season eval"               — Trigger end-of-season evaluation turn manually
```

---

## 19. OFFSEASON EVALUATION & ROLE OUTCOME RULE

The coaching career does not auto-advance. Every year-end role outcome must be earned and justified. This section defines the coaching-specific rules that supplement the Master Engine's offseason sequence (§5.5) and the full offseason evaluation system in `offseason_evaluation_and_job_cycle.md`.

### 19.1 Core Principle

A coach cannot:
- Self-promote
- Skip levels
- Retain a job automatically

All offseason outcomes must be:
- Evaluated
- Justified
- Tied to performance + trust + context

### 19.2 Role-Specific Year-End Outcomes

#### For GA / QC

Possible year-end outcomes:
- Retained same title
- Renewed on new one-year deal
- Retained with greater operational trust
- Blocked from outside interviews (2000-era NFL rule)
- Allowed to explore outside QC / assistant roles
- Promoted internally only if the club has BOTH:
  - A reason to move the character up (vacancy, need, restructure)
  - Confidence that he can now own a room or more formal responsibility

Promotion from QC requires more than trust. It requires proof of the next-layer skill:
- Direct teaching readiness
- Room-management readiness
- Role vacancy or organizational need
- Evaluator support

#### For Position Coach

Possible year-end outcomes:
- Retained same role
- Renewed with raise or added responsibility
- Promoted to coordinator if vacancy exists AND skill thresholds met
- Allowed to explore coordinator openings elsewhere
- Blocked from outside interviews (2000-era NFL rule)
- Non-renewed if room performance or trust declined

Promotion from Position Coach to Coordinator requires:
- Proven unit development track record
- Scheme design capability sufficient for the next level
- HC or organizational willingness to restructure

#### For Coordinator

Possible year-end outcomes:
- Retained same role
- Extended
- Promoted to HC if opening exists AND full threshold met
- Allowed to interview for HC openings elsewhere
- Blocked from outside HC interviews (2000-era NFL rule)
- Non-renewed if unit performance fell below expectation AND HC alignment degraded

#### For Head Coach

Possible year-end outcomes:
- Retained
- Extended
- Fired
- Forced resignation
- Buyout and separation
- Lateral move to another program (requires mutual interest)

### 19.3 Promotion Thresholds

Promotion is possible only if ALL are true:
- Evaluation score ≥ 75
- Trajectory is Rising or Strong
- Direct evaluator trust ≥ 70
- System mastery is high enough for next role
- Organizational opening or structural reason exists

Meeting the thresholds does not guarantee promotion. It makes promotion possible. The organization must also want it.

### 19.4 Retention Thresholds

- ≥ 60 = retainable
- ≥ 70 = positive retainable
- ≥ 80 = valued retainable

Retention may still come with no promotion. A coach can be valued and kept without being promoted. This is the most common outcome.

### 19.5 Non-Renewal / Release Thresholds

Below 60 becomes the danger zone, especially if:
- Trust is poor
- Growth stalled
- Politics are negative
- Role has become replaceable
- Organization is restructuring

Below 50 = near-certain non-renewal unless extraordinary mitigating circumstances exist.

### 19.6 Offseason State Block Integration

The offseason evaluation produces data that must be written to the State Block's `OFFSEASON STATUS` section. The fields tracked are:

```
Time Bubble Active: [Yes/No]
Bubble Stage: [Season Close / Internal Evaluation / Exit Meeting / Internal Decision / External Search / Hiring / Transition / Resolved]
Era Ruleset: [NFL_2000 / NFL_MODERN]
Evaluation Score: [X]/100
Trajectory: [Rising / Stable / Plateau / At Risk / Declining]
Scheme Mastery: [X]/100
Promotion Readiness: [None / Early / Emerging / Real / Strong]
Club Decision: [Pending / Retained / Renewed / Promoted / Released / Blocked / Allowed to Explore]
Outside Interest: [None / Quiet / Active]
Interview Access: [Open / Blocked / Approved]
Transition Pending: [Yes/No]
```

These fields are reset to defaults at the start of each new season after the time bubble resolves.

---

*Coaching Module — Complete. References Master Engine for realism rules, turn processing, randomness, and output modes. References offseason_evaluation_and_job_cycle.md for full offseason system. Interview Module loads separately when job searching.*