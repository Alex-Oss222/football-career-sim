# Library: 2014 NFL Draft Information Gates

**Status:** Runtime date-gating companion for the 2014 draft cycle. Research pass (pass 1 of 2) and verification pass (pass 2 of 2) complete. Pass 2 corrections are applied in the body and listed in the "Verification pass" section at the end.
**Purpose:** Prevent later pre-draft information from leaking backward into earlier simulation dates.
**Research date:** 2026-09-28. Branch date at research time: November 24 to December 1, 2013.

This file controls **when** 2014 draft-cycle information may become available to the simulation. It is modelled on `library/2013_draft_information_gates.md`. The companion eligibility file is `library/2014_draft_pool_registry.md`. There is no 2014 scouting snapshot yet.

## Source-access limitation (both passes)

During both passes, direct page retrieval (WebFetch) was blocked by the session's network egress policy. Only a search engine was reachable. Every fact below, including every pass 2 confirmation, rests on search-result text attributed to the cited URL, not on a first-hand read of the full page. "Confirmed" in this file means that at least two independent search results (different publishers, or a publisher plus a dated URL) agreed. Items that could not be settled that way are marked **unverified**.

## Core rule

At any simulation date, use only information that had become public by that date. A later board, all-star practice report, combine result, pro-day result, medical update, declaration or special-eligibility decision stays unavailable until its real publication or event date.

Never load a later snapshot merely because it exists in the repository. The real 2014 selection order, destinations, and anything that happened to any prospect after he was selected are quarantined history and never enter the simulation.

## Branch-resolved items (not imported)

These are determined by the simulation branch, not by real history:

