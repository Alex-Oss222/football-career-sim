# Writing a game turn

Adopted October 18, 2026 to change how future game turns are written. The [regular-season template](../foundation/templates/regular_season_output_template.md) retains Coach info and seven sections; the [preseason template](../foundation/templates/preseason_output_template.md) retains eight. Keep the complete receipt-derived statistics in their established place. A request to revise this process or a template does not authorize rewriting an existing game output. Historical reports remain unchanged unless the user separately requests their revision.

The earlier instructions encouraged writing one field at a time, covering the same statistics in several sections, borrowing transcript questions, and forcing answer shapes. That made a technically complete report sound assembled. The workflow below replaces those instructions. Mechanical validation checks the record; a separate editorial review checks whether the account and conversation work.

## 1. Establish the evidence and the scope

Read the applicable instructions, current season state, approved preparation and decisions, game receipt and public play record, medical changes and existing output. Use the actual season paths and active playbook. For a rewrite, work from the closed event: do not redraw, advance time, revise a user decision or add an activity that was never recorded.

Identify the football facts that matter, the authorized decisions, and any material unknowns. Retain preparation dates, already-recorded practice work, user wording and supporting sources. A style revision may reorganize that evidence; it must not silently turn documented work into an omission or use a plausible weekly schedule to invent missing work.

On a new game turn, establish the preparation and pregame media from the information available before the draw. Preserve already-written pregame material. If the final document is assembled after the result, use only the recorded pre-kickoff sources for those sections; do not backfill a prediction, concern, question or coaching intention because it fits the result.

Keep event metadata and statistical markers intact. The full box score is generated from the receipt by the supported renderer. Existing factual record tables and score summaries may also be generated and verified. No script should fill narrative paragraphs, coaching explanations or dialogue by reciting fields. `scripts/close_week.py` closes games and writes results and receipts; `scripts/render_box_score.py` fills the marked statistical block; `scripts/render_coach_record.py` supplies the coach record. Those operations do not author the football account or approve its claims.

Distinguish a recorded play, an attributed staff observation, an authorized decision and an inference before drafting. Read the active record's attribution rules before using a field as evidence of a player's skill or a coach's choice. A generated call label or timeout total does not by itself establish a coach's choice or its reason; a statistical credit can be valid for the box score without supporting a technique or development judgment. The active contract in [runtime documentation](../runtime/README.md) controls that distinction. Missing authoring data also does not establish that a coach failed to observe something. Keep these distinctions in the working review rather than turning them into repeated prose disclaimers.

## 2. Decide what the report needs to explain

Before filling the template, identify the sequences that explain the result, the supported coaching findings, the decisions that mattered and any actual change to availability or roles. Use a temporary outline if useful; do not create another permanent report or checklist. Choose the football substance first, then put it in its established section. The presence of a prompt is never evidence that something happened.

Each part has a different job:

| Part | What belongs here |
|---|---|
| Preparation | The actual dated work, approved choices, opponent context and material restrictions before kickoff. Retain existing evidence; do not substitute a generic NFL week. |
| Game narrative | The action that explains how the result happened, in the template's chronology. Select useful sequences and numbers; the statistical block already owns complete scoring and drive accounting. |
| Coaching review | What the recorded work supports about units, players, combinations and decisions, including contrary evidence and the opponent's contribution. Do not retell the quarters or invent technique and communication causes. |
| Media | A public conversation at its actual point in the week. Questions seek information and answers respond; this is not a spoken version of the coaching review. |
| Carry-forward | The specific work resulting from the review, with an owner and next opportunity where established. A proposal stays a proposal. Do not repeat the finding at full length. |
| Personnel and closure | Current roles, availability, material changes, record and next event, with links to their owners. Do not recopy each player's statistical line or create a new judgment for every unchanged group. |

The same play may matter in more than one section when each use adds something: the story reports a failed conversion, the review explains a supported cause, and the carry-forward names the resulting work. Repeating the result, numbers and qualification in all three adds nothing.

