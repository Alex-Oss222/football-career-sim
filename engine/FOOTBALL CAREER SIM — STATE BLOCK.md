# FOOTBALL CAREER SIM — STATE BLOCK

> The compact persistence layer for session continuity. This is what gets exported on `"Save"` and pasted to resume. Always active regardless of module.

---

## 1. PURPOSE

The State Block is the **single source of truth**. Every turn, the engine writes changes here. Every turn, the engine reads from here. If the State Block says it, it's true. If it doesn't, it didn't happen.

**Rules:**
- Narrative cannot contradict the State Block.
- State Block updates happen at Step 7 of turn processing (Master Engine §5.3), after all mechanics resolve.
- On resume from save, the engine validates the State Block before loading modules.
- The State Block must be compact enough to paste into a new chat session without exceeding practical limits.

---

## 2. PLAYER STATE BLOCK FORMAT

```
=== FOOTBALL CAREER SIM — SAVE STATE ===
MODE: PLAYER
TAPE: [MODE A (position X/Y) | MODE B (engine-generated)]

--- IDENTITY ---
Name: [Name]
Position: [POS] | Height: [X'X"] | Weight: [X] lbs | Age: [X]
School/Team: [Name] | Conference/Division: [Name]
Level: [HS/College/NFL] | Year: [Freshman/Sophomore/.../Rookie/Year X]
Head Coach: [Name] ([Scheme]) | Coach Trust: [X]/100

--- TIMELINE ---
Career Turn: [X]
Season Turn: [X]
Phase: [Camp/Regular Season/Playoffs/Offseason/Combine/Draft]
Date: [Month DD, YYYY]
Next Phase Change: [Event] in [X] turns

--- ON-FIELD ---
Depth Chart: #[X] [POS] ([Starter/Backup/Reserve/Scout Team])
Team Record: [W-L] ([Conference W-L]) | Previous Season: [W-L]
Season Expectation Band: [X–X wins]
Team OVR: [X] | Opponent Next: [Name] ([OVR], [Style])

--- RATINGS ---
Overall: [X]/100 | Cap: [X] ([Level] [Year])

Physical: SPD [X] | ACC [X] | AGI [X] | STR [X] | PWR [X] | STA [X] | DUR [X] | FLX [X] | JMP [X] | BAL [X]
Mental:   IQ [X] | VIS [X] | CMP [X] | LDR [X] | WRK [X] | COA [X] | COMP [X] | DIS [X] | AWR [X] | DEC [X]
Skills:   [Position-specific, abbreviated — e.g., ARM [X] | ACS [X] | ACM [X] | ACD [X] | TCH [X] | REL [X] | PKT [X] | TOR [X] | RPR [X] | PSR [X]]

--- BODY ---
Health: [X]% | Fatigue: [X]/100
Injury: [None | Type (X weeks remaining)]
Career Wear: [X] avg
Body Log: [Summary of major injuries — e.g., "ACL Year 2 College, Ankle Year 5 NFL"]

--- CHEMISTRY ---
Team Chemistry: [X]/100
Components: Leadership [X] | Performance [X] | Mesh [X] | Shared Exp [X]
Key Relationships:
  [Name] ([Role]): [X]/100 — [1-line status]
  [Name] ([Role]): [X]/100 — [1-line status]
  [Name] ([Role]): [X]/100 — [1-line status]

--- ACADEMICS --- (HS/College only)
GPA: [X.X] | Credits: [X/X] | Eligible: [Yes/No]
Academic Status: [Normal/Probation/Suspended]

--- FINANCES ---
[HS]: Family expenses this season: $[X]
[College]: NIL Value: $[X]/yr | Active Deals: [X] | Savings: $[X]
[NFL]: Contract: [Year X of Y] | Base: $[X] | Cap Hit: $[X] | Career Earnings: $[X] | Net Worth: $[X]

--- DRAFT STATUS --- (College Junior+ only)
Projection: [Round X / UDFA / N/A]
Draft Score: [X]/100
Declaration Score: [X]/100
Stock Trend: [Rising/Stable/Falling]

--- SEASON STATS ---
[Position-specific cumulative stats for current season — compact single line]
[e.g., QB: 145/232 62.5% 1,847yds 14TD 6INT 89.2 RTG | Rush: 43-187-2TD]

--- CAREER STATS ---
[Cumulative career totals — compact single line]

--- ACTIVE CONSEQUENCES ---
[Open consequence chains that must carry forward]
- [e.g., "Coach trust dropping after 2 bad games — one more poor performance triggers benching talk"]
- [e.g., "Rival WR transfer arriving next month — depth chart competition imminent"]
- [e.g., "NIL deal with regional brand requires 2 appearances before December"]

--- LAST 3 TURNS SUMMARY ---
Turn [X]: [1-line summary of key event/result]
Turn [X]: [1-line summary]
Turn [X]: [1-line summary]

=== END SAVE STATE ===
```

