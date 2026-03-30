# TURN OUTPUT TEMPLATE

> Default runtime output for coaching turns.
> Goal: compact, readable, role-sensitive, under 800 words.
> The turn should feel like football, not a dashboard dump.
> Full state, audit math, and long reports live elsewhere.

---

## OUTPUT RULES

- Hard cap: **800 words maximum** for the default turn.
- Use **only the sections that matter** this turn.
- Do **not** repeat static profile material already known from the Character Profile.
- Do **not** repeat full roster, full staff, full cap table, or full relationship table in the default turn.
- If a section has no meaningful update, omit it.
- Narrative should be direct, specific, and natural. No filler. No "AI recap voice."
- Character effects should appear through **behavior, trust, access, conflict, tone, and opportunity** — not forced instant stat jumps.

---

## ROLE-SENSITIVE RULE

The turn output adapts to the character's current role. Each role has a **base focus** and a **role add-on** section that maps directly to the role payload in the State Block. The data model is shared: what the State Block tracks, the turn surfaces. What the State Block does not track, the turn does not invent.

### If current role is GA / QC
Focus on:
- assignments
- film work
- scout-team execution
- system learning
- trust with supervisor
- whether ideas are invited upward

Do **not** center the turn on scheme control, public media power, or major personnel decisions.

### If current role is Position Coach
Focus on:
- position-room development
- meeting quality
- player trust
- drill/practice effectiveness
- room politics
- input to coordinator, not ownership of the whole team

### If current role is Coordinator
Focus on:
- game plan
- installation
- play-calling / adjustment influence
- staff coordination
- unit performance
- pressure from HC and media

### If current role is Head Coach
Focus on:
- organization direction
- staff management
- ownership / AD / GM pressure
- full-team culture
- game management
- public accountability

---

## CHARACTER EFFECT RULE

Character should show up in ways that fit the role and timing:
- how people respond to you
- what kind of responsibility you get
- which conflicts find you
- which mentors trust you
- what mistakes you make under pressure
- what opportunities open later because of repeated behavior

Character effects do **not** need to be immediate.
They should accumulate and feel earned.

Examples:
- A QC coach with humility and strong teaching instincts gets invited into more film conversations over time.
- A former star player with poor ego control gets frozen out even if his football eye is good.
- A calm coach changes the tone of a room slowly; he does not magically fix chemistry in one turn.

---

## DEFAULT TURN STRUCTURE

The turn uses a **base structure** (always present) plus a **role add-on** (one of four, matching the active State Block role payload). Sections that have no meaningful update are omitted.

### BASE SECTIONS

#### 1. STATE SNAPSHOT
**40-60 words max**
- Date
- Phase
- Role
- Team
- Record or current job-search stage
- Job security/stress only if relevant
- Reporting structure (who the character reports to)

#### 2. SCHEME & CONTROL
**30-50 words max**
Only include if scheme, control level, or delegation changed this turn.
- Current scheme philosophy
- Control level
- Any delegated authority granted or revoked

#### 3. STAFF CHAIN
**30-50 words max**
Only include if staff dynamics shifted.
- Who matters in the chain this turn
- Trust movement with direct supervisor
- Staff friction or alignment

#### 4. THE BUILDING
**80-120 words max**
One tight scene that tells the reader what this turn felt like.
This is the atmosphere section.
Use one concrete observation, one tension point, and one signal of where things are moving.

#### 5. WHAT HAPPENED
**140-180 words max**
The core of the turn.
What actually happened in the character's job this turn:
- film assignment
- interview stage
- meetings
- staff interaction
- practice work
- game outcome if one occurred

If a game happened, do **not** write quarter-by-quarter recap.
Instead cover:
- final result
- one decisive stretch
- one coaching truth about why it went that way

#### 6. FOOTBALL WORK
**100-130 words max**
Only the football substance that mattered this turn:
- install progress
- what the offense/defense/special teams struggled with
- what assignment the character handled
- where they helped
- where they were out of their depth

This is where role matters most.
A QC turn should feel like support work and learning, not command.

#### 7. PEOPLE & POWER
**90-120 words max**
Only the human and political shifts that matter now:
- trust movement with supervisor
- room dynamic
- media note if public-facing
- staff friction
- owner/AD/GM pressure if role justifies it

No big relationship table.
Just what changed and why it matters.

#### 8. WHAT CHANGED
**60-90 words max**
Compact numeric or state summary only.
Use bullets.
Include only real changes such as:
- trust + / -
- stress + / -
- skill development + / -
- job security + / -
- applications advanced / rejected
- playbook familiarity improved

#### 9. NEXT DECISION(S)
**100-140 words max**
Only the decisions that actually matter before the next turn.
Usually:
- 2-3 major choices
- up to 3 secondary actions
- 0-1 gate if a hard yes/no is needed

Each choice should be concrete.
Do not bury the user in five layers of menus.

---

### ROLE ADD-ON BLOCKS

One of these is appended based on Current Role. Each maps directly to its State Block role payload. Include only the fields that changed or matter this turn — not the full payload dump.

#### GA / QC ADD-ON

Include when relevant:
- Supervisor / reporting chain update
- Current assignment status (new, completed, ongoing)
- System familiarity movement (+/- with number)
- Building knowledge movement (+/- with number)
- Staff trust footprint movement (+/- with number)
- Access level changes (invited to new meetings, new film access, practice authority shift)
- Promotion readiness status if close to a threshold

