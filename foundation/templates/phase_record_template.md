# Phase record maintenance template

This template describes repository records. It does not replace the approved in-world response formats.

## Report owner

Use the appropriate football output template for the readable opening. Its header identifies the phase, team, location, actual dates and completed practice days, then the work addressed. A completed report is rendered directly in chat as well as saved.

The file has one `sim-meta` JSON comment: `kind: phase_output`, `status` (`NOT_STARTED`, `IN_PROGRESS` or `COMPLETE`), `through` (ISO date or null) and `event_ref` (the descriptive ID of its latest actual event). Before work starts, both `through` and `event_ref` are null. Never use a numbered ledger entry as the event identity.

Each completed block has an `event-record` JSON comment in its dated section. Supply `id`, `date`, `date_end` when the block spans dates, a one-sentence `summary`, and `status: closed`. For example, `2014-06-13-otas-complete` identifies the actual OTA close. These markers remain in the file and are omitted from the chat's football account. Multiple completed blocks can belong to one ongoing camp report; its latest `event_ref` follows the latest completed block without claiming the entire camp is complete.

The owner of a material checkpoint also carries that checkpoint's single `closure` object, with its exact `checkpoint`, `through` and `sequence`, under the [event-record handoff rules](../06_Event_Records_and_Handoff.md). Other records in the same event group link to the owner; they do not duplicate the closure. The annual record provides dated one-line links rather than another account of the activity.

The dated report preserves who participated, the work performed, communicated medical limits, observations, corrections, decisions actually made and remaining questions. Keep intent in the plan and outcomes here. Do not manufacture missing observations to fill a heading.

## Coaching findings

Include player and unit findings in the same report as their supporting work. Do not create another `player_assessments.md`, an empty future summary or a self-hash for this integrated owner. Existing frozen historical summaries are not a pattern for new records.

A material finding may add a dated update to the player's existing opening annual card or to an existing position-battle card. Neither is a new whole-player assessment. Each year has an opening assessment maintained through the season and one separate final assessment after season close. A practice finding alone does not award a role or force a grade change.

## Plans

Keep a durable-plan label and links to results. Do not duplicate the changing execution status inside the plan. Revise teaching content only when the user changes it.
