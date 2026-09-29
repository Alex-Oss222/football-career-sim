# Library: 2014 NFL League Calendar and Financial Rules

**Status:** Research pass (pass 1 of 2) and separate verification pass (pass 2 of 2) completed September 28, 2026. This file is the sourcing and verification record for the 2014 league year, which the simulation enters on **January 12, 2014**. It is research only. It changes no canon, closed result, roster, standings, calendar or state fact. It is modelled on `library/2013_league_calendar_and_financial_rules.md` (structure and sourcing discipline) and on `library/2014_draft_information_gates.md` (release-date gating). Where this file and a later Document 2 table disagree, treat that as a defect to fix, not a real disagreement.

**Method:** The first pass found each claim. The second pass searched each claim again from scratch, with different query wording and, where possible, a different outlet, without relying on the first pass's citation. Labels:

- **Confirmed**: two or more independent sources agree (different publishers, or a publisher plus a dated URL).
- **Corrected**: a first-pass source or search summary was wrong; the correction and the reason are stated.
- **Unverified**: one source only, a source that may only echo the query wording, or no direct source. An unverified figure must not be used for accounting or as a deadline until a later session confirms it.

**Access limits (read before relying on this file):** WebFetch is blocked by this environment's network egress policy (a test fetch of an NFL.com page returned `EGRESS_BLOCKED`). No page was opened. **Every source below was read through search-engine result text (title, URL, date metadata and extracted passage), not by opening the page.** No attempt was made to route around the block. The official NFL "2014 Important Dates" release, the 2011 CBA text and the NFL Record and Fact Book were not read directly. A future session with page access should reopen the URLs and upgrade or correct the labels.

**Hindsight and result boundary (read first):** No real 2014 transaction, franchise or transition tag applied to a named player, signing, trade, compensatory award to a named club, draft selection, the real 2014 draft order, real schedule result, playoff participant, champion or award winner is recorded here, and none may be imported as an answer key (Document 1 §8, Document 2 §4.3). Several cited pages carry such outcomes in their titles or text (for example, the kickoff game's clubs and score, Super Bowl XLIX's participants and result, and the 2014 compensatory recipients); they are cited only for dates, rules and league-wide figures. Clubs are named only where a rule or a pre-branch league scheduling fact requires it (the AFC South rotation and the London game designation).

**September 29 direct-source addendum:** [full calendar verification](2014_full_calendar_verification.md) opens the club bulletins and identifies their publication dates, confirms C19 and June tender dates, verifies the camp rule and adds late-year dates. Its explicitly scoped upgrades supersede the old access limitation only for the named claims; all other labels below remain unchanged.

## Information gates (core rule)

At any simulation date, use only information that had become public by that date. Each row below carries a **Public by** column. A figure or date whose public release came after January 12, 2014 stays unavailable to the simulation until its release date. Before its release, only the projections that were public at the time may be used, labelled as projections.

- The **2014 league calendar** was public in December 2013. Big Cat Country (dated URL December 21, 2013) and Battle Red Blog (dated URL December 23, 2013) both reported the NFL's announcement of the 2014 calendar, including the March 11 league year, the March 8 negotiating window and the May 8 to 10 draft. The official release date of December 20, 2013 rests on one search summary and is **Unverified**; treat the core calendar as public by **December 21, 2013**. Sources: https://www.bigcatcountry.com/2013/12/21/5232460/nfl-free-agency-schedule-calendar-2014 ; https://www.battleredblog.com/2013/12/23/5238474/2014-nfl-calendar-all-the-dates-you-need-to-know
- The fuller club-site "2014 National Football League Important Dates" lists (Saints, Bills, Patriots) carry no visible publication date in search text. Treat items found only there as public by **late January 2014** (Pro Football Rumors' January 2014 list and Cincy Jungle's January 27, 2014 list reproduce them), and **Unverified** as to the exact day.

## 1. Calendar

### 1a. End of the 2013 season to the start of the 2014 league year

