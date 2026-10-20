# Game Week v2: research, contract and implementation plan

**Status:** Uploaded by the user on October 20, 2026 and adopted for the build (see the [rebuild plan](rebuild_plan.md), step 4b). Phases A to C are built under the rebuild rules; Phase D changes the game engine and waits for the user's decision. Corrected October 20, 2026 after the process check and the user's rulings: any call in the active playbook may be named, the opening list is ideas in his order of preference, and only a decision that holds the game blocks the plan. Built the same day: the install and practice gates are removed from the check and the apply (section 4, item 5), and the Game Week Briefing lists only the standing instructions that apply to the game. The templates it describes are in [foundation/templates/game_week/](../foundation/templates/game_week/), and the worked example is [docs/examples/week_06_illustration.md](examples/week_06_illustration.md).

**Applies:** Every played regular-season game and every played postseason game. Byes belong to their separate workflow. Each game has exactly three decision pages in the game's folder. The same folder may also hold the week's `My_Responses.md` and links to separate event results ([event inserts](event_inserts.md)); those answer the week's other business and are not game pages.

1. `Game_Week_Briefing.md`: what the staff can responsibly tell the head coach as of a particular date.
2. `Game_Plan.md`: Alex Stone's decisions, expressed in football language.
3. `Game_Report.md`: what the game actually produced, written as an intelligible football account and complete official statbook.

## 1. Findings from the actual repository

- Week 6 briefing and plan are currently in `career/2014/Regular_Season/Games/Week_06/`. They were made by the PR #251 workflow. The Game Report is still prospective because the game has not been played.
- Week 5's 142-kilobyte `output.md` contains useful causal/game evidence, quarter narrative and rich gamebook accounting, but buries its main story beneath repeated stats, an entire 53-man availability inventory, technical notes and a large question-source bibliography. Its old `Week_05_Pittsburgh.md` packet is a useful example of football reasoning but an unreasonable weekly data-entry burden.
- Current `Game_Plan.md` forces the head coach to deal with `Opener`, `Returns`, `Family`, `Type`, `Motion`, `Tags`, exact table columns and defense row classification. These are compiler fields, not the decisions a head coach primarily needs to communicate.
- `runtime/game_plan.py` currently parses those exact fields. Merely replacing the Markdown page WILL BREAK the validator and apply pipeline. Build a new adapter/parser first; do not allow a 'friendly template' that silently fails to drive the game.
- `runtime/play_detail.py::canonical_call_sheet()` explicitly states the current possession model does not use call-level matchup effects. `_menu_select()` chooses compatible labels in a separate stream and may fall back to generic play descriptions. Do not report a retrospective snap label as proof of the tactical reason a coach called it.
- `runtime/game_runner.py::_team_packet()` drops the defensive call sheet from the outcome packet. The defensive sheet currently records information rather than resolving matchups.
- Real active decision blocks exist for fourth down, two-point attempts and kickoffs. Preserve their executable meaning and evaluate them at the actual situation.
- `scripts/render_box_score.py` fills a two-marker statistical block from the closed receipt. Move it to the end of the report only alongside corresponding validation changes.
- The three-page builder and plan checker currently find the controlled game through regular-season fixtures (`scripts/render_game_week.py` and `scripts/check_game_plan.py`). Although `runtime/decisions.py` has postseason folder routing and `runtime/week_inputs.py` has postseason schedule support, the full three-page pipeline needs explicit playoff work. Do not describe the three-page playoff route as tested or ready until it is.
- `docs/game_output_workflow.md` and `docs/head_coach_media_method.md` already include strong anti-generic writing guidance. Changing more adjectives alone cannot fix mechanical plan inputs or missing causal game evidence. Reconcile and replace conflicting old requirements rather than stacking checklists.

## 2. Actual NFL grounding and era discipline

- 2011 coverage of Kyle Shanahan's NFL play-calling describes weekly staff collaboration, situational call lists and opening scripts. A separate 2012 account assigns assistants first/second downs, third downs and empty sets, red zone, short yardage, protection and film work. This supports a head coach choosing matchups and priorities while assistants build detailed call sheets, rather than the head coach filling a software table of `Returns` positions.
  - https://www.washingtonpost.com/sports/redskins/nfl-play-calling-is-an-arduous-collective-process/2011/11/11/gIQAchJEGN_story.html
  - https://www.washingtonexaminer.com/sports/137554/redskins-email-report-crafting-a-game-plan/
- Jacksonville's actual September 2014 reports show seven game-day inactives announced about 90 minutes before kickoff. For the 2014 career with a full 53-man roster, that leaves a maximum 46 dressed, and the system must verify legal position-group coverage.
  - https://www.jaguars.com/news/gameday-inactives-wr-marqise-lee-inactive-wr-cecil-shorts-iii-to-play-13813022
