# FOOTBALL CAREER SIM — STATE BLOCK

> The compact persistence layer for session continuity. This is what gets exported on `"Save"` and pasted to resume. Always active regardless of module.

---

## 1. PURPOSE

The State Block is the **single source of truth**. Every turn, the engine writes changes here. Every turn, the engine reads from here. If the State Block says it, it's true. If it doesn't, it didn't happen.

**Rules:**
- Narrative cannot contradict the State Block.
- State Block updates happen at Step 7 of turn processing (Master Engine §5.2), after all mechanics resolve.
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

```
=== FOOTBALL CAREER SIM — SAVE STATE ===
MODE: COACHING
TAPE: [MODE A (position X/Y) | MODE B (engine-generated)]

--- IDENTITY ---
Name: [Name] | Age: [X]
Current Role: [GA/Position Coach/Coordinator/HC]
Position Detail: [e.g., QB Coach, Offensive Coordinator, Head Coach]
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

--- STAFF ---
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Role]: [Name] — Skills: [Key attributes] | Trust: [X]/100 | Status: [1-line]
[Additional staff as needed]

--- ROSTER SNAPSHOT ---
Team OVR: [X] | Starters Avg: [X] | Depth Avg: [X]
Key Players: [Name] [POS] [OVR] [Status] | [Name] [POS] [OVR] [Status] | [Name] [POS] [OVR] [Status]
Injuries: [Name] [POS] ([X weeks remaining]) | [None]
Recruiting Class Rank: #[X] (College only)

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

=== END SAVE STATE ===
```

---

## 4. VALIDATION ON LOAD

When a State Block is pasted to resume:

```
1. Check MODE → Load appropriate modules (Player or Coaching + Interview if active)
2. Validate all attributes against current caps
3. Verify timeline consistency (date vs turn count vs phase)
4. Confirm active consequences are parseable
5. Check for missing required fields → prompt user to fill gaps
6. Load tape mode and position if Mode A
7. Resume from next turn
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

## 6. DESIGN PRINCIPLES

- **Compact over comprehensive.** The State Block carries what's needed to resume, not a full history. Detailed history lives in Full Report output mode.
- **Structured over prose.** Every field is machine-parseable. No narrative sentences in the State Block.
- **Abbreviations are allowed** for attributes to save space, as long as they're consistent and defined in the relevant module.
- **Active Consequences is the most important section** after ratings. This is what prevents the sim from "forgetting" — open threats, promises, conflicts, and deadlines that must carry forward.
- **Last 3 Turns Summary** provides just enough recent context for the LLM to maintain narrative continuity without requiring the full conversation history.

---

*State Block — Complete. Always active. Provides persistence layer for Player Module, Coaching Module, and Interview Module.*
