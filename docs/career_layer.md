# Career layer: the current job and the decision queue

Two state files record the coach's job and the decisions still open. Code reads them to refuse an event that an open decision holds, and the views render from them: section 2 and section 8 of Document 5, the phase-control table of the staff register, and the head coach's desk in the active season's README. The code is [runtime/current_job.py](../runtime/current_job.py), [runtime/decision_queue.py](../runtime/decision_queue.py) and [scripts/render_career_views.py](../scripts/render_career_views.py).

## 1. What the two files own

[state/current_job.json](../state/current_job.json) owns:

- the holder, his employment status and his appointments: employer, title, role, unit, start and end, the term's recorded basis and the hire and retention history;
- the reporting line, with every field null where Document 3 records `[UNSET]`;
- an index of the employer's measures and requests, each linked to its source;
- a parity-checked transcription of Document 3's final authority by domain (the owner once the foundation pull request merges), with the holder's part in each row normalized;
- delegation by phase (who calls, who prepares, who transmits, who declares the front), the game-management decisions the head coach retains and how the game handles each, the game-day relays and the emergency leads;
- an index of standing instructions. The rule text stays in its own record.

[state/decision_queue.json](../state/decision_queue.json) owns the unresolved decisions as an index. The question's evidence stays in the linked record, and the decision itself, once made, belongs to its event owner (the packet, the game output, the transaction file). The queue entry links to it.

The files do not own:

- the contract terms (Document 3 section 3.1 and `career/2013/offseason/head_coach_contract.md`);
- the boundary rules on what reaches the coach (Document 3 section 6.2);
- the calendar of stops for the user and the user's open questions on the career's own rules ([season cycle and career milestones](season_cycle_milestones.md));
- the clock, the dated events, research gaps and labelled records (Document 5);
- the staff list, the assistants' contracts and the payroll (the staff register and the coaching payroll).

Neither file is a current record in `docs/repository_map.json`, because the season handoff copies every current record into the next year. The map names them under `career_layer`.

**The Document 3 handoff, in two phases.** Until the foundation pull request that turns Document 3's cells into pointers merges, [Document 3 section 5](../foundation/03_Head_Coach_Organization_and_Authority_Canon.md#5-authority-map) remains the stated sole source of final authority. The job record's authority rows are then a transcription that validation keeps identical to it: columns 3 to 7 byte for byte, except column 4 of rows 13 and 14, whose operational delegation the job record owns. Document 3 row 7 has six cells, its required-consultation cell missing, so the check reads its fifth and sixth cells as the rule limit and the provenance, and the job record holds no consultation for the row, until the foundation pull request repairs it. Any later change to a Document 3 cell fails validation until the job row and its normalized part are revisited. Once that pull request merges, Document 3 keeps the row taxonomy and the precedence rules, and each pointer cell names the job record, which then owns the values. The parity check accepts either form, so the foundation change needs no code change.

## 2. Schemas

Every `record` is `{"path", "anchor"?, "pointer"?}`: a repository-relative path (spaces allowed), a Markdown heading anchor, or a JSON pointer into a `.json` target. Dates are ISO. No line number is stored.

### The job record

| Field | Content |
|---|---|
| `holder`, `status`, `current_appointment` | The holder's party id; `EMPLOYED` or `BETWEEN_JOBS`; the one open-ended appointment, or null between jobs |
| `parties` | Every person or group the record names, with `name`, `kind` and optional `aliases` |
| `appointments[].employer`, `title`, `role`, `unit`, `start`, `end` | The job; `role` selects the desk (`head_coach` and `interim_head_coach` share one) |
| `term`, `contract`, `history` | The recorded end date or its basis, links to the contract, and dated `accepted` and `retained` entries with their events |
| `reporting` | Who decides employment (Document 3 row 1); supervisor, evaluator, cadence and escalation, null when unrecorded |
| `evaluation`, `employer_requests` | The employer's measures by season, with an optional `label` taken from the source (for example "first 2014 measures"), and requests with status `OPEN`, `MET` or `WITHDRAWN` |
| `default_sees` | A link to Document 3 section 6.2; no text is copied |
| `authority.domains` | One row per Document 3 row (1, 2, 3, 3a, 4 to 22): the verbatim columns, `final` party ids, `stone_action` (`decides`, `decides_part`, `recommends`, `consulted`, `responds`, `informs`, `none`, `unset`, `not_applicable`), `scope`, `inference` and `delegated` |
| `delegation.play_calling` | Dated intervals per phase: `caller`, `prepares`, optional `transmits`, `transmits_what`, `front_declaration`, `interim`, `instructed`, `from` (inclusive), `to` (the handover date, exclusive) and `stone_retains` |
| `delegation.game_management` | The retained game decisions, each with an `id` from the subject vocabulary below and a `mechanism`: `live` (a pause), `sheet_rule` (the frozen call sheet), `not_live` (set by the game model) or `not_modelled` |
| `delegation.relay`, `delegation.emergency` | Who carries what on game day; the emergency practice leads, their limits and the game-day caller (null: not appointed) |
| `standing_instructions` | `id`, `subject`, `status` (`IN_FORCE`, `RECORDED`, `SUPERSEDED`, `WITHDRAWN`), the queue classes it `closes`, `summary`, optional `applies`, `given` or `effective`, and its record |

