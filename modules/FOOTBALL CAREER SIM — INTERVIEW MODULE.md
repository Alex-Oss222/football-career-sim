# FOOTBALL CAREER SIM — INTERVIEW MODULE

> Loaded only during active job searches. Defers to Master Engine for realism and randomness. Defers to Coaching Module for attribute definitions, career ladder, and salary ranges.

---

## 1. JOB MARKET

### 1.1 Viewing Positions
Command: `"Search coaching jobs"`

The engine displays all open positions, not just qualified ones:
```
For each listing:
- Position title, school/team, level
- Salary range
- Minimum skill requirements
- Your current skills vs requirements (gap analysis)
- Estimated application success probability
- Competition level (approximate number of applicants)
- Program context (rebuilding, contender, scandal recovery, following legend, etc.)
```

### 1.2 Application Limits
- Up to 5 active applications per cycle
- Applying to reach positions (skills below minimums) is allowed but costs one of your 5 slots
- You can withdraw from any application at any time

### 1.3 Job Generation
Open positions are generated based on:
- Current season's firings and retirements across all levels
- Coaching carousel timing (November–February peak, spring secondary wave)
- Random vacancies (scandal, health, poaching by other programs)
- Positions scale to the coaching world's realistic churn rate

---

## 2. APPLICATION STAGE (Turns 1–2)

### 2.1 Application Package
```
Application Score =
  (Resume Strength × 0.25) +
  (Skill Match × 0.35) +
  (Cover Letter Quality × 0.20) +
  (References × 0.20)

Resume Strength: Career wins, player development record, previous titles, legacy points
Skill Match: Your relevant attributes vs position requirements
References: Based on relationships with former superiors (trust > 70 = strong reference)
```

### 2.2 Cover Letter (User Written)
The engine prompts:
> *"Write your cover letter for [Position] at [School/Team]. Explain why you're the right fit."*

**The user must type an actual response. Minimum 100 words.**

```
Cover Letter Scoring (LLM-evaluated, 1–10):

10: Exceptional — Perfectly tailored, compelling, memorable
8–9: Excellent — Strong case, specific to this program
6–7: Good — Solid reasoning, some generic elements
4–5: Average — Could be sent to any school
2–3: Poor — Vague, unfocused, red flags
1: Disqualifying — Wrong tone, wrong program, major errors
```

### 2.3 Screening Result
```
Application Score > 70:  Phone interview scheduled
Application Score 50–70: Waitlisted (called if others decline)
Application Score < 50:  Rejection email
```

---

## 3. PHONE INTERVIEW (Turns 3–4)

### 3.1 Format
3 questions. User must type actual written answers. Each scored 1–10 by the LLM.

### 3.2 Question Categories

**Question 1 — Philosophy:**
The engine selects a philosophy question appropriate to the position level and program context.

Examples:
- GA: *"What does being a graduate assistant mean to you, and how would you handle the workload?"*
- Position Coach: *"How do you develop players at [position]? Walk us through your approach."*
- Coordinator: *"Describe your scheme philosophy and how you'd install it here."*
- HC: *"What is your vision for this program in 3 years?"*

**Minimum 75 words.** Scored on: alignment with program, specificity, realism for experience level.

**Question 2 — Experience/Skills:**
Tailored to the specific role and the program's current needs.

Examples:
- *"How do you handle the grunt work and long hours?"* (GA)
- *"Walk us through your scheme installation process."* (Coordinator)
- *"How would you build a recruiting pipeline in this region?"* (HC)
- *"Our offensive line allowed 40 sacks last year. What's your plan?"* (OL Coach)

**Minimum 75 words.** Scored on: specific examples, practical knowledge, credibility relative to your actual skill levels.

**Question 3 — Situational:**
A scenario drawn from the program's real circumstances.

Examples:
- *"Our star player just got arrested. Walk us through the next 48 hours."*
- *"We're losing recruits to NIL deals at bigger schools. Your approach?"*
- *"The boosters want the defensive coordinator fired. You disagree. What do you do?"*
- *"Your predecessor went 2-10. The fanbase is furious. First team meeting — what do you say?"*

**Minimum 75 words.** Scored on: judgment, complexity awareness, practical resolution, political awareness.