Keep the main section order and established unit headings. Subordinate prompts describe possible coverage, not a list to answer sentence by sentence. Give important evidence room; let a quiet section be brief. Omit empty optional findings and lists. Do not force a controversy, an award, balanced praise and criticism, a question count, a paragraph count or a target word count. State a shared evidence limit once in supporting notes, and in the football analysis only where it changes a conclusion.

## 3. Compose the conversation separately

Use the [head-coach media method](head_coach_media_method.md). Establish what the reporter has seen or heard and what the question seeks to learn. Draft Stone's answer from the approved profile, the actual question and his authorized position. Then decide what the next reporter would pursue. Do not prewrite a list of answer topics and reverse-engineer questions to deliver it.

Apply the media method's distinction between the author's missing data and Stone's knowledge. Give an accurate routine response where supported; remove an unnecessary question whose answer would require invented substance. A genuinely consequential user-controlled choice still returns to the user. Do not fill the gap with a canned refusal or an invented reason.

## 4. Use research where it helps

The [media research](head_coach_media_method.md#5-research-basis-and-limits) and [game-report research](preseason_game_reports.md) supply inspected references for form and football explanation. Use those references without pretending to have researched them again. Read an additional relevant source when an unfamiliar situation calls for it; research and verify a material rule or factual gap under the existing sourcebook requirements.

Do not copy transcript questions and swap names. Do not borrow real results, diagnoses or player assessments to fill this career. A real transcript is evidence of its own conversation only. Keep new writing references in compact supporting notes outside the dialogue, together with existing evidence links. No per-question citations, per-section source quotas or routine research-status lines are needed.

## 5. Review the draft before delivering it

Run a distinct editorial pass after drafting, using a separate reviewer when available. Read the narrative and dialogue without the template prompts or full statistics first. Can the reader understand the game and the work? Would a reporter actually need to ask this question? Does Stone answer it in his established manner? Review the whole exchange, not just isolated sentence wording.

Return the affected passage for revision when:

- Its content follows a field list instead of explaining a football matter, or several sections repeat the same account.
- Questions mainly feed Stone a statistical recap or the author's desired talking points, and follow-ups could have been written without reading his answer.
- The answers repeatedly use the same confession, refusal, film deferral, polished slogan or sentence pattern. Do not repair this by imposing a different pattern.
- A speaker explains software limitations, knows private or later information without a basis, or supplies a new decision or motive to make an answer work.
- The prose claims a technical cause, completed coaching action or evaluation that its evidence does not establish.

Correct the passage and reread its surrounding section. Generic wording is repaired by finding the useful thought, not merely replacing words or shortening every answer. This is an authoring responsibility, not another user approval step, a word blacklist or a claim that automated tests can measure natural speech.

Then check score and chronology, names and participation, the information available at each session, medical authority, announced roles, and the meaning of Stone's decisions against the actual sources. Preserve uncertainty where it matters. A fluent answer still fails if its substance is invented.

Finally use the existing repository and statistical checks. Preserve exact generated-box-score agreement and source metadata. A presentation-only edit retains the event identity, result and career date. Update dependent source bindings only where the existing validation rules require it. Do not refresh a summary hash without reviewing the summary against the revised output. Follow [the update workflow](update_workflow.md); no new approval gate, linter or state format is introduced here.

## 6. Keep the process consistent

This file owns the authoring sequence and editorial review; the media method owns dialogue guidance; the two game templates own section order and content placement. AGENTS and the update workflow route here. When fixing a recurring writing problem, revise its controlling instruction and remove conflicting wording from both templates rather than appending another style mandate. Search those entry points for the superseded rule. Older reports and worked examples are evidence of their own events, not a standard to imitate over the current instructions.

For a template/process-only change, inspect the final diff: it must not change career outputs, event metadata, receipts, call sheets or current state. Verify that the complete statistics specification and established layout remain intact. Review the prose guidance separately from repository checks; a passing validator does not establish that the next report will read naturally.