A `subject`, on an instruction or a queue item, is one of `SUBJECTS` in `runtime/current_job.py`: `play_calling`, `inactives` and the game-management ids (`fourth_down`, `two_point`, `kickoff`, `timeouts_and_clock`, `replay_challenge`). Validation refuses any other, so an item cannot escape an instruction's coverage by a spelling.

### The decision queue

| Field | Content |
|---|---|
| `enforced_from` | The season and week from which a call sheet needs a resolved weekly plan item (2014, Week 6) |
| `id`, `title`, `class`, `subject` | Lowercase hyphenated id, a short title, a decision class (section 3) and, for a game-management rule, its subject |
| `owner`, `owner_note` or `owner_basis`, `advisers` | Party ids; an owner other than the class default needs a note or basis |
| `authority_rows`, `question` | The Document 3 rows involved and what is to be decided |
| `raised` | `date`, `by` (`user`, `workflow`, `staff`, `organization`, `medical`), optional closed `event` |
| `status`, `resolution` | `OPEN`, `RESOLVED` or `WITHDRAWN`; a settled item's `resolution` is `{date, by, record, summary, event?, standing_instruction?}`: `by` is `user`, `standing_instruction`, `organization`, `medical` or `staff`, the optional `event` is a closed event, and `standing_instruction` is the instruction's id when `by` is `standing_instruction` |
| `waits_on` | What the decision waits for, whose it is (null when the record names no one) and the date when one is recorded |
| `deadline`, `blocks` | The deadline with its label and the event it must precede; the events the item holds (section 4) |
| `standing_not_applied` | An in-force instruction that would cover the item, with the recorded reason it does not |
| `fallback`, `can_continue` | What happens if the item stays open, and what can continue meanwhile; neither is filled without a source |
| `record`, `sources`, `migrated_from` | The record the item points to, its sources, and where an item migrated from Document 5 came from |

## 3. Decision classes

Each item has one class. The class fixes the default owner, the Document 3 rows that let the decision reach the holder, the events it may hold and whether a standing instruction may close it. A holder-owned item is valid only when at least one of its rows gives the holder a decision, a part of one, a recommendation, a consultation or a response in the current appointment.

<!-- decision-classes:begin -->
| Class | Default owner | Document 3 rows | May block | Closable by a standing instruction | Raised only by the user |
|---|---|---|---|---|---|
| `weekly_game_plan` | the job holder (Stone) | 9, 10, 11, 12, 13, 14 | `week_inputs`, `week_close` | no | no |
| `game_day_inactives` | the job holder (Stone) | 8 | `week_inputs`, `week_close` | yes | no |
| `depth_and_roles` | the job holder (Stone) | 9, 10 | `week_inputs`, `week_close`, `season_stage`, `season_opening` | yes | no |
| `game_management_rule` | the job holder (Stone) | 12, 13, 14 | `call_sheet_part` | yes | no |
| `play_calling_delegation` | the job holder (Stone) | 12, 13, 14 | nothing | yes | yes |
| `emergency_succession` | the job holder (Stone) | 2, 12, 13, 14 | nothing | yes | yes |
| `staff_appointment` | the job holder (Stone) | 2, 6, 22 | `season_stage`, `season_opening` | no | no |
| `practice_plan` | the job holder (Stone) | 11 | nothing | yes | no |
| `discipline` | the job holder (Stone) | 18 | nothing | no | no |
| `media_statement` | the job holder (Stone) | 19 | nothing | no | no |
| `personnel_recommendation` | the job holder (Stone) | 3, 4, 7, 20 | nothing | no | no |
| `quarterback_consultation` | the job holder (Stone) | 3a | nothing | no | no |
| `employment_response` | the job holder (Stone) | 1 | nothing | no | no |
| `personnel_transaction` | David Caldwell | 3, 5, 7, 20 | nothing | no | no |
| `medical_status` | Team medical staff | 15, 16, 17 | nothing | no | no |
| `staff_work` | Jacksonville coaching staff | none | nothing | no | no |

Generated from `CLASSES` in `runtime/decision_queue.py` by `python scripts/render_career_views.py`.
<!-- decision-classes:end -->

## 4. Event kinds and the refusals

| Event kind | Keys | Also held |
|---|---|---|
| `week_inputs` | season, week | `week_close` of the same week |
| `week_close` | season, week | |
| `call_sheet_part` | season, week, part (`offensive_call_sheet`, `defensive_call_sheet`, `decisions.two_point`, `decisions.kickoff`, `decisions.fourth_down`) | |
| `season_stage` | season | `season_opening` of the same season |
| `season_opening` | season | |

An item holds an event when it is `OPEN` and one of its blocks, or an event a block implies, equals it. No block may name a week in which Jacksonville does not play: a bye has no plan, sheet or inactives.

