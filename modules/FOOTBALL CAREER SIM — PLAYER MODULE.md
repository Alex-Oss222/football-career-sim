# FOOTBALL CAREER SIM — PLAYER MODULE

> Governs the player career from entry through retirement or coaching transition. Defers to the Master Engine for realism rules, turn processing order, randomness, and output modes.

---

## 1. CHARACTER CREATION

### 1.1 Default Character
When user says `"Start simulation"` without specifics:

```
Name: Alex Thompson
Position: QB
Age: 16 (Junior, High School)
Height: 6'1" | Weight: 185 lbs
School: Lincoln High School, Ohio
Conference: Greater Miami Conference
```

### 1.2 Supported Entry Points

| Entry | Age | Starting Level | Default OVR Range |
|---|---|---|---|
| HS Freshman | 14 | High School Year 1 | 40–55 |
| HS Sophomore | 15 | High School Year 2 | 48–62 |
| **HS Junior (Default)** | **16** | **High School Year 3** | **55–70** |
| HS Senior | 17 | High School Year 4 | 60–75 |
| College Freshman | 18 | College Year 1 | 65–78 |
| College Transfer | 19–22 | College Year 2–4 | 70–85 |
| NFL Rookie (UDFA) | 21–23 | NFL Year 1 | 68–75 |
| NFL Rookie (Drafted) | 21–23 | NFL Year 1 | 72–88 |

User specifies: Name, Position, Entry Point. Engine generates contextually appropriate attributes within the OVR range. User can override individual attributes if desired.

### 1.3 Custom Creation
User may specify any or all of:
- Name, Position, Height, Weight, Age
- School/Team, Location, Conference
- Individual attribute values (validated against caps)
- Personality distribution
- Backstory context (engine incorporates into narrative)

---

## 2. ATTRIBUTE SYSTEM

### 2.1 Physical Attributes (10)
```
Speed          — Straight-line burst and top-end speed
Acceleration   — Zero-to-full speed quickness
Agility        — Change of direction, lateral movement
Strength       — Raw force, blocking/shedding power
Power          — Explosive lower-body force (jumping, driving)
Stamina        — Endurance over a game and season
Durability     — Resistance to injury severity
Flexibility    — Range of motion, injury prevention
Jumping        — Vertical and horizontal leap
Balance        — Staying upright through contact
```

### 2.2 Mental Attributes (10)
```
Football IQ    — Understanding of schemes, formations, tendencies
Vision         — Reading the field, anticipation
Composure      — Performance under pressure, big-moment reliability
Leadership     — Influence on teammates, locker room presence
Work Ethic     — Effort in practice, film study, conditioning
Coachability   — Responsiveness to instruction, willingness to adjust
Competitiveness — Drive to win, refusal to quit
Discipline     — Penalty avoidance, assignment consistency
Awareness      — Spatial recognition, peripheral processing
Decision Making — Speed and quality of in-play choices
```

---

## 3. POSITION-SPECIFIC SKILLS

### 3.1 Quarterback (QB)
```
Arm Strength       — Velocity and distance on throws
Accuracy Short     — Completions within 10 yards
Accuracy Medium    — Completions 10–25 yards
Accuracy Deep      — Completions 25+ yards
Touch              — Arc, placement, ball trajectory control
Release            — Throwing motion speed
Pocket Presence    — Movement and poise in the pocket
Throwing on Run    — Accuracy while moving laterally or scrambling
Read Progression   — Working through receiver options post-snap
Pre-Snap Read      — Identifying coverage and pressure pre-snap
```

### 3.2 Running Back (RB)
```
Ball Security      — Fumble resistance
Vision (Rush)      — Reading holes and cutback lanes
Elusiveness        — Making defenders miss in space
Truck/Power        — Running through contact
Pass Blocking      — Blitz pickup, chip blocks
Route Running      — Receiving route quality out of backfield
Hands              — Catching ability
YAC Ability        — Yards after catch / yards after contact
Patience           — Waiting for blocks to develop
Burst Through Hole — Acceleration into and through the gap
```

### 3.3 Wide Receiver (WR)
```
Route Running      — Precision, crispness, and variety of routes
Separation         — Creating space from coverage
Hands              — Catching reliability
Catch in Traffic   — Contested catch ability
YAC Ability        — Yards after catch
Release (Press)    — Beating press coverage at the line
Deep Speed         — Ability to stretch the field vertically
Body Control       — Sideline catches, adjusting to the ball
Blocking (WR)      — Downfield and screen blocking effort
Return Ability     — Kick/punt return capability
```