- Archived 2014 NFL injury reports use that era's `Probable`, `Questionable`, `Doubtful` and `Out` game statuses, alongside limited/full/no practice participation. Do not use rules introduced years later or infer clearance from a projected return date.
  - https://www.nfl.com/injuries/league/2014/reg17
- Contemporaneous September 2014 Raiders coach media show short answers, direct challenges and genuine follow-ups, without a preassigned quota of technical explanations. Do not copy this session into Stone's dialogue.
  - https://www.patriots.com/news/raiders-postgame-quotes-9-21-2014-208466
- 2012 NFL rules provided modified-sudden-death overtime, including a first-possession touchdown exception. In 2014 postseason games could not end tied; do not import subsequent league rule changes.
  - https://www.nfl.com/news/nfl-overtime-rules-09000d5d827ee2c0
- Use the recorded 2011 CBA padded-practice restrictions for 2014; do not treat a practice proposal as a completed practice or a clearance. The career's own documented practice violations in earlier closed weeks are historical, not permission to repeat them.

## 3. Ownership and evidence boundaries

| Question | Owner | What reaches the report |
|---|---|---|
| Final score, play, field position and stats | Closed game result and game book | Only recorded numbers/events; box score generated, never rewritten |
| Head coach's opening plan, eligible calls, depth/roles and standing policies | User's accepted Game Plan and standing instructions | Named football choices; never modified after the game to rationalize the result |
| Opponent scouting | Only dated game books, rosters, public transactions and genuinely charted information | Verified findings and clearly labeled tests, not fake coverage/pressure percentages |
| Medical restriction, game clearance and diagnosis | Team medical staff | Exact communicated status; projection is not clearance |
| Trades, signings, waivers and contracts | GM / front office | Actual result or coach's recommendation; not an invented completed move |
| Pregame conference | Pre-kickoff dated public record | Frozen before the game; do not backfill with result knowledge |
| Postgame conference | Actual event and established Stone views | Distinctive credible dialogue; no new commitment invented for Stone |
| An alleged coverage, missed block, audible or causal tactical answer | Pre-snap call/execution record, charted evidence, or actual staff film finding | State only the level of cause the evidence supports |
| Public/community narrative | Recorded consequential plays, score and public events | A readable story of a particular game, without fabricated fans or journalist quotes |

## 4. Page compiler contract

The user-facing `Game_Plan.md` must be editable in place, uploadable with exactly the same headings, and accepted in chat. It should **not** expose internal `Opener`, `Returns`, `Family`, `Type`, `Tags`, positional database keys, or defensive parser fields. Instead, adapt natural-football entries to the existing executable schema.

The compiler must:

1. Preserve exact date, briefing revision, user-authored original text and decision authority.
2. Resolve `Carry Week NN` only from that week's immutable applied plan and carry *eligible* calls, not game-specific use cases that no longer apply. If an inherited call is unavailable because of personnel, playbook or medical status, fail with a football explanation.
3. Resolve `No change` and `None` differently; a blank is **unanswered**, not accepted as a negative or carry-forward.
4. Validate active players, seven inactives when 53 are active, legal game-day units, role eligibility and dependent medical exams.
5. Validate calls and variations against the active book. Any call in the active book may be named for any situation Stone writes, whether or not that week's practice covered it, an earlier sheet carried it or the staff carded it (the user's ruling of October 20, 2026: "We can call anything from the playbook. It's accessible."). No call waits on an install line or a practice record, on offense or defense; the practice section of the page is information for the staff (what they will practice, who takes a limited player's work), never a condition. What stays: the active-book check (the playbook lock, so a call from a book whose range starts after the season is refused); the exact-name rule (a shorter name is asked about with "did you mean", and a new call whose words a longer call's name holds is written `New call: <its name>`); the roster, medical, role and inactives checks; and every frozen and paused refusal. A special play of the book that the call-family map gives no carrier or receiver for is set with both unspecified, so the play-by-play never names it on a snap until the map does. Do not hallucinate an unmentioned formation, tag, protection, or route in order to make a row legal.
5a. The opening list is **Opening ideas**: the calls Stone wants early, in his order of preference, with any call in the book still available. Today the order only fills the call sheet's opening slots, which name the early calls in the play-by-play and do not change results (the engine is untouched). The plan-level version (Phase D, awaiting the user's timing) will use the list by situation. A page written before October 20, 2026 with the old label "Opening calls, in order" reads the same.
6. Record *why* the user chose a call as author-intent metadata, with a provenance link and when-known date. Keep that separate from game outcome.
7. Produce the existing machine-readable `call_sheet.json` and decision policy blocks deterministically, with a reversible source mapping from every emitted call to the exact user text or inherited frozen item.
8. Refuse plan freeze while a briefing is stale, a medical dependency remains unresolved, or a head-coach decision that holds this game (one due before kickoff) remains open. Business that does not hold the game, such as an open trade call or an assistant's interview request, never blocks the plan. Reissue revised briefing when new facts arrive, preserving the earlier page and its date.
9. Hash the applied plan and compiled sheet. Treat a later revision as a new explicit apply event. Open/read-only pages never advance the game clock.
10. Store technical records in their existing data owners. Coach-facing Markdown is football, not diagnostics.