| # | Event | Date/time | Public by | Label | Sources |
|---|---|---|---|---|---|
| C1 | 2013 regular season ends; reserve/future contracts may be signed once a club's season is over | 2013 regular season ended Sunday, December 29, 2013. Futures signings were reported from December 30 to 31, 2013 for non-playoff clubs; a playoff club may sign futures contracts only after its own season ends. | Before branch entry | Confirmed (end date and general rule). The exact CBA wording of the earliest signing moment ("day after the club's last game") is **Unverified** | https://en.wikipedia.org/wiki/2013_NFL_season ; https://bleacherreport.com/articles/1947667-everything-you-need-to-know-about-nfl-futures-contracts ; https://en.wikipedia.org/wiki/2013_New_York_Jets_season (futures signings dated December 31, 2013; cited for date only) |
| C2 | Reserve/future contracts count against the next league year's cap and 90-man offseason limit, not the current 53 | Rule | Before branch entry | Confirmed | Bleacher Report (C1); https://www.behindthesteelcurtain.com/2023/5/29/23740996/explaining-how-the-nfl-works-part-4-futures-contracts-practice-squad-salary-steelers |
| C3 | Underclassman special-eligibility deadline | January 15, 2014 | Before branch entry | Confirmed (see `library/2014_draft_information_gates.md`) | https://www.neworleanssaints.com/news/98-players-granted-special-eligibility-for-2014-nfl-draft-12467237 ; https://www.cbsnews.com/texas/news/record-98-underclassmen-eligible-for-nfl-draft |
| C4 | Reese's Senior Bowl | Saturday, January 25, 2014, Ladd-Peebles Stadium, Mobile, Alabama | Before branch entry | Confirmed (cross-checked against `library/2014_draft_information_gates.md`) | https://en.wikipedia.org/wiki/2014_Senior_Bowl ; https://www.nfl.com/photos/2014-reese-s-senior-bowl-0ap2000000317785 |
| C5 | Pro Bowl (2013 season) and Super Bowl XLVIII | Pro Bowl Sunday, January 26, 2014; Super Bowl XLVIII Sunday, February 2, 2014 | Before branch entry | Confirmed in `library/2013_postseason_format_and_schedule.md` | See that file |
| C6 | Franchise/transition designation window | Opens Monday, February 17, 2014; closes **Monday, March 3, 2014, 4:00 PM ET** | December 21, 2013 (window) | Confirmed | https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates ; https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429 ; https://www.thephinsider.com/2014/3/4/5468790/nfl-franchise-tag-deadline-4-players-get-franchised-plus-2-transition (dated March 4, 2014; describes a Monday 4 PM deadline; cited for date only) |
| C7 | NFL Scouting Combine | February 19 to 25, 2014, Lucas Oil Stadium, Indianapolis; on-field workouts February 22 to 25 | Before branch entry (dates) | Confirmed (cross-checked against `library/2014_draft_information_gates.md`) | https://abcnews.com/Sports/2014-nfl-combine-schedule/story?id=22611536 ; https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates |
| C8 | **2014 salary cap announced** | Friday, February 28, 2014 (memo to clubs) | **Gate: February 28, 2014** | Confirmed | See §2 F1 |
| C9 | Negotiating period ("legal tampering") with certified agents of prospective unrestricted free agents | **Saturday, March 8, 2014, 12:00 noon ET** through 3:59:59 PM ET Tuesday, March 11. No contract may be executed with a new club before 4:00 PM ET March 11. No player visits and no direct club-to-player contact; self-represented players may not be negotiated with. | December 21, 2013 | **Corrected** (start time; see Verification notes V1) | https://www.nfl.com/news/nfl-s-negotiating-period-for-free-agents-kicks-off-today-at-noon-et ; https://www.steelers.com/news/free-agent-3-day-negotiating-period-begins-12716056 ; https://www.bleedinggreennation.com/2014/3/8/5484378/nfl-free-agency-2014-three-day-negotiating-window-schedule ; https://www.denverbroncos.com/news/nfl-free-agency-faq-12723855 |
| C10 | **2014 league year begins; free agency and trading period open** | **Tuesday, March 11, 2014, 4:00 PM ET**. Before 4:00 PM ET, clubs must be under the 2014 cap, exercise or decline player options, submit qualifying offers to their restricted free agents and minimum tenders to their exclusive-rights free agents. | December 21, 2013 | Confirmed | https://www.giants.com/news/2014-free-agency-questions-answers-12711854 ; https://www.steelers.com/news/key-dates-as-free-agency-approaches-12691947 ; https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates ; Big Cat Country (gate note) |

### 1b. League year to the draft

| # | Event | Date/time | Public by | Label | Sources |
|---|---|---|---|---|---|
| C11 | Annual League Meeting | March 23 to 26, 2014, Orlando, Florida (Ritz-Carlton Orlando Grand Lakes) | Late January 2014 | Confirmed (dates and city). Hotel: **Unverified** (one search summary) | https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates ; https://www.patriots.com/news/key-dates-on-the-2014-nfl-calendar-196016 ; https://si.com/2014/03/25/nfl-owners-meetings-primer |
| C12 | Compensatory picks announced | **Monday, March 24, 2014** (32 compensatory selections). Recipients are real-history outcomes and are **not imported**; the branch must resolve its own awards (§4). | **Gate: March 24, 2014** | Confirmed (date) | https://profootballtalk.nbcsports.com/2014/03/24/2014-nfl-compensatory-picks/ (dated URL) ; https://fansided.com/2014/03/24/2014-nfl-draft-compensatory-picks-full-list-announced/ (dated URL) ; nfl.com draft story 0ap2000000336490 (URL slug withheld: it names real 2014 compensatory-pick recipients) (title names clubs; cited for date only) |
| C13 | League-wide offseason workout program schedule for all 32 clubs released | April 3, 2014 | **Gate: April 3, 2014** | Confirmed (date). Per-club real dates are **not imported** (C18 note) | https://profootballtalk.nbcsports.com/2014/04/03/2014-nfl-offseason-workout-schedule/ (dated URL) ; https://www.nfl.com/news/nfl-offseason-workout-program-dates-announced-0ap2000000339264 |
| C14 | Earliest offseason program start: clubs that hired a new head coach after the end of the 2013 regular season | Monday, April 7, 2014 | Late January 2014 | Confirmed | https://www.neworleanssaints.com/news/2014-national-football-league-important-dates-12566525 ; https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429 ; https://www.cincyjungle.com/2014/1/27/5350276/important-nfl-offseason-dates-in-2014 |
| C15 | **Earliest offseason program start: clubs with returning head coaches (this includes Jacksonville in the branch; Jacksonville is not a new-head-coach club in 2014)** | **Monday, April 21, 2014** | Late January 2014 | Confirmed | Same as C14 |
| C16 | Pro Bowl (2014 season) site announced | April 9, 2014: University of Phoenix Stadium, Glendale, Arizona | **Gate: April 9, 2014** | Confirmed | https://www.washingtonpost.com/news/football-insider/wp/2014/04/09/pro-bowl-will-take-place-in-arizona-in-2015/ (dated URL) ; https://www.giants.com/news/pro-bowl-moves-to-arizona-hawaii-in-2016-12861112 |
| C17 | **2014 regular-season schedule released** | **Wednesday, April 23, 2014, 8:00 PM ET** | **Gate: April 23, 2014** | Confirmed | https://www.nfl.com/news/nfl-will-release-2014-schedule-on-wednesday-0ap2000000342996 ; https://detroitjockcity.com/2014/04/23/nfl-network-2014-schedule-release-start-time-tv-live-stream/ (dated URL) ; https://fbschedules.com/2014-nfl-schedule-announced/ |
| C18 | Restricted free agent offer-sheet deadline | Friday, May 2, 2014 | Late January 2014 | Confirmed | https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates ; https://www.patriots.com/news/key-dates-on-the-2014-nfl-calendar-196016 ; https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429 |
| C19 | Prior club's deadline to exercise its right of first refusal on an RFA offer sheet | Wednesday, May 7, 2014 | Late January 2014 | **Unverified** (one search summary quoting the Saints and Bills lists; not re-found in pass 2) | https://www.neworleanssaints.com/news/2014-national-football-league-important-dates-12566525 |
| C20 | **2014 NFL Draft** | **Thursday May 8 to Saturday May 10, 2014, Radio City Music Hall, New York.** Round 1 Thursday 8:00 PM ET; rounds 2 and 3 Friday; rounds 4 to 7 Saturday. **Moved later than the customary late-April window** because of a Radio City scheduling conflict. | May 28, 2013 (dates and venue) | Confirmed (see `library/2014_draft_information_gates.md` for the full gate record and first-round start-time caveat) | https://www.nfl.com/news/2014-nfl-draft-set-for-may-8-10-at-radio-city-music-hall-0ap1000000207063 ; https://www.espn.com/nfl/story/_/id/9318615/2014-nfl-draft-held-8-10-radio-city-music-hall |

