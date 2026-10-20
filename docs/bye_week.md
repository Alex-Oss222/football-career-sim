# Bye Week: three-page implementation and football-realism specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 5 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/bye_week/](../foundation/templates/bye_week/) and the worked example is [docs/examples/week_11_bye_illustration.md](examples/week_11_bye_illustration.md). No game, practice, medical decision, transaction or career date is advanced by these templates. Corrected October 20, 2026 after the process check and the user's answers: the other clubs' Week 11 games close while Stone's bye answers are open, and one reissue rule governs every brief.

## 1. Actual repository findings

- `docs/rebuild_plan.md` prescribes, and `runtime/decisions.py` registers, `Bye Week Review → My Adjustments → Bye Week Report`, marked **not implemented** in the registry. The first implemented decision type is `game_week`.
- `career/2014/Regular_Season/Games/Week_11/README.md` currently describes a bye; it has no three-page workflow.
- `career/2013/regular_season/week_09_bye/output.md` is a historical, already closed one-page event. Useful subject matter: first-half review, practice, self-scout, personnel and next-game implications. It must not be rewritten without explicit permission.
- `scripts/open_game_week.py` explicitly **does not** open ordinary Game Plan and inactive items for a bye. That is correct for those game-specific items. Do not reverse it.
- `scripts/build_week_inputs.py` can build the other teams' Week 11 games without a Jacksonville call sheet. That does not itself close Stone's new `My Adjustments` decision or verify that a bye report exists.
- `docs/career_layer.md` currently states that event blocks may not name a Jacksonville bye. That rule must be extended with a distinct **bye-close** event category, not weakened to allow `week_inputs` or `call_sheet_part` decisions for a nonexistent Jacksonville game.
- `docs/update_workflow.md` currently assigns the bye to that week's `output.md`: actual practice, recovery, self-scout and decisions, no game receipt. The new Bye Week Report should take over this event ownership cleanly from 2014 onward, while preserving old close records.

## 2. Scope and timing

The 2014 Jaguars' published schedule: Week 10, Sunday November 9, designated-home Dallas game at Wembley Stadium; Week 11, bye: no Jacksonville game; the career calendar dates the bye Sunday, November 16, and the league's other Week 11 games run November 13 to 17; Week 12, November 23 at Indianapolis. Only the *dates and fixtures* can be populated before Week 10 finishes. The simulated win-loss record, injuries, roster, Week 10 game issues and NFL Week 11 results cannot be guessed from the actual historical Jaguars season. Use branch records at the actual issue date.

A bye week does **not** include a Jacksonville game, frozen game-day call sheet, inactive decision, snap ledger, game box score, weekly player performance, or pre/postgame media event by default. The other 2014 games continue separately. The team's record remains the same through the bye, even if its division or playoff position changes when other teams play.

## 3. Page ownership and sequence

### Page A: Bye_Week_Review.md, staff-authored

The coaching staff supplies a dated, sourced **self-scout** through the last *closed* Jacksonville game. It lists actual evidence, reasonable football interpretation, contradictory evidence, what is unknown, player/medical constraints and realistic decisions needing Stone's input. The staff can disagree. No fabricated coverage breakdown, route error, practice grade, opponent tendency or improvement. A real current-game hypothesis can be given as an open question.

Issue after the Week 10 game closes and before work that needs Stone's approval. Archive issued copies immutable. Reissue under the one rule for every brief in the [event inserts design](event_inserts.md) (section A, item 6): a new event needing his answer, a dated finding that materially changes a pending choice (a medical evaluation, for example), or an answer due before the next scheduled issue. Preserve what Stone had seen earlier. Re-issuing a brief alone changes no career events.

### Page B: My_Adjustments.md, head coach-authored

Stone sets priorities and decisions for offense, defense, special teams, lawful work, eligible roles and any durable coaching changes. It must distinguish *keep*, *correct*, *test*, *remove* and *defer*. Saying **No change** is a full legal answer; do not force a correction merely because it's the bye. An unrecorded new promise, different play-caller, medical clearance or acquisition is not a valid assumption.

