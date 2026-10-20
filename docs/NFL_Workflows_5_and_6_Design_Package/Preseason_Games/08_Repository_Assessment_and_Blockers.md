# Preseason Games: repository assessment and implementation blockers

## What already works

- The 2014 career has four distinct completed preseason games under `career/2014/Training_Camp_and_Preseason/Preseason_Games/Game_01` through `Game_04`, each with a dated public `output.md`, stored game inputs, unique game result, rotations and individual medical consequences.
- `runtime/preseason.py` separates exhibition roster, opponent lineup, participation and game inputs from regular-season accounting. `runtime/rotation.py` already captures the important truth that a planned snap ceiling does not instantaneously terminate a possession.
- The private production resolver and `scripts/close_preseason_game.py` provide one-time closure and consequential Jacksonville injury pause. The preseason stat renderer and `tests/test_preseason_game.py`, `tests/test_preseason_rotation.py` cover several invariants.
- `foundation/templates/preseason_output_template.md` already insists on the game narrative, then real football analysis, then complete box score, with a cross-game coaching review inside the final game output. Do not throw this work away.
- Stone's play-calling, roster/role, medical authority and private actor independence are recorded in `state/current_job.json` and active canon. The dated owner/index system and event-insert design already state individual-outcome rules.

## Must change behind the scenes

1. **Decision-registry routing:** `runtime.decisions.folder('preseason_game', year)` currently uses the shared `training_camp_and_preseason` parent; it does **not** accept a game number or resolve `Game_0N`. Add a per-game router using `SeasonPaths.preseason_folder(n)` while retaining unrelated camp/final-cut routes.
2. **New-season page ownership:** Current code writes to `Game_0N/output.md`. The 3-page redesign calls for `Preseason_Game_Report.md`. Routing must choose the established 2014 legacy owner for frozen old games, and a *single* new owner for future games. Both should not be generated as rival full reports.
3. **Coach-plan compiler:** Add a football-language input accepting ordinary headings for one game, resolving personnel, named plays/defensive structures and rotation choices to existing game input formats. Never ask the user for JSON, numeric IDs or software concepts.
4. **Preseason-specific decision gate:** The present queue's `practice_plan` class has no input/close blocker; add season/game events and E2 dependencies. Do not let an unrelated hiring or contract response hold a playable game absent a real dependency.
5. **2015 rules and release:** Add a verified 2015 rules/calendar release, 15-yard PAT rule, 2015 fixture set and new-season opponent/strength/medical inputs before making the new four games playable. A 2014 release is not proof.
6. **2015 cutdown link:** The first reduction to 75 must be executed *before* the final preseason game; the fourth game's roster may differ from the third's. The final 53 comes after the fourth game, not before it.
7. **Sourced coaching review:** Use source-limited play observation, role/snap exposure and cautious attribution. A writer cannot invent film details, coaches' conversations, special-teams fault, progress grades or power causal connections the resolution never models.
8. **Event ownership:** Consequential injuries, player contracts, trades and any rejected proposals need separate dated owners. The game report and active index link these without duplicating a medical or transactional narrative.
9. **Immutable issued history:** New important information reissues the pregame brief under the standard materiality rule while preserving the original edition. A post-freeze answer cannot silently modify the frozen plan.
10. **Preserved completed work:** No rewritten 2014 scores, preseason player statistics, grades, career record, two-point rules, standings or draft results. Regressions must compare original pages and game-result bytes.

## Blocker classification

| Category | Status and resolution required |
|---|---|
| Design and file routes | Specified; choose one report owner at implementation time. |
| 2011 CBA / 2015 historical dates | Sufficient to design; per-season rule loader and publication gates not shown implemented. |
| 2014 completed precedent | Available and stable; never rerun it. |
| 2015 staff, roster, medical and player assessments | **Unavailable** until the 2014 season and the 2015 offseason genuinely occur. |
| 2015 preseason opponent rosters | **Unavailable** as of Oct 5, 2014; later sourced build required. |
| 2015 game release / 15-yard PAT behavior | **Unverified and not demonstrated implemented**; must pass season-specific tests. |
| Event router to this phase | Event-insert design exists; a functional full connection to preseason phase not demonstrated. |

No code or GitHub contents were modified for this design. Proposed tests have not been run in the repository.
