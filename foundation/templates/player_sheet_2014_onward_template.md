# [Player Name] — [Season] full player assessment (2014 onward)

This is the form of a full annual assessment, kept in the player's permanent record (`data/people/players/<id>.json`, `runtime/people.py`), not a page. No page shows it whole: every player page follows the [player card template](player_card_template.md) and shows only this assessment's short staff assessment, never its grades.

**Team:**  
**Season:**  
**Record:** The player's permanent record, this assessment's entry  
**Assessment stage:** Opening annual assessment  
**Evaluation policy:** Exactly two full assessments: this opening baseline, maintained with dated updates through the year, and a separate final assessment after season close. Statistics are not part of the assessment; the player page reads them from the closed games after each one.  
**Checkpoint:**  
**Position:**  
**NFL standing:**  
**Player identity:**  
**Previous annual profile:**  

> This is a dated personnel snapshot, not a game-engine rating card. Established
> abilities carry forward from the prior profile unless new causal evidence
> supports a change. A grade summarizes the staff view at this checkpoint; it
> does not directly set play probabilities, potential, or future development.

## How this assessment is maintained

Record the opening assessment once, using the previous final assessment and evidence available when this player joins. Retain that original judgment. Spring, camp, preseason and season reports supply specific coaching findings; add a dated update below when they materially change or qualify the staff view. Do not produce another whole-player assessment at each phase or automatically change a grade after a practice.

### Opening and final modes

Use this same 2014-onward form for both annual assessments. The opening assessment is kept on the player's permanent record: its grades, comparisons and staff read, whose view it is and when, and its dated coaching updates. Keep its initial grades and interpretation intact and append dated coaching updates to that record entry. `career/[year]/Team_Operations/Team/Player_Cards/[player].md` is his built player page, which shows no grade and no update. Write the assessment's short staff assessment on the same record entry: two to four sentences on his demonstrated level and role, his main strengths and his main limitation, drawn only from this assessment and its dated updates, every current figure written as a token the page reads from the closed games (docs/update_workflow.md, "Player, coaching and film records").

Write the separate final assessment only after the completed season and actual player and coach exit reviews, at `career/[year]/Season_Review/Player_Assessments/[player].md`, with its entry on the permanent record and its own short staff assessment on that entry (the page then shows that short). Set **Assessment stage** to `Final annual assessment` and **Checkpoint** to the season-close date. Link the same-year opening assessment and its dated updates beneath the header. Set **Evaluation policy** to `Frozen final assessment; preserve the opening baseline and dated evidence separately.`

In final mode retain every personnel section below: Overall and position traits, vs. Average / vs. Best / vs. Worst, established player state, year-over-year change, play style, strengths, weaknesses and evidence limits. Write the completed-season staff judgment from the actual work; explain meaningful changes from the opening view in the final-only section below. The year-over-year table compares with the previous year's final assessment. The statistics are the player page's, built from the closed games; the assessment cites the figures it relies on rather than copying tables. Link the year's dated updates instead of copying them into another running journal. Do not use the 2013-only position-baseline template for a 2014-onward final assessment.

A departure closes the player's Jacksonville work at its actual date. Retain that evidence and any actual exit review; do not invent the rest of his season or create a third full assessment.

## Player grades

| Category | Grade | NFL standing |
| --- | ---: | --- |
| Overall | — /10 | Unassessed |
| Athleticism | — /10 | Unassessed |
| Speed | — /10 | Unassessed |
| Strength / Power | — /10 | Unassessed |
| Agility / Change of direction | — /10 | Unassessed |
| Technique | — /10 | Unassessed |
| Football IQ | — /10 | Unassessed |
| [Position-specific trait] | — /10 | Unassessed |
| [Position-specific trait] | — /10 | Unassessed |
| [Position-specific trait] | — /10 | Unassessed |

### Grade meaning

Use the number as a human-facing NFL personnel summary at this exact checkpoint.
At the user's explicit request, give exact theoretical staff judgments for
thin-evidence traits. Identify that basis and preserve evidence limits
separately; do not hedge the number or invent measurements and statistics.
Replace blank template grade rows when completing the final player evaluation.
It may use half-points. Grade the current player, not his draft status, contract,
future career or theoretical potential. An overall grade is a synthesis, not an
average of the rows and not an engine input.

| Grade | Personnel meaning |
| ---: | --- |
| 10 | Best-in-league / historically exceptional current level |
| 9 | Elite current NFL level |
| 8 | High-end starter / top tier at the position |
| 7 | Solid NFL starter |
| 6 | Viable starter or strong role player |
| 5 | NFL-average rostered level |
| 4 | Backup level |
| 3 | Fringe roster level |
| 2 | Below normal NFL roster standard |
| 1 | Not currently at NFL roster standard |

**NFL standing** stays a plain-language field such as Top 5, Top 10, high-end
starter, starter, rotational/role player, backup, fringe roster, or unassessed.
It is not mechanically derived from the overall grade.

## League comparison