**Example validation:** `Red zone: 'Flood Sail' is not in the active playbook. Choose a call from the 2014 book.`

**Another:** `Your inactives are not final. Brynden Trawick's October 7 reassessment and Jordan Poyer's October 9 projected return have not been reconciled. Your football plan is complete, but it cannot be set as the final 46 yet.` (The dates and record state must be rechecked when run.)

## 5. Game-outcome realism contract

**Present limitation:** The offensive call name associated with a played snap may be a compatible label assigned after a separately resolved event. The defensive response is not an outcome input. Therefore the Game Report cannot truthfully write that a specific coverage caused a concept to succeed solely because the play label exists.

**Future tactical upgrade, separate from page redesign:**

1. At each snap, resolve legal personnel and relevant game situation.
2. Establish a defensible opposing presentation and available information, respecting what the controlled coach or opponent could know.
3. Choose an eligible offensive call and prepared defensive response *before* drawing the snap, based on football decision rules and coaching authority, not narrative words.
4. Resolve outcome with modest, calibrated, testable effects for personnel, protection, run surface, coverage, pressure and in-game adjustments. A correctly designed plan can still fail; a bad plan can still win.
5. Record choice, trigger, personnel, defensive presentation, pre-snap context, outcome, and which components were actually observed. Do not fabricate precise technique failures the model never established.
6. Only then allow the writer to say: `We used [call] because [recorded reason/presentation]`; distinguish planned intent, observed call and inferred postgame explanation.

No mechanism may change the game because the author writes confidently, uses a longer explanation or names Stone as protagonist. Run protagonist-swap and paraphrase-invariance tests.

## 6. Game Report editorial contract

- The main game section must read as a football account. Tell the action in order and use **particular** sequences, not one mechanical paragraph per drive. Quiet quarters may be short. Avoid declaring fake emotional turning points.
- Every named play with a supposed reason must pass: `Was that call actually chosen pre-snap? Was its reason established then? Does the evidence contain the opponent look?` If not, restrict the claim to what is recorded.
- A story may report `Jones-Drew gained 15 on a third-and-16 screen`, and separately note the pregame plan permitted the screen against a credible rush. It may **not** claim the defense rushed six or the coach read a linebacker blitz without that evidence.
- A coach's error is specific if recorded. Example: Week 5's choice was made before third down and stayed a field goal despite the conversion picture becoming fourth-and-1 at the 2. The new standing fourth-down policy must operate on the actual fourth-down picture.
- Put the complete generated gamebook, with scoring summary, team stats, player stats, penalties, drives and snaps, at the very end under `Full game statistics`. This keeps full statistical integrity without interrupting the story and media with hundreds of table lines. Update validation for this change.
- Do not force equal prose length across offense, defense, special teams or player discussions. No word quotas. Full statistics are preserved, but major numbers should not be repeated across the lead, each quarter, review and press questions.
- Pregame press is written and frozen from pregame knowledge. Postgame press is written from what was known immediately after the game. No forced press-conference question count, obligatory confessions or Q&A about every unit.
- If there was no documented media session, say so. If the user has not supplied authorization for a new public position, do not manufacture it.
- Section 6 is ONLY an after-action report: new injuries/holds/clearances, actual outstanding players, material role consequences and new decisions. No 53-man snapshot, unused bench biographies, status grades or implementation notes.
- No research-source catalogue, internal checks, file paths, source hashes, generation versions or program jargon inside the reader-facing story. Keep provenance in technical owners or a concise source link at the report's end.
- The score, possession math, overtime, standings, first downs, passing and rushing statistics must reconcile with the official game receipt. An eloquent but false play is a failure.

## 7. Postseason extension

Use the same three pages with `Game Week Briefing -> Game Plan -> Game Report`. No game pages on a bye. The briefing adds only material playoff facts: bracket position and seed, elimination consequences, confirmed opponent, venue, available rest, prior meeting evidence available by that date, and the correct overtime/roster context. Do not invent an opponent until the preceding bracket results establish it, or assume a next game after a loss. The regular-season carry-forward plan remains available subject to roster, medical and era legality.

