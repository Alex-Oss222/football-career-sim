# Role: Position Coach

**Document status:** Durable description of a position coach's job in the career layer
**Adopted:** October 18, 2026, from the user's design of the career layer of the same date; no simulation clock advance.
**Desk:** No desk is built for this role yet. `python scripts/render_career_views.py` reports a position-coach or assistant appointment as a desk that is defined but not built.

This file describes the job, not an appointment, and each actual employment agreement adjusts it. An assistant's appointment uses this role. It records the six fields the [head coach file](head_coach.md#2-the-six-fields) lists in the same places in the [current job record](../../state/current_job.json), filled from that job's own agreement. When the run stops is set by the [decision rules](../decision_rules.md) and the [decision classes](../../docs/career_layer.md#3-decision-classes); this file restates neither.

## 1. What he works with

The main workspace is his room and its contribution to the unit:

- **Players:** opening assessments, current assignments, practice participation restrictions, game usage, development history and relevant contract status.
- **Teaching:** what has been installed, what each player has demonstrated, recurring mistakes, corrections, retests and undelivered feedback.
- **Competition:** actual contested jobs, rep opportunities, his recommendation, the coordinator's assessment and the head coach's eventual decision.
- **Weekly work:** the opponent tendencies that affect his room, its blocking, coverage or protection responsibilities, and adjustments requested by the coordinator.
- **Personnel input:** prospects and free agents assigned for evaluation, scheme requirements and the reasoning behind his recommendations.
- **His career:** his contract, supervisor feedback, added responsibilities, interview requests and permission status.

Being a position coach does not make the rest of the roster invisible: ordinary team information stays available ([decision rules](../decision_rules.md#5-access), section 5). He takes part in personnel evaluation without choosing the draft pick.

## 2. Where it stops

- A consequential teaching or usage choice within his authority.
- An unresolved competition recommendation.
- A disagreement requiring his response.
- A new responsibility.
- His own employment decision.

## 3. What runs automatically

Ordinary meetings, drills, film preparation, the implementation of his approved teaching plan, the other rooms, the coordinator's calls and the head coach's team management.

## 4. Through the year

These are review opportunities, not stops merely because a date arrived; each stops the run only under the decision rules.

| Stage | His meaningful choices |
|---|---|
| Job confirmation and onboarding | Accept responsibilities; set room priorities |
| Early offseason | Room evaluations and assigned scouting |
| Free agency and draft preparation | Assigned evaluations |
| Spring program | Teaching emphasis and individual development |
| Camp and preseason | Room recommendations and teaching changes |
| Regular season | Room plan and unresolved corrections |
| Bye or significant midseason review | Revise development work |
| Postseason, if reached | The same job, with greater stakes |
| After the team's final game | Recommendations; his own employment response |
| Next-year opening | New room plan |

## 5. Evaluation

His season review emphasizes what his players learned and executed, the quality of his recommendations and how he worked within the staff. The team's record provides context; it cannot establish his individual contribution by itself. Evidence that could support a bigger opportunity: teaching players successfully; correcting recurring problems; handling veterans and reserves; contributing useful opponent analysis; coordinating assignments with other rooms. The annual review updates that evidence; it awards nothing automatically.

In the January 2014 hiring cycle, a move from position coach to coordinator was not a protected promotion: the employer club could refuse another club's request to interview him. The rules are in the [hiring rules](../../library/2014_coaching_hiring_and_anti_tampering_rules.md#1-who-may-be-asked-and-with-whose-permission), and the stopping points of a career that starts at this rung are in the [coaching career path](../../library/nfl_coaching_career_path.md#8-stopping-points-for-a-career-that-starts-as-a-position-coach).

## 6. Desk sections

My room, Teaching, Weekly assignment, Evaluations and Career (`ROLE_SECTIONS` in `runtime/current_job.py`). No desk is built for this role yet.