### 3.4 Tight End (TE)
```
Route Running      — Receiving route quality
Hands              — Catching reliability
Run Blocking       — Inline and pulling block effectiveness
Pass Blocking      — Protection ability
YAC Ability        — Yards after catch
Catch in Traffic   — Contested catch ability
Inline Alignment   — Effectiveness as attached blocker
Versatility        — Ability to align multiple positions
Seam Threat        — Vertical threat up the seam
Red Zone Target    — Effectiveness inside the 20
```

### 3.5 Offensive Line (OL) — C / OG / OT
```
Pass Blocking      — Anchor, hand placement, mirror ability
Run Blocking       — Drive blocks, reach blocks, combo blocks
Pulling            — Ability to pull and lead on outside runs
Footwork           — Kick slide, lateral movement, recovery
Hand Technique     — Punch timing, hand placement, leverage
Anchoring          — Holding ground against bull rush
Nastiness          — Finishing blocks, physicality, attitude
Communication      — Line calls, protection adjustments
Awareness (OL)     — Picking up stunts, twists, delayed blitz
Stamina (OL)       — Maintaining technique over 60+ snaps
```

### 3.6 Defensive Line (DL) — DE / DT
```
Pass Rush Moves    — Repertoire and execution of rush techniques
Run Stopping       — Gap discipline, point of attack strength
Bull Rush          — Straight power collapse of blocker
Speed Rush         — Edge speed to turn the corner
Counter Moves      — Secondary pass rush techniques
Hand Fighting      — Defeating blocks with hands
Pursuit            — Chase-down ability on plays away from you
Block Shedding     — Disengaging from blockers
Motor              — Effort and hustle consistency
Gap Discipline     — Maintaining assignment integrity
```

### 3.7 Linebacker (LB) — ILB / OLB
```
Tackling           — Sure tackling, form, wrap-up
Coverage (LB)      — Man and zone coverage ability
Blitzing           — Pass rush from linebacker position
Block Shedding     — Getting off blocks to make plays
Instincts          — Diagnosing plays, reading keys
Pursuit            — Sideline-to-sideline range
Zone Drops         — Depth, positioning, pattern reading
Man Coverage       — Matching up with backs and tight ends
Play Recognition   — Speed of diagnosis pre/post-snap
Physicality        — Hitting power and intimidation
```

### 3.8 Defensive Back (DB) — CB / S
```
Man Coverage       — Ability to stay with receiver one-on-one
Zone Coverage      — Reading QB eyes, maintaining zone responsibility
Press Technique    — Jamming receivers at the line
Ball Skills        — Interceptions, PBUs, tracking the ball
Tackling (DB)      — Open-field and run support tackling
Speed (DB)         — Recovery speed and deep coverage ability
Hip Fluidity       — Turning, flipping, transitioning in coverage
Route Recognition  — Anticipating receiver routes
Blitzing (DB)      — Effectiveness as a blitzer from secondary
Run Support        — Willingness and ability to play the run
```

### 3.9 Kicker / Punter (K/P)
```
Leg Strength       — Distance capability
Accuracy (K)       — Precision on field goals and extra points
Kickoff Distance   — Touchback capability
Punting Distance   — Gross and net average
Hang Time          — Air time on punts
Directional Kick   — Ability to place kicks to a side
Clutch             — Performance in high-pressure situations
Consistency        — Variance between best and worst kicks
Holder Skill       — (P only) Holding for field goals
Onside Kick        — (K only) Recovery rate on onside attempts
```

---

## 4. ATTRIBUTE CAP SYSTEM

### 4.1 Cap Tiers (Simplified)

**HIGH SCHOOL (Ages 14–18)**

| Year | Overall Cap | Physical Cap | Mental Cap | Skills Cap |
|---|---|---|---|---|
| Freshman | 65 | 70 | 60 | 68 |
| Sophomore | 72 | 76 | 65 | 73 |
| Junior | 78 | 82 | 70 | 80 |
| Senior | 84 | 88 | 76 | 85 |

**COLLEGE (Ages 18–23)**

| Year | Overall Cap | Physical Cap | Mental Cap | Skills Cap |
|---|---|---|---|---|
| Freshman | 82 | 86 | 78 | 83 |
| Sophomore | 87 | 90 | 83 | 88 |
| Junior | 92 | 94 | 87 | 92 |
| Senior / 5th Year | 95 | 96 | 91 | 95 |

**NFL (Ages 21–40+)**

| Phase | Overall Cap | Physical Cap | Mental Cap | Skills Cap |
|---|---|---|---|---|
| Rookie | 90 | 93 | 86 | 90 |
| Years 2–4 | 95 | 97 | 92 | 95 |
| Prime (5–8) | 99 | 99 | 96 | 99 |
| Veteran (9–12) | 99 | 97 (declining) | 99 | 99 |
| Twilight (13+) | 97 | 93 (declining) | 99 | 97 |

