# January Staff Review: Three-page system

**Design only.** These files are proposals for football-career-sim; they do not change a canonical game, job, contract, calendar, or personnel decision.

**Cycle illustrated:** Review of the 2014 Jacksonville Jaguars coaching staff, carried out on dates actually established after Jacksonville's last game in the 2014 NFL season. Relevant work may occur in January or February 2015. Do not invent a review day from the month name, or treat January 1 as an assistant's proven contract-expiration day.

## Documents

1. `Staff_Status_Report_TEMPLATE.md` — football operations presents verified staff responsibilities, evidence, contracts and open questions. It is a staff status report, not a new 53-player season review.
2. `My_Staff_Decisions_TEMPLATE.md` — Stone's fixed-heading fill-in page. A decision to pursue renewal is not an agreed contract.
3. `Staff_Moves_TEMPLATE.md` — the January phase's closing account and **index** of completed independent staff results, not a pooled substitute for them.
4. `Individual_Staff_Result_TEMPLATE.md` — one separate, dated reader-facing outcome for **each resolved staff event**. A completed renewal, rejected renewal offer, termination, contract lapse, interview permission disposition, resignation, hire or material role change gets its own event result if it actually occurs.
5. `Implementation_Spec.md` — authority, dates, routing, immutable issuance, event records, status transitions and tests.
6. `2014_Into_2015_Illustration.md` — the real current staff as recorded October 5, 2014; unresolved 2014-season football; no invented future contract or employment outcome.

## Place in the season

The 2014 team's football season review and coach exit interviews belong to the 2014 `Season_Review/`. The **January 2015** staff-retention and contract actions belong to the **2015** `Early_Offseason` staff-review or staff-changes owner, with links back to the 2014 exit-interview evidence. The current repository has not yet created the 2015 `Early_Offseason` directory; its implementation must route through `SeasonPaths` rather than hard-coding a raw path or prematurely switching the active playing season.

## Behavior

- Stone is the final staff-selection authority under his Jacksonville appointment, within the promised but unquantified assistant budget. Caldwell confirms contract funding and related administration. No one can sign the coach's acceptance on his behalf.
- Review only after Stone is confirmed as continuing Jacksonville's head coach. If he is dismissed, he does not get to decide Jacksonville's next staff; the employer's new chain of authority takes over.
- Only concluded events get separate individual outputs. Open proposals retain dated status and a link; a plan to retain nine coaches does not fabricate nine signed renewals.
- A staff review does not pre-decide the next `Candidate Report → My Hire → Staff Hire` workflow for genuine vacancies.
- Absent a staff concern, it is legitimate to keep the current duties intact. No praise/criticism quota, staff grade, or forced turnover.

## Research basis

Contemporary process references for **form**, not future simulated NFL outcomes:
- Brian Billick, NFL.com, 2014, [What offseason? NFL coaches busy preparing for 2014 campaign](https://www.nfl.com/news/what-offseason-nfl-coaches-busy-preparing-for-2014-campaign-0ap2000000323842): end-of-season staff evaluation and studying prior decisions.
- Chris Mortensen, ESPN, January 30, 2014, [Jason Garrett given latitude to make staff changes](https://www.espn.com/nfl/story/_/id/10376181/jason-garrett-coach-dallas-cowboys-had-authority-make-staff-changes): retained head coach evaluates assistants, with owner/GM authority depending on the club.
- Washington Post, December 29, 2014, [Jay Gruden to meet with management about assistants and team](https://www.washingtonpost.com/news/football-insider/wp/2014/12/29/jay-gruden-to-meet-with-bruce-allen-and-daniel-snyder-this-week-on-assistants-team/): film/evaluation first, decisions after management discussion.
- Andrew Brandt, Sports Illustrated, January 16, 2014, [Getting Down to Business](https://www.si.com/nfl/2014/01/16/nfl-finances-concussion-settlement-playoff-pay): coaching agreements, guaranteed money and offsets.
- DallasCowboys.com, January 3, 2014, [Rich Bisaccia head-coach interview](https://www.dallascowboys.com/news/st-coach-bisaccia-interviewing-for-skins-head-coaching-job-345951): the period-specific head-coach versus assistant-interview permission distinction.
- NFL.com, March 2013, [Rooney Rule not extended to coordinators](https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292): do not import later coordinator-hiring requirements into the 2014-15 cycle.

The repository's dated player/coach records, accepted employment authority, financial tables and canonical season result remain authoritative over generic process articles.