| Trait | vs. Average | vs. Best | vs. Worst |
| --- | --- | --- | --- |
| Speed | Unassessed | Unassessed | Unassessed |
| Size / Length | Unassessed | Unassessed | Unassessed |
| Strength | Unassessed | Unassessed | Unassessed |
| Explosiveness | Unassessed | Unassessed | Unassessed |
| [Position-specific trait] | Unassessed | Unassessed | Unassessed |
| [Position-specific trait] | Unassessed | Unassessed | Unassessed |

## Established player state

Record the abilities already demonstrated by this player. These are inherited
state. Do not make him prove the same arm, speed, catch radius, strength,
movement skill, technique or processing ability from zero every January.

- 

## Year-over-year change

| Area | Prior profile | Current checkpoint | Change | Evidence / football reason |
| --- | --- | --- | --- | --- |
| Established identity |  |  |  |  |
| Physical |  |  |  |  |
| Technical |  |  |  |  |
| Processing / Football IQ |  |  |  |  |
| Consistency |  |  |  |  |
| Role / system access |  |  |  |  |

A bad outcome may expose access, decision-making or consistency without erasing
the underlying tool. Example: a quarterback can retain the arm to make a tight
window throw while being late to identify the window.

## What makes him [NFL standing]

- 
- 
- 

## Historical comparison

**Level historically:**  
**Closest player comparison:**  
**What is similar:**  
**What is different:**  

Use only information permitted at the checkpoint. Do not import a later real
career as an answer key.

## Play style

## Best traits

- 
- 

## Main weaknesses

- 

## Evidence and uncertainty

- **Primary evidence:**  
- **What is established:**  
- **What remains uncertain:**  
- **What would change the assessment:**  

**One-line description:**  
[Simple sentence describing what kind of player he is at this checkpoint.]


The statistics an assessment draws on are on the player page, not in the
assessment. The page builds them from the closed games: regular season and
playoffs apart, every row led by Season, Team, Age and #, previous seasons
kept, a partial season labelled like 2014 (through Week 5), "No regular-season
games on record." or "No playoff games on record." when there are none, and N/A
where the records do not hold a field (zero is a recorded count, never a
substitute). No unplayed season gets a row, and no real-world statistic is
ever inserted.

Position columns an assessment may cite:

- QB: G, GS when recorded, CMP, ATT, CMP%, PASS YDS, Y/A, PASS TD, INT,
  Passer rating (never QBR), SCK, SCK YDS, RUSH ATT, RUSH YDS, RUSH TD, FUM, LOST.
- RB/FB: G, GS when recorded, CAR, RUSH YDS, Y/C, RUSH TD, RUSH LNG,
  TGT, REC, REC YDS, Y/R, REC TD, REC LNG, FUM, LOST.
- WR/TE: G, GS when recorded, TGT, REC, CATCH%, REC YDS, Y/R, REC TD,
  REC LNG, RUSH ATT, RUSH YDS, RUSH TD, FUM, LOST.
- OT/G/C: G, GS and offensive snaps when recorded, SCK ALLOWED only when
  individually attributable, penalties and penalty yards when recorded.
- DE/DT/LB: G, GS and defensive snaps when recorded, TOT, SOLO, AST, TFL,
  SCK, PRESS when recorded, QB HITS when recorded, PD, INT, INT YDS, FF, FR.
- CB/S/DB: G, GS and defensive snaps when recorded, TOT, SOLO, AST, TFL,
  PD, INT, INT YDS, SCK, PRESS when recorded, FF, FR.
- K: G, FGM, FGA, FG%, LONG, attempts/makes by distance band, XPM, XPA,
  PTS; kickoffs, touchbacks and kickoff yards when recorded.
- P: G, PUNTS, GROSS YDS, GROSS AVG, LONG, NET YDS/AVG when recorded,
  IN20, TB, returns and return yards allowed when recorded, blocks.
- LS: G, long snaps and field-goal/try/punt snap splits when recorded,
  attributed bad snaps when recorded, tackles and penalties when recorded.
- Add separate KR/PR and coverage-unit columns for any position when relevant
  and recorded; do not infer a return role from random historical attribution.

The comparison headings remain vs. Average / vs. Best / vs. Worst.
Best and worst still mean trait-specific, opportunity-qualified references in
the checkpoint's NFL season, not one universal best or a one-snap worst player.
Current grades require current recorded evidence. Reuse the prior established
player, including the completed 2013 baseline, without manufacturing change.
Create the opening assessment on his record when the player joins the controlled roster. Keep dated coaching updates on that record entry and write the separate final assessment only after season close.

## Change from the opening assessment

[Final mode only. Compare the opening view with the completed season: what the player could do reliably, what changed in his technique or decisions, how he fit the jobs actually assigned, and what remained untested. Explain any revised grade with dated football evidence and contrary observations. Include actual player and coach exit-review findings without inventing their statements. Link the preserved opening assessment and relevant reports. Omit this section from the opening assessment.]

## Dated coaching updates

### [Actual date] | [Work that changed or qualified the view]

[State the job, what the linked phase/game record demonstrated, the staff's interpretation and the next useful check. Preserve contrary evidence and the limits of the opportunity. A new role is recorded only when actually decided. This is an update to the opening assessment, not a fresh overall assessment or another grade table. Opening mode only; omit until there is a material update. In final mode link these notes from the opening assessment rather than duplicate them.]
