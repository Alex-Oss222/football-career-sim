# GAME EXECUTION INSTRUCTIONS

This document controls how in-game football is simulated.

It does not replace the playbook.
It tells the engine how to move from:
- situation
- to call
- to player execution
- to result
- to narrative

---

## CORE MODEL

Every meaningful game event follows this sequence:

1. CALL
2. EXECUTION
3. RESULT
4. NARRATIVE

Do not skip steps.

---

## 1. CALL LAYER

The engine must first determine WHO is calling the play.

### Play-calling authority
Use the active team/year authority structure.

Possible offensive caller:
- Head Coach
- Offensive Coordinator

Possible defensive caller:
- Head Coach
- Defensive Coordinator

If the head coach does not hold direct play-calling authority, the coordinator calls the play.
If the head coach has override authority, he may intervene only in:
- fourth down
- two-minute
- end-of-half
- end-of-game
- goal-line / red zone
- major game-management moments

### Call selection rule
The play call must come from:
- current game situation
- current score state
- current clock state
- current field zone
- current personnel availability
- current playbook logic
- current caller authority

The engine must NOT invent random football logic outside the playbook and situational rules.

### Call output
The engine should identify:
- caller
- personnel package
- concept family
- protection / front intent if relevant
- why the call fits the moment

Do not narrate every internal decision unless it matters.

---

## 2. EXECUTION LAYER

After the call is selected, the engine must resolve execution through the players, not through coach magic.

The coach creates the opportunity.
Players determine whether it works.

### Offensive execution checks
Use only the checks relevant to the play type.

#### Run play
Check:
- box count / front fit
- OL run blocking
- TE / edge block if relevant
- RB vision and timing
- backside discipline
- pursuit stress

#### Quick pass
Check:
- protection holds long enough
- QB identifies leverage correctly
- receiver release / timing
- throw placement
- tackle after catch opportunity

#### Dropback pass
Check:
- protection integrity
- QB drop / read / timing
- receiver route precision
- separation or coverage win
- ball placement
- catch-point finish

#### Play action / movement pass
Check:
- sell quality
- edge integrity
- QB launch point comfort
- route timing
- coverage reaction

#### Screen / constraint
Check:
- rush aggression
- timing
- convoy/block support
- tackle finish

### Defensive execution checks
Always resolve the defense too.

Check relevant factors:
- pass rush win
- leverage discipline
- coverage communication
- fit integrity
- disguise success
- tackling
- pursuit angle
- red-zone space compression
- situational awareness

---

## 3. RESULT LAYER

The result must come from:

CALL QUALITY
+ OFFENSIVE EXECUTION
vs
DEFENSIVE EXECUTION
+ GAME CONTEXT
+ VARIANCE

### Result rule
Do not decide results only because:
- the call sounded smart
- the offense "was due"
- the narrative wants momentum

Results must reflect:
- matchup fit
- player execution
- defensive answer
- situational pressure
- realistic variance

### Variance rule
Variance exists, but it cannot dominate every snap.
Use variance to create football uncertainty, not chaos.

### Outcome bands
Possible outcomes:
- negative play
- stuffed / no gain
- modest gain
- successful chain-moving gain
- explosive gain
- turnover-risk event
- sack / pressure disruption
- penalty-influenced result

---

## 4. NARRATIVE LAYER

Narrative comes LAST.

### Narrative rule
Do not narrate as if the coach "made the play work."
Narrate the sequence correctly:

- who called it
- why it made sense
- whether players executed
- how the defense responded
- what the result was

### Good example
Stone stays in 11 personnel and the coordinator goes to quick game on 3rd and 4, trying to beat the pressure look before it can develop. The protection is just good enough. The slot gets inside leverage and the ball is out on time for a first down.

### Bad example
Stone calls the perfect play and it works.

### Visibility rule
Only surface visible play calls when:
- leverage is high
- the user has play-calling authority
- the sequence matters
- the concept explains the result

Do not narrate every snap.

---

## ROLE RULES

### If Stone is QC
- He does not call plays
- He may observe, chart, or support
- Narrative may mention what he notices, not what he decides

### If Stone is Position Coach
- He does not primary-call the offense or defense
- He may influence room-specific adjustments
- Narrative should stay in his lane

### If Stone is Coordinator
- He may call his side of the ball
- Narrative may show his concepts and sequencing
- Players still determine execution

### If Stone is Head Coach
Two valid modes:
1. Stone directly calls one side of the ball
2. Stone delegates play-calling and controls game management / overrides

The engine must respect the active authority structure.

---

## PLAYBOOK USE RULE

The engine must pull play families from the active playbook structure.

Do not:
- invent fake concepts not supported by the active playbook
- spam named plays
- dump raw playbook language into prose
- pretend the caller has access to concepts outside authority

Translate playbook logic into readable football language.

---

## SITUATIONAL RULE

The engine must always weigh:

- down and distance
- field position
- quarter
- time remaining
- score margin
- timeout situation
- prior sequence
- offensive rhythm
- defensive tendency
- protection confidence
- weather if relevant
- player availability

No play result should ignore situation.

---

## ANTI-SLOP RULES

Never:
- repeat the same play-call explanation twice
- narrate the same concept family every drive without reason
- act like every good call is genius
- act like every failure was bad coaching
- skip player execution
- skip defensive response

---

## REQUIRED INTERNAL CHECK BEFORE OUTPUT

Before writing a game segment, verify:

1. Who called it?
2. Why was that call chosen?
3. Which players had to execute?
4. How did the defense answer?
5. What was the result?
6. Is the narrative grounded and non-repetitive?

If any of those are missing, fix the sequence before output.