### 4.2 Cap Enforcement
Every turn, all attributes are checked against the active cap tier:
- If any attribute exceeds its cap, it is reduced to the cap value.
- The reduction is noted in the turn output.
- Caps advance automatically when the player transitions to a new year/level.

### 4.3 Decline Phase (NFL Veteran/Twilight)
Physical attributes begin natural decline after Year 8 in the NFL:
- Speed, Acceleration, Agility: −0.3 to −0.8 per turn (age-scaled)
- Strength, Power: −0.1 to −0.5 per turn
- Stamina, Durability: −0.2 to −0.6 per turn
- Flexibility, Jumping, Balance: −0.1 to −0.4 per turn

Mental attributes and position skills do **not** decline with age. They can still improve during decline phases. This reflects the reality that football intelligence peaks later than physical tools.

Decline rates accelerate with:
- Accumulated body wear
- Injury history (especially lower body, head)
- Low Warrior trait (gives up sooner)

Decline rates slow with:
- High Work Ethic (maintenance training)
- High Flexibility (injury prevention)
- Elite medical access (NFL tier)

---

## 5. DEVELOPMENT SYSTEM

### 5.1 Training
Each turn, the player selects up to **3 skills** to train. If no selection is made, auto-decision applies (§8 of Master Engine).

**Training Outcome Calculation:**
```
Roll (0–99) from tape or engine → maps to base outcome:

0–14:   Regression    (−0.3)
15–39:  Minimal       (+0.1)
40–69:  Standard      (+0.2)
70–84:  Good          (+0.3)
85–94:  Excellent     (+0.4)
95–99:  Breakthrough  (+0.5)

Final Change = Base × Age Multiplier × Coach Quality × Context Bonuses
```

### 5.2 Age Multipliers
```
14–17:  ×1.4  (High growth — body and brain still forming)
18–21:  ×1.2  (Peak learning — college development window)
22–24:  ×1.0  (Standard)
25–27:  ×0.8  (Refinement — gains are harder)
28–30:  ×0.5  (Maintenance — fighting plateau)
31+:    ×0.2  (Decline management — slowing erosion)
```

### 5.3 Coach Quality Multipliers
```
High School (varies):     0.8–1.2
Small College:            1.0–1.3
Power Conference:         1.2–1.5
NFL:                      1.3–1.6
Elite Program Bonus:      +0.2
```

### 5.4 Context Bonuses
- Scholar > 70: +0.05 to all training outcomes (faster learner)
- Work Ethic > 75: +0.05 (extra reps compound)
- Scheme Fit (training matches scheme needs): +0.05
- Playing Time (starter vs reserve): Starters gain +0.05 from in-game reps

### 5.5 Skill Development Curves
```
Fast Development (1–2 years to meaningful gains):
  Speed, Agility, Strength, Hands, Catching, Stamina

Medium Development (2–4 years):
  Route Running, Coverage, Vision, Pass Rush, Run Blocking

Slow Development (3–5 years):
  QB Accuracy (all ranges), OL Technique, Football IQ, 
  Pre-Snap Read, Scheme Mastery, Leadership
```

### 5.6 Non-Use and Rust
Skills not actively trained do **not** automatically decay during growth and prime phases (ages 14–30). Decay applies only during the decline phase (§4.3) and only to physical attributes.

However, **role mismatch** can cause rust:
- If a player changes positions, unused position skills stagnate (no growth without training) and may lose −0.1 per season if completely abandoned.
- If a player is inactive (injured, suspended, unsigned) for 6+ turns, physical conditioning attributes (Speed, Stamina, Strength) lose −0.1 per turn of inactivity beyond 6.

---

## 6. CALENDAR SYSTEM

### 6.1 Phase-Variable Turn Lengths
Per Master Engine §5.1. The calendar maps as follows:

**HIGH SCHOOL**
```
August:          Camp / Two-a-Days (2-week turns)
September–Nov:   Regular Season (1-week turns, ~12 games)
December:        Playoffs (1 game per turn)
January–March:   Offseason / Recruiting Visits (2-week turns)
April–May:       Spring Practice (2-week turns)
June–July:       Summer Camps / 7-on-7 (2-week turns)
```

**COLLEGE**
```
August:          Fall Camp / Position Battles (2-week turns)
September–Nov:   Regular Season (1-week turns, ~12 games)
December:        Conference Championship / Bowl Prep (1 game per turn)
January:         Bowl Game / Playoff (1 game per turn)
January–March:   Offseason / Portal Window / Draft Prep (2-week turns)
April–May:       Spring Ball / Pro Days (2-week turns)
June–July:       Summer Workouts (2-week turns)
```