Do not include: roster data, scheme control notes, unit performance stats, media exposure.

#### POSITION COACH ADD-ON

Include when relevant:
- Room snapshot: starters and key rotation players with this month/game's stats
- Developmental player note (one player, one sentence)
- Room health change
- Room trust movement with specific players
- Teaching focus update
- Room priorities shift
- Room politics (coordinator friction, player complaints, positional competition)

Do not include: full team roster, other position groups, play-calling data, organizational pressure.

#### COORDINATOR ADD-ON

Include when relevant:
- Unit performance snapshot (points, yards, efficiency, third down, red zone, turnovers — compact line)
- Key unit player stat lines (2-4 players, one line each)
- Play-calling access status or change
- Adjustment grade if a game occurred
- HC alignment movement (+/-)
- Media exposure level if it shifted
- Call-influence notes if delegation changed

Do not include: other unit's stats, full roster, recruiting, organizational finance.

#### HEAD COACH ADD-ON

Include when relevant:
- Team snapshot (OVR, record, expectation band position, playoff status)
- Coordinator trust and status (one line each, OC/DC/STC)
- Roster snapshot: strongest/weakest unit, key injuries
- Organization pressure: owner/AD/GM patience, booster/media summary
- Full control vs delegated areas if changed
- Recruiting class rank (college) or cap space (NFL) if relevant

---

## OMIT FROM DEFAULT TURN

These belong in `Audit turn`, `Full report`, or `Save` only:
- protocol verification checklist
- full probability math unless audit requested
- full standings table
- full cap table
- full roster grades
- full relationship matrix
- full YAML state block
- full injury report unless directly relevant
- quarter-by-quarter game script
- repeated coach profile / ratings table every turn
- full role payload data dump (only changes belong in the default turn)

---

## GAME WEEK COMPRESSION RULE

If a game occurs, compress it into this format inside Sections 5 and 6:

- **Result:** one line
- **Why it turned:** one short paragraph
- **Adjustment battle:** one sentence
- **Cost:** one sentence (injury, trust hit, fatigue, political fallout)

No full box-score dump in the default turn.
Detailed stats are for `Full report`.

---

## MONTHLY TURN COMPRESSION RULE

For GA / QC / Position Coach roles operating on monthly turns (per Master Engine §5.2):

- Summarize 3–5 meaningful work blocks within the month.
- Aggregate game outcomes (e.g., "Team went 3-1 in October").
- Show stats as month-to-date or season-to-date, not week-by-week.
- Surface only one or two standout weekly incidents in prose.
- The Building section covers the month's tone, not a single week.
- What Happened covers the month's arc, not a single event.
- Do not write with weekly granularity when the clock is monthly.

---

## JOB SEARCH / INTERVIEW RULE

If the Interview Module is active, the turn centers on the interview process.
Default coaching sections still apply, but adapt them:

- State Snapshot = application stage / active jobs
- The Building = travel, interview room, hiring contact vibe
- What Happened = cover letter, phone interview, campus stage, callback, rejection, negotiation
- Football Work = only what was discussed or tested in the interview
- People & Power = who liked you, who hesitated, who now matters
- What Changed = application status / reputation / stress
- Next Decisions = apply / withdraw / answer / negotiate / wait

---

## TONE GUIDE

- Direct
- Specific
- Controlled
- Football-literate
- Human
- No fake drama
- No fake inspiration
- No mechanical recap voice

The turn should read like a sharp football sim update written by someone who understands the building.

---

## MINI FORMAT EXAMPLE (QC LEVEL)

**January 15, 1999 — Offseason / Coaching Carousel**
Stone is 33, unemployed, and chasing entry-level work for the first time in his life. No team yet. Stress is manageable. The Eagles QC job is open.

The week felt smaller than his playing career and heavier than he expected. He is not choosing plays or talking to media. He is trying to get in the room. The important shift came in how he framed that to himself: not "starting at the bottom," but starting at the beginning.

His focus this turn was the Eagles. Reid's profile, staff makeup, and system demands clarified the gap. Stone fits the culture better than the résumé. Teaching helps him. Humility helps him more. The real problem is not football intelligence; it is whether Reid believes a Hall of Fame player can do QC work without turning the room awkward.

Football-wise, the biggest task is obvious now: learn enough WCO language to sound serious without pretending mastery. Stone does not need to sell himself as a future TE coach. He needs to sound like a future good assistant.

People matter more than credentials here. Reid is the ultimate yes, but Dowhower is the practical gatekeeper. Shurmur is the delicate relationship if Stone gets in. Rivera looks like the natural peer ally.

**What changed**
- Eagles moved to top target
- Job-fit confidence: up
- Awareness of WCO gap: up sharply
- Application framing clarified

**QC add-on**
- System Familiarity: 12/100 (WCO base concepts only)
- Building Knowledge: 0/100 (not yet inside)
- Staff Trust Footprint: 0/100 (not yet inside)
- Access: none — external applicant

**Next decisions**
1. Apply to Eagles Offensive QC now or send one fallback application first.
2. In the cover letter, lead with teaching or lead with learning.
3. Decide whether to mention TE expertise directly or save it for later stages.

---

## IMPLEMENTATION NOTE

Use this template for the default runtime turn.
Keep `Audit turn`, `Full report`, and `Save` as separate output modes.
The role add-on block in the turn output must always reflect the same data model as the active role payload in the State Block. If the State Block tracks it, the turn can surface it. If the State Block does not track it, the turn does not invent it.