**Note on C13 to C15 and Jacksonville's own program dates.** A first-pass search summary attributed a start date of "April 20" and OTA dates that included Sundays to the real 2014 Jaguars. April 20, 2014 was a Sunday, and the CBA confines offseason program activity to weekdays (§1d), so that summary is internally inconsistent and was **rejected**. In any case, Jacksonville's 2014 program dates are a branch club decision made within the CBA limits below, not a real-history rail to import. A branch Jacksonville calendar must set its own dates on or after April 21, 2014.

### 1c. After the draft

| # | Event | Date/time | Public by | Label | Sources |
|---|---|---|---|---|---|
| C21 | Post-draft signing of undrafted free agents | Opens at the end of the draft (Saturday, May 10, 2014). The precise opening moment in the 2014 rules was not found. | n/a | **Unverified** (moment) | None found in search text |
| C22 | Post-draft rookie minicamp window | One three-day rookie minicamp, at the club's election on **either the first or second weekend after the draft**: for 2014, the weekends of **May 16 to 18** or **May 23 to 25, 2014** (the second pair is derived from the rule and the calendar). | Rule public before branch entry | Confirmed (rule; first-weekend example May 16 to 18). Second-weekend dates are derived, not directly sourced | https://www.ninersnation.com/2014/5/13/5715062/breaking-down-the-nfl-cba-minicamps-49ers-rookie-minicamp-dates ; https://overthecap.com/collective-bargaining-agreement/article/22 ; https://www.nfl.com/news/twenty-four-nfl-teams-open-rookie-minicamp-today-0ap2000000350700 ; https://www.cincyjungle.com/pages/important-nfl-dates-for-2013-and-2014 |
| C23 | Spring League Meeting | May 19 to 21, 2014, Atlanta | Late January 2014 | Confirmed | https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates ; https://www.steelers.com/news/top-takes-from-2014-spring-league-meeting-13045897 |
| C24 | "June 1 tender" deadline for unsigned unrestricted free agents (and substitute tender for unsigned restricted free agents without offer sheets) | Monday, June 2, 2014 | Late January 2014 | Confirmed | https://www.buffalobills.com/news/important-dates-on-the-2014-nfl-calendar-12566429 ; https://www.neworleanssaints.com/news/2014-national-football-league-important-dates-12566525 |
| C25 | Deadline to withdraw an RFA qualifying offer and substitute a "June 15 tender" | Monday, June 16, 2014 | Late January 2014 | **Unverified** (one search summary) | https://www.profootballrumors.com/2014/01/important-2014-nfl-offseason-dates |
| C26 | Training camp report dates for all 32 clubs released | July 14, 2014. Real per-club report dates are not imported. | **Gate: July 14, 2014** | Confirmed (date) | https://profootballtalk.nbcsports.com/2014/07/14/2014-nfl-training-camp-reporting-dates-locations/ (dated URL) ; https://www.nfl.com/news/2014-nfl-training-camp-reporting-dates-and-locations-0ap2000000364802 |

### 1d. Offseason program, OTA, minicamp and training camp limits (2011 CBA Articles 21, 22 and 23; unchanged for 2014)

| # | Rule | Label | Sources |
|---|---|---|---|
| R1 | Official voluntary offseason program: **nine weeks in three phases**. | Confirmed | https://overthecap.com/collective-bargaining-agreement/article/21 ; https://www.foxsports.com/stories/nfl/article-21-offseason-workouts ; https://www.ninersnation.com/2014/4/21/5635026/breaking-down-the-nfl-cba-the-offseason-workout-program (dated April 21, 2014) |
| R2 | **Phase One:** first two weeks; strength and conditioning and physical rehabilitation only. | Confirmed | Same as R1 |
| R3 | **Phase Two:** next three weeks; on-field individual instruction and drills, and team practice on a "separates" basis. No live contact and no offense against defense. | Confirmed | Same as R1 |
| R4 | **Phase Three:** final four weeks; up to **10 days of OTAs**, no live contact; 7-on-7, 9-on-7 and 11-on-11 permitted. At most three OTA days in each of the first two weeks of Phase Three; at most four OTA days in either the third or fourth week, with the mandatory veteran minicamp in the other week. | Confirmed | https://nflpaweb.blob.core.windows.net/website/Departments/Player-Affairs/Article-21-Off-Season-Workouts.pdf ; Fox Sports (R1) |
| R5 | Outside OTA and minicamp days: facility time at most four hours per day, four days per week, no weekends; on-field time at most 90 minutes per day. OTA days: at most six hours at the facility and two hours on the field per player. | Confirmed (four hours, four days, no weekends). Ninety-minute and OTA six-hour/two-hour figures: **Unverified** (one search summary) | https://www.ninersnation.com/2014/4/21/5635026/breaking-down-the-nfl-cba-the-offseason-workout-program ; Over The Cap Article 21 |
| R6 | **Mandatory veteran minicamp:** one per club, at most three days plus one day for physicals, on weekdays; counts as one of the nine program weeks. | Confirmed | https://overthecap.com/collective-bargaining-agreement/article/22 ; https://bleacherreport.com/articles/2098532-everything-nfl-fans-should-know-about-mandatory-minicamps |
| R7 | **New-head-coach voluntary veteran minicamp:** only a club that hired a new head coach since the end of the preceding season may hold one additional voluntary veteran minicamp, before the draft. **Not available to Jacksonville in 2014.** Its exact placement relative to the program start (a search summary said "three weeks after the start") is **Unverified**. | Confirmed (existence and new-coach limit); timing detail Unverified | Over The Cap Article 22 ; https://www.nfl.com/news/10-teams-with-new-head-coaches-kick-off-voluntary-workouts-this-week |
| R8 | **Training camp report limit:** a veteran may not be required to report earlier than **15 days before the club's first scheduled preseason game, or July 15, whichever is later**. Rookies and first-year players may not be required to report earlier than **seven days before** the club's veteran mandatory report date. Any exception for quarterbacks or injured players is **Unverified**. | Confirmed | https://overthecap.com/collective-bargaining-agreement/article/23 ; https://www.neworleanssaints.com/news/2014-national-football-league-important-dates-12566525 (July 15 item) |