---

## 3. COACHING STATE BLOCK FORMAT

The coaching state block uses a **universal shell** (present for all coaching roles) plus a **role-specific payload** (changes when role changes). On promotion, the old role payload is removed and the new one is initialized.

### 3.1 Universal Coaching Shell

This section is present for every coaching role. It is the permanent skeleton.

```
=== FOOTBALL CAREER SIM — SAVE STATE ===
MODE: COACHING
TAPE: [MODE A (position X/Y) | MODE B (engine-generated)]

--- IDENTITY ---
Name: [Name] | Age: [X]
Current Role: [GA/QC/Position Coach/Coordinator/HC]
Position Detail: [e.g., Offensive QC, TE Coach, Offensive Coordinator, Head Coach]
School/Team: [Name] | Level: [HS/College/NFL]
Conference/Division: [Name]

--- TIMELINE ---
Career Turn: [X] (Coaching Turn [X])
Season Turn: [X]
Phase: [Camp/Regular Season/Playoffs/Offseason]
Date: [Month DD, YYYY]
Next Phase Change: [Event] in [X] turns

--- RECORD ---
Season Record: [W-L] ([Conference W-L])
Career Coaching Record: [W-L]
Season Expectation Band: [X–X wins]
Team OVR: [X]

--- JOB STATUS ---
Job Security: [X]/100 ([Secure/Stable/Warm/Hot/Critical])
Stress: [X]/100
Contract: [Year X of Y] | Salary: $[X] | Buyout: $[X]
AD/Owner Trust: [X]/100
Booster Confidence: [X]/100 (College) | Owner Patience: [X]/100 (NFL)

--- COACHING ATTRIBUTES ---
Core:    TAC [X] | TCH [X] | LDR [X] | REC [X] | MAN [X] | MOT [X]
Scheme:  SDN [X] | GMG [X] | PEV [X] | MED [X] | STF [X] | ADM [X]
Advanced: INV [X] | DEV [X] | CNT [X] | CMB [X] | TRD [X]

Traits: Disciplinarian [X] | Players' Coach [X] | Innovator [X] | Traditionalist [X]

--- SCHEME ---
Offense: [Philosophy] | Installation: [X]% | Complexity: [X/10]
Defense: [Philosophy] | Installation: [X]% | Complexity: [X/10]
Control: [Full/Delegate One/Delegate Both/Collaborative]

--- REPORTING STRUCTURE ---
Reports To: [Name] ([Role])
Serving System: [Name]'s [Offense/Defense/Overall Program]
Delegated Authority: [None | specific area]
Source: [N/A | who granted it]
Duration: [N/A | turn-limited / ongoing]

--- STAFF CHAIN ---
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Additional staff as needed]

--- RELATIONSHIPS ---
Key Relationships:
  [Name] ([Role]): [X]/100 — [1-line status]
  [Name] ([Role]): [X]/100 — [1-line status]
  [Name] ([Role]): [X]/100 — [1-line status]

Rival Coaches:
  [Name] ([Team]): [Archetype] — [Current situation]
  [Name] ([Team]): [Archetype] — [Current situation]

--- FINANCES ---
Salary: $[X]/yr | Career Coaching Earnings: $[X] | Net Worth: $[X]
Career Total Earnings (Playing + Coaching): $[X]

--- LEGACY ---
Legacy Points: [X]
Key Achievements: [Compact list — e.g., "2x Conf Champ, 14 players developed +10 OVR, 2 assistants now HCs"]

--- ACTIVE CONSEQUENCES ---
- [e.g., "AD expects bowl game this year — missing it triggers hot seat"]
- [e.g., "OC and DC in open conflict — resolution needed within 2 turns"]
- [e.g., "Star QB considering transfer — must address by end of month"]

--- JOB SEARCH STATUS --- (If active)
Interview Module: [Active/Inactive]
Applications:
  [Position] at [School]: Stage [X] — [Status]
  [Position] at [School]: Stage [X] — [Status]
Calendar Frozen: [Yes/No]

--- LAST 3 TURNS SUMMARY ---
Turn [X]: [1-line summary]
Turn [X]: [1-line summary]
Turn [X]: [1-line summary]
```