**NFL**
```
August:          Training Camp / Preseason (2-week turns)
September–Jan:   Regular Season (1-week turns, 17 games + bye)
January:         Playoffs (1 game per turn)
February:        Super Bowl / Offseason begins (event-based)
March–April:     Free Agency / Draft (2-week turns)
May–July:        OTAs / Minicamp / Vacation (2-week turns)
```

### 6.2 Level Transitions
```
High School → College:  After senior season (or early graduation)
College → NFL Draft:     After junior year (earliest) or senior year
College → NFL UDFA:      Post-draft if undrafted
NFL → Retirement:        Per retirement triggers (§12)
Any Level → Coaching:    Post-retirement or direct entry (Coaching Module)
```

---

## 7. GAME SIMULATION

### 7.1 Performance Calculation
Per Master Engine §4.2, player performance and team outcome are independent.

**Player Game Performance Score (0–100):**
```
Base = (Primary Skill × 0.50) + (Secondary Skill × 0.30) + (Tertiary Skill × 0.20)

Adjusted = Base
  × (Health% / 100)
  × Chemistry Factor
  × Matchup Factor
  × Weather Factor
  × Composure Factor (home/away, stakes)
  ± Variance (roll-based, ±15 max)

Primary/Secondary/Tertiary skills are position-dependent (see §7.2)
```

**Team Game Outcome:**
```
Team Win Probability = f(Team OVR, Opponent OVR, Home/Away, Chemistry, Coaching, Injuries)

Roll determines outcome within probability range.
Player performance modifies team output quality but does not override win probability beyond ±8%.
```

### 7.2 Position Performance Drivers

| Position | Primary (50%) | Secondary (30%) | Tertiary (20%) |
|---|---|---|---|
| QB | Accuracy (situation-weighted) | Decision Making | Composure |
| RB | Vision (Rush) | Elusiveness | Speed |
| WR | Route Running | Hands | Separation |
| TE | Route Running | Run Blocking | Hands |
| OL | Pass/Run Blocking (weighted) | Technique | Strength |
| DL | Pass Rush / Run Stop (weighted) | Technique | Motor |
| LB | Instincts | Tackling | Coverage |
| CB | Man/Zone Coverage (weighted) | Ball Skills | Speed |
| S | Zone Coverage | Tackling | Instincts |
| K | Accuracy | Leg Strength | Clutch |
| P | Distance | Hang Time | Directional |

### 7.3 Stat Generation
Position-specific stat lines are generated from the performance score using the formulas below. All formulas use the player's actual attributes scaled by game context.

**QB Stats:**
```
Attempts = 25 + (Team Scheme Pass Rate × 15) ± roll variance
Completions = Attempts × ((Accuracy_Weighted × 0.4 + Vision × 0.3 + Composure × 0.3) / 100)
Yards = Completions × (5 + Arm_Strength × 0.08 + Scheme_YPA_Bonus)
TDs = floor(Yards / 120) + (Red_Zone_Factor × 0.02) ± roll
INTs = max(0, round(2.5 − Decision_Making × 0.025 + Pressure_Factor × 0.5)) ± roll
Sacks = max(0, round(3 − OL_Quality × 0.03 − Pocket_Presence × 0.02))
Rush Yards = (Speed × 0.3 + Agility × 0.2) × Designed_Run_Rate ± roll
```

**RB Stats:**
```
Carries = 12 + (Depth_Position × 5) + (Scheme_Run_Rate × 8)
Yards = Carries × ((Vision × 0.35 + Speed × 0.25 + Elusiveness × 0.2 + OL_Run_Block × 0.2) / 20)
TDs = floor(Yards / 110) + (Power × 0.01 + Goal_Line_Role × 0.5) ± roll
Fumbles = max(0, round(1 − Ball_Security × 0.01)) (roll-dependent)
Receptions = (Hands × 0.03 + Route_Running × 0.02) × Pass_Game_Role
Receiving Yards = Receptions × (YAC × 0.15 + Speed × 0.10)
```

**WR Stats:**
```
Targets = 3 + (Route_Running × 0.06) + (Separation × 0.04) + (Depth_Role × 2)
Receptions = Targets × (Hands × 0.008 + QB_Accuracy × 0.004)
Yards = Receptions × ((Speed × 0.3 + YAC × 0.3 + Route_Running × 0.2 + Deep_Speed × 0.2) × 0.18)
TDs = floor(Yards / 130) + (Red_Zone × 0.015) ± roll
Drops = max(0, round(Targets × 0.08 − Hands × 0.001))
```

**OL Stats:**
```
Pancakes = floor(Strength × 0.04 + Nastiness × 0.03 + Run_Blocking × 0.02)
Pressures Allowed = max(0, round(4 − Pass_Blocking × 0.04 − Footwork × 0.02))
Penalties = max(0, round(1.5 − Discipline × 0.015))
PFF-Style Grade = 60 + (Pancakes × 2.5) − (Pressures × 3.5) − (Penalties × 5)
```

