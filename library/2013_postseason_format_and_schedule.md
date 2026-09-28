# Library: 2013-14 NFL postseason format and schedule

**Status:** Research pass and separate verification pass completed September 28, 2026. This file records the 2013 NFL postseason **format, seeding and hosting rules, postseason-specific playing rules, and the real 2013-14 time-slot schedule**, so the simulation can seat the branch's own playoff pairings on real rails. It is research only. It changes no canon, closed result, roster, standings or calendar fact. Its machine-readable companion is `library/data/2013_postseason_slots.json`.

**Method:** The project's two-pass discipline applies. The first pass found each claim. The second pass searched each claim again from scratch, with different query wording and, where possible, a different outlet, without relying on the first pass's citation. Labels: **Confirmed** (two or more independent sources agree and at least one is contemporaneous with, or describes, the 2013 rule or schedule), **Confirmed (unchanged rule)** (two or more sources agree; some post-date 2013 and a later source dates the next change), **Corrected** (a source or search summary was wrong; the correction and reason are stated) or **Unverified** (one source, or no direct source).

**Hindsight and result boundary (read first):** The branch date is December 29, 2013, and the branch's playoff field and pairings differ from real history. **No real 2013 postseason game result, score, winner, advancing club, champion, Super Bowl participant, attendance or player statistic is recorded here**, and none may be imported as an answer key (Document 1 §8, Document 2 §4.3). Several source pages carry results in their titles or text; they are cited only for dates, kickoff times, networks, seeds known before any postseason game, and rules. Real clubs are named only in the Wild Card table, where the seeds were fixed by the regular season before any postseason game. For the Divisional and Conference rounds only the **host seed** of each slot is recorded (the 1 or 2 seed, known from the bye), never the realized visitor, because the visitor's seed would reveal Wild Card results. The Super Bowl designated home team is recorded by conference only.

**Access limits (read before relying on this file):** WebFetch is blocked by this environment's network policy, so no page was opened. **Every source below was read through search-engine result text (title, URL, date metadata and extracted passage), not by opening the page.** No attempt was made to route around the block. The league's own 2013 postseason release and the 2013 Official Playing Rules text were not read directly. A future session with page access should reopen the URLs and upgrade or correct the labels.

**Time zones:** All kickoff times are Eastern. Club sites in the Central zone (Saints.com, Battle Red Blog) printed Central times; they were converted by adding one hour, and the converted value matched the Eastern-time sources in every case.

## 1. Format, seeding and hosting

| # | Rule (2013 postseason) | Label | First pass | Verification pass |
|---|---|---|---|---|
| F1 | **12 clubs, six per conference:** the four division winners and the two non-division winners with the best records (wild cards). | Confirmed | P1 | P2, P3 |
| F2 | **Seeding:** division winners are seeded 1-4 by record; wild cards are seeded 5-6. **A division winner is always seeded above a wild card, whatever the records** (a wild card with a better record than a division winner still gets seed 5 or 6 and plays on the road in the Wild Card round). | Confirmed | P1 | P4 (a 7-9 division winner hosted an 11-5 wild card in the January 2011 Wild Card round under the same rule), P5 |
| F3 | **Byes:** seeds 1 and 2 in each conference receive a first-round bye. | Confirmed | P1, S1 | P3 |
| F4 | **Wild Card round:** seed 3 hosts seed 6; seed 4 hosts seed 5. | Confirmed | P1 | P3 (every 2013-14 Wild Card slot below is 6 at 3 or 5 at 4) |
| F5 | **Divisional round (reseeding):** the 1 seed hosts the lowest remaining seed; the 2 seed hosts the other survivor. The bracket is not fixed: pairings depend on which seeds survive. | Confirmed | P1 | P3 (Phinsider, December 30, 2013: "the top-ranked [NFC club] would face the lowest seeded team to win the Wildcard round, while the second-seeded [club] would face the higher seeded team"; the same stated for the AFC) |
| F6 | **Conference championships:** the higher remaining seed hosts. | Confirmed | P1 | S5 (the championship pairings as published show the higher seed at home; no result used) |
| F7 | **Super Bowl:** neutral site; one club per conference; a designated home team by annual AFC/NFC rotation (see §2). | Confirmed | S6 | S7 |
| F8 | **Seeding tiebreakers** (see §4): the 2013 seeding procedure used the league's regular-season division and wild-card tiebreaking procedures; no separate playoff-only tiebreaker exists. To set home-field priority among division winners the wild-card tiebreakers apply; among wild cards, the division tiebreakers apply if the clubs share a division, otherwise the wild-card tiebreakers. | Confirmed (unchanged rule) | P6 | P7 |

