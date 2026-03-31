# PLAY CALL VISIBILITY RULES

This document controls WHEN play calls appear in the narrative and HOW detailed they should be.

The goal:
- show meaningful coaching decisions
- avoid play-by-play spam
- maintain realism and readability
- keep focus on leverage moments, not every snap

---

## CORE RULE

```text
Not every play should be shown.
Only meaningful plays should be visible.
````

The simulation should compress routine football and expand important decisions.

---

## VISIBILITY TIERS

### TIER 1 — FULL VISIBILITY (SHOW PLAY CALL)

Use detailed play-call narration when:

* 3rd down (all distances)
* 4th down decisions
* red zone plays (inside +20)
* goal line / short yardage
* two-minute offense / defense
* four-minute offense
* end-of-half / end-of-game sequences
* explosive plays (20+ yards)
* turnovers or turnover-risk plays
* critical momentum swings
* major adjustments after repeated failure
* first scripted plays (opening drive)
* when the user has play-calling authority (OC/HC)

### Output style:

* personnel
* concept family
* intent (why)
* execution result

---

### TIER 2 — PARTIAL VISIBILITY (LIMITED DETAIL)

Use when:

* early downs (1st / 2nd) in normal field position
* midfield drives without leverage
* standard rhythm drives
* balanced sequences without stress

### Output style:

* mention play type, not full breakdown

Example:

* "They stay in 11 personnel and lean on quick game to stay on schedule."
* "Stone keeps the run game involved, trying to stay ahead of the chains."

---

### TIER 3 — COMPRESSED (DO NOT SHOW CALL)

Use when:

* routine early-down trades
* no meaningful change in game state
* repeated similar calls
* clock-management sequences without tension
* drives that stall without key decisions

### Output style:

* summarize the sequence

Example:

* "They move the ball in short increments but stall near midfield."
* "The drive never finds rhythm and ends with a punt."

---

## PLAY CALL DETAIL RULES

### When showing a play call, include:

* personnel grouping (only if relevant)
* concept family (not full playbook code)
* situational reason (why it was called)

### Do NOT include:

* full playbook naming strings
* internal file references
* excessive route detail unless it matters

---

## REPETITION CONTROL

Never:

* show the same concept family repeatedly without explanation
* restate identical reasoning across multiple plays
* narrate "quick game" five times in a row without variation

If a concept repeats:

* explain the adjustment or reason
* or compress it

---

## SEQUENCE RULE

Football is played in sequences, not isolated plays.

When showing plays:

* connect them logically
* show cause → effect

Example:

Bad:

* "They run the ball."
* "They pass the ball."
* "They convert."

Good:

* "After establishing the run, Stone comes back with play-action, trying to hit behind the linebackers. This time the defense stays disciplined and the window closes."

---

## COACH VISIBILITY RULE

### If Stone is QC:

* DO NOT show him calling plays
* Only show observation, not control

### If Stone is Position Coach:

* DO NOT show primary play calls
* May reference how his room performs

### If Stone is Coordinator:

* Show offensive/defensive calls for his side only
* Limit to meaningful situations

### If Stone is Head Coach:

Two modes:

1. Delegated play-calling → show calls sparingly
2. Direct play-calling → show more detail

Still follow visibility tiers.

---

## DRIVE STRUCTURE RULE

Each drive should contain:

* 1–3 detailed plays (max)
* 1–2 partial references
* rest compressed

Never:

* show every snap in a drive

---

## EXPLOSIVE PLAY RULE

Always show:

* how it was set up (if relevant)
* what concept was used
* what broke down or worked

---

## FAILURE VISIBILITY RULE

When something fails:

* show why (execution, call mismatch, defense)
* do NOT default to blaming coaching

---

## SUCCESS VISIBILITY RULE

When something succeeds:

* do NOT over-credit the coach
* include player execution
* include defensive context

---

## ANTI-MADDEN RULE

This is NOT:

* a video game log
* a broadcast script
* a play-by-play feed

This IS:

* a coaching simulation

---

## FINAL CHECK

Before output:

Ask:

1. Did I show only meaningful plays?
2. Did I avoid repetition?
3. Did I explain why key calls happened?
4. Did I keep it readable?
5. Did I respect role authority?

If not → fix before output.