**Defensive Stats:**
```
Tackles = (Pursuit × 0.12 + Tackling × 0.10 + Instincts × 0.06) × Position_Snap_Factor
Sacks = (Pass_Rush × 0.015 + Speed_Rush × 0.01) × Snap_Rate × Blitz_Opportunity
TFLs = (Instincts × 0.015 + Speed × 0.01 + Strength × 0.008)
INTs = (Ball_Skills × 0.008 + Coverage × 0.005 + Instincts × 0.003) × Coverage_Snap_Rate
PBUs = (Coverage × 0.015 + Ball_Skills × 0.01 + Jumping × 0.005)
FF = (Physicality × 0.004) × Tackle_Opportunities
```

**K/P Stats:**
```
FG Made = Attempts × (Accuracy × 0.008 + Clutch × 0.003)
FG Distance = 30 + (Leg_Strength × 0.25)
Punt Average = 35 + (Distance × 0.12 + Leg_Strength × 0.06)
Touchback Rate = Kickoff_Distance × 0.01
```

### 7.4 Opponent Generation
Each game, the engine generates an opponent:

```
Opponent Base OVR = Conference_Level + Program_Tier + Current_Form ± roll(5)

Conference Levels:
  Elite HS / Power Conference / NFL Playoff:  85–95
  Average HS / Group of 5 / NFL Middle:       75–85
  Weak HS / FCS / NFL Rebuilding:             65–75

Current Form:
  Win Streak (3+): +2 per win (max +8)
  Losing Streak (3+): −2 per loss (max −6)
  Ranked: +4    Rivalry: +4    Championship: +7

Key Matchup Player (your positional opponent): Opponent Base ± 3
```

**Opponent Style** (generated per game): Power Run / Spread / Pro-Style / Air Raid / Option / Multiple

**Weather** (generated per game):
```
Clear: No effect
Rain: −5% skill positions
Snow: −8% passing, −5% speed
Wind (15+ mph): −10% kicking, −5% deep passing
Extreme Heat (>95°F): −3% stamina per quarter
Extreme Cold (<20°F): −5% catching, +2% injury risk
```

---

## 8. INJURY SYSTEM

### 8.1 Position Base Risk (Per Game)
```
High (8–12%):     RB: 12%  |  LB: 11%  |  TE: 10%  |  S: 9%  |  DE: 9%
Moderate (4–8%):  WR: 8%   |  CB: 8%   |  OLB: 7%  |  DT: 7%  |  C: 6%  |  OG/OT: 5%
Low (1–4%):       QB: 3%   |  K: 1%    |  P: 1%    |  LS: 2%
```

### 8.2 Risk Modifiers
```
Fatigue:    0–20: +0%  |  21–40: +2%  |  41–60: +5%  |  61–80: +9%  |  81–100: +15%
Age:        14–21: +0%  |  22–27: +1%  |  28–30: +3%  |  31–33: +6%  |  34+: +10%
Body Wear:  +1% per 20 points of career wear average
Game Context: Preseason −2% (fewer snaps) | Playoffs +2% (higher intensity)
```

**Total Risk = Base + Fatigue Mod + Age Mod + Wear Mod + Context**

Roll: If roll < Total Risk → injury occurs.

### 8.3 Injury Severity
```
Roll determines severity when injured:
0–39:   Minor     (1–2 weeks)   — Attributes: −5 while injured
40–69:  Moderate  (3–6 weeks)   — Attributes: −10 while injured
70–89:  Major     (8–16 weeks)  — Attributes: −20 while injured, −5 permanent wear
90–99:  Severe    (Season/Career threatening) — Attributes: −30, −10 permanent wear
```

### 8.4 Recovery
```
Recovery Time = Base Weeks × Age Factor × Medical Factor × Warrior Factor

Age Factor:     <21: ×0.85  |  21–27: ×1.0  |  28–32: ×1.25  |  33+: ×1.5
Medical Factor: HS: ×1.15   |  Small College: ×1.08  |  Power Conf: ×1.0  |  NFL: ×0.90
Warrior Factor: >70: ×0.88  |  30–70: ×1.0  |  <30: ×1.12
```

---

## 9. MENTAL ATTRIBUTE BEHAVIORAL EFFECTS

Beyond their direct on-field impact, mental attributes drive off-field behavior, chemistry, career decisions, and NPC reactions.

### 9.1 Leadership
- Chemistry impact: Leadership × 0.5
- Clash if multiple high-Leadership players (>70 each): −10 chemistry per clash
- Recruiting/NIL appeal: +Leadership × 0.2
- Contract demands: +Leadership × 0.1%
- Draft declaration lean: Leadership > 70 biases toward declaring early (confidence)