**Note on "reseeding" wording.** One search summary said "there is no reseeding in the NFL playoffs" and in the same passage described the 1 seed hosting the lowest surviving seed. That is reseeding in the usual sense (the Divisional pairing depends on which seeds survive). The rule in F5 is what the sources describe; only the label in that one summary was inconsistent.

## 2. Super Bowl XLVIII, Pro Bowl and the off week

| # | Fact | Label | First pass | Verification pass |
|---|---|---|---|---|
| B1 | **Super Bowl XLVIII: Sunday February 2, 2014, 6:30 p.m. ET, FOX, MetLife Stadium, East Rutherford, New Jersey.** Neutral site; the first Super Bowl played outdoors at a cold-weather site. | Confirmed | S1, S6 | S7 (CBC), S8 (Battle Red Blog, December 29, 2013: "FOX, 5:30 PM CT"), Jacksonville master calendar §6 |
| B2 | **Designated home team: the AFC champion.** The rotation makes the AFC representative the designated home team in odd-numbered seasons, which are the even-numbered Super Bowls (the 2013 season's game is Super Bowl XLVIII, number 48). The designated home team chooses its jersey colour; the designated visitor calls the opening coin toss. | Confirmed (AFC for XLVIII). Coin-toss detail: **Unverified** (one post-2013 source) | S9 | S10 (CBS Sports: the AFC club would wear its home colours as designated home team), S11 |
| B3 | **Pro Bowl: Sunday January 26, 2014, 7:30 p.m. ET, NBC, Aloha Stadium, Honolulu.** | Confirmed | S8 ("NBC, 6:30 PM CT") | S12, `2013_nfl_awards_structure.md` (Pro Bowl date) |
| B4 | **Two-week gap:** the conference championships (January 19) and the Super Bowl (February 2) are 14 days apart; the Pro Bowl fills the off week between them (January 26). | Confirmed (follows from B1, B3 and C1 below) | S8 | S1 |

**Corrected (designated home team).** One first-pass search summary stated "Even-numbered Super Bowls: NFC team is designated home". Its own underlying text said "the NFC representative is the home team in even-numbered **seasons**", and the summary confused seasons with Super Bowl numbers. The verification pass found two independent statements that the AFC club was the designated home team for Super Bowl XLVIII (S10, S11), which fits "AFC home in odd-numbered seasons" (2013). The AFC controls. The club identity in those sources is not recorded.

## 3. Real 2013-14 slot schedule

### 3.1 Announcements

| Round | Announced | Label | Sources |
|---|---|---|---|
| Wild Card dates, kickoff times and networks | **Sunday December 29, 2013**, the night Week 17 ended (the NFC East was decided in the Sunday night game, and the schedule followed it) | Confirmed (date). Exact hour: **Unverified** | S13 (Phinsider "Wildcard game times set", 2013/12/29), S14 (Canal Street Chronicles, 2013/12/29), S15 (Arrowhead Pride, 2013/12/29), S16 (Saints.com), S17 (Bleeding Green Nation, 2013/12/30) |
| Conference championship kickoff times and networks | Published with the Wild Card schedule on **December 29, 2013**, by conference (AFC early on CBS, NFC late on FOX), before any pairing was known | Confirmed | S8 (2013/12/29), S3 (2013/12/30) |
| Divisional pairings, dates, times and networks | **Sunday January 5, 2014**, after the last Wild Card game | Confirmed (date). Exact hour: **Unverified** | S18 (Phinsider "Divisional Round set", 2014/1/5), S19 (Canal Street Chronicles, 2014/1/5), S20 (fbschedules) |
| Conference championship pairings | After the Divisional round (January 12, 2014) | Confirmed (follows from reseeding; S21, 2014/1/13) | S21 |

Whether the Divisional round's day and time for each pairing were fixed by a published formula, or chosen by the league and its network partners after the Wild Card round, was **not found**. The branch rule in §3.5 therefore maps pairings to slots by the realized host-seed pattern, not by a claimed league formula.

### 3.2 Wild Card round (Week 18): January 4-5, 2014

Seeds were fixed by the regular season before any postseason game; clubs are named only to identify each seed matchup.

| Day, date | Kickoff (ET) | Network | Seed matchup | Clubs (seed identification only) | Label | Sources |
|---|---|---|---|---|---|---|
| Saturday January 4 | 4:35 p.m. | NBC | **AFC 5 at AFC 4** | Kansas City at Indianapolis | Confirmed | S2, S13, S15, S16 ("3:35 p.m." CT) |
| Saturday January 4 | 8:10 p.m. | NBC | **NFC 6 at NFC 3** | New Orleans at Philadelphia | Confirmed | S16 ("7:10 p.m." CT), S17, S22 |
| Sunday January 5 | 1:05 p.m. | CBS | **AFC 6 at AFC 3** | San Diego at Cincinnati | Confirmed | S2, S15, S16 ("12:05 p.m." CT) |
| Sunday January 5 | 4:40 p.m. | FOX | **NFC 5 at NFC 4** | San Francisco at Green Bay | Confirmed | S16 ("3:40 p.m." CT, Fox), S23 |

Network pattern: NBC carried both Saturday games (one per conference); CBS the Sunday AFC game; FOX the Sunday NFC game.

### 3.3 Divisional round (Week 19): January 11-12, 2014

Only the host seed is recorded (1 or 2, known from the byes). The visitor is the lowest surviving seed for the 1 seed's game and the other survivor for the 2 seed's game (F5). The realized visitor seeds are deliberately omitted because they would reveal Wild Card results.

| Day, date | Kickoff (ET) | Network | Slot type | Label | Sources |
|---|---|---|---|---|---|
| Saturday January 11 | 4:35 p.m. | FOX | **NFC: lowest survivor at NFC 1** | Confirmed | S20, S24, S18 |
| Saturday January 11 | 8:15 p.m. | CBS | **AFC: other survivor at AFC 2** | Confirmed | S20, S24 |
| Sunday January 12 | 1:05 p.m. | FOX | **NFC: other survivor at NFC 2** | Confirmed | S20, S24, S25 |
| Sunday January 12 | 4:40 p.m. | CBS | **AFC: lowest survivor at AFC 1** | Confirmed | S20, S24, S25 |

**Corrected (Divisional Saturday NFC time).** One verification-pass search summary gave the Saturday NFC Divisional game as "8:10 p.m. ET". Three independent sources (S20, S24, and the Phinsider/Bleacher Report divisional guides in S18) give 4:35 p.m. ET on FOX, and 8:10 p.m. is the Wild Card Saturday night slot a week earlier. 4:35 p.m. controls; the 8:10 figure was a summary conflation.

Network pattern: CBS carried the AFC games, FOX the NFC games. Each day had one game per conference; the 1 seeds' games were split across the two days (NFC Saturday, AFC Sunday), as were the 2 seeds' games (AFC Saturday, NFC Sunday).

### 3.4 Conference championships (Week 20): Sunday January 19, 2014

| Game | Kickoff (ET) | Network | Slot type | Label | Sources |
|---|---|---|---|---|---|
| AFC Championship | 3:00 p.m. | CBS | **AFC: lower remaining seed at higher remaining seed** | Confirmed | S8 ("CBS, 2:00 PM CT", 2013/12/29), S5, Jacksonville master calendar §6 |
| NFC Championship | 6:30 p.m. | FOX | **NFC: lower remaining seed at higher remaining seed** | Confirmed | S8 ("FOX, 5:30 PM CT"), S5, Jacksonville master calendar §6 |

The realized host and visitor seeds are omitted (they would reveal Divisional results).

### 3.5 Result-blind slot rule for the branch (derived)

This is a derivation from the verified tables above, not a league rule. It is result-blind: a branch pairing is placed by its round, its conference and (for the Wild Card round) its seed matchup or (for later rounds) its host seed, never by which club is in it, how it was reached, or whether Jacksonville is involved.

1. **Wild Card:** AFC 5 at 4, Saturday 4:35 p.m. NBC; NFC 6 at 3, Saturday 8:10 p.m. NBC; AFC 6 at 3, Sunday 1:05 p.m. CBS; NFC 5 at 4, Sunday 4:40 p.m. FOX.
2. **Divisional:** NFC game at the 1 seed, Saturday 4:35 p.m. FOX; AFC game at the 2 seed, Saturday 8:15 p.m. CBS; NFC game at the 2 seed, Sunday 1:05 p.m. FOX; AFC game at the 1 seed, Sunday 4:40 p.m. CBS.
3. **Conference:** AFC 3:00 p.m. CBS; NFC 6:30 p.m. FOX; higher remaining seed hosts.
4. **Super Bowl:** February 2, 2014, 6:30 p.m. FOX, MetLife Stadium (neutral); the AFC champion is the designated home team.
5. **Information timing:** the branch should not treat a round's slot assignment as public before the real announcement date in §3.1 (Wild Card and conference kickoff times December 29, 2013; Divisional January 5, 2014; conference pairings after the Divisional round).
6. **Limit:** the real 2013-14 mapping reflected one realized set of seeds. The branch uses it as a fixed rail by slot type; it does not claim the league would have chosen the same day or time for a different field.

## 4. Postseason playing and administrative rules

| # | Rule | Label | First pass | Verification pass |
|---|---|---|---|---|
| R-P1 | **Postseason overtime: no ties.** Modified sudden death applies to the first overtime possession (the rule in `2013_nfl_playing_rules_for_simulation.md` R2, in the postseason since 2010); play continues in 15-minute periods until a winner. A first possession still in progress when a period ends carries into the next period. Matches the existing rules library **R5**; no correction to R5 is needed. | Confirmed | O1, O2 | O3 (2010 adoption of modified sudden death for the playoffs), O4 and O5 (2022 owners' change to guarantee both clubs a postseason possession; post-2013, dates the change and so fixes the 2013 rule) |
| R-P2 | **Postseason overtime timing detail:** a three-minute intermission after regulation before overtime; each club has three timeouts per half, with general timing provisions as in a regular game. | **Unverified** (one search summary attributing the text to the NFL.com overtime pages; not independently re-found). Does not affect the kernel, which does not simulate timeouts | O1 | none |
| R-P3 | **Game-day actives: 46, with 7 inactive, for every regular-season and postseason game.** The pre-2011 rule text applied its active/inactive list to "each regular-season and postseason game"; 2011 raised the active list to 46 and dropped the third-quarterback rule. No postseason exception was found. Matches the existing rules library R15. | Confirmed | A1 | A2, `2013_league_calendar_and_financial_rules.md` (46 dress, 7 inactive in 2013) |
| R-P4 | **Weekly AFC/NFC Players of the Week are not awarded for postseason games.** No postseason Players of the Week release was found for the 2013-14 playoffs or the following postseason, and the fan-voted weekly programmes describe voting "each week of the regular season". | **Unverified** (absence of evidence, not a rule text). **Branch guidance:** do not draw postseason weekly awards. Also: AP season awards are voted before the playoffs and postseason play does not count (`2013_nfl_awards_structure.md` §3.1) | W1 | W2, W3 |
| R-P5 | **Seeding tiebreakers** match the regular-season standings procedures (F8). The branch's existing seeding implementation needs no postseason-specific tiebreaker. | Confirmed (unchanged rule) | P6 | P7 |

## Sources

Dates are publication dates where the search result showed one. "Post-2013" marks a source used only for an unchanged rule or to date a later change. A source whose title or text carries a real postseason result is cited only for the scheduling or rule fact stated in the tables; the result is not used.

**Format and seeding**
- P1. Wikipedia, "2013-14 NFL playoffs": https://en.wikipedia.org/wiki/2013%E2%80%9314_NFL_playoffs (format, seeding, hosting, reseeding).
- P2. Wikipedia, "2012-13 NFL playoffs": https://en.wikipedia.org/wiki/2012%E2%80%9313_NFL_playoffs (same format the season before).
- P3. The Phinsider, "NFL Playoffs schedule 2014: Wildcard, Divisional games and matchups released" (December 30, 2013): https://www.thephinsider.com/2013/12/30/5255774/nfl-playoffs-schedule-2014
- P4. Bleacher Report, "Embarrassing!!! The Saga of the 2010-2011 Seattle Seahawks": https://bleacherreport.com/articles/560187-embarrassing-the-saga-of-the-2010-2011-seattle-seahawks; Wikipedia, "2010-11 NFL playoffs": https://en.wikipedia.org/wiki/2010%E2%80%9311_NFL_playoffs (division winner hosts regardless of record; a pre-2013 structural example only).
- P5. Football Perspective, "Should Division Winners Get Home Field?": https://www.footballperspective.com/should-division-winners-get-home-field/; FOX Sports, "NFL Playoff Format: How does the NFL postseason work?" (post-2013): https://www.foxsports.com/stories/nfl/nfl-playoff-format-how-does-the-nfl-postseason-work
- P6. NFL.com, "NFL Tiebreaking Procedures": https://www.nfl.com/standings/tie-breaking-procedures; ESPN.com, "NFL playoffs tiebreaking procedures": https://www.espn.com/espn/print?id=893804
- P7. Patriots.com, "NFL Tiebreaking Procedures": https://www.patriots.com/news/nfl-tiebreaking-procedures-194486; FOX Sports, "NFL Tiebreakers: Playoff and wild-card rules" (post-2013): https://www.foxsports.com/stories/nfl/nfl-playoff-tiebreaking-procedures

**Schedule**
- S1. FBSchedules, "2013-14 NFL Playoffs Schedule announced": https://fbschedules.com/2013-14-nfl-playoffs-schedule-announced/; FBSchedules, "2013 NFL Playoff Schedule": https://fbschedules.com/2013-nfl-playoff-schedule/
- S2. Bleacher Report, "NFL Playoff Schedule 2014: Complete Guide to Wild Card Weekend": https://bleacherreport.com/articles/1911023-nfl-playoff-schedule-2014-complete-guide-to-wild-card-weekend
- S3. The Phinsider (December 30, 2013), as P3.
- S5. FBSchedules, "2014 AFC and NFC Championship Games set": https://fbschedules.com/2014-afc-nfc-championship-games-set/ (times and networks only).
- S6. Bleacher Report, "Super Bowl 2014: Start Time and TV Schedule": bleacherreport.com article 1932490 (URL slug withheld: it names the real Super Bowl XLVIII participants); Patch, "Super Bowl 2014: What Time Is Kickoff?": https://patch.com/massachusetts/newton/super-bowl-2014-what-time-is-kickoff-newton
- S7. CBC Sports, "Super Bowl XLVIII: 5 things to know": https://www.cbc.ca/sports/football/nfl/super-bowl-xlviii-5-things-to-know-1.2520452 (6:30 p.m. ET; MetLife Stadium; first outdoor cold-weather-site Super Bowl).
- S8. Battle Red Blog, "2014 NFL Playoff Schedule: Wild Card, Divisional Round, And Conference Championship Game Times" (December 29, 2013): https://www.battleredblog.com/2013/12/29/5255548/2014-nfl-playoff-schedule-wild-card-divisional-round-and-conference (conference championships CBS 2:00 PM CT and FOX 5:30 PM CT; Pro Bowl NBC 6:30 PM CT, January 26, Aloha Stadium; Super Bowl FOX 5:30 PM CT, February 2).
- S9. FanSided, "How does the NFL determine the home team in the Super Bowl?" (post-2013): https://fansided.com/how-home-team-determined-super-bowl; Pro Football Network, "How Is the Home Team Decided for the Super Bowl?" (post-2013): https://www.profootballnetwork.com/how-is-the-home-team-decided-for-super-bowl/
- S10. CBS Sports, "[AFC club] will wear [its home colour] jerseys in Super Bowl XLVIII" (title colour withheld): cbssports.com NFL news item (URL slug withheld: it names the real AFC champion) (cited for the AFC club's home-team designation only).
- S11. American Football Wiki, "Super Bowl XLVIII": https://americanfootball.fandom.com/wiki/Super_Bowl_XLVIII ("designated home team in the annual rotation between AFC and NFC teams"; cited for the conference only).
- S12. Wikipedia, "2014 Pro Bowl": https://en.wikipedia.org/wiki/2014_Pro_Bowl (date, kickoff, network, venue only).
- S13. The Phinsider, "NFL Playoff schedule 2014: Wildcard game times set" (December 29, 2013): https://www.thephinsider.com/2013/12/29/5255462/nfl-playoff-schedule-2014-wildcard-game-times-set
- S14. Canal Street Chronicles, "NFL Playoff Schedule 2014 Announced" (December 29, 2013): https://www.canalstreetchronicles.com/2013/12/29/5255420/nfl-playoff-schedule-2014-saints
- S15. Arrowhead Pride, "NFL playoff schedule 2014: [AFC 5] will face [AFC 4] on Wild Card weekend" (December 29, 2013): https://www.arrowheadpride.com/2013/12/29/5254680/chiefs-vs-colts-2014-nfl-playoffs-schedule-times-tv-channel-wild-card-weekend
- S16. NewOrleansSaints.com, "New Orleans Saints to play at Philadelphia on Saturday night at 7:10 p.m.": https://www.neworleanssaints.com/news/new-orleans-saints-to-play-at-philadelphia-on-saturday-night-at-7-10-p--12305642 (the full Wild Card slate in Central time).
- S17. Bleeding Green Nation, "NFL Playoff Schedule 2014: [NFC 3] to Face [NFC 6] in Philadelphia on Wild Card Weekend" (December 30, 2013): https://www.bleedinggreennation.com/2013/12/30/5255040/eagles-vs-saints-2014-nfl-playoff-schedule-times-tv-channel-wild-card-weekend
- S18. The Phinsider, "NFL Playoffs 2014 Schedule: Divisional Round set" (January 5, 2014): https://www.thephinsider.com/2014/1/5/5277998/nfl-playoffs-2014-schedule-divisional-round-set; The Phinsider, "NFL Playoff schedule 2014: Dates and times for Divisional round games" (January 10, 2014): https://www.thephinsider.com/2014/1/10/5294098/nfl-playoff-schedule-2014-tv-channels-date-and-time; Bleacher Report divisional guides: https://bleacherreport.com/articles/1914496-nfl-playoff-schedule-2014-what-you-need-to-know-for-the-divisional-round
- S19. Canal Street Chronicles, divisional bracket update (January 5, 2014): https://www.canalstreetchronicles.com/2014/1/5/5278066/nfl-playoff-schedule-bracket-schedule-update (announcement date only; its search summary's "8:10 p.m." time was rejected, see §3.3).
- S20. FBSchedules, "2013-14 NFL Playoffs: Divisional Round match-ups set": https://fbschedules.com/2013-14-nfl-playoffs-divisional-round-match-ups-set/
- S21. Canal Street Chronicles, conference championship games set (January 13, 2014): https://www.canalstreetchronicles.com/2014/1/13/5302866/nfl-playoffs-2014-afc-nfc-conference-championships (timing of the pairing announcement only).
- S22. Pro-Football-Reference, Wild Card game page, January 4, 2014 (Philadelphia): https://www.pro-football-reference.com/boxscores/201401040phi.htm (kickoff time and network only).
- S23. Bleacher Report, "NFL Playoff Schedule 2014: Viewing Guide for Sunday's Wild-Card Matchups": https://bleacherreport.com/articles/1910935-nfl-playoff-schedule-2014-viewing-guide-for-sundays-wild-card-matchups; Pro-Football-Reference, Wild Card game page, January 5, 2014 (Green Bay): https://www.pro-football-reference.com/boxscores/201401050gnb.htm (kickoff time and network only).
- S24. Bleacher Report, "NFL Playoff Schedule 2014: Complete Guide and Predictions for Divisional Round": https://bleacherreport.com/articles/1912877-nfl-playoff-schedule-2014-complete-guide-and-predictions-for-divisional-round (times and networks only; its predictions are not used).
- S25. Bleeding Green Nation, "NFL Playoff Schedule 2014: Divisional Round Preview, TV Schedule" (January 10, 2014): https://www.bleedinggreennation.com/2014/1/10/5296918/nfl-playoff-schedule-2014-divisional-round-preview-tv-schedule-online-stream-odds-picks

**Postseason rules**
- O1. NFL.com, "Postseason overtime rules": https://www.nfl.com/news/postseason-overtime-rules-09000d5d81d817d7; NFL.com, "NFL overtime rules": https://www.nfl.com/news/nfl-overtime-rules-09000d5d827ee2c0
- O2. ESPN, "What are NFL overtime rules for regular and postseason play?" (2024; post-2013): https://www.espn.com/nfl/story/_/id/39111637/what-nfl-rules-regular-postseason-play
- O3. Bleacher Report, "NFL Playoff Overtime Rules: Modified Sudden Death Changes for Postseason": https://bleacherreport.com/articles/1015925-nfl-playoff-overtime-rules-modified-sudden-death-changes-for-postseason
- O4. CBC Sports, "NFL owners approve playoff OT rule change" (March 2022; post-2013, dates the change): https://amp.cbc.ca/sports/football/nfl/nfl-owners-approve-playoff-ot-rule-change-1.6401397
- O5. CBS News, "NFL announces change to overtime rules, giving both teams possession in postseason games" (2022; post-2013): https://www.cbsnews.com/news/nfl-overtime-posession-coin-toss-new-rules-playoffs
- A1. Wikipedia, "Third quarterback rule": https://en.wikipedia.org/wiki/Third_quarterback_rule (the active/inactive list applied to "each regular-season and postseason game"; abolished for 2011 when the active list rose to 46).
- A2. Hogs Haven, "Why does the NFL have inactive players on game day?" (2020; post-2013): https://www.hogshaven.com/2020/6/20/21296520/why-does-the-nfl-have-inactive-players-on-game-day
- W1. NFL.com, "FedEx Air and Ground Players of the Week": https://www.nfl.com/voting/air-and-ground (voting "each week of the regular season").
- W2. Wikipedia, "FedEx Air & Ground NFL Players of the Week": https://en.wikipedia.org/wiki/FedEx_Air_&_Ground_NFL_Players_of_the_Week
- W3. Pro-Football-Reference, "Players of the Week": https://www.pro-football-reference.com/awards/players-of-the-week.htm (lists regular-season weeks; no postseason entries were surfaced in search).

## Verification notes

- **Wild Card slots.** The first pass (FBSchedules, Bleacher Report, Arrowhead Pride) gave the Saturday AFC and Sunday AFC slots; the Saturday night NFC and Sunday NFC slots were missing from the first-pass extracts. The verification pass took the complete slate from Saints.com (Central times, all four games) and independently re-found each game's Eastern time and network (Bleeding Green Nation and Pro-Football-Reference for 8:10 p.m. NBC; Bleacher Report and Pro-Football-Reference for 4:40 p.m. FOX). All four slots are Confirmed.
- **Divisional slots.** FBSchedules, Bleacher Report and The Phinsider agree on all four times and networks. One Canal Street Chronicles search summary said 8:10 p.m. for the Saturday NFC game; rejected (§3.3).
- **Conference championships.** Battle Red Blog (December 29, 2013), FBSchedules and the existing Jacksonville master calendar agree: AFC 3:00 p.m. CBS, NFC 6:30 p.m. FOX.
- **Super Bowl.** Date, kickoff, network and venue agree across Bleacher Report, Patch, CBC, FBSchedules and Battle Red Blog. The designated home team was corrected from a misread search summary (§2) to the AFC.
- **Division winners above wild cards.** Wikipedia's 2013-14 format text, a 2011 example of a losing-record division winner hosting, and later format explainers agree; the rule was unchanged from 2002 realignment through 2013.
- **Postseason Players of the Week.** Not confirmed by any rule text. The guidance not to draw them rests on the absence of any postseason release and on the regular-season wording of the weekly programmes; it stays **Unverified**.
- **Announcement hours** for the Wild Card and Divisional schedules were not found; only the dates are recorded.
- **No correction to `2013_nfl_playing_rules_for_simulation.md` R5 or R15, or to the Jacksonville master calendar §6, was needed.** Every overlapping fact matches.
