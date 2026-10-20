# Every Preseason Game: implementation and validation contract

**Status:** Proposed design, not implemented or executed. Repository inspected at `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on 2026-10-20. No source file, game, player status, decision queue or state has been changed by this package.

## A. Operating interpretation and governing authority

Each actual preseason game has **one three-page decision workflow**:

1. `Preseason_Game_Briefing.md`, issued by coordinators and specialists using facts knowable at its issue time.
2. `Preseason_Game_Plan.md`, Stone's owned and editable head-coach instruction, including the game roster/roles, offensive and defensive menus, specialist groups and rotation.
3. `Preseason_Game_Report.md`, published only after the verified game closes, with the game narrative, football review and complete generated box score. It is the game's sole canonical *reader-facing result* for the new workflow, not an alternate recap beside an `output.md` owning identical facts.

Use the registered `runtime.decisions.REGISTRY['preseason_game']` page names. **Instantiate four independent triplets**, not a single page for the entire preseason. Keep a separate final coaching synthesis when the last played game's report is closed, as the existing preseason-review method directs. It summarizes and links prior games; it is not a substitute for any game's report or off-field event result.

The game is an exhibition, but its participation, medical, signed-contract eligibility, transactions and CBA practice constraints are real. Stone controls his depth chart, legal playing assignments, game plans and game management, including taking or delegating calls. Under the existing 2014-10-05 appointment, Stone calls offense and defense, Crennel prepares/transmits defensive calls and Mike Westhoff operates special teams; Mike Tice runs offensive preparation. The arrangement persists until Stone changes it. Qualified medical staff control diagnosis and clearance; David Caldwell controls player contracts, trades, acquisitions and cuts. The annual active-playbook lock and the revised rebuild rule allowing any **active-book** play to be selected for the game apply. Do not impose a fake 'practiced-call required' gate.

Stone's head-coach agreement remains four years, fully guaranteed, accepted January 15, 2013; assistant budget/authorities remain as recorded. No preseason win changes the regular-season head-coach record. Standing two-point, kickoff and fourth-down policies carry if legally applicable, but 2015 playing-rule changes must be applied before freezing 2015 game inputs.

## B. Historical calendar and information gates

Historical 2015 Jacksonville fixtures, **not played in this career**:

| Game | Official opponent | Date, 2015 | Kickoff ET | Dated source |
|---|---|---|---|---|
| 1 | Pittsburgh at Jacksonville | Fri Aug 14 | 7:30 p.m. | Jaguars April 20 release |
| 2 | Jacksonville at New York Giants | Sat Aug 22 | 7:30 p.m. | Jaguars April 20 release |
| 3 | Detroit at Jacksonville | Fri Aug 28 | 8:00 p.m. | Jaguars April 9/20 releases |
| 4 | Jacksonville at Washington Redskins | Thu Sep 3 | 7:30 p.m. | Jaguars April 20 release |

The NFL/club announced opponents and weeks April 9; the exact four kickoff dates/times are verified by the April 20 Jacksonville release. Earlier in-world briefings may know only what had been announced by their cutoff. The 2015 extra-point rule adopted May 19 moves one-point kick line of scrimmage to the 15 (ordinary ~33-yard try), keeps two-point attempts at the 2, permits defensive two-point returns; it **cannot** silently be applied to 2014 game records. This is a game-release requirement, not just a prose note.

**Mandatory cutdown interaction:** 2015 reduction to 75 on Sept 1 before 4 p.m. ET occurs **before** preseason game 4 on Sept 3, and therefore gates the legal roster/input for game 4. Final 53 is Sept 5 before 4 p.m. ET, after game 4. The 2014 cutdown dates differ; never hardcode one season's deadlines for the next. A 2015 calendar is a historical scheduling reference, not a roster, opponent lineup, player performance or result oracle.

## C. Repository reality, reusable machinery and specific conflicts

| Existing file or subsystem | Verified function | Required adjustment |
|---|---|---|
| `runtime/decisions.py` | `preseason_game` triplet registered but `implemented=False`; its shared `training_camp_and_preseason` place currently resolves to the **parent training-camp/preseason folder, not a particular Game_0N folder** | **Fix route:** accept a preseason game number and use `SeasonPaths.preseason_folder(n)` for that triplet. Do not change the camp and cutdown routes by accident. Mark implemented **only after** tests prove the workflow. |
| `runtime/seasons.py`, `runtime/season_layout.py` | Year-specific `SeasonPaths.preseason_folder(n)`, `preseason_data(n)` and logical folder map | Use these exclusively. No new hardcoded `career/2015/...` in runtime/builders. |
| `runtime/preseason.py` | Builds a preseason package from controlled roster, frozen game depth, call sheet, opponent and rotation; distinct receipts | Keep as compiler and adapt to each year's rules/current source records. No illegal move or defaulting unknown roster to 2014. |
| `runtime/rotation.py` | Possession-boundary substitutions, optional unit blocks, default rotation and validation | Compile Stone's natural-language rotation into exact supported blocks; warn that a snap cap ends at a possession boundary. Do not silently invent missing player IDs or counts. |
| `scripts/close_preseason_game.py` | Runs one game through private service; supports E2 pause, builds receipt, `output.md` box score, stats; rejects repeat closure | **Blocker:** currently hardcoded to `Game_0N/output.md`; change result-page ownership for the new period, while keeping 2014 frozen `output.md` and receipts unchanged. Do not render two competing results. |
| `foundation/templates/preseason_output_template.md` | Prior eight-section complete report, narrative + coaching review in game section, stats and consolidated review | Do not erase this design. The new report owns its football substance; preserve the meaningful sections (media only if real), the game story and full final box score, and the postgame synthesis, without duplicating an eight-section page. This alignment must be accepted and regression-tested. |
| `tests/test_preseason_game.py`, `tests/test_preseason_rotation.py` | 2014 fixture, PAT trial, input, rotation, repeat-close, pause and cross-mode isolation tests | Add 2015-specific contract/rule/fixture/pagination checks, leave 2014 proofs unchanged. |
| `runtime/decision_queue.py` | Current blocking events cover weekly inputs/close and season stage/opening; `practice_plan` has no explicit game freeze block | Add `preseason_inputs` and `preseason_close` scoped by `(season, game)` and prerequisite-aware status. Integrate Stone plan + E2 pause; unrelated contract offers cannot hold a game unless they genuinely change a needed input. |
| `docs/event_inserts.md`, `runtime/decisions.EVENTS` | Shared event insertion and separate dated outcomes established by design | Reuse the shared insert system, immutable issue versions, response journal, event owner and one-event/one-result rules. Do not code a second insert router or a `Preseason_Event_Results.md` omnibus. |
| `docs/season_structure.md`, `runtime/events.py`, `scripts/render_annual_record.py` | Owner-based annual event index; records from event-owning Markdown pages | Each game gets one game event, each separately concluded trade/transaction etc. gets its own owner/event, and indexes link without copying accounts. |

**Current implementation blockers:** The known 2014 kernel, service and prepared 2014 game artifacts do not constitute a released 2015 game environment. No 2015 controlled lineup, 2015 opponent camp roster, medical status, completed camp or in-world game plan exists at the October 5, 2014 live checkpoint. 2015 must pass the existing season handoff and **separate game-readiness/release gates**. No template is permission to run a game with 2014 strength, roster, PAT or schedule data.

## D. Minimum source and state contract

`preseason_game` (one event) requires, before freeze:

- fixture: year, preseason ordinal, teams, local kickoff, venue, public-information gate, unique event ID;
- current employment/authority, current-year effective offensive and defensive books, in-force standing instructions;
- legal controlled roster, contracted/eligible list, reserve-list state, medical communication through the accepted date, Stone's actual depth/role choices;
- opponent dated roster and legitimate availability knowledge, with other-club historical personnel rails restricted to their actual permitted dates; no future injury, game or depth hindsight;
- prior camp/played-game evidence as-of report issuance, and *source-labeled* pregame scouting assumptions;
- current game-specific Stone decisions in editable natural headings, preserved with timestamp, and parsed freeze artifact for eligible players, offense/defense menu, specialist operation, roster, rotation and inactives;
- season-appropriate game rules, private service/release status and idempotency key.

Game close yields exactly one immutable game-result record and one readable `Preseason_Game_Report.md` with generated statistics, plus recorded pause answers and any actual new injuries/events at their owners. A dated coach assessment may be appended to opening player assessments only if sourced, not calculated from invented advancement. Play-by-play/boxscore evidence is not itself film; film analysis needs stored observational evidence or must be labeled unavailable.

**Event relationships:** `briefing_event_ids` -> `My_Responses` (only for real non-game events) -> `individual outcome at canonical owner`; game plan -> frozen game inputs -> game result -> single game report -> phase indexes/positions. The game and each off-field event have distinct identities. A medical incident has its existing medical owner, not a duplicate transaction write. A trade rejection has its own dated result, even if no roster change.

## E. Execution and atomicity

1. At the appropriate season/date, acquire two independent calendar checks, job authority, eligible controlled roster, medical holds and the latest actual coaching evidence; issue the first game-specific brief. The page is an as-of view, not an independent fact source.
2. If Stone's answer is missing, preserve the unanswered plan and block that game's input freeze. User text remains verbatim in its decision record; compiler creates structured input only after checking players, book names, legal dates, roles, no duplicate lineup/roster, use constraints and game-management rules.
3. Material new information before freeze creates a new issued brief while preserving prior issued text/date and exactly one current issue pointer. Nonmaterial FYI is allowed to wait until the next issue.
4. Freeze the accepted plan **once** and stamp all source revisions. Post-freeze off-field event changes do not mutate that package; a legitimate subsequent roster/health change must follow the existing pregame re-approval/invalidating rules. Never reroll with a convenient new input.
5. Confirm the independent season/game release, correct 2015 PAT/try treatment and permitted four-game slate. Run the one-game private-service event exactly once. On E2 consequential Jacksonville injury removal, stop for Stone's answer unless his valid prior instruction covers it; continue only from the existing frozen event.
6. On closure render game narrative from verifiable play-by-play, actual unit rotations, special teams, substitution and injuries; put the complete generated box score last. Cite/resolve off-field events at their own owners and link. Do not infer film or dialogues from statistical totals.
7. Update game-specific preseason records/position-battle cards and season current views from actual owners; do **not** change regular-season standings/awards/records, and do not create extra player grades. Save latest completed-game consolidated review without rewriting old individual game histories.
8. Run read-only validators and shadow checks before actual future integration commit. Keep the 2014 legacy path checks byte-stable and commit only under the authorized rebuild PR flow, not as part of this design package.

## F. Proposed regression tests (not executed)

### Calendar, eligibility and 2014 preservation

1. On Oct 5, 2014 no 2015 preseason report/lineup/score may be closed.
2. Game 1 2015 is Pittsburgh at Jacksonville on Aug 14 at 7:30 ET; source gate April 20 for precise timing.
3. Game 2 2015 is at New York Giants on Aug 22 at 7:30 ET.
4. Game 3 2015 is Detroit at Jacksonville on Aug 28 at 8 ET; national timing announced April 9.
5. Game 4 2015 is at Washington on Sep 3 at 7:30 ET, and Washington is the contemporary Redskins.
6. An Aug 2015 game does not include players removed at the Sep 1 reduction when freezing game 4.
7. The Sep 5 final-53 action does not retroactively change the Sep 3 game roster.
8. All completed 2014 preseason pages/receipts retain identical bytes and four distinct game IDs.
9. A 2014 game retains that year's PAT implementation, not the May 2015 permanent rule.
10. A 2015 kick try uses the 15-yard line, a two-point try the 2-yard line and can award defensive two points.
11. A 2015 game is refused if year-specific rule/release, private service or legal roster is missing.
12. A 2015 opponent camp roster cannot load a later Week 1 history as though known in August.

### Head-coach authority and plans

13. No signed Stone game plan means no game input freeze; opening a page never advances time.
14. Stone's defensive caller role and Crennel transmission continue without a repeated prompt.
15. Calling arrangement changes only on actual Stone instruction, not on program phase transition.
16. A referenced play from the active book is legal even if unpracticed, per latest rebuild rule.
17. A play from a later, not-yet-effective book is refused with the specific reason.
18. A player's name missing from the controlled roster is rejected and not replaced automatically.
19. A player unavailable medically cannot be inserted by the head coach as 'cleared'.
20. A legitimate voluntary football holdout by Stone is recorded without inventing medical status.
21. Frozen game timeouts, two-point/kickoff/fourth-down defaults persist unless expressly changed.
22. Game-day legal player availability honors completed earlier Caldwell transactions only.
23. A missing receiver or backup role with an available legal group produces a focused clarification, not an invented depth promotion.
24. A stated running-back touch or wideout target preference is not treated as guaranteed game distribution.

### Rotation, game result and causality

25. Whole-unit rotation blocks compile to valid offense, defense and special teams groups.
26. A snap ceiling ends at possession boundary, with actual snap overrun shown honestly.
27. A player may receive zero snaps if possessions never reach his block; do not write a failure evaluation.
28. Opposing team rotations are independent of which club is Stone's, under protagonist-swap test.
29. Rephrasing Stone's reason without changing actual inputs leaves the outcome packet identical.
30. A substituted quarterback is legally eligible and appears in actual team/drive snap records.
31. An E2 injury removal stops for Stone's uncovered consequential replacement.
32. A continuation reuses original event and private draw, not a new attempt or altered result.
33. A game cannot close twice or produce two conflicting final reports.
34. A scoring line without a matching scoring play/period fails output verification.
35. The full box score reconciles points, possession, attributed player stats and field position; unexplained residuals stay explicit.
36. Preseason game stats do not enter regular-season or playoff career totals.
37. An opponent's real 2015 score does not appear in the generated game outcome or as model evidence.
38. An output says 'tackle lost the rep' only with actual assignment or film evidence, not because a sack was charged at a slot.
39. A receiver with no targets is not classified as having run poor routes without observed route evidence.
40. A pressure producing a sack does not establish contain or correct peel responsibility without the relevant record.
41. Correct conversion/returner attribution uses actual 2015 rules, not old 2014 two-week PAT trial.
42. Game review discusses actual first/second/reserve combinations, not a score-only recap.

### Individual events, rendering and navigation

43. Three separate concluded trade talks in one preseason game window, including rejections, create three dated owner-result documents.
44. An unresolved trade inquiry creates no closed trade result and no player movement.
45. A single answered shared response does not merge distinct event conclusions.
46. A medical incident remains in the medical department and is linked, not copied under game output.
47. Midweek action requires a dated briefing revision when material; previous issued versions stay immutable.
48. A rejected trade is visible on its final date even if a later game has not been played.
49. One canonical game report and one full statbook are produced, rather than the old `output.md` and a competing new duplicate.
50. All new reader-facing output passes `runtime.clean_pages` checks: no internal IDs, paths, system labels, fabricated grades or executable code.
51. A phase-level preseason summary links four actual game reports and does not replace any of them.
52. Re-rendering a closed report changes neither game record nor incident outcome.
53. The annual event index points at the correct dated owner without duplicated event IDs.
54. Missing raw game evidence blocks factual claims but never prompts an invented number to fill a template.
55. All links are relative, path-mapped and do not point to a future season's created results; opening games 1–4 resolves four distinct `Game_0N` directories rather than the common parent.
56. Prior regression tests for 2014 preseason, postgame statistics, game packages and season isolation remain green.

## G. Acceptance sequence (future integration, not run here)

Use a **fixture-only 2015 dry run** first (no players/results), then a separately labeled synthetic season with fabricated test fixtures confined to `tests/`, then a no-write, all-four-game walkthrough on an isolated 2014 clone comparing closed output bytes to originals. Verify the first three games' roster counts, Sep 1 stage before game four, and final 53 after game four. Finally exercise three independent off-field concluded events, one rejected, and verify three dated outputs and no duplicate account. Actual 2015 simulation remains blocked until career events and private-season release allow it.
