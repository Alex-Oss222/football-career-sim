# 2014 preseason opponent rosters: Tampa Bay Buccaneers, August 8, 2014

**Research date:** October 1, 2026 (branch clock August 1, 2014). **Football information window:** Tampa Bay's first 2014 unofficial depth chart, released Tuesday, August 5, 2014; the club's transaction log through August 8; and the club's pregame report of Friday, August 8, 2014, all published before kickoff of the preseason opener at Jacksonville. **Status: PREPARED, gated: usable for the August 8, 2014 preseason game and after.** This library is prepared research under [rails method section 7](../career/2014/league/personnel/method.md#7-week-1-depth-charts), applied to a preseason opponent. It is the 90-man camp roster Tampa Bay carried into the game, reconciled to branch control, not a 53. No preseason score, statistic, game participation or later transaction is an input.

**Machine artifact:** [data/2014_preseason_opponent_rosters.json](data/2014_preseason_opponent_rosters.json) (top-level `season`, `game` = `preseason-01`, `as_of` = `2014-08-08`, `gate`, `sources`, one club under `clubs`; the same per-player fields as the [Week 1 library](2014_week1_depth_charts.md), plus `availability_note` for a held-out player). **Builder:** `scripts/research/build_2014_preseason_opponent_rosters.py` (reuses the Week 1 builder's control, identity, tie-break and compaction functions; takes an optional transient workspace for the nflverse identity files). **Tests:** `tests/test_2014_preseason_opponent_rosters.py`. The game folder's `opponent_roster.json` is copied from this artifact when the game is prepared; this file is the source, not the game input.

Jacksonville is not in this library. Its input always comes from the branch roster, its medical state and Stone's staff.

## Sources

| Use | Source | Scope read |
|---|---|---|
| Depth chart (primary) | Tampa Bay Buccaneers, [Depth Chart Reflects Ongoing Competition](https://www.buccaneers.com/news/depth-chart-reflects-ongoing-competition-13395752), August 5, 2014 ("2014 TAMPA BAY BUCCANEERS *UNOFFICIAL* DEPTH CHART") | Quarterbacks, the first- and second-team offensive line, the defensive starters, second-team defensive tackles and cornerbacks |
| Depth chart (transcriptions) | Sports Illustrated, [Tampa Bay Buccaneers release depth chart: Mike Evans behind Chris Owusu](https://www.si.com/nfl/2014/08/06/tampa-bay-buccaneers-depth-chart-2014), August 6, 2014; Bucs Nation, [Buccaneers Depth Chart: Observations and Reaction](https://www.bucsnation.com/2014/8/5/5971459/buccaneers-depth-chart-observations-and-reaction-to-the-bucs-2014), August 5, 2014; Bleacher Report, [Buccaneers 2014 Virtual Program](https://bleacherreport.com/articles/2182481-buccaneers-2014-virtual-program-depth-chart-analysis-x-factors-and-more); Heavy/Yahoo, [Several Buccaneers Put on Notice by First Depth Chart](https://heavy.com/sports/nfl/tampa-bay-buccaneers/depth-chart-roster-notice/) | Every column of the chart: the full offensive table (QB, RB, FB, both WR columns, TE, LT-LG-C-RG-RT with third strings), the defensive line with third strings and "Other" entries, the three linebacker columns, the cornerback columns, SS and FS, kicker, kick and punt returners |
| Transactions | ESPN, [Tampa Bay Buccaneers 2014 Roster Transactions](https://www.espn.com/nfl/team/transactions/_/name/tb/season/2014); Pro Football Reference, [July 2014](https://www.pro-football-reference.com/years/2014/07_transactions.htm) and [August 2014](https://www.pro-football-reference.com/years/2014/08_transactions.htm) transactions; ProFootballTalk, [Carl Nicks, Buccaneers part ways](https://profootballtalk.nbcsports.com/2014/07/25/carl-nicks-buccaneers-part-ways/) (July 25) and [Bucs sign Kip Edwards, officially cut Carl Nicks](https://profootballtalk.nbcsports.com/2014/07/30/bucs-sign-kip-edwards-officially-cut-carl-nicks/) (July 30); Bucs Nation, [waive Gettis, sign Joyce](https://www.bucsnation.com/2014/8/4/5968621/buccaneers-waive-receiver-david-gettis-sign-safety-mark-joyce) (August 4) and [waive Grable, Swaim; sign Giddins, Ruffin](https://www.bucsnation.com/2014/8/5/5972557/buccaneers-waive-jeremy-grable-mycal-swaim-sign-ryne-giddins-james) (August 5); Buccaneers, [Bucs Sign S Joyce, Release WR Gettis](https://www.buccaneers.com/news/bucs-sign-s-joyce-release-wr-gettis-13387763) | Every move July 21 to August 9, 2014, and the dated later arrivals that exclude players from this roster |
| Availability | Buccaneers, [Jacksonville Pregame Report](https://www.buccaneers.com/news/jacksonville-pregame-report-13424501), August 8, 2014; [Camp Notes: Verner Easing Back In](https://www.buccaneers.com/news/camp-notes-verner-easing-back-in-13439836); Bucs Nation camp notes of [August 3](https://www.bucsnation.com/2014/8/3/5965357/buccaneers-training-camp-injuries-position-battles) and [August 6](https://www.bucsnation.com/2014/8/6/5975703/buccaneers-training-camp-position-battles-injuries-and-notes-from) | The three players the club said would not play; practice absences during the week |
| Membership cross-check | nflverse [roster_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2014.csv) (season rosters) | The 75 players who reached a Tampa Bay regular-season roster or reserve list; jersey numbers; it carries no camp-only player |
| Identity | `library/data/player_birth_dates.json`; nflverse [players.csv](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv); `library/data/2014_week1_depth_charts.json` (bio fields); `library/data/player_photos.json` | gsis id and birth date for 82 of 87 players; Wikimedia Commons photographs with license and credit for 44; Pro Football Reference page for 81 |
| Branch control | `career/2014/team/roster/roster.md`, August 1, 2014 | The 78 controlled players (74 signed, four unsigned tenders), matched by gsis id as in the Week 1 build |
| Branch pairing, trades, free agency, retirements | [draft_pairing.md](../career/2014/league/personnel/draft_pairing.md), [udfa_signings.md](../career/2014/draft/udfa_signings.md), [trades.md](../career/2014/trades/completed_trades/trades.md), [signings.md](../career/2014/free_agency/signings.md), [fa_draws.md](../career/2014/league/personnel/fa_draws.md), [retirements.md](../career/2014/league/personnel/retirements.md) | Every branch event touching a Tampa Bay player |

## Verification

The two-pass discipline was applied under a real constraint: from this session the club's, ESPN's, Pro Football Reference's, Wikipedia's and the Internet Archive's pages could not be fetched (egress denied), and nflverse carries no preseason depth charts, weekly rosters or injury reports for 2014. Every chart and transaction fact below was therefore read from dated search-engine extracts of the named pages, and the second pass re-queried each fact with different wording and from a second outlet. What that pass established:

- **Quarterback order** (McCown, Glennon, Kafka, Tanney): the club's own article and the Bucs Nation and SI transcriptions agree. Confirmed.
- **First-team offensive line** (Collins, Cousins, Dietrich-Smith, Meredith, Dotson) and second team (Pamphile, Edwards, Daniels, Omameh, Patchan): the club's article and the SI table agree; the third strings (Shugarts LT; Allen LG and C; Foster, Allen, Miller C; Miller RG) are from the SI table only. Logan Mankins, listed first at guard in the Bleacher Report piece, arrived August 26; that article was updated after the chart and is not used for the line.
- **Skill positions** (RB Martin, Rainey, Sims, James, Demps; FB Lane, Pryor, Thompson; the two WR columns; TE Myers, Wright, Stocker, Seferian-Jenkins, Brate): SI table, with Heavy/Yahoo and Bucs Nation confirming Evans behind Owusu and Seferian-Jenkins fourth at tight end. Confirmed for the order; the assignment of receivers to the two columns is the SI transcription alone.
- **Defensive line**: the club's article (starters, Bowers and Spence second at tackle), SI (third strings and "Other") and Bleacher Report (Sutton, Talley, Cummings) agree. Confirmed.
- **Linebackers**: SI table (SLB Casillas, Glaud, Askew, Grable; MLB Foster, Fletcher, Munoz; WLB David, Lansanah, Magee), with the club's article confirming the three starters and Fletcher and Lansanah as reserves. Confirmed.
- **Secondary**: the club's article (Verner, Jenkins, Johnson starting; Melvin and Banks second), Bleacher Report (Pointer the third reserve) and the SI table (RCB Jenkins, Banks, Carr, with Lewis and Gaitor "Other"; SS Barron, Wright, McDougald; FS Goldson, Tandy, McCray) agree where they overlap. The cells of Kip Edwards, Danny Gorrer and Mark Joyce were not located in any extract; they are placed below every listed defensive back.
- **Specialists**: SI table (K Barth, Murray; KR Page, Demps, James; PR Page, Rainey, Herron, Dawson). The long-snapper order between DePaola and Cain was not located; Cain is removed by branch control, so it has no effect.
- **Held out August 8**: the club's pregame report names Verner, Jenkins and Goldson; the later Camp Notes and the Bucs Nation notes give the reasons (Verner and Jenkins hamstring, Goldson offseason foot surgery). Confirmed from two club articles.
- **Membership**: every listed player's presence on August 8 was checked against the transaction log. Date discrepancies found and recorded: Kip Edwards signed July 29 (PFT, PFR) or July 31 (ESPN); Carl Nicks released July 30 (PFT, the official transaction) after the July 25 parting (ESPN lists July 29); Mark Joyce waived August 9 (PFR) or August 12 (ESPN). None changes the August 8 roster. Players excluded by their dates: David Gettis (released August 3), Jeremy Grable and Mycal Swaim (waived/injured August 4), Larry English (signed August 13), Rishaw Johnson (traded for Kelcie McCray August 21), R.J. Mattes (August 21), Edawn Coughman (August 20), Marc Anthony and Jeremiah Warren (claimed August 25), Logan Mankins (August 26), Garrett Gilkey (August 31), Brandon Dixon (September 6), George Uko (practice squad, October 13), Brett Smith (waived May 21). Kimario McFadden and Derrius Brooks were practice-squad signings of September 1 and never camp members.
- **Count**: 90 players under contract on August 8, 2014 (the chart's listed players less Grable and Swaim, plus Giddins, Ruffin, Joyce, Edwards and Gorrer), consistent with the club's statement that the August 4 moves "turned over two of their 90 training camp spots". After the three branch removals, 87.
- **Identity**: 82 of 87 players carry a gsis id and birth date (41 from the identity registry, 41 from nflverse players, each a single 2014-active match by name). Five camp-only players have no nflverse record (Euclid Cummings, Jibreel Black, Ryne Giddins, Damaso Munoz, Mark Joyce) and carry name only.

**Not independently verified:** the WR column assignments, the offensive-line third strings and the specialists' order are single-transcription; the three unlocated defensive-back cells; jersey numbers of the 33 camp-only players (stored only for the 54 who reached a 2014 regular-season roster, from nflverse). No page was read directly.

## How the unit is built

1. **Players:** everyone under contract to Tampa Bay on August 8, 2014, once each: the chart's listed players as of its August 5 release, less the two waived/injured August 4, plus the five under contract on August 8 whose cells were not located (two signed after the chart was prepared).
2. **Position:** the roster position of the player's column (T, G, C for the line; DE, DT; OLB, MLB; CB, SS, FS; S for Joyce). Every position maps to one of the twelve kernel groups.
3. **Depth:** within each kernel group by chart string (first, second, third, "Other"), then line slot LT-LG-C-RG-RT, then chart column order, then jersey number, then name. The one addition to the Week 1 rule is the column order, so that the first-listed receiver column (Jackson) and tackle column (McCoy) rank ahead of the second at the same string; without it the tie would fall to jersey number, which the camp-only players lack. Unlisted players rank below every listed player of their group.
4. **Roles:** Eric Page carries `kick_return` and `punt_return` (first string at both); Barth and Murray `placekicker`; Koenen `punt`.
5. **Availability:** a player the club said would not play is unavailable (`available: false`, `injury_report: "Out"`, with the reason in `availability_note`). Practice absences alone (Dietrich-Smith and Keith Lewis earlier in the week, Bowers and Streeter on August 5, Barron resting on August 6) do not make a player unavailable; the pregame report named only three.
6. **Ids:** the player's name. No name collides with a Jacksonville-controlled player or another Tampa Bay player, so no id carries a club code.
7. **Bio fields:** birth date from the registry or nflverse; the Week 1 library's open-licensed headshot and page fields by gsis id, the photo file where the Week 1 library has none, and a Pro Football Reference page from the nflverse pfr id. Identity data only.

## The starting lineup as the chart listed it

Offense: QB Josh McCown; RB Doug Martin; FB Jorvorskie Lane; WR Vincent Jackson and Chris Owusu; TE Brandon Myers; LT Anthony Collins, LG Oniel Cousins, C Evan Dietrich-Smith, RG Jamon Meredith, RT Demar Dotson. Defense: LDE Adrian Clayborn, DT Gerald McCoy, DT Clinton McDonald, RDE Michael Johnson; SLB Jonathan Casillas, MLB Mason Foster, WLB Lavonte David; LCB Alterraun Verner (removed; Rashaan Melvin next), RCB Mike Jenkins (held out), NB Leonard Johnson; SS Mark Barron, FS Dashon Goldson (held out). Specialists: K Connor Barth, P Michael Koenen, LS Andrew DePaola, KR and PR Eric Page.

## Branch reconciliation

| Change | Player | Basis | Effect |
|---|---|---|---|
| Removed | Alterraun Verner, CB (LCB1) | Signed by Jacksonville March 11, 2014 ([fa_draws.md](../career/2014/league/personnel/fa_draws.md); replay log Entry 95). His real Tampa Bay contract does not occur in the branch | Rashaan Melvin moves up to the first string at LCB; the secondary counts 17 |
| Removed | Cameron Brate, TE (TE5) | Undrafted signing by Jacksonville May 10, 2014 ([udfa_signings.md](../career/2014/draft/udfa_signings.md), row 9); he leaves Tampa Bay under the pairing rule | Four tight ends remain |
| Removed | Jeremy Cain, LS | Re-signed by Jacksonville March 19, 2014 ([cain_negotiation](../career/2014/free_agency/cain_negotiation_2014-03-19.md)); his real March 18 Tampa Bay signing does not occur | Andrew DePaola is the only long snapper |
| Added below listed DL | Ryne Giddins, DE; James Ruffin, DE | Signed August 4, 2014, after the chart was prepared | DL 16 |
| Added below listed DB | Kip Edwards, CB (signed July 29); Danny Gorrer, CB (re-signed March 13; injured in camp, to injured reserve August 25); Mark Joyce, S (signed August 3, waived August 9) | Under contract on August 8; chart cells not located | DB 17 |
| Held out | Mike Jenkins, CB; Dashon Goldson, FS | Pregame report, August 8 (hamstring; offseason foot surgery) | Unavailable; Banks and Tandy next at their columns |
| No effect | Daniel Te'o-Nesheim, DE; Dekoda Watson, OLB | Jacksonville-controlled and unplaced respectively (Week 1 library); neither was on Tampa Bay's 2014 camp roster, as in real history | None |
| No effect | Draft pairing, branch trades, 2013 placements, retirements | No branch pairing or trade touches Tampa Bay; no Tampa Bay player retired by August 8, 2014; no 2013 branch placement sits on this roster | None |

A real Tampa Bay move the branch's Jacksonville overrides (Verner, Brate, Cain) is applied by removal with the next man up, exactly as the Week 1 build applied it. Nothing else about Tampa Bay changes: its coaching staff in the branch (Greg Schiano retained; [replay log](../career/2014/free_agency/march_2014_replay_log.md)) does not alter which players ride the rails (rails rule 2).

## Transactions July 21 to August 9, 2014

| Date | Move |
|---|---|
| July 21 | Signed LB Jeremy Grable (undrafted) and OT J.B. Shugarts |
| July 23 | Claimed LB Brandon Magee off waivers from Cleveland; placed DE Ronald Talley on the active/non-football injury list (he was activated by August 3) |
| July 27 | Re-signed CB Anthony Gaitor; signed DT Jibreel Black (undrafted); waived WR Quintin Payton and RB Brendan Bigelow |
| July 29 | Signed CB Kip Edwards (ESPN also lists July 31) |
| July 30 | Released G Carl Nicks, the mutual parting announced July 25 (ESPN lists July 29) |
| August 3 | Signed S Mark Joyce; released WR David Gettis with an injury settlement |
| August 4 | Signed DE Ryne Giddins and DE James Ruffin; waived/injured LB Jeremy Grable and S Mycal Swaim |
| August 9 | Waived S Mark Joyce (ESPN lists August 12): after the game, not applied |

## Limitations

- **Transcription, not the document:** the chart itself was not read; its contents are reconstructed from four dated transcriptions that agree wherever they overlap. The artifact's `sources` and this record name every page so that the chart can be re-read when a page is reachable, and the builder's `CHART` table can then be corrected in place.
- **Jersey numbers:** 54 players carry their 2014 Tampa Bay regular-season number (nflverse); the 33 camp-only players carry none. A camp number from a game-program listing was not used because the extracts available disagreed with each other.
- **Capture timing:** the chart was released August 5, before the August 4 moves were reflected in it (Grable and Swaim still appear); the roster is as of August 8.
- **Inactives and snap plans:** a preseason game has no inactive list; `runtime.week_inputs.game_day_actives` trims mechanically by depth when the game is built. McCown was expected to play briefly and Glennon more (pregame report); that is narration context, not an input.
- **No later information:** nothing from the game or after it is read. Danny Gorrer's August 25 injured-reserve placement and Mark Joyce's waiver are recorded only as the dates that bound their membership.

## Gate and later use

- **Information gate:** gated: usable for the August 8, 2014 preseason game and after. Until the master clock reaches that game, no rail in this file informs any evaluation, board or decision.
- **Later preseason games** (Chicago August 14, Detroit August 22, Atlanta August 28) need their own records on the same method, built when the clock reaches each game.
- **Game input:** the parent game preparation copies this club into the game folder's `opponent_roster.json`; the loader supplies the unit anchors (Document 7 section 2.2). Preseason statistics never enter the regular-season statbook, standings, awards or the draft order.

## Updating

```
python scripts/research/build_2014_preseason_opponent_rosters.py SOURCE_DIR > library/data/2014_preseason_opponent_rosters.json
python -m unittest tests.test_2014_preseason_opponent_rosters
```

`SOURCE_DIR` is a transient workspace holding nflverse `players.csv` and `roster_2014.csv`; it is never committed. Without it the build still runs from the checked-in identity files, with fewer gsis ids and jersey numbers.