### 3.3 Phone Interview Scoring
```
Total = (Q1 + Q2 + Q3) + (Your Communication-equivalent Skills × 0.5)

35+:   Advance to campus interview
28–34: Second phone interview required (1 additional turn)
<28:   Eliminated
```

---

## 4. CAMPUS / IN-PERSON INTERVIEW (Turns 5–6)

### 4.1 Multi-Stage Interview Day
5 stages. User writes responses for each.

**Stage 1 — AD / Owner Meeting:**
> *"What's your vision for this position over the next 3 years?"*

Minimum 100 words. Scored on: leadership, vision, realistic ambition.

**Stage 2 — Current Staff Meeting** (Coordinator/HC only):
> *"How would you evaluate and potentially reshape this staff?"*

Minimum 100 words. Scored on: diplomacy, evaluation skills, management approach.

**Stage 3 — Player/Captain Meeting:**
> Players ask: *"Are you going to come in here and change everything?"*

Minimum 75 words. Scored on: connecting with players, building trust, managing expectations.

**Stage 4 — Tactical Presentation:**
Prompt scales to position:
- GA: *"How would you scout our next opponent?"*
- Position Coach: *"Design a practice plan for your position group."*
- Coordinator: *"Present your base offensive/defensive package."*
- HC: *"Present your 100-day plan."*

Minimum 150 words. Scored on: tactical knowledge, organization, innovation/tradition balance.

**Stage 5 — Final Panel (3 Rapid-Fire):**
```
Q1: "Why should we hire you over the other finalists?"  (Min 50 words)
Q2: "What's your biggest weakness as a coach?"           (Min 50 words)
Q3: "Any questions for us?"                              (Min 25 words)
```

### 4.2 Campus Interview Scoring
```
Total = Sum of all stage scores + (Relevant Skills Average × 0.5)

60+:   Finalist
50–59: Strong candidate, pending references
40–49: Backup option only
<40:   Eliminated
```

---

## 5. FINAL ROUND (Turns 7–8)

### 5.1 Competition
The engine generates 2–3 other finalists with scores ±10 of yours. Each has distinct strengths and weaknesses. You can be outscored but still hired if you're the better fit.

### 5.2 Reference Checks
```
Former coaches/colleagues with relationship > 70:  +5 per reference (max 3)
Former coaches/colleagues with relationship < 50:  −5 per reference
No references available: −10
```

### 5.3 Final Statement
The engine prompts:
> *"We're deciding between you and [finalist description]. Make your closing argument."*

**Minimum 100 words.** This statement can swing the decision ±15 points.

### 5.4 Decision
```
Your Total = Interview Scores + References + Fit Bonus + Final Statement
vs
Best Other Candidate Total

Win: Proceed to negotiation
Lose: Rejection (feedback available if relationship with hiring contact > 50)
```

---

## 6. SALARY NEGOTIATION (If Offered)

### 6.1 Initial Offer
```
Offer = Market Rate × (0.7 to 1.0 based on demand for you)
```

### 6.2 Negotiation Rounds (Up to 3)
Each round, the user states what they want and why (written response).

```
Negotiation Success = Contract Negotiation Skill + Argument Quality (LLM-scored 1–10)

90+: Offer increases 20%
75–89: Increases 10%
60–74: Increases 5%
45–59: No change — take it or leave it
<45:  Offer reduced or pulled
```

### 6.3 Negotiable Terms
- Base salary
- Contract length
- Buyout clause
- Assistant coach salary pool (HC)
- Performance bonuses
- Moving expenses
- Facilities commitments (HC)

---

## 7. INTERVIEW FAILURE

### 7.1 Feedback
```
Relationship with hiring contact > 70: Honest, specific feedback
Relationship 50–70: Generic feedback
Relationship < 50: No feedback, just rejection
```

### 7.2 Consequences
```
Failed at same school: −10 to future applications there (2-year duration)
Scored < 30 (spectacularly bad): Word spreads, −5 to ALL applications for 1 year
Scored 50+ (impressed but lost): +5 to future applications at similar level
```

### 7.3 Learning
- Each failed interview: +0.5 to relevant communication/interview skills
- Specific weaknesses identified for targeted development

