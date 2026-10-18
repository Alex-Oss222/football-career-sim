# Role: Coordinator

**Document status:** Durable description of an offensive, defensive or special-teams coordinator's job in the career layer
**Adopted:** October 18, 2026, from the user's design of the career layer of the same date; no simulation clock advance.
**Desk:** No desk is built for this role yet. `python scripts/render_career_views.py` reports a coordinator appointment as a desk that is defined but not built.

This file describes the job, not an appointment, and each actual employment agreement adjusts it. A coordinator appointment records the six fields the [head coach file](head_coach.md#2-the-six-fields) lists in the same places in the [current job record](../../state/current_job.json), filled from that job's own agreement. When the run stops is set by the [decision rules](../decision_rules.md) and the [decision classes](../../docs/career_layer.md#3-decision-classes); this file restates neither.

## 1. What he works with

The workspace expands from one room to the whole unit:

- every position group's personnel, readiness and development reports;
- unit installation, shared assignments and communication;
- opponent study, self-scout, situational performance and available counters;
- package composition, replacement options and the consequences of injuries;
- position-coach responsibilities and disagreements;
- his head coach's priorities, constraints and assessment of his work;
- personnel recommendations and the resources the front office says are available;
- an explicit record of whether he calls plays.

He receives the other units' information that matters to complementary football, but their weekly calls do not become his decisions. Ordinary team information stays available; another club's confidential information never does ([decision rules](../decision_rules.md#5-access), section 5).

## 2. Calling

Whether he calls his unit is a fact of the appointment, recorded in the job record's `delegation.play_calling`, and never implied by the title: a coordinator may organize the unit without calling plays. A non-calling coordinator receives no call menu that implies control; defensive calls change no result in the current game model. The defensive call sheet is recorded beside the game and never enters the outcome, so a desk that credited a chosen coverage for a stop would overstate what happened. A non-calling coordinator still has a substantial coordination job.

## 3. Where it stops

- Adopting the unit plan.
- A material change to scheme or deployment.
- A replacement choice reserved to him.
- An important recommendation to the head coach.
- A disagreement about his authority.
- His own career decisions.

## 4. What runs automatically

The position coaches' ordinary teaching, preparation within his plan, the other units, and the decisions the head coach or the general manager retains.

## 5. Through the year

These are review opportunities, not stops merely because a date arrived; each stops the run only under the decision rules.

| Stage | His meaningful choices |
|---|---|
| Job confirmation and onboarding | Clarify scheme and calling authority; set unit priorities |
| Early offseason | Unit changes and staffing and personnel recommendations |
| Free agency and draft preparation | Unit needs, fit and priorities |
| Spring program | Unit installation and coordination |
| Camp and preseason | Packages, unit readiness and recommendations |
| Regular season | Weekly unit plan and material adjustments |
| Bye or significant midseason review | Revise unit operation |
| Postseason, if reached | The same job, with greater stakes |
| After the team's final game | Unit and staff review; his own employment response |
| Next-year opening | New unit plan |

## 6. Authority

He recommends acquisitions for his unit; the general manager decides them. He coordinates his position coaches; the head coach retains the authority the appointment gives him. The appointment's authority rows say which of these it grants.

## 7. Evaluation

Evidence that could support a bigger opportunity for a coordinator: building a coherent unit; supervising position coaches; adapting to personnel; managing installation; making adjustments; producing results with an identifiable personal contribution. At year end the evaluation separates his unit's contribution from the head coach's overall team result. A successful year can improve his candidacy without guaranteeing a head-coaching job, and the annual review awards nothing automatically. The 2014 hiring and permission rules for a coordinator's next move are in the [hiring rules](../../library/2014_coaching_hiring_and_anti_tampering_rules.md#1-who-may-be-asked-and-with-whose-permission).

## 8. Desk sections

Unit (Defense for a defensive coordinator), Staff, Installation, Opponent, Personnel recommendations and Career (`ROLE_SECTIONS` in `runtime/current_job.py`). No desk is built for this role yet.