- **2014 draft order.** Jacksonville's slot, and every other club's, comes from the simulated 2013 standings and the branch's playoff results, under the Document 2 tiebreak rules. The real 2014 order is not imported.
- **Traded picks.** Pick ownership follows the branch transaction record (for example, Jacksonville's 2014 second-round pick belongs to Washington in this branch, per `career/2013/scouting/2014_draft_focus_directive.md`).
- **Compensatory picks.** Real 2014 compensatory awards depended on real 2013 free-agent gains and losses. The branch changed 2013 free agency, so the real awards are not imported. They must be resolved from branch free-agency records under the compensatory formula, or marked unresolved.
- **Senior Bowl coaching staffs.** In real history the Atlanta and Jacksonville staffs were announced as the 2014 Senior Bowl coaches on Thursday, January 2, 2014 (confirmed: https://www.nfl.com/news/falcons-jaguars-staffs-to-coach-senior-bowl-0ap2000000308308 ; https://www.jaguars.com/news/falcons-jaguars-to-coach-2014-game-12344336 ; dated URL https://www.bigcatcountry.com/2014/1/2/5266876/2014-senior-bowl-roster-jaguars-coaches-south-team). That assignment rested on real 2013 results and real staff decisions, so in this branch it is branch-resolved and must not be imported. The Senior Bowl's selection rule for its coaching staffs remains **unverified**.

## Already public before the branch date

### Draft dates and venue (public Tuesday, May 28, 2013)

The NFL announced that the 2014 NFL Draft would be held **May 8 to 10, 2014, at Radio City Music Hall, New York**, moved from its customary late-April window because of a scheduling conflict at the venue (an April show at Radio City). Confirmed: the announcement is described as made on a Tuesday, and the Washington Times URL is dated May 28, 2013, which was a Tuesday.

Sources:
- NFL.com: https://www.nfl.com/news/2014-nfl-draft-set-for-may-8-10-at-radio-city-music-hall-0ap1000000207063
- ESPN: https://www.espn.com/nfl/story/_/id/9318615/2014-nfl-draft-held-8-10-radio-city-music-hall
- Washington Times, dated URL 2013/may/28: https://www.washingtontimes.com/news/2013/may/28/2014-nfl-draft-date-moved-may-change-might-become-/
- Pass 2 independent confirmations: https://www.patriots.com/news/2014-nfl-draft-to-be-may-8-to-10-at-radio-city-music-hall-188836 ; https://www.cbsnews.com/newyork/news/2014-nfl-draft-to-be-held-from-may-8-10-at-radio-city/

**First-round start time:** 8:00 PM ET on Thursday, May 8, 2014, with rounds 2 and 3 on Friday, May 9 and rounds 4 to 7 on Saturday, May 10. Confirmed from pre-draft May 2014 reports (https://www.buffalobills.com/news/2014-nfl-draft-facts-figures-12964777 ; https://espnpressroom.com/press-release/espns-presentation-of-the-2014-nfl-draft/) and the round split from AP text of January 2014 (https://www.cbsnews.com/texas/news/record-98-underclassmen-eligible-for-nfl-draft). When the 8:00 PM start time was first published is **unverified**; treat it as public no later than those May 2014 reports.

## December 2013: end of the college season

At the branch date (November 24 to December 1, 2013):

- the 2013 FBS regular season is in its final weeks; it ran **August 29 to December 14, 2013** (confirmed: https://en.wikipedia.org/wiki/2013_NCAA_Division_I_FBS_football_season ; https://fbschedules.com/2013-college-football-schedule/). The last regular-season date is the Army-Navy game, played **Saturday, December 14, 2013**, at Lincoln Financial Field, Philadelphia (confirmed: https://www.ncaa.com/game/football/fbs/2013/12/14/army-navy ; https://www.army.mil/article/117072/army_navy_football_game_2013). No result may be imported before it occurs;
- conference championship games have not been played;
- no bowl game has been played;
- no all-star roster is final, no declaration has closed, and no combine or pro-day information exists.

Conference championships (dates and venues only; no result may be imported before it occurs):

- MAC Championship Game: Friday, December 6, 2013, Ford Field, Detroit. Confirmed: https://en.wikipedia.org/wiki/2013_MAC_Championship_Game ; https://www.fordfield.com/events/detail/mac-championship-2 (second source by search text only).
- SEC Championship Game: Saturday, December 7, 2013, Georgia Dome, Atlanta. Source: https://en.wikipedia.org/wiki/2013_SEC_Championship_Game (pass 2 did not find a second source; date consistent with the other December 7 games; venue **not independently re-confirmed**).
- ACC Championship Game: Saturday, December 7, 2013, Bank of America Stadium, Charlotte. Confirmed in pass 2: https://en.wikipedia.org/wiki/2013_ACC_Championship_Game ; https://fbschedules.com/2013-acc-championship-football-tickets-duke-florida-state/
- Big Ten Championship Game: Saturday, December 7, 2013, Lucas Oil Stadium, Indianapolis. Confirmed in pass 2: https://en.wikipedia.org/wiki/2013_Big_Ten_Football_Championship_Game ; https://fbschedules.com/2013-big-ten-championship-football-tickets-michigan-state-ohio-state/
- Pac-12 Championship Game: Saturday, December 7, 2013, Sun Devil Stadium, Tempe. Confirmed: https://en.wikipedia.org/wiki/2013_Pac-12_Football_Championship_Game ; https://pac-12.com/article/2013/11/30/football-championship-game-will-be-tempe (the Pac-12 announced the Tempe site on November 30, 2013).
- Mountain West Championship Game: Saturday, December 7, 2013, Bulldog Stadium, Fresno. Confirmed in pass 2: https://en.wikipedia.org/wiki/2013_Mountain_West_Conference_Football_Championship_Game ; https://utahstateaggies.com/news/2013/12/2/Utah_State_Will_Face_24th_Ranked_Fresno_State_in_Inaugural_Mountain_West_Football_Championship_Game_Saturday_Night_on_CBS (dated URL December 2, 2013).

Bowl season: **December 21, 2013 to January 6, 2014**, 35 bowl games, ending with the BCS National Championship Game at the Rose Bowl, Pasadena, on January 6, 2014. Confirmed: https://en.wikipedia.org/wiki/2013%E2%80%9314_NCAA_football_bowl_games ; https://fbschedules.com/2013-14-college-football-bowl-schedule/

FCS and Division II postseason (researched in pass 2):

- FCS playoffs: 24-team bracket; first round Saturday, November 30, 2013; rounds through December 21; championship game Saturday, January 4, 2014, Toyota Stadium, Frisco, Texas. Sources: https://en.wikipedia.org/wiki/2013_NCAA_Division_I_FCS_football_season ; bracket PDF https://www.ncaa.com/sites/default/files/external/gametool/brackets/football_fcs_2013.pdf (single publisher family plus NCAA PDF; treat as confirmed for dates, search text only).
- Division II championship game: Saturday, December 21, 2013, Braly Municipal Stadium, Florence, Alabama. Source: https://en.wikipedia.org/wiki/2013_NCAA_Division_II_Football_Championship_Game (**single source**).
- Whether West Alabama played in the 2013 Division II playoffs, and so the date of its last 2013 game, is **unverified**.

Postseason college honors become usable only on their dated announcement. Dates found in pass 2:

- AP All-SEC team: announced on or about Monday, December 9, 2013 (dated URL https://www.dallasnews.com/sports/texas-am-aggies/2013/12/09/texas-am-places-three-on-ap-s-all-sec-first-team-including-johnny-manziel/). The coaches' All-SEC team release is dated December 10, 2013 (https://12thman.com/news/2013/12/10/209337697). Each is gated to its own date.
- All-Mountain West team: announced on or about Tuesday, December 10, 2013 (dated URL https://unlvrebels.com/news/2013/12/10/trio_of_rebels_named_second_team_all_mw.aspx; single dated source).
- All other conference and All-America announcement dates (ACC, MVFC, Gulf South, Division II All-America lists): **unverified**; treat each as unavailable until its date is confirmed.

**Runtime consequence:** a college game or honor is usable only after it happens or is announced. A player's final college season statistics are complete only after his team's last game.

## All-star games (January 2014)

All-star invitations and acceptances become usable on their dated announcement. Practice-week reports become usable day by day. Game results are usable after the game.

| Game | Date | Venue | Sources (pass 2 status) |
|---|---|---|---|
| East-West Shrine Game | Saturday, January 18, 2014, 4:00 PM ET | Tropicana Field, St. Petersburg, Florida | Confirmed: https://en.wikipedia.org/wiki/2014_East%E2%80%93West_Shrine_Game ; https://broncosports.com/news/2014/1/2/Charles_Leno_Jr_to_Play_in_East_West_Shrine_Game . Rosters: https://www.nfl.com/news/2014-east-west-shrine-game-rosters-0ap2000000311902 (release date unverified) |
| NFLPA Collegiate Bowl | Saturday, January 18, 2014, 6:00 PM ET | StubHub Center, Carson, California | Confirmed: https://psacsports.org/news/2014/1/10/FOOT_0110143419.aspx ; https://bluehens.com/news/2014/1/15/209374067 ; https://bleacherreport.com/articles/1923141-nflpa-collegiate-bowl-2014-roster-top-prospects-for-college-all-star-game |
| Reese's Senior Bowl | Saturday, January 25, 2014 | Ladd-Peebles Stadium, Mobile, Alabama | Confirmed: https://en.wikipedia.org/wiki/2014_Senior_Bowl ; https://www.nfl.com/news/players-who-have-accepted-invites-for-2014-senior-bowl-0ap2000000291817 . Rosters: https://www.nfl.com/news/2014-senior-bowl-rosters-0ap2000000313902 (release date unverified) |

Senior Bowl acceptances: NFL.com maintained a running list of players who had accepted Senior Bowl invitations (https://www.nfl.com/news/players-who-have-accepted-invites-for-2014-senior-bowl-0ap2000000291817). Its original publication date and update history remain **unverified**. Pass 2 found no second source for the December 30, 2013 date that pass 1 associated with one listed player, so that date is withdrawn as a gate. Treat each acceptance as usable only from its own dated report.

Senior Bowl eligibility: pass 2 search text indicates that underclassmen who had not graduated were not permitted in the Senior Bowl in 2014 (the rule allowing draft-eligible juniors dates from November 2023: https://www.espn.com/nfl/story/_/id/38850163/college-football-all-star-games-allow-nfl-draft-eligible-juniors), and that graduated underclassmen were eligible before that change. The exact 2014 written policy on graduated underclassmen is **unverified**. An underclassman may not be treated as a Senior Bowl participant by default.

## January 15, 2014: underclassman declaration deadline

The deadline for the NFL to receive underclassman applications for special eligibility was **January 15, 2014**. Confirmed: league release text via https://www.neworleanssaints.com/news/98-players-granted-special-eligibility-for-2014-nfl-draft-12467237 and AP text via https://www.cbsnews.com/texas/news/record-98-underclassmen-eligible-for-nfl-draft .

Individual declarations reported before the deadline become usable on their dated report. A reported intention is not the same as NFL-granted eligibility; an underclassman is draftable in the simulation only once the NFL's special-eligibility list is public, or on dated evidence that his application was granted.

## Special-eligibility announcement (Sunday, January 19, 2014)

The NFL announced that **98 players** had been granted special eligibility for the 2014 draft. Each met the three-year rule and submitted a written application renouncing remaining college eligibility; the application deadline was January 15. The 98 exceeded the prior record of 73 (2013), an increase of 25. Separately, four players who had already graduated (Dion Bailey, Carl Bradford, Teddy Bridgewater, Adrian Hubbard) entered with eligibility remaining and were not counted in the 98, bringing players entering with remaining eligibility to 102.

**Publication date: confirmed as Sunday, January 19, 2014.** AP text says the league released the list "Sunday", and a Forbes commentary on the record 98 is dated January 19, 2014 (a Sunday). The runtime gate is **January 19, 2014**: the official list is unavailable before that date.

Sources:
- NFL.com list: https://www.nfl.com/news/list-of-underclassmen-granted-eligibility-for-2014-nfl-draft-0ap2000000314901
- New Orleans Saints (league release): https://www.neworleanssaints.com/news/98-players-granted-special-eligibility-for-2014-nfl-draft-12467237
- Pass 2: AP via CBS, https://www.cbsnews.com/amp/newyork/news/a-record-98-underclassmen-are-eligible-for-the-2014-nfl-draft ; ESPN, https://www.espn.com/nfl/draft2014/story/_/id/10318142/record-98-underclassmen-nfl-draft-pool ; Forbes, dated URL https://www.forbes.com/sites/darrenheitner/2014/01/19/no-need-to-bash-the-record-ninety-eight-underclassmen-declaring-for-nfl-draft/

The names of the four graduated players come from pass 1 search text only; pass 2 confirmed the count of four and Bridgewater's inclusion but did not re-confirm the other three names. **Partly unverified.**

The full 98-name list has not been transcribed yet (see the pool registry).

## February 2014: combine invitations and testing

- **Invitation list:** 335 invitees, including a then-record 85 underclassmen. Confirmed: https://www.nfl.com/news/draft-prospects-invited-to-2014-nfl-scouting-combine-0ap2000000323950 ; https://www.philadelphiaeagles.com/news/combine-to-feature-85-underclassmen-12596498 ; https://www.steelers.com/news/335-invited-yet-some-slip-through-cracks-12635756 .
- **Invitation-list gate (corrected in pass 2): February 6, 2014.** The official NFL release date is still **unverified**. Pass 2 found two dated public reports earlier than the pass 1 gate of February 9: https://stripehype.com/2014/02/05/2014-nfl-draft-scouting-combine-list-revealed/ (February 5, 2014) and https://www.bigcatcountry.com/2014/2/6/5384842/nfl-combine-2014-scouting-invitees-list (February 6, 2014), the latter reporting that CBS Sports had published the entire list of 335 invitees. Invitation status is therefore usable from February 6, 2014, the first date on which two independent dated reports carry the full list. Until an official release is verified, treat that list as a reported list, and prefer the official NFL.com list for any disputed name.
- **Combine dates:** February 19 to 25, 2014, Lucas Oil Stadium, Indianapolis. Confirmed: https://abcnews.com/Sports/2014-nfl-combine-schedule/story?id=22611536 ; https://www.colts.com/news/who-has-been-invited-to-the-2014-nfl-combine-12592259 . On-field workouts ran February 22 to 25. Offensive linemen and tight ends worked out on Saturday, February 22 (confirmed by the ABC schedule text, and consistent with a Boise State release dated February 24 reporting its two linemen's completed workouts: https://broncosports.com/news/2014/2/24/NFL_Combine_Results_for_Leno_Paradis). The per-position workout day for every other group remains **unverified**.

Combine measurements and drill results become available only after the player actually measures or works out. Do not preload combine numbers before the event.

Combine results for Jacksonville's board prospects, their comparisons and the undrafted line list, each dated by its public release (February 21 to 25, 2014), are recorded in [2014_combine_results.md](2014_combine_results.md).

## March to April 2014: pro days and medical or workout updates

NFL.com published a 2014 pro-day schedule (https://www.nfl.com/news/2014-pro-days-schedule-0ap2000000326264; publication date **unverified**). The schedule begins **Monday, March 3, 2014**, with pro days at Concordia (Minn.), Minnesota, Mississippi and Pittsburgh (confirmed by pass 2 search text of the same NFL.com page; an independent schedule exists at https://www.baltimoreravens.com/news/2014-pro-day-schedule-12753323 but its content was not shown in search text). The end of the window is **unverified**; the draft moved to May, so pro days and private workouts may run later than in 2013.

A pro-day result, private workout, visit, or public medical update is usable only on or after its dated event or report. No 2014 pro-day result is recorded in this library yet.

## Final public boards

No 2014 final public board (for example, Mayock or Brandt rankings) has been researched. Each becomes usable only on its publication date once added.

## Final hard cutoff

The 2014 NFL Draft begins on **Thursday, May 8, 2014, at 8:00 PM ET**. Before the first selection, only pre-selection information already public may be used. Once the first selection begins, the real draft is quarantined history and must not be imported into the simulation's selection process.

## Runtime loading rule

- Through December 2013: use this gate file, `library/2014_draft_pool_registry.md`, and prospect-specific evidence dated on or before the simulation date. College games and honors only as they occur or are announced (AP All-SEC December 9; All-Mountain West December 10; others unverified).
- From each all-star invitation or practice date: add that dated information.
- January 15, 2014: declaration window closes. Individual reported declarations before this date are intentions only.
- From January 19, 2014: add the official special-eligibility list.
- From February 6, 2014: add combine invitation status (reported list; official release date unverified).
- February 22 to 25, 2014: add each position group's combine results only after that group works out.
- March 3, 2014 onward: add each pro day or workout on its date.
- May 8, 2014, before the first selection: all pre-selection information then public may be loaded.
- After the first selection: resolve the simulation draft from simulation state only. Never consult the real selection order or destinations.

## Verification pass

**Pass 2 date:** 2026-09-28. **Method:** each factual claim was re-searched from scratch with new queries rather than by reopening the pass 1 citation. WebFetch remained blocked by the environment's egress policy, so pass 2, like pass 1, relied on search-result text, not full page reads. A claim is marked confirmed only where two independent search results agreed.

### Confirmed

- Draft dates May 8 to 10, 2014, Radio City Music Hall, New York; moved because of an April scheduling conflict at the venue; announced Tuesday, May 28, 2013 (NFL.com, ESPN, Washington Times dated URL, Patriots.com, CBS New York).
- FBS regular season August 29 to December 14, 2013; Army-Navy on December 14, 2013 (NCAA.com, army.mil, Wikipedia, FBSchedules).
- MAC (December 6, Ford Field), ACC (December 7, Charlotte), Big Ten (December 7, Indianapolis), Pac-12 (December 7, Tempe) and Mountain West (December 7) championship dates.
- Bowl season December 21, 2013 to January 6, 2014, 35 bowls, BCS title game at the Rose Bowl on January 6, 2014.
- East-West Shrine Game, Saturday, January 18, 2014, Tropicana Field; NFLPA Collegiate Bowl, Saturday, January 18, 2014, StubHub Center, Carson; Senior Bowl, Saturday, January 25, 2014, Ladd-Peebles Stadium, Mobile.
- Underclassman application deadline January 15, 2014.
- 98 players granted special eligibility, prior record 73, plus four graduated players with remaining eligibility outside the 98 (102 in all).
- Combine: 335 invitees, record 85 underclassmen; February 19 to 25, 2014, Lucas Oil Stadium; offensive linemen and tight ends on-field on February 22.
- Pro-day schedule begins March 3, 2014.

### Corrected (old to new, with reason)

- **Special-eligibility publication date:** "unverified, on or about January 19, 2014" to **confirmed Sunday, January 19, 2014**. Reason: AP text says the list was released "Sunday", and an independent Forbes piece is dated January 19, 2014.
- **Combine invitation gate:** February 9, 2014 to **February 6, 2014**. Reason: two independent dated reports (February 5 and February 6, 2014) published the full reported list before February 9. The official release date is still unverified.
- **First-round start time:** "unverified" to **8:00 PM ET, Thursday, May 8, 2014**. Reason: two pre-draft May 2014 sources agree. First publication date of the start time remains unverified.
- **Senior Bowl coaching-staff assignment:** publication date "unverified" to **Thursday, January 2, 2014**. Reason: NFL.com and Jaguars.com releases plus a Big Cat Country URL dated January 2, 2014. The item stays branch-resolved.
- **Senior Bowl acceptance date of December 30, 2013:** withdrawn as a gate. Reason: no second source; one reference source instead associates a January 21, 2014 announcement with a listed player (see the registry).
- **ACC and Big Ten championship dates:** "unverified" to **December 7, 2013** with venues. Reason: two sources each.
- **Mountain West championship venue:** added as Bulldog Stadium, Fresno. Reason: two sources.
- **FCS and Division II postseason dates:** "not researched" to dated entries (FCS confirmed from two sources; Division II title game single-source).
- **All-conference announcement dates:** AP All-SEC (December 9, 2013) and All-Mountain West (December 10, 2013) added from dated URLs.

### Still unverified

- The official NFL release date of the combine invitation list.
- The per-position combine workout day for groups other than offensive linemen and tight ends.
- NFL.com publication dates of the Shrine Game roster, Senior Bowl roster, Senior Bowl acceptance list and pro-day schedule.
- The end date of the 2014 pro-day window.
- The Senior Bowl's rule for choosing its coaching staffs and its 2014 written policy on graduated underclassmen.
- SEC Championship Game venue (single source in both passes) and the Division II championship game (single source).
- Whether West Alabama played in the 2013 Division II playoffs.
- Announcement dates of ACC, MVFC, Gulf South and Division II All-America honors.
- The names of three of the four graduated early entrants (Bailey, Bradford, Hubbard); only the count of four and Bridgewater were re-confirmed.
- When the 8:00 PM ET first-round start time was first announced.
