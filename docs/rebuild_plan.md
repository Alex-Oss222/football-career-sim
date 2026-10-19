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

Two folders sit outside the seasons, because they follow Stone and the league across years:

- **career/Stone/:** his coach profile, his contract, his career history and his job opportunities (permission requests, interviews, offers and his agent's reports).
- **The league pages:** every player, standings and other clubs, as they are today.

The files the system works from (stored facts, game files, call sheets) live in a separate data area that the user never needs to open. From Week 6 they are written there, and the existing ones move there too, so the season folders hold only pages to read.

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
| 3 | Every Jaguars player page, the league player pages in the same style, and the coach, team, staff, contract and desk pages; the clean-page check in validation | Before 2014 Week 6 | Merged with the check passing on every new page |
| 4 | The three-page decision system, starting with Game Week Briefing, Game Plan and Game Report for Week 6 | Before 2014 Week 6 | Week 6 is played through it |
| 5 | In-season decisions: injury replacements, the bye week, trade calls, and the weekly check for coaching changes at every club | Before 2014 Week 8 | Merged |
| 6 | Season end and January: season review, extension, firing, agent's report, permission requests, offers, staff status, staff hires, coaching and GM changes across the league, Jacksonville running without Stone if he leaves, the 2015 calendar checked, the 2015 season opened in this structure, Documents 4 and 5 as short summaries built from the stored facts | Before 2014 Week 17 closes (December 28, 2014) | Merged |
| 7 | February to June 2015: re-signing, free agency, trades, offseason program, draft, OTAs and minicamp | Before February 2015 | Merged |
| 8 | July and August 2015: camp, position battles, preseason games, final cuts | Before July 2015 | Merged |

Each step is built lean: one builder and one reviewer, no new research except a season's historical dates.

## Status

| Step | Status |
|---|---|
| 1 | Done (merged) |
| 2 | Layout approved; the player record is built with step 3 |
| 2b | Built, awaiting merge |
| 3 to 8 | Not started |

## Change log

- October 19, 2026: plan adopted. The user approved the numbered season folders as they stand, asked for realistic names instead of system names, for a brief that tells him what he needs, and for this plan to hold its decisions across context resets.
- October 19, 2026: the user asked to drop the numbers from the season folder names. From 2015 the folders carry no numbers; 2014 keeps its numbered folders as history.
- October 19, 2026: the user asked for the new system from Week 6 on, not from 2015. Their words, verbatim: "For the rest of 2014 they stay where they are now no i want to use the new sytem going into the new week everthing before can move around as need as long but we dont have to change anthing to cnform to the new process". The 2014 folders are renamed and their system files moved before Week 6; nothing written before Week 6 is rewritten.
- October 19, 2026: the user approved the player page layout on the Kirk Cousins sample, without a weekly section and with transactions instead of a season narrative. Their words, verbatim: "layout prefect please this is me aske move his b-day to 1991 hes, 23 now please srry" and "keep the histoy though but lest that early a summart like you have in 2013 of the season  and keep hisroy should be like traded, signings ect cuts ect". Canon change by the user: Kirk Cousins's birth date is August 19, 1991 (23 on October 5, 2014), applied with step 3 wherever his birth date is stored; pages written before Week 6 that give his old age stay as written.
- October 19, 2026: the user asked that Cousins's college years shift to match the 1991 birth date, and that his history be cleaned up last, after the rest of the rebuild. Their words, verbatim: "want his college years shifted to match, we can cleean up the hisrty for kirk last lets do the rest fist". This is the final rebuild task, after step 8.