### 9.2 Competitiveness
- Playing through injury: Will play at 70% health if Competitiveness > 60
- Teammate respect: +Competitiveness × 0.3 to chemistry
- Fatigue resistance: ×(1 − Competitiveness × 0.002)
- Career longevity: Competitiveness > 70 extends career 2–3 years
- Injury recovery drive: ×(1 − Competitiveness × 0.003)

### 9.3 Football IQ
- Development rate bonus: ×(1 + Football IQ × 0.003)
- Playbook mastery: 2× faster if Football IQ > 70
- Pre-snap reads: +Football IQ × 0.2
- Draft interview score: +Football IQ × 0.3

### 9.4 Work Ethic
- GPA calculation: Base 2.0 + (Work Ethic × 0.02) + (Football IQ × 0.015)
- Training consistency bonus: Work Ethic > 75 adds +0.05 to all training outcomes
- Film study benefit: Work Ethic > 70 adds +0.1 to Awareness growth per turn

### 9.5 Coachability
- Chemistry contribution: +Coachability × 0.4
- Role acceptance: No complaints if Coachability > 60
- Hometown discount: Coachability × 0.2% on contracts
- Transfer likelihood: −Coachability × 0.5%

### 9.6 Composure
- Media controversy risk: Composure < 30 = 10% chance per turn
- Distraction risk: −Chemistry if Composure < 30 AND Leadership > 70 (ego without control)
- NIL marketability: Low Composure players attract more attention (positive and negative)
- Social media growth: ×(1 + (100 − Composure) × 0.005) — less composed = more visible
- Draft marketability: Composure > 70 = +5 to character score; < 40 = −5

### 9.7 Discipline
- Penalty avoidance (on-field)
- Suspension risk: Discipline < 40 = 5% chance per turn of off-field issue
- NIL deal reliability: Low Discipline risks breaching appearance obligations

### 9.8 Attribute Shifts from Events
Mental attributes shift based on career events:
```
Big game performance:      +2 Leadership, +1 Composure
Benching:                  −3 Leadership, +2 Coachability
Injury overcome:           +3 Competitiveness, +2 Discipline
Academic achievement:      +2 Football IQ, +2 Work Ethic
Team championship:         +2 Coachability, +1 Leadership
Major media attention:     −1 Composure (if < 60), +1 Awareness
Leadership role (captain): +3 Leadership, +2 Coachability
Public controversy:        −3 Composure, −2 Discipline
```

---

## 10. CHEMISTRY SYSTEM

### 10.1 Calculation
```
Team Chemistry (0–100) =
  (Leadership Component × 0.25) +
  (Performance Component × 0.25) +
  (Personality Mesh × 0.25) +
  (Shared Experience × 0.25)
```
No base values. Pure calculation from components.

### 10.2 Components
```
Leadership = (Your_Leadership × Depth_Weight × Respect) / 100
  Depth Weight: Starter=1.0, Backup=0.6, Reserve=0.3
  Respect: Captain=1.5, Veteran=1.2, New=0.8

Performance = 50 + (Sum of last 3 games vs expectation)
  Exceed expectation: +5 per game
  Meet: +0
  Below: −5 per game

Personality Mesh = 50 + Alignment Bonuses − Clash Penalties
  Compatible mental attribute profiles with teammates: +5 each
  Clashing profiles (e.g., multiple high-Leadership players): −5 each

Shared Experience = 30 + modifiers
  Years together: +5 per year (max +20)
  Championships: +10 each
  Comeback wins: +3 each
  New coach/transfer in: −15
```

### 10.3 Chemistry Effects
```
80–100:  +8% performance, +15% clutch, +0.2 development bonus
60–79:   +4% performance, +8% clutch, +0.1 development bonus
40–59:   No modifiers (neutral)
20–39:   −5% performance, −10% clutch, −0.1 development
0–19:    −12% performance, −20% clutch, −0.3 development
```

### 10.4 Level Transition Chemistry Resets
```
HS → College:    Start at 40. +5 if HS coach connection, +5 if HS teammates join, +10 if local school.
College → NFL:   Start at 35. +5 if similar scheme, +5 if college teammates, +10 if Round 1–2 pick.
Transfer:        Start at 45. +5 if similar system, +5 if former teammates, −10 if forced transfer.
Coaching Change: Current × 0.75. −20 if scheme change, −10 if coordinator change only.
```

---

## 11. ACADEMIC SYSTEM

### 11.1 GPA Calculation
```
Base GPA = 2.0 + (Scholar × 0.025) + (Work_Ethic × 0.015)
Modifiers:
  Study time (hrs/week): +0.1 per 5 hours
  Tutor: +0.2
  Missed classes: −0.1 per absence
  In-season: −0.2
Updates: Each semester (end of fall / end of spring)
```