### 1e. Preseason, roster limits and regular season

| # | Event or rule | Date/time | Public by | Label | Sources |
|---|---|---|---|---|---|
| C27 | Hall of Fame Game (opens the preseason) | Sunday, August 3, 2014, 8:00 PM ET, Canton, Ohio. Recorded as a date only. | No later than the April 23, 2014 schedule release (earlier release **Unverified**) | Confirmed (date) | https://www.profootballhof.com/events/2014/08/events-nfl-hall-of-fame-game/ ; https://bleacherreport.com/articles/2149526-pro-football-hall-of-fame-game-2014-game-info-and-preview-for-bills-vs-giants ; https://www.nfl.com/news/buffalo-bills-new-york-giants-to-kick-off-2014-nfl-preseason-0ap2000000329631 |
| C28 | Offseason roster limit | 90 players | Before branch entry | Confirmed (unchanged from 2013; see C2 sources and the 2013 file) | Bleacher Report (C1) ; Behind the Steel Curtain (C2) |
| C29 | **First roster cutdown: 75** | **Tuesday, August 26, 2014**, 4:00 PM ET | No later than August 3, 2014 (Phinsider calendar); presence in the December 2013 calendar **Unverified** | Confirmed (date). Time of day: **Unverified** | https://www.bloggingtheboys.com/2014/8/20/6048057/nfl-calendar-2014-roster-cuts-ir-designations-trade-deadline-important-dates ; https://www.cbssports.com/nfl/news/2014-nfl-roster-cuts-tracking-teams-down-to-75/ ; https://www.bigcatcountry.com/2014/8/24/6062381/jaguars-nfl-roster-cuts-2014-tracker |
| C30 | **Final roster cutdown: 53** | **Saturday, August 30, 2014, 4:00 PM ET** | Same as C29 | Confirmed | https://www.cbssports.com/nfl/news/2014-final-nfl-cuts-teams-trim-rosters-down-to-53-players/ ; https://www.acmepackingcompany.com/2014/8/30/6083171/packers-roster-cut-deadline-tracker-2014-53-man ; Blogging The Boys (C29) |
| C31 | Game-day active list | 46 of 53 dress (unchanged from 2013) | Before branch entry | Confirmed (unchanged rule; see 2013 file) | `library/2013_league_calendar_and_financial_rules.md` |
| C32 | **Practice squad size, 2014: 10** (expanded from 8). Also: a practice-squad season counts toward the three-season limit only with at least **six** games on the squad (was three); each club may carry at most **two** practice-squad players with no more than **two** accrued seasons (previously no more than one accrued season). Agreed for 2014 and 2015. | Agreement announced **Tuesday, August 19, 2014**; effective immediately | **Gate: August 19, 2014** (until then the 8-player rule governs) | Confirmed | https://nflpa.com/press/nfl-nflpa-agree-to-expand-practice-squads ; https://www.washingtonpost.com/news/football-insider/wp/2014/08/19/nfl-expanding-practice-squads-to-10-players/ (dated URL) ; https://www.si.com/nfl/2014/08/19/nfl-practice-squad-gets-bigger (dated URL) ; https://www.patriots.com/news/nfl-practice-squads-expand-to-10-players-200576 |
| C33 | **Regular-season kickoff** | **Thursday, September 4, 2014**; regular season runs through Sunday, December 28, 2014 (17 weeks, 256 games, one bye per club). The kickoff game's clubs are not recorded (one of them was set by a real Super Bowl XLVIII result). | Gate: April 23, 2014 schedule release (presence of the September 4 date in the December 2013 calendar is **Unverified**) | Confirmed | https://en.wikipedia.org/wiki/2014_NFL_season ; https://fbschedules.com/2014-nfl-schedule-announced/ ; https://www.nfl.com/news/complete-2014-nfl-schedule-0ap2000000343699 |
| C34 | **Trade deadline** | **Tuesday, October 28, 2014, 4:00 PM ET** (after Week 8) | No later than August 3, 2014 | Confirmed | https://bleacherreport.com/articles/2229739-nfl-trade-deadline-2014-date-end-time-and-teams-in-need-of-a-shake-up ; https://www.thephinsider.com/2014/8/3/5963741/nfl-calendar-2014-when-are-roster-cuts-other-important-dates ; Blogging The Boys (C29) |
| C35 | Jacksonville's designated home game against the NFC East opponent Dallas at **Wembley Stadium, London** (International Series) | Matchup confirmed Thursday, October 24, 2013; game date Sunday, November 9, 2014 (Week 10), 1:00 PM ET | Matchup: October 24, 2013. Game date: no later than the April 23, 2014 schedule release (an SI wire item dated November 28, 2013 titled "NFL announces 2014 London dates" may have published it earlier; content **Unverified**) | Confirmed (matchup and date). This is a pre-branch league scheduling decision; whether the branch honours it is for the calendar owner to decide, not this file | https://www.wembleystadium.com/news/2013/oct/24/nfl-confirm-2014-international-series-fixtures (dated URL) ; https://www.nfl.com/news/six-nfl-teams-set-for-2014-international-series-games-in-london-0ap2000000268789 ; https://www.raiders.com/news/2014-international-series-games-confirmed-11617947 ; https://www.jaguars.com/news/2014-international-series-schedule-finalised-12867159 ; https://www.si.com/si-wire/2013/11/28/nfl-announces-2014-london-dates |