The text is easy for a human to fill. A parser/compiler extracts **explicit** choices, checks players and the active playbook, and attaches stable source/provenance. Preserve original text as the authoritative expression of intent. A conditional medical alternative remains conditional until the medical staff acts. Unresolved required decisions stop the bye's final closure; they do not silently default to approval.

### Page C: Bye_Week_Report.md, staff-authored after the work

The report records what **actually occurred**: film findings, permitted practice and meeting participation, meaningful observations, dates off, medical information as communicated, exactly which Stone adjustments were installed, what remains a test, and useful league context. A planned action is not a completed action. A three-paragraph report can be sufficient if not much happened. No compulsory media Q&A; preserve only an actual documented session if one occurred.

Unlike game week, the result page has **no box-score renderer** for Jacksonville. A league page may list other clubs' games and their independently drawn results. The bye report owns *coaching activity*, not a second copy of standings, roster, medical history or transactions.

## 4. The hard era constraints

Neither CBA rule below is yet in the library, and the Week 5 check of the padded-practice rule rests on one secondary source. Step 5 adds a two-pass library entry for each, and stores each practice's date and equipment and each player day off as data, before any check counts them.

- **Player days off (2011 CBA, Article 24 Section 2):** At least four consecutive player days off including Saturday and Sunday, except where a club plays Thursday after the bye and the correct Wednesday-Saturday exception applies. Medically necessary treatment during the break may be required by the medical staff. No required player practice, meeting or disguised team activity during their mandated four-day rest. Staff can study film separately.
- **Padded practice (2011 CBA, Article 24 Section 1):** Total 14 regular-season padded practices, 11 allocated to the first eleven weeks and 3 to the final six. Two in one week is allowed only in one week of the first eleven. Helmets plus shoulder pads count. The actual permitted remaining number must be calculated from *closed* practice records; don't assume an available pad day merely because it is the bye.
- **Medical:** Recovery time alone does not prove a player was cleared or improved. Only a dated authorized medical determination alters the medical record or permitted participation. The staff can adapt nonmedical eligible roles separately.
- **Authority:** Stone controls coaching priorities, practices within lawful limits and his authorized on-field/depth decisions. Caldwell controls transactions and contracts. Coordinators prepare and recommend in assigned areas. Do not change who calls plays through a passing remark on a report.
- **No bye bonus:** Time off cannot automatically add arbitrary player ratings, improve team strength, eliminate fatigue or create a guaranteed win after the bye. If a future tactical model measures learning or fatigue, it must have independent calibrated mechanisms and prior-to-result input commitments, not keyword-triggered prose multipliers.

