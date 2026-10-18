# Decision Rules

**Document status:** Durable rule for when an automatic run stops for the user and what it presents when it does
**Adopted:** October 18, 2026, from the user's design of the career layer of the same date (its sections 6 and 7); no simulation clock advance.
**Change rule:** Amend only by an explicit user instruction or a documented canon correction.

These rules apply in every job Stone holds. They do not say what his current job lets him decide, which decisions are open, or when in the football year each stop falls. Those have their own owners:

- what the current appointment lets him decide, recommend or see: the [current job record](../state/current_job.json), under the row taxonomy of [Document 3's authority map](03_Head_Coach_Organization_and_Authority_Canon.md#5-authority-map);
- the decisions still open: the [decision queue](../state/decision_queue.json);
- the fixed decision classes, each with its default owner, its Document 3 rows, the events it may hold and whether a standing instruction may close it: the [class table](../docs/career_layer.md#3-decision-classes);
- when the stops fall in a season: the [season cycle](../docs/season_cycle_milestones.md#1-the-yearly-cycle) and the [career milestones](../docs/season_cycle_milestones.md#2-career-milestones);
- what each job's working view holds: the role files for the [head coach](roles/head_coach.md), the [coordinator](roles/coordinator.md), the [position coach](roles/position_coach.md) and the coach [between jobs](roles/between_jobs.md).

The operating principle is the user's: prepare the evidence automatically, let independent people make their own decisions, and return control before Stone makes a consequential commitment that the user has not already authorized.

## 1. When the run stops

A stop is warranted when all four conditions hold:

1. Stone has a decision or a required substantive recommendation.
2. The choice is consequential.
3. Existing instructions do not already cover it.
4. The next action would commit the choice or remove a meaningful alternative.

The stop comes before that next action. The run advances until the earliest unresolved decision affecting Stone's authorized work, and work that commits nothing may continue while he decides. A date arriving is not by itself a stop: the stages of the football year are review opportunities, and one stops the run only when a decision in it meets the four conditions.

The code enforces a stop only through a decision-queue item. An open item names the events it holds, and the scripts that would commit one of them refuse while it is open ([the career layer](../docs/career_layer.md#4-event-kinds-and-the-refusals), section 4). A question written only in prose halts nothing. Open the item in the commit that closes the event that raised it.

A position coach usually meets fewer stops than a coordinator, and a coordinator fewer than a head coach, because fewer team decisions belong to him. A user-authored standing instruction can cover repeated situations at any level.

## 2. What a presented decision contains

Every decision put to the user carries the following, drawn from the queue item and the record it links. The queue is an index: the evidence and the full account stay in the linked record, and no field is filled without a source.

| The user sees | Where it comes from |
|---|---|
| What happened and when | `question` and `raised` (the date, who raised it and the closed event) |
| Why it reaches Stone | `class` and `authority_rows`: a holder-owned item is valid only when one of its class's rows gives him a decision, a part of one, a recommendation, a consultation or a response in his current appointment |
| What he knows and what remains uncertain | The linked `record` and `sources`; `waits_on` names what is still awaited, from whom and by when |
| His actual authority | `authority_rows`, read against the job record's authority rows |
| Staff advice, attributed to its source | `advisers`, with the advice itself in the linked record ([Document 3](03_Head_Coach_Organization_and_Authority_Canon.md#81-agency-and-communication-controls) section 8.1, item 4) |
| Feasible alternatives and their consequences | The linked record; `fallback` says what happens if the item stays open |
| The deadline | `deadline`: the date, its label and the event it must come before |
| What can continue while he decides | `can_continue` |

A listed set of alternatives is not closed: the user may choose any other physically, legally, contractually and institutionally possible action (Document 3 section 8.1, item 3).

## 3. Events and where control returns

| Event | Automatic part | Where control returns |
|---|---|---|
| Injury | Occurrence, medical evaluation and communicated restrictions | Replacement or plan change requiring Stone |
| Owner fires Stone | Employer's decision and notification | Stone's response and next career direction |
| Coordinator leaves | Departure and resulting vacancy | Staff response belonging to Stone |
| Interview request | Interest, permission process and available dates | Whether to pursue; material commitments |
| Offer arrives | Employer's terms and deadline | Accept, reject or counter |
| Routine retention | Record continuing employment | Only if duties, terms or Stone's intentions change |
| Award or statistical milestone | Record the achievement | Only if it creates an actual choice |
| Technical readiness failure | Diagnose and repair the system | User involvement only for a genuine unresolved choice |

Interest, an offer and an acceptance are separate events. A medical restriction is information Stone must respect; choosing the replacement is his football decision.

Routine media follows the role and runs under established instructions; a consequential statement remains Stone's choice.

The live in-game pauses are not queue items. The game itself stops, through `close_week.py`'s pause exit, for a Jacksonville fourth down that the frozen call sheet does not decide, a frozen rule that says ask, a legal backup passer and a Jacksonville injury replacement, and it resumes with `--continue` once the user answers. Which retained game decisions pause, follow a frozen rule or are not yet live is the job record's `mechanism` field under `delegation.game_management`.

## 4. How a decision closes

An item closes in the commit that closes the event that settled it, in one of three ways:

1. **By the user.** The user decides, and the event owner (the packet, the game record, the transaction file) records the decision; the item is marked resolved `by: "user"` with that record.
2. **By a standing instruction.** An instruction the job record lists as `IN_FORCE` covers the item's class (and its subject, when the item has one). The item is resolved `by: "standing_instruction"` and names the instruction. Only classes the class table marks as closable by a standing instruction close this way. An instruction recorded but not in force (`RECORDED`) neither closes an item nor answers a live pause, and an unrecorded standing choice is never inferred. An open item that an in-force instruction covers is settled as covered, or it records why the instruction does not apply.
3. **By the party that owns it.** A decision that belongs to someone else (the general manager, the medical staff, another staff member) closes when that party decides under its own authority and information, and the record says so.

The workflow never settles Stone's item. An item the job holder owns is resolved only by the user or by an in-force standing instruction; validation refuses any other resolution. Some classes, such as a change in who calls a phase, can be raised only by the user; the class table marks them.

## 5. Access

Each role file says what that job's working view holds. Ordinary team information stays available where appropriate: the distinction is between ordinary knowledge, working access, confidential information and decision rights. Another club's confidential scouting, medical or negotiation information is never exposed merely because it exists somewhere in the repository. The repository is public, so role-based access is a presentation rule only, governing what the desk shows and what reports may cite ([the career layer](../docs/career_layer.md#8-visibility), section 8). Protected medical, legal, personnel and private information reaches the coach only through a plausible authorized channel (Document 3 section 6.2, item 8).