### 1f. 2014 postseason (dates and sites only; no participant or result)

| # | Event | Date | Public by | Label | Sources |
|---|---|---|---|---|---|
| P1 | Wild Card round | Saturday January 3 and Sunday January 4, 2015 | Before branch entry (season structure); slot times only when the league publishes them | Confirmed | https://fbschedules.com/2014-nfl-playoff-schedule/ ; https://en.wikipedia.org/wiki/2014%E2%80%9315_NFL_playoffs |
| P2 | Divisional round | Saturday January 10 and Sunday January 11, 2015 | Same | Confirmed | Same as P1 ; https://fbschedules.com/nfl-playoff-schedule-2014-15-divisional-round-set/ |
| P3 | Conference championships | Sunday, January 18, 2015 | Same | Confirmed | Same as P1 |
| P4 | Pro Bowl | Sunday, January 25, 2015, University of Phoenix Stadium, Glendale, Arizona | Site gate: April 9, 2014 (C16) | Confirmed | https://en.wikipedia.org/wiki/2015_Pro_Bowl ; https://espnpressroom.com/press-release/2015-nfl-pro-bowl-espn/ |
| P5 | **Super Bowl XLIX** | **Sunday, February 1, 2015, University of Phoenix Stadium, Glendale, Arizona.** Site awarded by owners' vote announced October 11, 2011. | Site: October 11, 2011 | Confirmed | http://www.nfl.com/news/story/09000d5d82309487/article/owners-vote-arizona-as-super-bowl-host-for-third-time ; https://en.wikipedia.org/wiki/Super_Bowl_XLIX (cited for date and site only) ; https://www.patriots.com/press-room/super-bowl-xlix (cited for date only) |

The 2014 postseason format (12 clubs, seeding, byes, reseeding) is the same rule set recorded in `library/2013_postseason_format_and_schedule.md` §1. This file did not separately re-verify that it was unchanged for 2014; treat "unchanged for 2014" as **Unverified** until checked.

## 2. Salary cap and financial rules, 2014

| # | Item | Value | Public by | Label | Sources |
|---|---|---|---|---|---|
| F1 | **2014 salary cap** | **$133,000,000 per club**, up from $123,000,000 in 2013; then the highest in league history (previous high $127,997,000 in 2009). Clubs had to be compliant by 4:00 PM ET March 11, 2014. | **Gate: Friday, February 28, 2014** | Confirmed | https://www.buffalobills.com/news/nfl-announces-2014-salary-cap-12688830 ; https://www.denverbroncos.com/news/2014-nfl-salary-cap-set-12724393 ; https://www.acmepackingcompany.com/2014/2/28/5458418/nfl-sets-salary-cap-at-133-million-packers-have-35-million-to-spend (dated URL) ; https://www.cbssports.com/nfl/news/2014-nfl-salary-cap-set-at-133m/ ; https://www.milehighreport.com/2014/2/28/5458324/broncos-cap-space-2014 (dated URL) ; Tom Pelissero's published cap history (https://x.com/TomPelissero/status/2017326690779730379) |
| F1a | **Pre-gate projections (usable before February 28, 2014 only as labelled projections)** | About $126.3 million (reported December 2013); "approach $130 million" (SI, February 20, 2014); ESPN NFL Nation cap-space tables were built on $132 million before the memo | December 2013 onward, each on its own date | Confirmed as projections that were published; they are not the cap | https://steelersdepot.com/2013/12/2014-nfl-salary-cap-projection/ ; Big Cat Country (gate note) ; https://www.si.com/nfl/2014/02/20/nfl-salary-cap-2014 ; https://www.espn.com/blog/nflnation/post/_/id/118418/inside-slant-cap-space-based-on-132m |
| F2 | Minimum cash spend | Unchanged 2011 CBA rule for the **2013 to 2016** measurement period: each club must reach **89%** of its aggregate salary caps in cash over the four years, and the league as a whole **95%**. Not a single-season 2014 floor; a 2014 shortfall is not by itself a violation. | Before branch entry | Confirmed (consistent with the corrected rule in the 2013 file) | https://www.lawinsport.com/topics/item/an-introductory-guide-to-the-nfl-s-salary-cap ; https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/per-team-spending-minimum-doesnt-apply-until-2013 ; 2013 file |
| F3 | **Top-51 rule** | From the first day of the league year (March 11, 2014) until the club's first regular-season game, a club's cap figure counts its **51 highest cap numbers**, plus all bonus proration and other bonus/cap charges for every player (including those outside the Top 51). From the first regular-season game, every contract counts: the 53, injured reserve, PUP and the practice squad. | Before branch entry | Confirmed | https://russellstreetreport.com/2014/09/02/baltimore-ravens-salary-cap/ask-the-cap-man-whats-the-rule-of-51/ (dated URL) ; https://www.behindthesteelcurtain.com/pittsburgh-steelers-nfl-features-news-blog-long-form/2016/2/26/11111236/nfl-101-explaining-futures-contracts-and-the-rule-of-51 ; 2013 file |
| F4 | Cap carryover | Unused cap room may be carried into the next league year under 2011 CBA Article 13 §6 by written notice to the league. **Deadline wording conflicts across sources**: one describes notice "prior to 4:00 PM on the day **following** the club's final regular-season game"; a 2014-era description says "the day **before**" that game; a third says "the Tuesday after the regular season". For the 2013 to 2014 carryover the deadline fell at or near December 29 to 31, 2013, before branch entry, so the branch's carryover amount is either already on the branch record or must be marked unresolved; it must not be taken from any real club's reported rollover. | Before branch entry | Confirmed (rule exists). Notice deadline: **Unverified** | https://overthecap.com/collective-bargaining-agreement/article/13 ; https://russellstreetreport.com/salarycap/nfl-salary-cap-faqs/ ; https://www.capandtrade.football/p/nfl-salary-cap-carryover |
| F5 | Rookie wage scale rules | Unchanged 2011 CBA Article 7 rules as recorded in the 2013 file: fixed four-year contracts for drafted rookies, fifth-year club option for first-round picks only, a Rookie Compensation Pool slotted by draft position, and the 25% rule. The **2014 pool dollar total** was not found in any official source; a figure of about $955 million appears only as a fan-forum and commentator estimate and is **Unverified; do not use**. | Before branch entry (rules) | Confirmed (rules unchanged). Pool total: **Unverified** | https://overthecap.com/collective-bargaining-agreement/article/7 ; https://overthecap.com/explaining-the-nfls-rookie-salary-cap ; https://bleacherreport.com/articles/2056910-nfl-rookie-salary-cap-2014-explaining-pay-scale-rules-and-minimum-contracts ; 2013 file |
| F6 | Practice squad minimum weekly pay, 2014 | **$6,300 per week** (no maximum) | Before branch entry (2011 CBA schedule) | Confirmed | https://www.bloggingtheboys.com/2014/8/26/6069461/2014-nfl-practice-squad-primer-rules-size-eligibility-salary ; https://www.thephinsider.com/2014/8/30/6086009/nfl-practice-squad-salary-eligibility-and-rules ; https://en.wikipedia.org/wiki/Practice_squad |

