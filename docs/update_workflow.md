# Keeping the career records current

The actual event owns its dated facts. [Document 5](../state/05_Current_Season_State.md) owns the current checkpoint, and the [repository map](repository_map.json) names current paths and dependencies. [Document 6](../foundation/06_Event_Records_and_Handoff.md) governs event records and handoffs. `Record.md` is a generated one-line index of those owners, not another narrative or a place to resolve an event.

Write names, dates and football findings in ordinary language. Descriptive event metadata and compatibility aliases connect evidence internally; readers should not have to decode entry numbers. Software releases and migrations belong in their technical owners and do not appear as football events.

## Write once, update the affected views

| Completed event | Authoritative record | Views to update when their facts change |
|---|---|---|
| Practice or camp work | The phase's `training_report.md`, including its assessment | Dated player updates, an actual position-battle card, availability, current state and any changed role or medical instruction |
| Signing, release, tender or trade | The actual contract or transaction record | Roster, contract register, cap and future obligations, depth chart, pick ownership, player development cohort and Documents 4 and 5 |
| Draft selection or rookie contract | Drafted or undrafted result record | Player control, contracts, finances, pick ownership, working player record, development cohort and current state |
| Outside staff request, permission, interview or outcome | Dated staff request/outcome record; preserve frozen method and result artifacts | Staff timeline and current pending decisions; employment and payroll only if a departure or appointment occurred |
| Staff hire, departure or delegated responsibility | Staff hiring/departure/decision record | Current staff, contracts, authority where affected and Documents 4 and 5 |
| Medical decision | Dated medical record or the phase/game record that received the instruction | Current availability and permitted work; role or roster changes only if separately decided |
| Game | Game output and public result receipt | Box score, relevant season statistics and standings, awards when due, actual injuries/roles, player updates and current state |
| Bye | That week's output | Actual practice, recovery, self-scout and decisions; no game receipt |
| Technical or foundation correction | The affected technical or rule owner | Source hashes, references and readiness when affected; no fabricated football event |

Plans retain intended teaching, priorities and authorized limits. A report owns observed work. The calendar retains dates, opponents, windows and deadlines, with sources and dated corrections. Do not append completed-event narratives, cap snapshots, role assessments or engine status to the calendar. A historical financial as-of date remains correct until a financial event changes it.

Trades and free agency are year-round areas under `00_Team_Operations`; their position in the file tree does not limit when transactions can occur. Staff records in `01_Early_Offseason` likewise keep their dated sources when an event falls later. Update an existing owner instead of creating a duplicate phase-specific transaction history.

## Close an event

1. Read current state, the team's calendar, the applicable plan and the relevant sources. Respect the active playbook iteration and dated information gates. The [2014 NFL calendar](../library/2014_nfl_calendar.md) provides league research; [Jacksonville's calendar](../career/2014/Calendar.md) supplies the team route. Actual historical opponents, dates, venues, byes and published amendments control every year. Branch standings determine draft order and playoff qualification.
2. Write the completed event in its domain owner. Keep its actual date, authority, conditions, uncertainty and consequences. A mixed date window may contain several separately dated events. Preserve prior facts and identify a correction where needed; do not silently alter a result or present a proposal as completed.
3. Attach the descriptive event metadata to that owner and its closure metadata to the record that closes the bounded progression. New phase metadata names the source event through `event_ref`. Legacy identifiers are resolved by the single compatibility map, not displayed as a second history. Generate the year's `Record.md` from the owners.
4. Update each genuinely affected current view in the same commit. Reconcile control, contracts, known financial effects, medical instructions and roles even when an unrelated amount remains unknown. Never use an unknown figure as zero. Preserve unexecuted plans and frozen pre-result choices.
5. Reconcile Documents 4 and 5 checkpoints and source pointers. Document 4 may retain its older content version if none of its facts changed; Document 5 must name that exact version. After a foundation edit, refresh its Git-blob hash in Document 5 using `git hash-object`.
6. Refresh player ages after a master-date or roster change, and refresh the development cohort after any signing, departure, trade, draft addition or tender resolution. Verify a new player's identity and birth date before a game. Review updated reports and assessments against their evidence, run validation and the appropriate tests, and commit the complete dependency set through a pull request.

Phase metadata uses `NOT_STARTED`, `IN_PROGRESS` or `COMPLETE`, its actual evidence-through date and the descriptive source event. Future reports keep null evidence dates and event references. From 2014, assessment is inside `training_report.md`; no separate phase assessment or summary receipt is created. Legacy 2013 phases that still have separate summaries retain their SHA-256 source receipts. For those only, review the actual summary first and then use `refresh_summary_receipt.py PHASE --reviewed`. That command acknowledges review; it does not generate observations or prove the prose correct.

Useful maintenance commands, with the actual season supplied:

