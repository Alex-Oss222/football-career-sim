# Career records

Start with [Jacksonville's 2014 season](2014/README.md) and the [current season state](../state/05_Current_Season_State.md). Each year's folders hold the actual football records and explicitly identified current views. The [season structure guide](../docs/season_structure.md) defines the full layout and ownership rules.

## Following the year

From 2014 onward, the route is `01_Early_Offseason`, `02_Offseason_Training`, `03_Draft`, `04_Training_Camp_and_Preseason`, `05_Regular_Season`, `06_Postseason` and finally `07_Season_Review`. Draft and training work overlap on their actual dates. `00_Team_Operations` contains the roster, depth chart, staff, working player assessments, film, development, transactions and finances used throughout those phases.

Open `Calendar.md` for the month-by-month schedule and `Record.md` for the one-line dated account of completed events. Follow each record link to its owner. Trades stay in Trades, signings in Free_Agency, practice in the appropriate training report and games in their game outputs. There is no narrative ledger to maintain alongside those records.

The 2013 season retains its established domain paths. Its January and February 2014 playoff outputs still belong to the 2013 NFL season. Historical results, receipts and source evidence are preserved when paths change; the runtime resolves earlier references through the repository map.

## Plans, reports and player records

Each training phase has `staff_plan.md` and `training_report.md`. The plan says what the staff intends to teach and evaluate. The report describes the actual work, player and unit performance, corrections, retests and next coaching work. The matching [spring template](../foundation/templates/offseason_training/README.md) or [camp template](../foundation/templates/training_camp_and_preseason/README.md) controls its presentation. Preparation never establishes attendance, improvement, a role or medical clearance.

Games use the complete [regular-season output template](../foundation/templates/regular_season_output_template.md) or [preseason output template](../foundation/templates/preseason_output_template.md). Preseason keeps its authorized bulk workflow and separate statistics. A bye output records the week's work without a game. Only played playoff rounds acquire results.

A player's opening assessment and dated updates remain together through the whole year. A separate final assessment is written with the season review. Earlier statistical rows remain intact, and a departed player's evidence remains history. The [career player index](player_profiles/README.md) connects seasons. Individual development plans and film records supply proposed work and actual distribution receipts without becoming duplicate assessment collections.

[Coaching profiles](coaching_profiles/README.md) retain Stone's and the assistants' development from their actual work. [Shared finances](finances/README.md) retain contract obligations and accounting across seasons. Neither set is rewritten into a second chronological account.

## Starting and handing off a career

The pre-hire search is a limited exception to full initialization: [the 2013 search record](2013/offseason/hiring_search.md) owns frozen criteria, authorized instructions, applications, offers and the accepted job. Its [supporting brief](2013/offseason/hiring_search_brief/README.md) owns the user's prepared material. No player transaction, team practice or game is authorized merely because the search has begun.

After acceptance, reconcile the governing documents, roster, staff, contract, rules, calendar and readiness. The user then initializes the active career. A prepared future season or historical calendar never performs that transition on its own.

At the end of a season, player and coach exit reviews come last in the year’s football route. The season-review handoff carries the reviewed roster, medical instructions, contracts, staff, draft assets and unfinished development into the next year; fresh season statistics and awards start empty. `scripts/season_handoff.py` stages that transfer after the required reviews. A new folder is preparation, not proof that its events have happened.

## Maintaining the records

The [update workflow](../docs/update_workflow.md) and [repository map](../docs/repository_map.json) determine which owners and current views change together. Write the actual result first, update only affected views, regenerate the annual record and other derived pages, and validate the complete change. Do not create a new document for every practice, conversation, transaction summary or accounting scenario.

Public game receipts own statistics. Box scores, standings and season totals are rendered from those receipts rather than hand-added. Missing evidence remains a gap. The [game-readiness checks](../state/game_readiness.md) still control whether either game path may run; a populated calendar or green document check supplies no game authorization.