### 2a. 2014 minimum salaries by credited seasons (2011 CBA Article 26 schedule)

| Credited seasons | 2014 minimum | Label |
|---|---:|---|
| 0 | $420,000 | Confirmed (Steelers Depot 2011-2014 table; Pro Football Rumors; both search texts state $420K for 2014) |
| 1 | not recorded | **Unverified**: no search text independently stated the value; left unresolved |
| 2 | not recorded | **Unverified**: no search text independently stated the value; left unresolved |
| 3 | $645,000 | **Unverified**: one search text stated it, and that text may echo the query wording |
| 4 to 6 | $730,000 | **Unverified**: same caveat as 3 |
| 7 to 9 | $855,000 | **Unverified**: same caveat as 3 |
| 10 or more | $955,000 | Confirmed (Steelers Depot; Pro Football Rumors) |

Sources: https://steelersdepot.com/2011/07/2011-2014-nfl-minimum-base-salaries/ ; https://www.profootballrumors.com/2014/02/minimum-maximum-salaries ; https://overthecap.com/collective-bargaining-agreement/article/26/section/1 ; https://overthecap.com/minimum-salaries . A future session with page access should read the Article 26 table directly before any minimum-salary accounting at the unverified tiers.

### 2b. 2014 franchise tag values by position (non-exclusive; cap = $133M)