```sh
python scripts/render_annual_record.py YEAR
python scripts/render_player_ages.py
python scripts/build_player_progression_roster.py
python scripts/render_jaguars_cap_tracker.py --check
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

Regenerate cap views before their check when financial inputs changed. Generated trade and award pages likewise come from their source owners. Resolve paths with `SeasonPaths`, never by recreating an old flat folder named in a frozen reference.

## Games and their statistical evidence

`Run Week N` remains the complete one-command regular-season workflow defined in `AGENTS.md`. Read the week's actual plan, current roster and medical instructions, calendar, active books and existing output. Internal readiness preparation, an already-authorized migration, input construction, closure, statistics, PR bookkeeping and snapshot handling belong to the task. The user does not have to operate helper scripts. A genuinely new consequential Stone decision still returns to the user.

Before a draw, `build_week_inputs.py N --season YEAR` freezes the full TeamInput package and checks player exclusivity, legal game-day roles and the scheduled game count. An ad-hoc package must pass `check_week_input_exclusivity.py PACKAGE --expected-games COUNT`. Jacksonville's actual control overrides conflicting historical personnel rails. Preserve the frozen `call_sheet.json`; a permitted technical rerun reuses its pre-result decisions.

Run `check_game_readiness.py --season YEAR` before either game path. A green repository check, populated schedule, accepted kernel or prepared future roster does not waive a missing game gate. Keep private engine state outside Git and public reports.

For a closed regular-season or postseason Jacksonville game, retain `runtime.statbook.make_receipt(..., detail="full")`, including complete public player dictionaries, snap play ledger and named-call statistics. Ordinary background games use `detail="compact_stats"`: every nonzero generated statistic and a row for every game-day active player remain, while background snap details and zero counters are omitted. Compression changes no result or total. Every scheduled game must have its one canonical receipt before a weekly statistical closure is complete.

Render the box score into the game's output, and render standings, cumulative statistics, team tracker and relevant awards from those receipts. The full gamebook block of the [regular-season template](../foundation/templates/regular_season_output_template.md) contains the scoring summary, team and individual statistics, drive chart and supported snap counts; `runtime/gamebook.py` defines what the receipt can supply. Coach-record tables use `render_coach_record.py`. Do not invent missing plays, hand-add cumulative numbers or import historical results to fill gaps. Incomplete coverage withholds formal rankings. Read the calibration audit; an `OUTSIDE` result prompts investigation of inputs or implementation, never a new draw selected for a better outcome.

```sh
python scripts/build_week_inputs.py WEEK --season YEAR
python scripts/close_week.py WEEK --season YEAR --close
python scripts/render_standings.py YEAR
python scripts/render_season_stats.py YEAR --team TEAM_ID
python scripts/render_team_tracker.py YEAR
python scripts/league_awards.py week WEEK --season YEAR --close
```

`render_box_score.py --season YEAR --write OUTPUT_PATH` fills the resolved game's actual output path. Preserve regular-season and postseason totals separately. From 2014, working player records retain prior yearly rows and receive only supported statistical updates; game rendering does not silently re-grade a player.

Jacksonville's game uses user-controlled management. A consequential injury/removal pause writes the completed prefix and waits for Stone's replacement decision through the same private event; do not close the remaining slate first or invent an answer. The private snapshot advances only from the merged canonical branch under the normal workflow, never from an unmerged PR.

Preseason uses the [complete preseason template](../foundation/templates/preseason_output_template.md), its authorized bulk presentation and ordinary material-decision stops. Preserve each game's actual output and supported statistics without adding preseason totals to regular-season standings or statbooks.

Postseason uses the same one-command workflow and the actual era's bracket. For the current 2013/2014 era, weeks 18 through 21 identify Wild Card, Divisional, Conference and Super Bowl. Build each round only after its predecessor closes, using branch qualifiers and historically correct slots. An eliminated Jacksonville plays no further game; other clubs' rounds still close. Postseason receipts, totals and honours remain distinct, with no invented weekly playoff awards.

## Player, coaching and film records

Create the opening player assessment for the controlled roster at the start of the year, and add a record when a player joins. Retain its baseline and append dated evidence updates through rookie camp, the spring program, camp, preseason, regular season and postseason. Preserve departed players' history. Write the separate final player assessment with the season review after the season closes. These are the two assessment records; do not create another set under every phase.

The phase report comes first. A player update or position-battle card points to the relevant work and explains what it changes: assignment recognition, communication, technique, physical execution, decision-making, support and opportunity remain distinct. An unresolved question remains unresolved. Comparable reserve work matters, but a calendar advance or a single corrected rep supplies no automatic upgrade. Preserve players' actual perspectives only where recorded. Numeric personnel judgments follow the user-authorized player-sheet rule and never become invented measurements or engine inputs.

Open battle cards are grouped by unit, position and contested spot. Add one only when a real competition and its candidates are established. A cross-training lane, an empty roster place or a coaching question is not by itself a competition. Record the decision in the roster-decision owner and update the actual depth chart when Stone resolves a role.

The roster generates the development cohort. `build_player_progression_roster.py --check` must agree before resolving development. Frozen exit interviews from a prior season are evidence, not a mechanism to restore departed players. Development plans describe intended work and remain separate from the player's observed assessment.

Film preparation, distribution, acknowledgment, comprehension and delayed retention are separate facts. The film delivery record owns the actual packet revision, recipient, delivery date, lawful basis and source. A prepared queue is not a delivered packet. Check control, medical instructions and the pre-program contact rules before any distribution or teaching. Update the queue after a real receipt, not to manufacture completion.

[Coaching records](../career/coaching_profiles/README.md) separate adopted identity, performance and career statistics. Record the actual coaching contribution in its source report. Update Stone's [performance review](../career/coaching_profiles/alex_stone_performance_review.md) after a season, an employment decision or a material change to a standing concern; keep routine teaching observations in the season reports. Add completed-season records, statistics and defined league ranks to his [NFL Coach Sheet](../career/coaching_profiles/alex_stone_nfl_coach_sheet.md). His [coaching profile](../career/coaching_profiles/alex_stone_coaching_profile.md) holds the user's approved approach; change that identity when the user revises it, and refresh current job or delegation facts when their source changes. Assistant assessments keep their existing dated record. A profile edit alone cannot hire a coach, change authority, claim a new practice or supply an engine effect.

## Handoff and checks

After the team's final game, finish player and coach exit reviews in `07_Season_Review`. Reconcile medical status, roster rights, player and staff contracts, cap obligations, picks, development and open decisions before `scripts/season_handoff.py` stages the next year. Team closeout and league statistics/awards have separate gates. Future calendars can be researched before the next season opens; actual historical dates remain binding without importing future outcomes.

Validation checks paths and anchors, source hashes, owned event identities, checkpoint continuity, annual record freshness, phase evidence, controlled-player membership/counts, receipt coverage and generated statistics. It cannot decide whether football analysis is true, a medical claim is supported or a financial assumption is justified. Review the evidence and diff as well as passing the checks. CI does not simulate missing events to repair a document.

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - May 23, 2013 - repository continuity and readiness reconciled", "sequence": 13, "through": "2013-05-23"}, "date": "2013-05-23", "id": "2013-05-23-repository-continuity-and-readiness-reconciliation", "kind": "technical", "status": "closed", "summary": "Repository continuity and readiness records were reconciled."} -->

## 2014 closure acceptance (October 1, 2026)

The `season_closure` release gate in `runtime/season_readiness.json` was accepted on an isolated end-to-end closure, kept green as `tests/test_2014_season_closure.py`.

- **What ran.** One complete synthetic Week 1 slate: the sixteen real 2014 Week 1 fixtures from `career/2014/05_Regular_Season/Schedule/fixtures.json`, each club a synthetic depth-ordered 46-player unit (`tests/support_rosters.py`), season-qualified event ids (`2014-week01-<away>-at-<home>`), closed through `scripts/close_week.py`'s own `close_slate` and `write_receipts`: Jacksonville's game first under user control through the kernel 2014.4 pause and continuation path (every consequential removal answered with the depth default), the other fifteen as one autonomous batch. The private closure went to a local instance of the private service with a pinned store seed (`tests/local_private_service.py`), never the live runtime, and the production runner's season-release check ran against the temporary root's own accepted release record, never the real one.
- **On what root.** A copy of the repository in a temporary directory (`.git`, `.sim_cache` and caches excluded) with every 2014 gate marked VERIFIED, the installed kernel accepted and a synthetic game depth chart in place, so the release check, the receipt-season checks and the validator exercised the real routing. The real `career/` tree, the real `.sim_cache/` and the real receipts folder were checked unchanged afterwards.
- **What was generated and checked.** A full receipt for Jacksonville and compact receipts for the other games under `career/2014/05_Regular_Season/Statistics/records/game_receipts/`; the statbook views (`render_season_stats.render_views`) under `Statistics/records/`; `05_Regular_Season/standings.md` through Week 1 (`render_standings.render`); the gamebook box score filled between the markers of `05_Regular_Season/Games/Week_01/output.md` (`render_box_score.fill`, confirmed not stale); the award pages (`league_awards.render`); the team tracker (`render_team_tracker.render`); the working player cards (`update_player_cards.refresh_cards`); then `scripts/validate_repository.py`'s `validate()` on the temporary root, which must report no error beyond any the live checkout already carries at that moment (and reported none in the acceptance run).
- **What it does not cover.** No real 2014 input, no live service, no award draw (no 2014 `methodology.json` exists yet; freeze it from the actual schedule before Week 1), no postseason round and no preseason game. It is acceptance of the closure path, not of any 2014 result.

<!-- event-record: {"closure": {"checkpoint": "Canonical update - January 5, 2014 - Player age register reconciled", "sequence": 63, "through": "2014-01-05"}, "date": "2014-01-05", "id": "2014-01-05-player-birth-dates-calendar-ages-and-historical-retirement-audit", "kind": "technical", "season": 2013, "status": "closed", "summary": "Player age metadata and historical retirement research were reconciled."} -->