### 3.2 Role Payload: GA / QC

Appended after the universal shell when Current Role is GA or QC.

```
--- ROLE PAYLOAD: GA_QC ---
Supervisor: [Name] | Role: [OC / DC / Position Coach / HC]
Primary Responsibilities: [Film / Scout Team / Admin / Install Support]
Current Assignments:
  - [Task] — [Status]
  - [Task] — [Status]
  - [Task] — [Status]
Learning Track:
  System Familiarity: [X]/100
  Building Knowledge: [X]/100
  Staff Trust Footprint: [X]/100
Access Level:
  Meetings: [What rooms — e.g., "Offensive staff only" / "All staff" / "Position meetings"]
  Practice Authority: [Scout team only / limited / none]
  Film Access: [What cutups / who assigns]
Promotion Readiness:
  [What is being evaluated next — e.g., "Needs 70+ system familiarity and supervisor trust 65+ for position coach consideration"]
season_evaluation:
  last_score: [X]
  trajectory: [up/stable/down]
  outcome: [retained/promoted/etc]
```

### 3.3 Role Payload: Position Coach

Appended after the universal shell when Current Role is Position Coach.

```
--- ROLE PAYLOAD: POSITION_COACH ---
Room: [TE / WR / OL / QB / DL / LB / DB / ST etc.]
Reports To: [Coordinator Name] ([OC/DC]) / [HC Name] if no coordinator layer
Room Health: [Stable / Thin / Chaotic]
Starters:
  [Player] — [OVR] — [Season/month stats]
  [Player] — [OVR] — [Season/month stats]
Rotation / Bench:
  [Player] — [OVR] — [Season/month stats]
  [Player] — [OVR] — [Season/month stats]
Practice Squad / Developmental:
  [Player] — [OVR] — [Development note]
  [Player] — [OVR] — [Development note]
Room Priorities:
  - [Need — e.g., "Develop backup TE blocking technique"]
  - [Need — e.g., "Starter needs route-tree expansion"]
Teaching Focus:
  - [Technique — e.g., "Inline blocking hand placement"]
  - [Assignment issue — e.g., "Pass-pro ID system recognition"]
Room Trust:
  [Player]: [X]/100
  [Player]: [X]/100
  [Player]: [X]/100
season_evaluation:
  last_score: [X]
  trajectory: [up/stable/down]
  outcome: [retained/promoted/etc]
```

### 3.4 Role Payload: Coordinator

Appended after the universal shell when Current Role is Coordinator.

```
--- ROLE PAYLOAD: COORDINATOR ---
Side: [Offense / Defense]
Reports To: [Head Coach Name]
Control Level: [Install only / Shared call / Full play-call]
Unit Identity: [Scheme philosophy — e.g., "West Coast, spread formations, tempo variable"]
Unit Performance:
  Points/Game: [X] | Yards/Game: [X] | Efficiency: [X]
  Third Down: [X]% | Red Zone: [X]% | Turnovers: [+/- X]
Key Unit Players:
  [Player] — [Position] — [Season/game stats]
  [Player] — [Position] — [Season/game stats]
  [Player] — [Position] — [Season/game stats]
  [Player] — [Position] — [Season/game stats]
Play-Calling Access:
  [None / Situational / Full]
Call-Influence Notes:
  [Short line — e.g., "HC overrides on 4th down and red zone"]
Adjustment Grade:
  [X]/10
HC Alignment:
  [X]/100
Media Exposure:
  [Low / Moderate / High]
season_evaluation:
  last_score: [X]
  trajectory: [up/stable/down]
  outcome: [retained/promoted/etc]
```