**Gate: February 28, 2014** (released by the NFL together with the cap). Before that date, only labelled projections (for example the CBS Sports projections reported February 17, 2014: https://www.thephinsider.com/2014/2/17/5420198/what-are-the-nfl-franchise-tag-amounts) may be used. **Label: Confirmed** (NFL.com release as quoted in two separate search texts, plus the ESPN wire table at http://www.espn.com/espn/wire?id=10545749; each value below appeared identically in both passes). Values appeared rounded to the thousand dollars; the full-dollar official memo was not read.

| Position | Value |
|---|---:|
| QB | $16,192,000 |
| DE | $13,116,000 |
| WR | $12,312,000 |
| CB | $11,834,000 |
| OL | $11,654,000 |
| LB | $11,455,000 |
| DT | $9,654,000 |
| RB | $9,540,000 |
| S | $8,433,000 |
| TE | $7,035,000 |
| K/P | $3,556,000 |

Source: https://www.nfl.com/news/nfl-releases-2014-franchise-transition-tag-numbers-0ap2000000330088

### 2c. 2014 transition tag values by position (cap = $133M)

**Gate: February 28, 2014.** **Label: Confirmed** for QB, RB and WR (stated in both passes' search texts); the remaining positions appeared in one search text only (pass 2) and are **Unverified** until the NFL.com or ESPN table is read directly.

| Position | Value | Label |
|---|---:|---|
| QB | $14,666,000 | Confirmed |
| DE | $10,633,000 | Unverified |
| WR | $10,176,000 | Confirmed |
| CB | $10,081,000 | Unverified |
| OL | $10,039,000 | Unverified |
| LB | $9,754,000 | Unverified |
| DT | $8,060,000 | Unverified |
| RB | $8,033,000 | Confirmed |
| S | $7,253,000 | Unverified |
| TE | $6,106,000 | Unverified |
| K/P | $3,205,000 | Unverified |

Sources: https://nfl.com/news/story/0ap2000000330088/article/nfl-releases-2014-franchise-transition-tag-numbers ; http://www.espn.com/espn/wire?id=10545749

### 2d. 2014 restricted free agent tender amounts

**Gate: the published tender amounts were reported March 6, 2014** (dated Big Cat Country and Falcoholic URLs). Tenders had to be submitted by 4:00 PM ET March 11 (C10). The exact day the league first circulated the amounts to clubs is **Unverified**; treat them as public from March 6, 2014.

| Tender | 2014 amount | Compensation if the prior club declines to match | Label |
|---|---:|---|---|
| First round | $3,113,000 | First-round pick | Confirmed |
| Second round | $2,187,000 | Second-round pick | Confirmed |
| Original round | $1,431,000 | Pick in the player's original draft round | Confirmed |
| Right of first refusal only | $1,431,000 | None (right to match only) | Confirmed |

Sources: https://www.bigcatcountry.com/2014/3/6/5478230/2014-jaguars-restricted-free-agents-tender-amounts (dated URL) ; https://www.thefalcoholic.com/2014/3/6/5476122/nfl-announces-restricted-free-agent-tenders-for-2014 (dated URL) ; https://overthecap.com/explaining-nfl-free-agent-designations . Whether the 2011 CBA's "110% of prior salary" alternative applies to a given player is a player-specific contract question, not recorded here.

## 3. 2014 scheduling formula (for deriving branch opponents)

**Formula (2002 realignment, in force for 2014): 16 games.**

| # | Component | Games | Label | Sources |
|---|---|---:|---|---|
| S1 | Home and away against each division rival | 6 | Confirmed | https://operations.nfl.com/calendar-events/nfl-schedule/making-the-schedule ; https://en.wikipedia.org/wiki/NFL_regular_season |
| S2 | All four clubs of one other division in the same conference, on a **three-year rotation** (two home, two away) | 4 | Confirmed | Same as S1 ; https://en.wikipedia.org/wiki/2002_NFL_season |
| S3 | All four clubs of one division in the other conference, on a **four-year rotation** (two home, two away) | 4 | Confirmed | Same as S1 |
| S4 | **Same-place-finish games:** one game against the club in each of the **two remaining same-conference divisions** (the two divisions not drawn in S2) that finished in the **same place** in its division in the previous season as this club did in its own (first plays first, second plays second, and so on). One home, one away. | 2 | Confirmed | Same as S1 ; https://www.nbcsportsboston.com/nfl/nfl-schedule-explained-how-it-works/609618/ |

**2014 AFC South rotation (standings-independent):** every AFC South club plays **all of the AFC North** (S2) and **all of the NFC East** (S3). The two remaining AFC divisions for S4 are therefore the **AFC East** and the **AFC West**. Label: **Confirmed** (Big Cat Country, dated URL December 29, 2013, for Jacksonville; ESPN NFL Nation's 2014 opponents list and the Titans' 2014 opponents for Tennessee; Jaguars.com's 2014 home-schedule release).

**Jacksonville's 2014 home/away split for the rotation games (standings-independent, set by the formula):** home against **Cleveland, Pittsburgh, New York Giants and Dallas** (the Dallas game designated as Jacksonville's London home game, C35); away at **Baltimore, Cincinnati, Philadelphia and Washington**. For S4, Jacksonville **hosts the same-place AFC East club** and **visits the same-place AFC West club**. Label: **Confirmed** (Big Cat Country December 29, 2013, and the Jaguars.com home-schedule release; the Titans' reported road games at Baltimore, Cincinnati and Philadelphia fit the same grid).

**Branch derivation rule.** The S4 opponents come from the **branch's** final 2013 AFC East and AFC West standings, matched to the branch's final 2013 AFC South place for Jacksonville (and likewise for every other club). Do not import the real "third-place" opponents: Jacksonville's real 2013 place and the real 2013 standings differ from the branch. Game dates, times and the bye come only from the April 23, 2014 release gate (C17), and the branch schedule owner decides how real date rails map onto branch pairings.

Sources for §3: https://www.bigcatcountry.com/2013/12/29/5254478/jaguars-nfl-schedule-2014-opponents (dated URL) ; https://www.jaguars.com/news/jaguars-announce-2014-home-schedule-11617599 ; https://www.espn.com/blog/nflnation/post/_/id/110538/opponents-for-the-2014-nfl-season ; https://bleacherreport.com/articles/2023214-2014-tennessee-titans-schedule-full-listing-of-dates-times-and-tv-info ; https://operations.nfl.com/calendar-events/nfl-schedule/making-the-schedule

## 4. 2014 draft-order rules (applied to the branch's 2013 season)

| # | Rule | Label | Sources |
|---|---|---|---|
| D1 | **Non-playoff clubs (20 in the 12-club playoff era) select 1 to 20** in reverse order of regular-season winning percentage. | **Corrected** (see V2) | https://www.patriots.com/news/2014-patriots-draft-101-197921 ; https://stripehype.com/2014/02/03/2014-nfl-draft-order-set-super-bowl/ (dated URL) ; https://www.nfl.com/standings/tie-breaking-procedures |
| D2 | **Playoff clubs select 21 to 32 by round of elimination:** Wild Card losers 21 to 24, Divisional losers 25 to 28, Conference Championship losers 29 to 30, **Super Bowl loser 31, Super Bowl winner 32**. Within each elimination group, order is by regular-season record (worse record picks earlier). | Confirmed | Patriots Draft 101 ; Stripe Hype (D1) ; https://www.foxnews.com/sports/2014-nfl-draft-order-finalized |
| D3 | **Ties within any group (except Super Bowl winner and loser):** broken by **strength of schedule** (the club whose opponents had the lower combined winning percentage picks earlier). | Confirmed | https://www.nfl.com/standings/tie-breaking-procedures ; https://www.profootballnetwork.com/nfl-draft-tiebreakers/ ; nesn.com, December 2013 item on the tentative 2014 draft order procedure (URL slug withheld: it names real draft-order positions) (dated URL; cited for the procedure only) |
| D4 | **If strength of schedule is also tied:** apply the **division tiebreakers** if the clubs are in the same division, otherwise the **conference tiebreakers** if in the same conference (clubs in different conferences go to the next step), using the reverse sense (the club that would lose the tiebreaker picks earlier). If still tied, a **coin flip**. The within-procedure detail for more than two tied clubs and for inter-conference ties beyond coin flip is **Unverified**. | Confirmed (sequence); multi-club detail Unverified | Same as D3 ; https://sports.yahoo.com/heres-tiebreakers-draft-picks-implications-235943388.html |
| D5 | **Rotation within tied groups:** clubs tied on record rotate their positions round by round within the tied block in later rounds. This is a long-standing rule but no 2014-era source text confirming it was found. | **Unverified** | None found in search text |
| D6 | **Compensatory picks:** awarded by the NFL Management Council's formula (salary, playing time and postseason honours of qualifying unrestricted free agents lost and signed the prior year; not every free agent qualifies); a club receives picks equal to its **net loss** of qualifying free agents, **up to four**; placed at the **end of rounds 3 to 7**; **32 in total**; **cannot be traded in the 2014 draft** (a later rule change, voted in 2016, made them tradable; it does not apply to 2014). Announced at the Annual Meeting (March 24, 2014; C12). The formula's detailed weights are not public. Branch compensatory awards must be computed from branch 2013 free-agency records or marked unresolved; the real 2014 awards are not imported. | Confirmed (all elements except the fill mechanism) | https://www.thephinsider.com/2014/3/26/5548312/football-101-compensatory-picks (dated URL) ; https://bleacherreport.com/articles/2003927-nfl-compensatory-picks-2014-rules-formula-explanation-and-latest-projections ; https://www.steelers.com/news/compensatory-picks-a-mystery-history-12801380 ; https://bleacherreport.com/articles/2591148-nfl-competition-committee-votes-compensatory-picks-can-be-traded-next-year |
| D7 | **Fill to 32:** if the formula yields fewer than 32 compensatory picks, additional selections are added to reach 32. One search summary said they go to the clubs with the worst prior-season records; the exact placement and order in 2014 are **Unverified**. | **Unverified** | Same as D6 |
| D8 | **Forfeited picks:** a pick forfeited by league discipline is removed from the draft and the clubs after it move up one slot in that round. No 2014-era source text was found confirming the mechanism. | **Unverified** | None found in search text |

**Gate note for §4.** The rules are league procedure, public before branch entry. The **order itself** is branch-resolved: it comes from the branch's 2013 regular-season standings, the branch's 2013 postseason results, the rules above, branch pick trades and branch compensatory awards. Real tentative or final 2014 orders (for example the December 2013 NFL tentative order, the February 3, 2014 order after Super Bowl XLVIII, and the March 24, 2014 final order with compensatory picks) are never imported.

## 5. Verification pass: corrections and discrepancies

- **V1. Negotiating-window start time: Corrected.** Big Cat Country's December 21, 2013 summary gave the start as 4:00 PM ET Saturday, March 8, and one pass 1 search summary gave "noon on March 10". Pass 2 found four independent sources (NFL.com headline "kicks off today at noon ET", Steelers.com, Broncos.com FAQ, Bleeding Green Nation dated March 8, 2014) giving **12:00 noon ET Saturday, March 8, 2014**, through 3:59:59 PM ET March 11. The noon March 8 start controls; "4:00 PM" and "March 10" were errors in the summaries.
- **V2. Non-playoff pick range: Corrected.** One pass 2 search summary, quoting a Record and Fact Book, said non-playoff clubs "select in the first through 18th positions". That wording belongs to the 14-club playoff era (from the 2020 season). In the 2013 season's 12-club format there were 20 non-playoff clubs, so they selected **1 to 20**, and playoff clubs 21 to 32, as the 2014-era sources (Patriots Draft 101, Stripe Hype February 3, 2014) state.
- **V3. RFA offer-sheet deadline.** A pass 1 query used "April 25"; no source supports it. Every source gives **May 2, 2014** (the draft moved to May 8 to 10, and the offer-sheet deadline moved with it).
- **V4. Combine dates.** A pass 1 query used "February 22 to 25"; sources give the event as **February 19 to 25**, with on-field workouts February 22 to 25. This matches `library/2014_draft_information_gates.md`.
- **V5. Jacksonville's real 2014 program dates rejected** (see note after C20).
- **V6. Minimum-salary tiers.** Pass 1 supplied candidate values for every tier in the query. Pass 2 found search text independently stating only the 0 and 10+ values; the 3, 4 to 6 and 7 to 9 values appeared once in text that may echo the query, and the 1 and 2 values not at all. Those tiers are downgraded to Unverified or left unrecorded (§2a) rather than kept.
- **V7. Transition tag table.** Pass 1 found QB, RB and WR values; pass 2 found the full table in one search text. Only the three twice-found values are Confirmed (§2c).
- **V8. Carryover deadline.** Three incompatible descriptions of the notice deadline were found (F4); none is adopted.

## 6. Not verified (open items for a session with page access)

- Official release date of the 2014 league calendar (December 20, 2013 per one summary).
- Right-of-first-refusal deadline (May 7) and June 15 tender substitution deadline (June 16).
- The precise post-draft undrafted-free-agent signing moment.
- OTA-day six-hour and two-hour limits; the 90-minute on-field limit outside OTAs; the placement rule for the new-head-coach voluntary minicamp; report-date exceptions for quarterbacks and injured players.
- Whether the September 4 kickoff and the August 26/30 cutdown dates were in the December 2013 calendar (they are gated to their confirmed publication dates meanwhile).
- The 75-cut time of day.
- 2014 minimum salaries for 1 to 9 credited seasons; transition tag values other than QB, RB and WR; the 2014 Rookie Compensation Pool total.
- The cap-carryover notice deadline.
- Draft-order rotation within tied blocks, multi-club tie detail, the compensatory fill-to-32 mechanism and the forfeited-pick mechanism.
- Whether the 2014 postseason format was unchanged from 2013 (assumed but not re-verified here).
