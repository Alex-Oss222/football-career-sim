# Career layer: the current job and the decision queue

Two state files record the coach's job and the decisions still open. Code reads them to refuse an event that an open decision holds, and the views render from them: section 2 and section 8 of Document 5 and the head coach's desk, the whole of the active season's README. The Staff page (who calls what) is built from the job record by [scripts/render_coach_pages.py](../scripts/render_coach_pages.py); the staff register's phase-control table is history through October 5, 2014 and is no longer written. The code is [runtime/current_job.py](../runtime/current_job.py), [runtime/decision_queue.py](../runtime/decision_queue.py) and [scripts/render_career_views.py](../scripts/render_career_views.py).

## 1. What the two files own

[state/current_job.json](../state/current_job.json) owns:

- the holder, his employment status and his appointments: employer, title, role, unit, start and end, the pointer to the contract in the coach's permanent record (`contract_record`) and the hire and retention history;
- the reporting line, with every field null where Document 3 records `[UNSET]`;
- an index of the employer's measures and requests, each linked to its source;
- the current values of final authority by domain, one row for each row of Document 3's authority map, with the holder's part in each row normalized;
- delegation by phase (who calls, who prepares, who transmits, who declares the front), the game-management decisions the head coach retains and how the game handles each, the game-day relays and the emergency leads;
- an index of standing instructions. The rule text stays in its own record.

[state/decision_queue.json](../state/decision_queue.json) owns the unresolved decisions as an index. The question's evidence stays in the linked record, and the decision itself, once made, belongs to its event owner (the packet, the game output, the transaction file). The queue entry links to it.

The files do not own:

- the contract terms and the term's end: Stone's coach record, `data/people/coaches/alex_stone.json`, holds the signed terms (`career/2013/offseason/head_coach_contract.md`) and the amendment that completed the rest (in-world January 15, 2013; recorded October 19, 2026), and `current_job.term` and `current_job.contract_terms` read them there;
- the boundary rules on what reaches the coach (Document 3 section 6.2);
- the calendar of stops for the user and the user's open questions on the career's own rules ([season cycle and career milestones](season_cycle_milestones.md));
- the clock, the dated events, research gaps and labelled records (Document 5);
- the staff list, the assistants' contracts and the payroll (the coach records in `data/people/coaches/`, shown on the Staff page and the coaching payroll).

Neither file is a current record in `docs/repository_map.json`, because the season handoff copies every current record into the next year. The map names them under `career_layer`.