---

## 8. ANSWER SCORING RUBRIC

All user-written answers are scored by the LLM using this rubric:

```
10 — EXCEPTIONAL:
  Directly addresses the question with deep understanding.
  Specific, detailed examples. Perfect fit. Memorable.

8–9 — EXCELLENT:
  Strong response. Good knowledge. Relevant examples. Would impress.

6–7 — GOOD:
  Adequate. Some good points. Generally relevant. Few red flags.

4–5 — AVERAGE:
  Generic. Misses key points. Vague examples. Borderline.

2–3 — POOR:
  Weak understanding. Off-topic. Concerning red flags.

1 — DISQUALIFYING:
  Completely wrong approach. Major red flags. Ends candidacy.
```

**Scoring integrity rules:**
- The LLM scores based on content quality relative to the position level. A GA answer is judged by GA standards; an HC answer by HC standards.
- High coaching attributes make it easier to sound credible, but a well-written answer from a low-skill coach still scores on its own merits.
- A poorly written answer from a high-skill coach still scores poorly. Your attributes open the door; your words close the deal.

---

## 9. SPECIAL SITUATIONS

### 9.1 Emergency Hires
```
Random event (1–5% per turn):
  Mid-season firing or scandal creates emergency vacancy.
  Abbreviated process: skip to phone interview, decision in 2 turns.
  Lower requirements but also desperation — may be a bad job.
```

### 9.2 Unsolicited Recruitment
```
Random event (1–3% per turn):
  Someone recommends you for a position you didn't apply for.
  Skip to phone interview. Usually a better position than expected.
```

### 9.3 Dream Job Opens
```
Random event (1–2% per turn):
  A position above your current qualification opens.
  Can attempt anyway. High risk, high reward.
  Must score 20% higher than normal threshold to compensate for skill gap.
```

### 9.4 Internal Promotion
```
If already on staff when a position opens above you:
  +20 to all interview scores (known quantity)
  Skip phone interview
  But must score 10% better than external candidates (higher expectations)
```

---

## 10. TIMELINE INTEGRATION

### 10.1 Time Bubble Rule
**The interview process runs in a silo.** Interview turns advance mechanically (stage by stage) but **the in-game calendar does not advance** during the interview process. The coaching world, season, games, recruiting — all freeze while interviews play out.

**Time resumes only when the coach is hired** (or all applications are exhausted/withdrawn). At that point the calendar picks up exactly where it paused and normal turns continue at the new position.

This prevents the interview process from consuming weeks of in-game season time and avoids the impossible situation of coaching your current team while simultaneously being on campus at three other schools.

### 10.2 Interview Stage Progression
```
Stage 1:  Search and apply (cover letters, submissions)
Stage 2:  Phone interviews (callbacks, screens, results)
Stage 3:  Campus visits (multi-stage interviews, presentations)
Stage 4:  Final round (references, last interviews, negotiations)
Stage 5:  Decision and transition (accept/decline, begin new role)
```

Each stage = 1 interview turn. Multiple applications can be at different stages simultaneously. Withdrawing from one frees bandwidth for another.

### 10.3 Re-Entry to Normal Time
When hired:
- Calendar resumes from the exact date it paused
- New role, team, and context are loaded
- First normal turn reflects the transition (introductions, facility access, initial impressions)
- Stress from the interview process carries over into the new role

---

## 11. COMMANDS (INTERVIEW-SPECIFIC)

```
"Search coaching jobs"       — View all open positions with requirements
"Apply for [job]"            — Begin application (must write cover letter)
"Submit answer"              — Provide written response to interview question
"Check application status"   — See where each application stands
"Withdraw from [job]"        — Drop an application to free a slot
"Interview feedback"         — Request feedback from failed interview (if available)
"Compare offers"             — Side-by-side comparison of active offers
"Accept [offer]"             — Accept a position
"Decline [offer]"            — Decline and continue searching
"Negotiate [offer]"          — Enter salary negotiation
```

---

*Interview Module — Complete. Loads only during active job searches. Defers to Coaching Module for attributes and career ladder. Defers to Master Engine for realism and randomness.*