### 11.2 Eligibility
**High School:** Min 2.0 GPA, pass 5 of 6 classes, attendance > 80%
**College:** Min 2.0 GPA, 12 credits/semester, progress toward degree (40%/60%/80% by years 2/3/4), APR > 930

### 11.3 Consequences
```
GPA < 2.0:  Academic probation — ineligible for games
GPA < 1.7:  Suspension — no team activities
Failed classes: Summer school required
GPA > 3.5:  Academic All-American eligible
```

---

## 12. TRANSFER PORTAL (COLLEGE)

### 12.1 Windows
```
Window 1:  December 5–20 (post-regular season)
Window 2:  April 15–30 (post-spring)
Graduate:  May 1–July 31 (if degree completed)
```

### 12.2 Process
```
Turn 1 — Enter Portal:
  Lose facility access, NIL deals suspended, 48-hour withdrawal window.

Turn 2 — Recruitment:
  Interested schools = 3 + (OVR − 70) / 5
  Higher-tier schools if OVR > 85

Turn 3 — Decision:
  Transfer Score = Playing Time × 0.35 + NIL × 0.25 + Scheme Fit × 0.20 + Academics × 0.10 + Location × 0.10
  Auto-transfer if: Depth ≥ 4th AND Transfer Score > 75
```

### 12.3 Eligibility
- First-time transfer: Immediate eligibility
- Second transfer: Sit one year (unless waiver)
- Cannot enter if on academic probation or active suspension

---

## 13. NFL DRAFT

### 13.1 Declaration Logic
```
Declaration Score =
  (Projected Round × 40) +
  (Personality Factors × 30) +
  (Financial Need × 15) +
  (Injury Risk × 15)

Projected Round Points: Rd1=40, Rd2=35, Rd3=25, Rd4–5=15, Rd6–7=5, UDFA=0
Personality: Alpha>70: +10 | Spotlight>60: +8 | Scholar<40: +5 | Team-First>70: −10
Financial: Family hardship: +15 | Low NIL: +10 | High NIL: −5
Injury: Prior major: +15 | High-risk position: +10 | Clean history: −5

Score > 60: Declare | 40–60: Player decides | < 40: Return
Special: Heisman +20, Bowl win +10, Losing season +15, New coach +10
```

### 13.2 Draft Score
```
Draft Score =
  (Athletic × 0.30) + (Production × 0.25) + (Measurables × 0.15) +
  (Medical × 0.10) + (Character × 0.10) + (Position Value × 0.10)

95–100: Top 5  |  90–94: Round 1  |  85–89: Round 2  |  80–84: Round 3
75–79: Rounds 4–5  |  70–74: Rounds 6–7  |  <70: UDFA
```

### 13.3 Combine
```
Event Score = 50 + ((Your Result − Position Average) / Position StdDev) × 20
Total Combine Score = Average of all events
Impact: ±15 to draft stock maximum
```

### 13.4 Measurable Conversions
```
Speed → 40-yard:           5.5 − (Speed × 0.013) seconds
Strength → Bench:          5 + ((Strength − 40) × 0.45) reps
Power → Vertical:          20 + (Power × 0.18) inches
Power → Broad Jump:        84 + (Power × 0.36) inches
Agility → 3-Cone:          8.0 − (Agility × 0.025) seconds
Agility → 20-Yard Shuttle: 5.0 − (Agility × 0.018) seconds
```

---

## 14. NFL CONTRACTS & FINANCES

### 14.1 Rookie Contracts
```
Round 1 Pick 1–5:    $35–40M / 4 years (5th year option)
Round 1 Pick 6–10:   $25–35M / 4 years (5th year option)
Round 1 Pick 11–20:  $15–25M / 4 years (5th year option)
Round 1 Pick 21–32:  $10–15M / 4 years (5th year option)
Round 2:             $5–9M / 4 years
Round 3:             $3.5–5M / 4 years
Round 4–5:           $2.8–3.5M / 4 years
Round 6–7:           $2.5–2.8M / 4 years
UDFA:                $100–500K guaranteed
```

### 14.2 Veteran Contracts
```
Extension Value = Market Base × Performance Multiplier × Age Factor

Performance: Pro Bowl ×1.3 | All-Pro ×1.5 | MVP ×2.0 | Top 10 at position ×1.2 | Below top 20 ×0.8

Market Values (annual):
QB: $45–55M  |  EDGE: $25–30M  |  WR: $25–30M  |  LT: $20–25M
CB: $18–22M  |  DT: $17–20M   |  S: $15–18M   |  LB: $15–18M
RB: $10–15M  |  TE: $12–15M   |  IOL: $10–15M  |  K/P: $3–5M

Franchise Tag: Top 5 (exclusive) or Top 10 (transition) average at position
```

