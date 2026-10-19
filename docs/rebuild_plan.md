# Repository rebuild plan

Adopted October 19, 2026, from the user's instructions of October 18 and 19, 2026. This file governs every rebuild task. Read it first. Its decisions stay as written until the user changes them; a change is recorded in the change log at the end with the date and the user's words, never made silently.

## What the rebuild is

The rebuild changes how the career is organized, stored, presented and decided. It does not change the game engine, the private service, how games are played or any result.

The user's goal, in their words: a complete process from start to finish, realistic to football, clean pages with no system clutter, and a brief that says what is needed before every decision.

## Rules that never change

1. **The new system starts with 2014 Week 6.** Everything written up to the close of 2014 Week 5 may be moved to its place in the new folders, but its content is not rewritten to fit the new process. From Week 6 on, everything follows this plan.
2. **The engine is untouched.** Games, draws, the private service and outcomes are outside the rebuild.
3. **Historical dates.** Every season runs on the real NFL dates. Before a new season opens, its calendar is researched and checked in two independent passes.
4. **Clean pages.** A page the user reads is football only. It never shows internal codes or identifiers (for example 1C, 5A, 7D), file paths, script or module names, system notes, disclaimers, version labels or words such as engine, branch, receipt, kernel, ledger, snapshot or checkpoint. An assessment carries one dated line saying whose view it is, nothing more. A check in repository validation fails any page that breaks this rule.
5. **One fact, one place.** Every fact is stored once. Pages are built from those stored facts, so a page can never disagree with another page.
6. **Realistic authority.** Stone only decides what his job lets him decide. Everything else is decided by the person who owns it and reaches him as news, or as a request for his input when a real coach would be asked.
7. **One step at a time.** Each build step is its own pull request, merged only after its tests, repository validation and the clean-page check pass. The next step starts after the merge.

## The season folders

Each season has these folders, with no numbers in their names:

- Team_Operations
- Early_Offseason
- Offseason_Training
- Draft
- Training_Camp_and_Preseason
- Regular_Season
- Postseason
- Season_Review

The 2014 folders are renamed the same way before Week 6, with their existing files moved inside them as they are. The season folder's README is the head coach's desk: today's date, his job, what is waiting on him, the next event and where each record is. Calendar.md and Record.md stay beside it.

These folders sit outside the seasons, because they follow Stone, his staff and the league across years:

- **career/Stone/:** everything that is his. The Coach page (`README.md`) and Contract and jobs (`Contract_and_Jobs.md`), both built from his coach record; his coaching profile (`Coaching_Profile.md`, the philosophy the user wrote, which the Coach page quotes); the reviews he has received (`Performance_Reviews.md`); the coach sheet as history (`Coach_Sheet_through_October_2014.md`: it gains no later season, because the Coach page carries the current facts, his record by season and awards built from the closed games and award results); his photo (`photos/`); his own contract file (`Head_Coach_Contract.md`) when the user writes it; and his job opportunities (permission requests, interviews, offers and his agent's reports).
- **career/Assistant_Coaches/:** the assistants' profiles (`staff_profiles.md`) and their index (`README.md`). Who coaches what each season is the Staff page in that season's Team_Operations. The template for writing any coach's profile, review or coach sheet is `foundation/templates/coach_profile_template.md`, with the folder method beside it in `foundation/templates/coach_records_method.md`.
- **The league pages:** every player, standings and other clubs, as they are today.

The files the system works from (stored facts, game files, call sheets) live in a separate data area that the user never needs to open. From Week 6 they are written there, and the existing ones move there too, so the season folders hold only pages to read.

## How the stored facts are kept

These rules keep the year-to-year move small and the structure safe to change:

1. **People and contracts are stored once, not per season.** Each player, coach and contract has one permanent record under the data area that grows by dated entries (signed, traded, injured, assessed). Nothing is copied into a new season; only what belongs to one season (games, decisions, the calendar) lives in that season.
2. **One folder map.** All code finds files through one map of the layout. A test fails if a script writes a folder name or a year into a path itself.
3. **The same shape every season.** Every season has the same folders, created from one template, never copied from the year before.
4. **Built pages are never the source.** Pages, statistics and standings are built from the stored facts and game files, and a check confirms they match. Nothing built is carried forward or kept in sync by hand.
5. **Closed seasons are packed and locked.** When a season closes, its game files are packed into one compressed file with a checksum, read by the same tools, and the season becomes read-only.
6. **Document 5 is a short summary built from the stored facts:** the date, the job, open decisions, availability and the next events, so it changes only when a fact changes.
7. **Safeguards.** Before each real year change, a copy of the repository runs the whole move into the next season first. Tests work out the current week from the stored facts instead of naming a date.

## How a decision works

Every decision point produces three pages in the folder where it happens:

1. **The brief.** Named for whoever really brings it: the GM, the scouting department, the medical staff, the agent. It tells Stone what he needs to know and what is being asked of him, in the voice that person would use. Tables first, built from the stored facts: injuries, how players played, contracts, needs, who is calling. Then a short read from the staff member who gives it, which may only cite what the page shows. Then who else decides what, and the deadline.
2. **His page.** A fill-in page with fixed headings, named for what it is (Game Plan, My Draft Recommendations). He fills it in place, or uploads a .md or .txt file with the same headings. Choices are limited to what is legal: players on the roster, calls in the active playbook. Before anything runs, a check tells him exactly what is missing or invalid. His page stays as the record of his decision.
3. **The result.** Named for where it is decided (Game Report, Draft Room Results). It says what happened and what changed.

Decisions covered by a standing rule he has given, and decisions that belong to someone else, do not produce a page for him to fill. The clock waits for an answer he owes; silence never counts as yes or no. Opening a page never moves time or creates an event. If the situation changes after a brief goes out, a new brief replaces it, and the old one stays as what he saw.

Contacts from other clubs are always named for what they are: a rumor, a call, an interview request, an offer, or an accepted job. His standing answer to "open to job offers" decides whether calls reach him as decisions (yes) or only as news (no).

## The decisions in a year

The page names below are fixed.

| When | Brief | His page | Result | Folder |
|---|---|---|---|---|
| Every game week | Game Week Briefing | Game Plan | Game Report | Regular_Season, a folder per week; Postseason for playoffs |
| Bye week | Bye Week Review | My Adjustments | Bye Week Report | Regular_Season, the bye week's folder |
| Injury replacement in season | Roster Move Request | My Recommendation | Transaction | The week's folder |
| Trade talks | Trade Call | My Recommendation | Trade Result | Team_Operations/Trades |
| Season ends | Season Review (owner and GM) | My Response | Club Decision | Season_Review |
| Contract extension | Extension Offer | My Answer | New Contract or Unchanged | career/Stone |
| Fired, or contract ending | Agent's Report | Instructions to My Agent | Interviews and Offers | career/Stone |
| Another club calls | Permission Request | My Answer | Interview or Declined | career/Stone |
| After an interview | Offer Sheet | My Answer | Signed or Talks Ended | career/Stone |
| January staff | Staff Status Report | My Staff Decisions | Staff Moves | Early_Offseason |
| Staff vacancy | Candidate Report | My Hire | Staff Hire | Early_Offseason |
| February | Re-signing Report | My Re-signing Priorities | Front Office Moves | Team_Operations/Free_Agency |
| March | Pro Personnel Report | My Free-Agent Priorities | Free Agency Results | Team_Operations/Free_Agency |
| April | Offseason Program Brief | My Program Plan | Program Report | Offseason_Training |
| May | Scouting Department Report | My Draft Recommendations | Draft Room Results | Draft |
| May and June | OTA Brief | My Install Plan | OTA Report | Offseason_Training |
| Camp | Position Battle Report | My Depth Calls | Depth Chart | Training_Camp_and_Preseason |
| Preseason games | Preseason Game Briefing | Preseason Game Plan | Preseason Game Report | Training_Camp_and_Preseason |
| Final cuts | Roster Cutdown Report | My Cut Recommendations | Final 53 | Training_Camp_and_Preseason |

As head coach under David Caldwell, Stone decides the game plan, depth, inactives, practice, his staff within the budget and his own career. For acquisitions, the draft, contracts and cuts he recommends and Caldwell decides. In another job the same pages appear with that job's scope: a defensive coordinator's Game Plan covers the defense only, and he receives requests for his evaluations instead of recommendation pages he does not own.

## The pages to read

Each kind of page has one fixed layout, built from the stored facts:

- **Player:** a header line (name; team, position, number, age, status), a line of height, weight, birth date, college and draft, and the photo; then Staff assessment (the grades, the staff read and one dated line naming whose view it is); Contract (salary by year); Statistics, regular season and playoffs separate, every table led by Season, Team, Age and #; Awards (Pro Bowl, All-Pro and the like); and Transactions (drafted, signed, traded, released, re-signed, reserve lists), one dated line each. There is no weekly section: only the statistics change week to week, and the assessment changes only at the two annual assessments. Approved by the user on October 19, 2026, on the Kirk Cousins page.
- **Coach (Stone):** his job and employer, his contract and remaining term, his record by season, career history, philosophy (written by the user), reviews he has actually received, and any open opportunities.
- **Team:** results and standings, roster, staff, who decides what at the club, and what the owner and GM have asked of him.
- **Staff:** who coaches what, who calls what, contract status where a head coach would know it, open jobs.
- **Contract and jobs:** his terms, what is owed, interview requests, offers and deadlines, with the stage of each contact named.
- **The desk:** what needs him now, then the next event, then everything else.

## Build steps

| Step | What | Needed by (career calendar) | Done when |
|---|---|---|---|
| 1 | This plan, and the instruction in CLAUDE.md to follow it | Now | Merged |
| 2 | The stored player facts and the Kirk Cousins page | Before 2014 Week 6 | The user approves the page |
| 2b | The 2014 season moved into the new folders: numbers dropped from the folder names, system files moved to the data area, every link kept working, no file's content rewritten | Before 2014 Week 6 | Merged with every link resolving |
| 3 | The permanent player, coach and contract records (stored-facts rules 1 to 4), every Jaguars player page, the league player pages in the same style, and the coach, team, staff, contract and desk pages; the clean-page check and the folder-map test in validation | Before 2014 Week 6 | Merged with the check passing on every new page |
| 4 | The three-page decision system, starting with Game Week Briefing, Game Plan and Game Report for Week 6 | Before 2014 Week 6 | Week 6 is played through it |
| 5 | In-season decisions: injury replacements, the bye week, trade calls, and the weekly check for coaching changes at every club; the player contract records, with the contract pages built from them | Before 2014 Week 8, or before the first Jacksonville transaction after Week 5 if that comes first | Merged |
| 6 | Season end and January: season review, extension, firing, agent's report, permission requests, offers, staff status, staff hires, coaching and GM changes across the league, Jacksonville running without Stone if he leaves, the 2015 calendar checked, a rehearsal of the year change on a copy, the 2014 season packed and locked, the 2015 season opened in this structure, Documents 4 and 5 as short summaries built from the stored facts | Before 2014 Week 17 closes (December 28, 2014) | Merged |
| 7 | February to June 2015: re-signing, free agency, trades, offseason program, draft, OTAs and minicamp | Before February 2015 | Merged |
| 8 | July and August 2015: camp, position battles, preseason games, final cuts | Before July 2015 | Merged |

Each step is built lean: one builder and one reviewer, no new research except a season's historical dates.

## Status

| Step | Status |
|---|---|
| 1 | Done (merged) |
| 2 | Layout approved; the player record is built with step 3 |
| 2b | Done (merged) |
| 3a | Done (merged): the permanent player records (`data/people/players/`, holding only the assessments and transactions; every other fact, awards included, is read from its owner in the order `runtime/people.py` lists), the canon-override layer with Kirk Cousins's birth date, one builder for every player page (`scripts/render_player_pages.py`), and the clean-page and folder-map checks in validation |
| 3b | Done (merged): the coach records (`data/people/coaches/`, with Stone's contract and its completed terms), the roster record and the depth chart's update log in the data area, and the built Coach, Contract and jobs, Staff, Team, roster, depth chart, player ages, payroll and cap pages and the desk; the clean-page check now lets an event owner gain dated entries, and the page history is pinned |
| 4 to 8 | Not started |

Pages written before Week 6. The clean-page check exempts such a page while its bytes match the digest recorded for it in `data/pages/history.json` (the map is pinned in code, so an entry cannot be added or changed quietly). A page that keeps those bytes as an exact prefix is checked only on what follows them: event owners such as the medical history and the annual record gain dated entries this way, each with its invisible event line. Any other rewrite, by hand or by a generator, is checked like a new page, so each living view is cleaned by the step that next rewrites it, before that rewrite. One change keeps a page history: when a page it links to moves, the link's destination may be rewritten (rule 1 lets content move) and nothing else on the page changes. The commit that does it records the page's new digest and length in the history map and moves a moved page's entry to its new path, with the pin updated, and an audit shows that each re-recorded page equals its earlier bytes with only link destinations substituted. The history map's own description and the clean-page check's notes state the same rule:

- **Step 3b** cleaned or replaced: the desk (`career/2014/README.md`), the Team page, roster, player ages and depth chart (now built from the roster record and the depth chart's data and update log), the Staff page, the Coach and Contract and jobs pages, the coaching payroll and the cap views under `career/finances/`, and the four folder READMEs whose statements the moves made false (Roster, Depth_Chart, `career/finances/`, `career/finances/supporting_records/`). No script rewrites `career/README.md` or the coach profiles (since October 19, 2026 in `career/Stone/` and `career/Assistant_Coaches/`, with their links moved); they stay as written until the season-end step updates the coach profiles. The staff register `coaching_staff.md` stays as written: the coach records own its facts from now on.
- **Step 4**, under which Week 6 is played: every view a game week's close rewrites: `Record.md` (`scripts/render_annual_record.py`), `Calendar.md` when a date changes, `Regular_Season/standings.md` (`scripts/render_standings.py`), the Statistics pages and the team tracker (`scripts/render_season_stats.py`, `scripts/render_team_tracker.py`), the award pages (`scripts/league_awards.py render`), the Games and League_Results indexes and week pages, the in-season rails page (`scripts/render_inseason_rails.py`) and the medical pages (`Team_Operations/Medical/`): the current injury report is rewritten each week, while the medical history only gains entries.
- **Step 5, before the first Jacksonville transaction after Week 5**: the player contract owners under `Team_Operations/Finances/` (`player_contracts/contracts.md` with its update log, `contract_status.md` and the cap worksheet) move into stored records with built pages. A transaction edits them in place, and as written they fail the clean-page check, so a transaction in Week 6 or 7 brings this work forward. AGENTS.md's contract-table rule changes with that move.

Carried from 3a to step 6 (season end):

- The season-close tools (the final player assessments in `scripts/build_annual_player_sheets.py` and the opening cards staged by `scripts/season_handoff.py`) still read the earlier card layout; at the year change they move to the records, where the opening assessments now live. Until then a season's player folder holds built pages, its opening assessments are checked on the records, and the folder stops being written once the season review closes the season.
- The successor season's opening guide (`runtime/season_layout.opening_guides`) still links its roster to `roster.md` and its staff to `coaching_staff.md`. From 2015 the roster page is built from the season's roster record and the Staff page from the coach records, so the guide links the built pages once the season opens; a staged successor without its own README would otherwise carry two dead links.
- The 2014 player-state table (`library/data/2014_player_state_public.json`) was built and frozen before the birth-date change and applied Cousins's 2014 aging once, at 26. It does not read the birth-date registry, so the override does not reach it and no 2014 game changes; the 2015 aging, built at the year change, must read the birth dates through `runtime/player_bios.py`.

## Change log

- October 19, 2026: plan adopted. The user approved the numbered season folders as they stand, asked for realistic names instead of system names, for a brief that tells him what he needs, and for this plan to hold its decisions across context resets.
- October 19, 2026: the user asked to drop the numbers from the season folder names. From 2015 the folders carry no numbers; 2014 keeps its numbered folders as history.
- October 19, 2026: the user asked for the new system from Week 6 on, not from 2015. Their words, verbatim: "For the rest of 2014 they stay where they are now no i want to use the new sytem going into the new week everthing before can move around as need as long but we dont have to change anthing to cnform to the new process". The 2014 folders are renamed and their system files moved before Week 6; nothing written before Week 6 is rewritten.
- October 19, 2026: the user approved the player page layout on the Kirk Cousins sample, without a weekly section and with transactions instead of a season narrative. Their words, verbatim: "layout prefect please this is me aske move his b-day to 1991 hes, 23 now please srry" and "keep the histoy though but lest that early a summart like you have in 2013 of the season  and keep hisroy should be like traded, signings ect cuts ect". Canon change by the user: Kirk Cousins's birth date is August 19, 1991 (23 on October 5, 2014), applied with step 3 wherever his birth date is stored; pages written before Week 6 that give his old age stay as written.
- October 19, 2026: the user asked that Cousins's college years shift to match the 1991 birth date, and that his history be cleaned up last, after the rest of the rebuild. Their words, verbatim: "want his college years shifted to match, we can cleean up the hisrty for kirk last lets do the rest fist". This is the final rebuild task, after step 8.
- October 19, 2026: the user asked for the data underneath to be kept so that the year change and the structure cause no problems, with as little stored as possible. The stored-facts rules above were added and placed in steps 3 and 6.
- October 19, 2026 (a build record of step 3a, not a change to the plan's decisions): the cap tracker (`career/finances/salary_cap/cap_tracker.md`) now reads every birth date through `runtime/player_bios.py` and works out each age as of the tracker's own date, September 8, 2014. Besides Kirk Cousins's age under the user's canon birth date (25 to 23), this corrected 30 stale ages that the removed `age_at_checkpoint` inputs had left one year low, for example Marcedes Lewis 29 to 30, Eugene Monroe 26 to 27 and Lane Johnson 23 to 24.
- October 19, 2026 (step 3b): Stone's contract terms that were never recorded (end date, salary, offset, dismissal terms) are completed as a labelled reconstruction under the user's delegation in their employment answers of October 18, 2026, verbatim: "you can decide the rest". The length and the full guarantee stay the signed terms. Reconstructed: the contract ends on the later of January 31, 2017 or the day after Jacksonville's last game of the 2016 season (the wording of Jacksonville's own 2010 assistant extensions); $2,800,000 in each of 2013 to 2016 (Ron Rivera's four-year, $11.2 million first contract at Carolina in 2011, the most recent reported first contract of a coordinator promoted to a first head-coaching job; no raise, because none is sourced); after a dismissal without cause the unpaid remainder is owed less a dollar-for-dollar offset for another coaching job, with no separate buyout; nothing further is owed after a dismissal for cause. The research is `library/nfl_head_coach_contracts_2005_2014.md`. The user may change any of these terms.
- October 19, 2026 (a build record of step 3b, not a change to the plan's decisions): six independent reviews recorded 37 findings, some overlapping, and the confirmed ones were fixed before merge. The game path was checked unchanged: every reader game preparation uses returns what it returned before, and a Week 6 rehearsal built a byte-identical game package. Four folder READMEs not on the build list were rewritten because the moves made their statements false (Roster, Depth_Chart, `career/finances/`, `career/finances/supporting_records/`). The depth chart's update log moved to the data area with 22 entries reworded in football terms; each keeps its original wording in an unrendered field, so no fact is lost. Still saying that Stone's pay is not established, as history or rulebook text: Document 3 §3.1, the 2013 coach sheet, `career/2013/offseason/head_coach_contract.md` and the coaching performance review. The rulebook line changes only when the user asks.
- October 19, 2026: the user asked where the coaching profiles belong. Their words, verbatim: "So we have two things, we have coaching profiles, and then we have stone, right? Don't the stuff under coaching profile belong under stone? Let me know if I'm wrong." Stone's own files moved under `career/Stone/`: the coaching profile to `Coaching_Profile.md`, the performance review to `Performance_Reviews.md`, the NFL coach sheet to `Coach_Sheet_through_October_2014.md` (history; the built Coach page carries the current facts) and his photo to `photos/`. The assistants' profiles are not his, so they moved to `career/Assistant_Coaches/staff_profiles.md`, with a short index as that folder's README; the writing template moved to `foundation/templates/coach_profile_template.md` and the old folder README's method to `foundation/templates/coach_records_method.md`, both listed in the template catalog; the coach sheet gains no later season, and the workflow and milestone pages now say so. `career/coaching_profiles/` is gone. The moved pages and the pages linking to them changed only in their link destinations, and their history entries were re-recorded under the link-only rule above.
- October 19, 2026: the user ruled on Kirk Cousins's 2014 opening assessment. Their words, verbatim: "A. Keep the 2014 opening as written." His opening assessment of March 31, 2014 stands as written, beside his 2013 final assessment.