Extend `scripts/render_game_week.py` and `scripts/check_game_plan.py` to use postseason fixtures and `week_pages(..., postseason=True)` with correct folder/data routing. Exercise full check, apply, report and stat-render flows in a postseason fixture test. The core `runtime/week_inputs.py` already routes playoff weeks to a separately built schedule, but this fact alone does not prove the user-facing page workflow is complete.

## 8. Non-negotiable acceptance tests

1. Three, and only three, decision pages per played game; the week's My Responses page and separate event results are not game pages. Existing roster and medical pages remain their own source owners.
2. `Game_Plan.md` contains no required `Opener`, `Returns`, `Family`, `Type`, internal menu key or artificial frequency number.
3. A valid plan compiles to a legal `call_sheet.json`; an invalid one fails with a specific football reason, never a silently filled fake.
4. Rephrasing a coach's explanation without changing choices produces the same executable plan and outcome. Longer prose cannot act as a bonus.
5. No user silence creates an approved decision. Opening or re-reading a page advances no date or state.
6. Changes to an injury, transaction or opponent after a briefing create a new dated version, preserving the original.
7. A pregame statement never references the still-unplayed outcome. User-controlled commitments cannot be invented in dialogue.
8. Every game story moment matches actual play/clock/score/stat evidence. Claims of schematic cause require the extra, correct causal provenance.
9. One controlled team report uses the complete existing statistical renderer, with every generated number still reconciling. Full stats are last, not repeated in prose.
10. An uneventful personnel week has a terse after-action statement. No automatic roster inventory.
11. The same Game Plan/parser/validator works on a season game and a Wild Card, Divisional, Conference Championship or Super Bowl game, on established bracket matchups only.
12. Win or loss, the report explains the game to the same standard. There is no protagonist guarantee and no automatic `W`.
13. A reviewer can read the report *without* the numbers appendix and identify the deciding possessions, meaningful calls, authentic media and next football issue.
14. Frozen Weeks 1-5 stay unchanged unless the user explicitly requests a historical rewrite. A new layout does not rewrite old game outcomes or move the career date.

## 9. Repository change plan, in safe dependency order

**Phase A, presentation only:** Set the new Game Report layout in `foundation/templates/regular_season_output_template.md`, adjust `docs/game_output_workflow.md` and `docs/head_coach_media_method.md` to one consistent owner of prose guidance, and update `AGENTS.md` routing only as necessary. Modify report renderer/validation expectations for the statistical appendix, without touching existing results or receipts. Add an editorial acceptance fixture for a quiet game, a turnover-heavy game and a playoff game.

**Phase B, coach input:** Replace the printed briefing and Game Plan builders in `scripts/render_game_week.py`; implement the v2 natural-football parser and deterministic adapter in `runtime/game_plan.py`; update `scripts/check_game_plan.py`, `scripts/apply_game_plan.py` and related tests so readable choices actually drive the same executable paths. Migrate Week 6's blank form only after validating the adapter; preserve the existing issued October 5 briefing as the archived version rather than overwriting it.

**Phase C, postseason routing:** Add postseason test fixtures and explicit folder/schedule logic to briefing, parser, check and apply. Preserve round and seed information, game-day count, playoff overtime rules and the bracket's actual unknowns.

**Phase D, deeper engine realism (separate proposal):** Move call choices before snap outcomes, implement opposing presentation/response and modest matchup effects, and enrich the play record with causal provenance. Calibrate and regression-test. Do not silently apply this to the unplayed Week 6 without authorized runtime/version changes and full verification.

## 10. Which current repo records were reviewed

- `career/2014/Regular_Season/Games/Week_05/output.md`
- `career/2014/Regular_Season/Games/Week_05/Week_05_Pittsburgh.md`
- `career/2014/Regular_Season/Games/Week_06/Game_Week_Briefing.md`
- `career/2014/Regular_Season/Games/Week_06/Game_Plan.md`
- `career/playbook/alex_stone_2013_offensive_playbook_iteration_i.md`
- `career/Stone/Coaching_Profile.md`
- `docs/run_week.md`, `docs/game_output_workflow.md`, `docs/head_coach_media_method.md`
- `foundation/templates/regular_season_output_template.md`
- `scripts/render_game_week.py`, `scripts/check_game_plan.py`, `scripts/render_box_score.py`
- `runtime/game_plan.py`, `runtime/game_runner.py`, `runtime/play_detail.py`, `runtime/decisions.py`, `runtime/week_inputs.py`, `runtime/postseason.py`