Sources (for research and internal design, **not** a claim these real events happened in Stone's branch):

- 2014 Jaguars published schedule: https://www.jaguars.com/news/2014-jaguars-schedule-released-12908209
- Original 2011 collective bargaining agreement, Article 24: https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf
- 2014 Colts midseason self-scout: https://www.colts.com/news/bye-week-allows-chuck-pagano-colts-staff-to-self-scout-before-stretch-r-14208922
- 2013 Raiders coach on self-scout situations: https://www.raiders.com/news/coach-allen-discusses-bye-week-defense-11539929
- 2014 Chiefs coach describing bye timing and film work: https://www.chiefs.com/news/reid-speaks-for-first-time-since-bye-13989755

## 5. Execution pathway to implement, not available as-is

1. Use the registry's existing `bye_week` decision (Bye Week Review, My Adjustments, Bye Week Report) and add a `bye_close` block kind, separate from `week_inputs`/`week_close`/`call_sheet_part`. Scope it only to a scheduled controlled-team bye; event and decision queue records use season, week and one authoritative owner. Do not open game-plan or inactives decisions for the bye.
2. Add a `render_bye_week.py`-style builder with one source owner per page, as with regular game weeks. Load the prior Week 10 game, season stats, current roster, medical record, staff roster, historical league calendar and playable practice budget. Issue the dated brief and blank form; **do not run** a league week when generating them.
3. Add `check_bye_adjustments.py` and a deterministic compiler/validator: exact headings, legal names and concepts, no unauthorized medical or Caldwell transaction, legal rest dates, valid practice budget, no future knowledge, no duplicate implemented decisions. Output specific football-language errors, not silent auto-fills. No need to force all phases to change.
4. Add `apply_bye_adjustments.py` (or equivalent) to store an immutable approved decision record and queue resolution; apply *only* immediate authorized assignments or durable changes. Proposed tests and Week 12 ideas stay proposals. The next week's Game Plan must explicitly choose what goes onto its actual executable sheet.
5. Make the bye's closure process independently verify that Stone's required bye adjustments are settled. This must not manufacture a Jacksonville TeamInput, game receipt, result or box score. The league's other Week 11 games close while Stone's bye answers are open: his answers hold only the bye's own close and Jacksonville's next game (the user's answer of October 20, 2026). The workflow may not record the bye **as complete** before Stone has answered and lawful scheduled work is resolved.
6. Write the result *after* actual dated practices, staff study and medical actions. Update roster, medical and depth records only for genuine changed facts. Close the bye event on its actual date. Regenerate dependent views from their canonical owners, no manual shadow standings/league-score copies.
7. Make Week 12's game-plan opening independent of the bye report's future guesses. Preserve the bye's approved durable instructions, but do not auto-carry any opponent-specific unknown, future inactives, or a hypothesized play's effectiveness.
8. Test for idempotence, old-brief preservation, unknown-source handling, activity chronology and no accidental changed NFL results.

## 6. Concrete failure messages

- `You scheduled required player film work on Saturday, November 15, inside the four-day player break. Move it before the break or make it staff-only.`
- `This practice requests pads but the earlier recorded practices have used the season's available first-eleven-week allocation. Choose helmets-only work or no field period.`
- `Your role change names a player who has not been medically cleared for the assignment. Record a conditional option or wait for the staff's medical determination.`
- `You marked a new coverage adjustment 'installed' but no legal installed or practiced call has been identified. Mark it 'study/test only' or settle the additional coaching and install decision.`
- `The report describes improved quarterback recognition, but no permitted practice observation or other new evidence is recorded. State the work done and leave improvement unassessed.`
- `Your Week 11 league summary uses real historical Jaguars or Colts results instead of this career's simulated completed game record. Rebuild the summary from the closed league slate.`

## 7. Acceptance tests

1. Current Week 11 fixture is recognized as a bye. Week 10 Dallas at Wembley and Week 12 Indianapolis are anchored to the published schedule, but **the results and roster are never pre-filled from real history**.
2. All three reader-facing bye pages exist within `career/2014/Regular_Season/Games/Week_11/` after implementation, without replacing earlier closed 2013 pages.
3. Opening/reopening a page does not advance time or play a game. An unanswered required Stone decision blocks completed bye closure, not the background clubs' football by accident.
4. **No Jacksonville score or box score is produced**, no phantom W-L-T change, and no Jacksonville game-specific inactive or call sheet is demanded.
5. `No change` or an approved standing instruction fully answers a legitimately unchanged area. No artificial change quota, practice-rep quota or roster grading exercise.
6. The four consecutive player days off and legal practice limits are validated against the season's era and recorded work. If work is canceled, report cancellation rather than a fabricated performance result.
7. Medical status changes only by dated medical staff actions, player roles only by proper authority, roster/cap decisions only by Caldwell's actual separate actions.
8. No automatic skill growth, fatigue erasure or tactical advantage from rest/verbosity. The same substantive decision yields the same compiled choices no matter how eloquently it was written.
9. Every post-bye statement has the right evidence date; a Week 11 game elsewhere cannot influence Monday's review, and a Week 12 future result cannot appear anywhere.
10. The report may be concise in a quiet bye. It never repeats the whole 53-man roster or fabricates press dialogue and self-scout discoveries.
11. The Week 12 Game Week Briefing reads the actual new record and medical instructions. It does not claim a proposed bye-week concept was successfully installed when no practice occurred.
12. No 2013 Week 9 report text, Week 5 historical result, Week 6 issued briefing or current head-coach decision is rewritten by installing the bye template.