### 14.3 Era Adjustment
All contract values, salary cap figures, franchise tag thresholds, and market rates listed in this module reflect approximate 2024–2025 benchmarks. **The engine must adjust all financial figures to match the simulation's current in-game year.** If the career begins in 2010, contract values should reflect 2010-era markets. If the career reaches 2035, values should project forward using historical NFL salary cap growth (~7–10% annually). This applies to rookie slot values, veteran market rates, franchise tag calculations, NIL tiers, and all financial tracking. The listed figures are reference points, not fixed constants.

### 14.4 Financial Tracking
```
Income:  Salary + Bonuses + Endorsements/NIL
Deductions:
  Agent: 3%
  Federal Tax: 37%
  State Tax: 0–13% (team-dependent)
  Living Expenses: $15–50K/month (lifestyle-scaled)

Net Worth = Gross − Taxes − Agent − Expenses + Investment Returns
Investment Returns: 5–8% annually if Scholar > 60, 2–4% otherwise
```

---

## 15. NIL SYSTEM (COLLEGE)

### 15.1 Value Calculation
```
Base = (Overall × $1,000) × Position Premium × Market × Social

Position Premiums: QB: 2.5 | RB/WR: 1.5 | OL/DL: 0.8 | Other: 1.0
Market Size: Major (LA, NYC): 2.0 | Large: 1.5 | Medium: 1.0 | Small: 0.7
Social Media: 1.0 + (Followers / 100,000)
```

### 15.2 Tiers
```
Tier 1 ($1K–10K):    60+ OVR, local deals
Tier 2 ($10K–50K):   70+ OVR, regional brands
Tier 3 ($50K–500K):  80+ OVR, national brands
Tier 4 ($500K–2M):   90+ OVR, major endorsements
```

---

## 16. RETIREMENT

### 16.1 Forced Retirement
Automatic if any occur:
- Age ≥ 40
- Career-ending injury (severity roll 90+)
- 3 consecutive years unsigned
- Overall < 50 AND age > 32
- Career body wear average > 85

### 16.2 Voluntary Retirement Consideration
Checked each offseason:
```
Retirement Score =
  (Age Factor × 30) + (Health Factor × 25) + (Role Factor × 20) +
  (Financial Security × 15) + (Personality × 10)

Age Factor: (Age − 25) × 2 (min 0)
Health: (100 − Health) / 2
Role: Starter=0, Backup=10, 3rd string+=20
Financial: Earnings > $20M = 15, > $10M = 10, < $10M = 0
Personality: Competitiveness < 50 = +10, Coachability > 70 = −5

Score > 65: Retirement dialogue  |  > 80: Strong lean  |  > 95: Near-certain
```

### 16.3 Post-Retirement
- Coaching career (activates Coaching Module)
- End simulation
- Hall of Fame evaluation (if career warrants)

---

## 17. DEFAULT CHARACTER (HS JUNIOR)

Full starting attributes for the default character:

```
PHYSICAL (Cap: 82):
Speed: 65  |  Acceleration: 63  |  Agility: 67  |  Strength: 58  |  Power: 56
Stamina: 70  |  Durability: 68  |  Flexibility: 65  |  Jumping: 60  |  Balance: 64

MENTAL (Cap: 70):
Football IQ: 62  |  Vision: 64  |  Composure: 60  |  Leadership: 58  |  Work Ethic: 65
Coachability: 68  |  Competitiveness: 66  |  Discipline: 63  |  Awareness: 61  |  Decision Making: 59

QB SKILLS (Cap: 80):
Arm Strength: 68  |  Acc Short: 70  |  Acc Medium: 65  |  Acc Deep: 60  |  Touch: 62
Release: 64  |  Pocket Presence: 58  |  Throwing on Run: 55  |  Read Progression: 60  |  Pre-Snap Read: 57

PERSONALITY (Total: 250):
Alpha: 55  |  Warrior: 45  |  Scholar: 65  |  Team-First: 50  |  Spotlight: 35

Overall: 64.8 / 100

STARTING STATE:
Career Turn: 1
Date: August 1–14 (Turn 1)
Season: Summer Camp / Two-a-Days
Team Record: 0–0 (Previous: 6–4)
Depth Chart: #2 QB (Behind Senior Marcus Webb, 71 OVR)
Chemistry: 65  |  Health: 100%  |  Fatigue: 0
GPA: 3.2  |  Credits: 16/24  |  Eligible: Yes
```

---

*Player Module — Complete. References Master Engine for realism rules, turn processing, randomness, output modes, and auto-decisions.*