**The Document 3 handoff.** Document 3 rebuild draft 2.9 (October 18, 2026) turned its employer, title, start-date, reporting, delegation, final-authority and standing-instruction cells into pointers to the job record and the queue. [Document 3 section 5](../foundation/03_Head_Coach_Organization_and_Authority_Canon.md#5-authority-map) keeps the row taxonomy and the precedence rules; each of its rows points to the job record, which owns the values. Before that, the job record's authority rows were a transcription that validation kept identical to Document 3. The conversion also gave Document 3 row 7 the standard shape: its required-consultation cell had been missing, and the job record holds no consultation for the row. Validation requires each job row to name a Document 3 row with the same decision domain, and each Document 3 row to take one of two forms: exactly `| N | domain | [job record](../state/current_job.json) row N |`, with no other cell, or the full seven-cell value form, compared again with the job row, columns 3 to 7 byte for byte except column 4 of rows 13 and 14, whose operational delegation the job record owns. A Document 3 row with no job row, lettered subrows included, and a repeated row number also fail, and a section 3.1 employer, title or start-date cell that names the job record must be exactly the pointer to the current appointment by its id. So section 5, those three cells and the job record cannot drift apart without failing validation; the prose pointers in Document 3 sections 3.2, 4, 8 and 9 are not checked.

## 2. Schemas

Every `record` is `{"path", "anchor"?, "pointer"?}`: a repository-relative path (spaces allowed), a Markdown heading anchor, or a JSON pointer into a `.json` target. Dates are ISO. No line number is stored.

### The job record

| Field | Content |
|---|---|
| `holder`, `status`, `current_appointment` | The holder's party id; `EMPLOYED` or `BETWEEN_JOBS`; the one open-ended appointment, or null between jobs |
| `parties` | Every person or group the record names, with `name`, `kind` and optional `aliases` |
| `appointments[].employer`, `title`, `role`, `unit`, `start`, `end` | The job; `role` selects the desk (`head_coach` and `interim_head_coach` share one) |
| `contract_record`, `history` | The coach record and the contract in it that hold the term (read through `current_job.term`), and dated `accepted` and `retained` entries with their events |
| `reporting` | Who decides employment (Document 3 row 1); supervisor, evaluator, cadence and escalation, null when unrecorded |
| `evaluation`, `employer_requests` | The employer's measures by season, with an optional `label` taken from the source (for example "first 2014 measures"), and requests with status `OPEN`, `MET` or `WITHDRAWN` |
| `default_sees` | A link to Document 3 section 6.2; no text is copied |
| `authority.domains` | One row per Document 3 row (1, 2, 3, 3a, 4 to 22): the verbatim columns, `final` party ids, `stone_action` (`decides`, `decides_part`, `recommends`, `consulted`, `responds`, `informs`, `none`, `unset`, `not_applicable`), `scope`, `inference` and `delegated` |
| `delegation.play_calling` | Dated intervals per phase: `caller`, `prepares`, optional `transmits`, `transmits_what`, `front_declaration`, `interim`, `instructed`, `from` (inclusive), `to` (the handover date, exclusive) and `stone_retains` |
| `delegation.game_management` | The retained game decisions, each with an `id` from the subject vocabulary below and a `mechanism`: `live` (a pause), `sheet_rule` (the frozen call sheet), `not_live` (set by the game model) or `not_modelled` |
| `delegation.relay`, `delegation.emergency` | Who carries what on game day; the emergency practice leads, their limits and the game-day caller (null: not appointed) |
| `standing_instructions` | `id`, `subject`, `status` (`IN_FORCE`, `RECORDED`, `SUPERSEDED`, `WITHDRAWN`), the queue classes it `closes`, `summary`, optional `applies`, `given` or `effective`, and its record; the practice instruction also has its `schedule` (below) |

A `subject`, on an instruction or a queue item, is one of `ITEM_SUBJECTS` in `runtime/current_job.py`: `play_calling`, `inactives`, the game-management ids (`fourth_down`, `two_point`, `kickoff`, `timeouts_and_clock`, `replay_challenge`), the two career answers in `CAREER_SUBJECTS` (`assistant_interview_permission`, Jacksonville's permission for an assistant to interview elsewhere, and `outside_job_approach`, the holder's own answer to another club's approach), and the week's practice schedule in `PRACTICE_SUBJECTS` (`practice_schedule`, Document 3 row 11). A game-management decision takes only a game subject, and the Game Week Briefing lists only the game's standing instructions; the desk and Document 5 list every one. Validation refuses any other, so an item cannot escape an instruction's coverage by a spelling.

The standing practice instruction (`current_job.practice_instruction`, one in force a season; the user's answer of October 23, 2026, recorded in the [rebuild plan's change log](rebuild_plan.md#change-log)) closes the week's `practice_plan` question. Its `schedule` is the instruction's own words as data, in the practice record's vocabulary (`runtime/practices.py`): the `season` and the `from_week` it applies from; the `week` shape before a game on its `game_day` (the players' `days_off` and each session's `day` and `type`); the `equipment` (`pads` by week and day, in `padded`, every other session in `otherwise`); and the `added_days_off` by date. Validation holds it to that vocabulary; the padded-practice and rest limits are the practice record's check of each week's schedule (rebuild step 5), not this record's.

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
| `outside_job_approach` | the job holder (Stone) | 1a | nothing | yes | no |
| `staff_permission` | the job holder (Stone) | 2 | nothing | yes | no |
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

A stop is warranted when the head coach has a decision or a required substantive recommendation, the choice is consequential, existing instructions do not already cover it, and the next action would commit the choice or remove a meaningful alternative. The stop comes before that next action, and the queue item is what makes the code stop there; a stop written only in prose halts nothing. The rule's full text is in the [decision rules](../foundation/decision_rules.md), and each job's working view, stops and automatic work in its role file: the [head coach](../foundation/roles/head_coach.md), the [coordinator](../foundation/roles/coordinator.md), the [position coach](../foundation/roles/position_coach.md) and the coach [between jobs](../foundation/roles/between_jobs.md).

The live in-game pauses are not queue items: a Jacksonville fourth down that the call sheet does not freeze, a legal backup passer and a Jacksonville injury replacement stop the game through `close_week.py`'s pause exit.

An `IN_FORCE` standing instruction may answer a live pause or close a queue item of a class the table marks closable by a standing instruction (validation refuses any other such resolution); a `RECORDED` one never does. An open item that an in-force instruction covers is a validation error unless the item records why the instruction does not apply. Stone's standing fourth-down rule is in force and is frozen into each week's call sheet as its `decisions.fourth_down` block, and no item asks how it reads when the third down moves the ball: a frozen block is applied by the game at the actual fourth-down distance and spot (`runtime/kernel.py` builds `policy_state` from the down-4 state before `fourth.decide`; [fourth-down specification](../library/2014_6_fourth_down_specification.md) section 8), so the live pause's third-down picture (section 9 there) does not arise once the standing rule is frozen, and the two Week 5 cases stay as played.

## 6. Rendering and checking

`python scripts/render_career_views.py` maintains three named blocks and two complete reader pages. The named blocks appear once between their matching `NAME:begin` and `NAME:end` markers:

| View | File |
|---|---|
| `current-job` | Document 5, section 2 |
| `decision-queue` | Document 5, section 8 (the open items, the holder's first, each group by deadline) |
| `decision-classes` | This file, section 3 |
| `desk` | The whole of the active season's README |
| `calendar` | The active season's Calendar.md, with the current month first |

The injury report and the Statistics README are not career views: each has one builder of its own (`render_week_pages.py` and `render_season_stats.py`), and `python scripts/rebuild_pages.py` runs every builder in order.

It also keeps two rows after Document 4's in Document 5's manifest, naming the git blob of each file. That binds both files into Document 5's digest and so into the private snapshot: every change to either file moves the digest.

The job and decision blocks read the two state files, the coach record, the master date, the dated events and the published fixture list. The coach's desk continues to show the coach-owned decisions from the current decision record. Its season performance, standings, player production and medical sections are derived from the completed games and the roster's current medical communication (`scripts/render_season_hub.py`, through `runtime/season_summary.py`, which gives the statistics index and the injury report the same words). The calendar is assembled from the recorded dates and the same fixtures, keeping the complete historical year below the current month. None of these pages stores an independent game result, injury clearance or depth decision.

Links are relative to each reader page and must resolve. The head coach's desk and the calendar are checked for reader-friendly football prose. The voice check rejects internal process wording before writing. The coach's desk remains available only for the head-coach role; the other roles are defined separately.

`--check` is read-only. It reports a stale block or desk, a missing or duplicated marker, a desk block in any README and anything that stops the render, and exits 1. Repository validation runs the same check. Writing is refused while any regular-season, postseason or preseason Jacksonville game is paused.

## 7. Cadence

- Open and resolve items in the commit that closes the event that raised or settled them.
- When a week closes, open the next items for the next week in which Jacksonville plays, never a bye: the weekly game plan and, unless a standing instruction covers them, the game-day inactives. An open item that still holds a closed week is a validation error. An item on a call-sheet part the closed week's sheet did not freeze held nothing, so the closing commit moves that block to the next week in which Jacksonville plays; that is bookkeeping, not a settlement. Any other open item is resolved or withdrawn in the closing commit by whoever may settle it, and never by the workflow when it is the holder's (below).
- An `IN_FORCE` instruction may answer a live pause or close an item; a `RECORDED` one never does.
- Never edit either file, or Document 5, while a game is paused: the paused game's packet carries Document 5's digest, so any edit makes the same `--continue` impossible.
- The holder's items are resolved only `by: "user"` or by a standing instruction. The workflow never settles his decision.
- Every change moves Document 5's digest, so it needs the merged-main private snapshot advance before the next close.

## 8. Visibility

The repository is public, so every file is readable by anyone who opens it. Role-based access is a presentation rule only: what the desk shows and what reports may cite. Hidden values stay in the private service.