### 3.5 Role Payload: Head Coach

Appended after the universal shell when Current Role is Head Coach.

```
--- ROLE PAYLOAD: HEAD_COACH ---
Team Snapshot:
  Team OVR: [X] | Record: [W-L] | Expectation Band: [X–X wins] | Playoff Status: [In / Out / Contending / Eliminated]
Coordinator Status:
  OC: [Name] — Trust: [X]/100 — [1-line status]
  DC: [Name] — Trust: [X]/100 — [1-line status]
  STC: [Name] — Trust: [X]/100 — [1-line status]
Roster Snapshot:
  Strongest Unit: [Unit] ([Avg OVR])
  Weakest Unit: [Unit] ([Avg OVR])
  Key Injuries: [Player] [POS] ([X weeks]) | [None]
  Recruiting Class Rank: #[X] (College) | Cap Space: $[X]M (NFL)
Organization Pressure:
  Owner/AD/GM: [Name] — Patience: [X]/100 — [1-line]
  Boosters/Media: [1-line summary]
Full Control Areas:
  [List — e.g., "Scheme direction, staff hires, roster cuts, game management, media"]
Delegated Areas:
  [List — e.g., "Play-calling to OC, defensive scheme detail to DC"]
season_evaluation:
  last_score: [X]
  trajectory: [up/stable/down]
  outcome: [retained/promoted/etc]
```

### 3.6 Closing Tag

Always end with:

```
=== END SAVE STATE ===
```

---

## 4. VALIDATION ON LOAD

When a State Block is pasted to resume:

```
1. Check MODE → Load appropriate modules (Player or Coaching + Interview if active)
2. Check Current Role → Validate that the correct role payload is present
3. Validate all attributes against current caps
4. Verify timeline consistency (date vs turn count vs phase)
5. Verify Reporting Structure and Delegated Authority fields are present and parseable
6. Confirm active consequences are parseable
7. Check for missing required fields → prompt user to fill gaps
8. Load tape mode and position if Mode A
9. Resume from next turn
```

If validation fails, the engine reports which fields are problematic and asks the user to correct before proceeding. It does not silently guess or fill in defaults for critical fields.

---

## 5. SAVE/LOAD COMMANDS

```
"Save"          — Export current State Block (copy-pasteable)
"State"         — Display current State Block inline (not as export)
"Load"          — Paste a State Block to resume
"Validate"      — Run validation checks on current state without advancing
```

---

## 6. PROMOTION TRANSITIONS

When a coaching role changes (e.g., QC → Position Coach, Position Coach → Coordinator, Coordinator → HC):

```
1. Remove the old role payload section entirely.
2. Initialize the new role payload with appropriate defaults based on the new position.
3. Update Current Role and Position Detail in the Identity section.
4. Update Reports To in Reporting Structure.
5. Reset Delegated Authority to None unless the hiring context specifies otherwise.
6. Carry forward all universal shell data unchanged.
7. Log the promotion in Active Consequences if it creates new expectations or deadlines.
```

The engine does not blend payloads. The character is either a QC or a Position Coach — never a hybrid.

---

## 7. DESIGN PRINCIPLES

- **Compact over comprehensive.** The State Block carries what's needed to resume, not a full history. Detailed history lives in Full Report output mode.
- **Structured over prose.** Every field is machine-parseable. No narrative sentences in the State Block.
- **Abbreviations are allowed** for attributes to save space, as long as they're consistent and defined in the relevant module.
- **Active Consequences is the most important section** after ratings. This is what prevents the sim from "forgetting" — open threats, promises, conflicts, and deadlines that must carry forward.
- **Last 3 Turns Summary** provides just enough recent context for the LLM to maintain narrative continuity without requiring the full conversation history.
- **Role payloads match turn output.** The data tracked in the role payload is the same data surfaced in the Standard Turn's role add-on sections. State Block and turn output share the same data model.
- **One role at a time.** The State Block never contains more than one role payload simultaneously. Promotion replaces the payload cleanly.

---

*State Block — Complete. Always active. Provides persistence layer for Player Module, Coaching Module, and Interview Module.*