| Script | Events checked | Refusal |
|---|---|---|
| `scripts/build_week_inputs.py N --season YEAR` | `week_inputs`; then `call_sheet_part` for each part present in the week's committed call sheet | Prints `WEEK_INPUTS: BLOCKED` and one line per item; exit 1; no package is left |
| `scripts/close_week.py N --season YEAR --close` (and `--continue`) | `week_close`, and `call_sheet_part` for each part of the committed sheet or of Jacksonville's inputs in the frozen package (`offensive_call_sheet`, `defensive_call_sheet`, `try_policy`, `kickoff_policy`, `fourth_down_policy`) | Prints `WEEK_CLOSE: BLOCKED`; exit 1, never the pause exit 2. While the week's game is paused (with or without `--continue`) it says to revert the edit and rerun with `--continue`; after a partial slate, to revert and rerun, never to void or redraw. In both cases the refusal line drops its settle-and-rerun instruction |
| `scripts/close_week.py` without `--close` | The same | Reports each line as a note; exit 0 |
| `scripts/season_handoff.py` opening check and stage | `season_opening`; `season_stage` | The opening errors list the item; staging prints `HANDOFF BLOCKED`; exit 1 |

An unreadable or missing queue refuses every gated event: the gate fails closed. A sheet, or a frozen package, without a given part is never held by an item on that part. Nothing that resolves a game reads either file, and closing an event depends on an item's status and the event's identity, never on a result.

## 5. When the workflow stops

A stop is warranted when the head coach has a decision or a required substantive recommendation, the choice is consequential, existing instructions do not already cover it, and the next action would commit the choice or remove a meaningful alternative. The stop comes before that next action, and the queue item is what makes the code stop there; a stop written only in prose halts nothing. Once the foundation pull request merges, the rule's full text is in `foundation/decision_rules.md`.

The live in-game pauses are not queue items: a Jacksonville fourth down that the call sheet does not freeze, a legal backup passer and a Jacksonville injury replacement stop the game through `close_week.py`'s pause exit.

An `IN_FORCE` standing instruction may answer a live pause or close a queue item; a `RECORDED` one never does. An open item that an in-force instruction covers is a validation error unless the item records why the instruction does not apply. Stone's standing fourth-down rule is in force and is frozen into each week's call sheet as its `decisions.fourth_down` block, and no item asks how it reads when the third down moves the ball: a frozen block is applied by the game at the actual fourth-down distance and spot (`runtime/kernel.py` builds `policy_state` from the down-4 state before `fourth.decide`; [fourth-down specification](../library/2014_6_fourth_down_specification.md) section 8), so the live pause's third-down picture (section 9 there) does not arise once the standing rule is frozen, and the two Week 5 cases stay as played.

## 6. Rendering and checking

`python scripts/render_career_views.py` writes five generated blocks, each between `NAME:begin` and `NAME:end` comment markers that appear once in their file:

| Block | File |
|---|---|
| `current-job` | Document 5, section 2 |
| `decision-queue` | Document 5, section 8 (the open items, the holder's first, each group by deadline) |
| `phase-control` | The staff register, under Phase control |
| `desk` | The active season's README, after its calendar line; the begin marker names the role and season |
| `decision-classes` | This file, section 3 |

It also keeps two rows after Document 4's in Document 5's manifest, naming the git blob of each file. That binds both files into Document 5's digest and so into the private snapshot: every change to either file moves the digest.

The views read only the two files, Document 5's master-date cell and the section 9 rows still marked Scheduled, the active season's fixtures, `docs/repository_map.json`, and whether the next game's week README and call sheet and the last game's `output.md` exist. They never read a receipt, standings, awards or the wall clock. Every link is written relative to its file and must resolve, headings included. The desk and phase-control blocks are reader prose: a word from the voice rule in AGENTS.md stops the render and names the source field to reword. The desk is built for the head coach only; any other role reports that its desk is defined but not built.

`--check` is read-only. It reports a stale block, a missing or duplicated marker, a desk anywhere but the active season's README and anything that stops the render, and exits 1. Repository validation runs the same check. Writing is refused while any regular-season, postseason or preseason Jacksonville game is paused.

## 7. Cadence

- Open and resolve items in the commit that closes the event that raised or settled them.
- When a week closes, open the next items for the next week in which Jacksonville plays, never a bye: the weekly game plan and, unless a standing instruction covers them, the game-day inactives. An open item that still holds a closed week is a validation error. An item on a call-sheet part the closed week's sheet did not freeze held nothing, so the closing commit moves that block to the next week in which Jacksonville plays; that is bookkeeping, not a settlement. Any other open item is resolved or withdrawn in the closing commit by whoever may settle it, and never by the workflow when it is the holder's (below).
- An `IN_FORCE` instruction may answer a live pause or close an item; a `RECORDED` one never does.
- Never edit either file, or Document 5, while a game is paused: the paused game's packet carries Document 5's digest, so any edit makes the same `--continue` impossible.
- The holder's items are resolved only `by: "user"` or by a standing instruction. The workflow never settles his decision.
- Every change moves Document 5's digest, so it needs the merged-main private snapshot advance before the next close.

## 8. Visibility

The repository is public, so every file is readable by anyone who opens it. Role-based access is a presentation rule only: what the desk shows and what reports may cite. Hidden values stay in the private service.
