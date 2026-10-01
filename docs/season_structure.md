# Season folders and record ownership

The [2014 season](../career/2014/README.md) supplies the layout for 2014 onward. Numbered folders put the football year in its usual order. The actual [Jacksonville calendar](../career/2014/Calendar.md) controls overlapping work: the draft falls during the spring program, and trades and signings can occur in several phases. The 2013 domain folders retain their historical paths.

## The season route

| Folder | Work kept here |
|---|---|
| `00_Team_Operations` | Current roster and depth chart, working player assessments, staff, individual development, film, medical history, trades, free agency and finances |
| `01_Early_Offseason` | Staff changes, scouting and preparation before the new league year |
| `02_Offseason_Training` | Phase One, Phase Two, rookie minicamp, OTAs and mandatory minicamp |
| `03_Draft` | Scouting board, pick ownership, selections and undrafted signings |
| `04_Training_Camp_and_Preseason` | Camp, preseason games, actual position battles and roster decisions |
| `05_Regular_Season` | Weekly games, schedule, standings, statistics, league results and awards |
| `06_Postseason` | Playoff games, separate postseason statistics, honours and Pro Bowl |
| `07_Season_Review` | Player and coach exit reviews, final player assessments and the handoff to the next season |

`League` holds the other clubs' permitted personnel records. `Supporting_Records` holds operational support. These are reference areas, not extra phases in the football year. Shared career finances remain in [career/finances](../career/finances/README.md); a season's finance pages link to those owners rather than copying balances.

## Calendar, annual record and event owners

`Calendar.md` is the team's schedule by month: league deadlines, filing and interview windows, program dates, reporting, camps, roster limits, games, byes and conditional postseason dates. The [2014 NFL calendar](../library/2014_nfl_calendar.md) owns the sourced league schedule and each club's dated program information. Jacksonville's calendar selects its applicable dates. A published date does not establish attendance or completion. Calendars contain no practice assessment, transaction narrative, cap snapshot, engine release or checkpoint bookkeeping.

`Record.md` is generated from the actual event owners. Each line gives the date, a plain description and a link to the full record. Several events on one date receive separate lines when they have different owners. A date window is used only when the record actually covers a block of work. Software changes do not become football events.

A trade is written in Trades, a signing in Free_Agency, a medical decision in the medical record, a practice in its phase report and a game in its game output. There is no central narrative ledger and no second editable account of the same event. Descriptive event metadata stays with the owner; the repository map carries compatibility aliases for old references without recreating their narratives. The current roster, depth chart and contract views summarize current facts and link their dated sources.

## Training reports and assessments

Each training phase has two substantive files: `staff_plan.md` for intended work and `training_report.md` for what happened. The report begins with the phase, location, dates, days completed and the football the staff addressed. Its assessment follows in the same report. Do not create another phase assessment document or one file per drill, meeting or practice correction.

Across the year, each player has two assessment records. The opening assessment in `00_Team_Operations/Team/Player_Cards` retains its starting baseline and adds dated updates from rookie camp through the postseason. The separate final assessment belongs in `07_Season_Review/Player_Assessments` after the season closes. Preserve former players' history and earlier yearly statistics. Individual development plans own proposed work; they are not a third set of player evaluations.

Open competitions live under `04_Training_Camp_and_Preseason/Position_Battles`, grouped by unit, then position, then the actual contested spot. The existing 2014 cards are WR1, WR3, left guard, the conditional right-guard alternative, Edge 1 and long snapper. A vacancy or a cross-training exercise does not create a battle. Compare the actual candidates and their relevant work, link the source reports, and retain the dated decision when a competition closes. The depth chart remains the owner of current assignments.

## Season continuity

A season folder identifies the NFL season being prepared and played. Its playoff outputs and statistical receipts stay with that season when games fall in the following January or February. The annual record likewise keeps postseason events with their NFL season; every displayed date remains the date on which the event occurred. A bye has a weekly output for practice, recovery and self-scout, but no invented game.

After Jacksonville's actual last game, finish player and coach exit reviews and reconcile roster control, medical instructions, staff, contracts, cap obligations, future picks and unfinished work. Use `scripts/season_handoff.py` to review and stage the next year. Team closeout and league-wide statistical or award closure are checked separately. A staged folder does not activate a season, renew a contract, clear an injury or authorize a game.

Staging copies eight provisional current records: roster, staff, working depth, contracts, contract status, cap worksheet, development roster profiles and staff decisions. It strips copied event-owner comments, rebases evidence links and refuses conflicting files or existing successor game receipts. Individual development plans, film delivery obligations, medical sources/history, coach development and draft ownership remain at their real owners, explicitly inventoried and reviewed in the existing handoff manifest. Changed inventory membership or reviewed evidence requires renewed review; no duplicate transition dossier is created.

From 2014 onward, staging queues each returning player's new opening assessment with the prior reviewed final and opening card as sources. It does not generate new judgments or copy old opening grades into a newly named card. The new opening is authored and reviewed, inherits earlier yearly statistics, and links the actual final. Departures remain prior-year history; new arrivals receive entry assessments from their available evidence. Final assessments and actual exit interviews must be complete and reviewed before staging.

`python scripts/season_handoff.py check-opening YEAR` checks the authored cards, inherited statistics, current source hashes and seven opening reconciliations without writing. `review-opening YEAR` runs that validation and records its acceptance in the existing opening and prior handoff manifests; it never activates the season. The later authorized administrative event changes live ownership and the clock. Repository validation rejects an active successor whose opening review was never accepted or whose accepted manifest changed. Later current roster, medical and statistical work is not frozen by that historical approval.

The opening check also rereads the prior handoff: team reviews, required owners and their reviewed source snapshot must still match what was staged. Later league-statistics and awards gate closures are allowed. A genuinely blocking choice in `pending_decisions` uses `{"id":"opening-contract-choice","status":"OPEN","blocks_opening":true}`; it remains a blocker until its recorded resolution changes `status` to `RESOLVED`. An ordinary carried decision, future-dated question or `requires_user` flag alone does not block opening.

New-season game receipts, statistics, standings, awards, position competitions and phase reports begin fresh. Prior reports, resolved battles, receipts and annual assessments remain in their season. An unresolved medical incident keeps its original owner across years; the next current-participation report links it without assuming clearance. Actual historical calendar research may be prepared in advance without importing future results or advancing the career clock. Team opening readiness does not require unrelated league-wide awards/statistics to have closed, and it does not replace the separate game-release gates.

## Path and rendering rules

Use `runtime.seasons.SeasonPaths` and its `record()` method for season paths. `runtime.season_layout` translates old physical and logical names to the current layout; frozen receipt and source bytes retain their original evidence. Do not recreate old folders because an older reference names one.

The annual record, trade index, cap views, standings, statistics and award pages are generated views. Change the actual owner or input first, then run the relevant renderer. `python scripts/render_annual_record.py 2014 --check` verifies that the dated index agrees with its owners. The [update workflow](update_workflow.md) gives the complete closure and validation procedure.

<!-- event-record: {"closure": {"checkpoint": "Canonical update - February 2, 2014 - 2014 season set up", "sequence": 68, "through": "2014-02-02"}, "date": "2014-02-02", "id": "2014-02-02-2014-season-set-up", "kind": "technical", "status": "closed", "summary": "2014 season set up."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical update - March 24, 2014 - Historical schedule and annual handoff", "sequence": 101, "through": "2014-03-24"}, "date": "2014-03-24", "id": "2014-03-24-historical-schedule-and-annual-handoff", "kind": "technical", "status": "closed", "summary": "Historical schedule and annual handoff."} -->
