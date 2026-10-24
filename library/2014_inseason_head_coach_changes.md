# In-season head-coach changes, 2002-2012: the weekly check's rate table

[Season end, "How the club decides"](../docs/season_end.md#how-the-club-decides) · [Event inserts, section D](../docs/event_inserts.md#d-year-specific-rules-and-authority) · [The January base rates](data/2012_hc_change_base_rates.json) · [Employment decision research](2014_jacksonville_employment_decision_research.md) · [The 2014 method](../data/2014/League/Coaching_Changes/method.json)

**What this is.** The sourced in-season rate the designs require before the weekly check for head-coach changes may generate a change ([season end](../docs/season_end.md#how-the-club-decides), section C, item 3; [event inserts](../docs/event_inserts.md), section D): the real 2002 to 2012 chance, per game, that a club's head coach is gone before its next game, by the club's record and the coach's season with the club. The artifact is [`library/data/2012_hc_inseason_hazard.json`](data/2012_hc_inseason_hazard.json), built by `scripts/research/build_hc_inseason_hazard.py` (pass 1, with a `--check` mode) and checked by `scripts/research/verify_hc_inseason_hazard.py` (pass 2, separate code). Nothing in it is typed by hand. The weekly check (`scripts/coaching_check.py`, `runtime/league_coaches.py`) reads only this committed table; nothing at run time opens the source file.

**Hindsight boundary.** The career diverged on January 15, 2013. Every outcome counted here is a change during a real regular season from 2002 to 2012; the last counted change came in the 2011 season. No row after 2012 is read, and no 2013 or 2014 change, real or branch, enters the table. The one exception is inherited, not added: the block written for step 6 (the January table conditional on no in-season change) is derived from the January table, which reads its 2012 club-seasons' outcomes from the September 2013 openers ([employment research](2014_jacksonville_employment_decision_research.md), section 1.8, item 4); this record takes no new post-boundary reading.

**Status.** Built October 23 to 24, 2026 for rebuild step 5 (part D2), in two passes. Adopted as the weekly check's rate by the user's answer of October 23, 2026, "One draw for all 32 (Recommended)" ([rebuild plan change log](../docs/rebuild_plan.md#change-log)). The cells, the smoothing and the merge rule are the career's labelled modelling choice, like the January factors: the user may change them before the first weekly draw, never after (the [method](../data/2014/League/Coaching_Changes/method.json) records the table's sha256, and every week's check record carries it). The user confirmed them as built, with no split by recent playoffs, on October 24, 2026, verbatim: "No playoff split (Recommended)" (the method's `adopted.confirmed`; [rebuild plan change log](../docs/rebuild_plan.md#change-log)).

**Labels.** As in the [employment research](2014_jacksonville_employment_decision_research.md): **Confirmed** is a repository fact re-read and recomputed with separate code; **Modelling choice** is the career's own labelled choice, not a fact found; **Inherited** is a reading taken over from an earlier record with that record's own label.

## Source

| Item | Value | Label |
|---|---|---|
| File | nflverse nfldata, `data/games.csv` | Confirmed |
| Commit | `04a6ffcccc8a58451f45cd282c0f14766aaa3479` (September 28, 2026, 19:45:13 UTC; the file was current until the next change at 20:15:15 UTC) | Confirmed |
| Pinned URL | https://raw.githubusercontent.com/nflverse/nfldata/04a6ffcccc8a58451f45cd282c0f14766aaa3479/data/games.csv | Confirmed |
| sha256 | `c14c7de28c9eb7027699b9b316f7276ea03e34a077c8ae65010f15a44a6780d1` | Confirmed |

**How the commit was found.** The January base-rate builder (`scripts/research/build_hc_change_base_rates.py`, committed September 28, 2026 at 20:26:45 UTC in repository commit 35f1276) took a local copy of the file and recorded only nfldata's moving master URL and the sha256 above; no copy is in the repository. On October 23, 2026 nfldata's history was cloned without file contents and the 421 commits that changed `data/games.csv` from September 21 to 29, 2026 were listed (413 distinct versions of the file). The file was then hashed at the commits before the January builder's, newest first: the second, at commit `04a6ffcc`, matched. It was the version current in the half hour before the January builder was committed. The commit-pinned URL then returned the same bytes. The builder fetches that URL by default and refuses any other digest, so no slice of the file is committed.

## Pass 1: what is counted

- **The event.** The coach who coached a club's game k does not coach game k+1 or any later regular-season game that season. An interim who finishes the season counts. A stand-in for a coach who returns does not: the season's opening coach coached a later game. Indianapolis 2012, the case the brief names, shows one coach (Chuck Pagano) in every row of this file, so no stand-in arises there. A change counts whatever its cause (a firing, a resignation, an illness after which the coach did not return); the file says only who coached each game.
- **Left out.** New Orleans 2012, the suspension season, as in the January data.
- **The risk set.** Every club-season of 2002 to 2012 (351), after each of its games 1 to 15: game 16 has no later regular-season game, so a change after it is the season-end draw's. A club leaves the risk set after its first change that season, as the weekly check never draws a club again after its change. Every season of the window has sixteen regular-season games.
- **Cells (Modelling choice).** The club's losses minus wins after game k, ties counting neither: 0 or fewer, 1 to 2, 3 to 4, 5 or more; by the coach's season with the club: his first (he did not open the club's previous season) or a later one, counted as the January builder counts seasons (consecutive seasons he opened, back to 1999; 1999 to 2001 are read only for this count).
- **Smoothing (Modelling choice).** Each cell toward the overall per-game rate: rate = (changes + 75 × overall) / (club-games + 75). The prior weight of 75 club-games is the January table's prior of five club-seasons at fifteen at-risk games a club-season.
- **Merge rule (Modelling choice).** A cell with fewer at-risk club-games than the prior weight would be merged into the next band toward 0 or fewer with the same tenure, with the reason recorded. The smallest cell has 171 club-games, so none is merged.
- **Not split by recent playoffs (Modelling choice).** The January table also splits by whether the club reached the playoffs in either of the two seasons before. Of the seventeen in-season changes, 6 came at clubs with such a season, 10 at clubs without one, and 1 in a coach's first season (pass 2's listing below); a third split of eight cells holding seventeen changes was not made. The user confirmed this on October 24, 2026 ("No playoff split (Recommended)").

## The table

| Cell (losses minus wins after the game, coach's season) | Changes | At-risk club-games | Raw rate | Smoothed rate |
|---|--:|--:|--:|--:|
| 0 or fewer, first season | 0 | 466 | 0.000000 | 0.000455 |
| 0 or fewer, later season | 0 | 2,473 | 0.000000 | 0.000097 |
| 1 to 2, first season | 0 | 265 | 0.000000 | 0.000724 |
| 1 to 2, later season | 2 | 830 | 0.002410 | 0.002482 |
| 3 to 4, first season | 0 | 171 | 0.000000 | 0.001001 |
| 3 to 4, later season | 6 | 433 | 0.013857 | 0.012296 |
| 5 or more, first season | 1 | 190 | 0.005263 | 0.004703 |
| 5 or more, later season | 8 | 349 | 0.022923 | 0.019449 |
| All | 17 | 5,177 | 0.003284 | |

Every value: **Confirmed** (pass 2 reproduced each count and rate exactly). Applied back to the window's own club-games, the smoothed table expects 15.88 changes against the 17 counted: the smoothing pulls the thin cells toward the overall rate.

## The seventeen changes

The club is shown with the file's own code (nfldata codes St. Louis LA and Oakland LV, as the January builder does).

| Club (the file's code) | Season | Game | Week | Coach | Coach of the next game | Record after the game | Coach's season with the club | Cell |
|---|--:|--:|--:|---|---|---|--:|---|
| Atlanta (ATL) | 2003 | 13 | 14 | Dan Reeves | Wade Phillips | 3-10 | 5 | 5 or more, later season |
| Atlanta (ATL) | 2007 | 12 | 13 | Bobby Petrino | Emmitt Thomas | 3-9 | 1 | 5 or more, first season |
| Buffalo (BUF) | 2009 | 9 | 10 | Dick Jauron | Perry Fewell | 3-6 | 4 | 3 to 4, later season |
| Cleveland (CLE) | 2004 | 11 | 12 | Butch Davis | Terry Robiskie | 3-8 | 4 | 5 or more, later season |
| Dallas (DAL) | 2010 | 8 | 9 | Wade Phillips | Jason Garrett | 1-7 | 4 | 5 or more, later season |
| Denver (DEN) | 2010 | 12 | 13 | Josh McDaniels | Eric Studesville | 3-9 | 2 | 5 or more, later season |
| Detroit (DET) | 2005 | 11 | 12 | Steve Mariucci | Dick Jauron | 4-7 | 3 | 3 to 4, later season |
| Jacksonville (JAX) | 2011 | 11 | 12 | Jack Del Rio | Mel Tucker | 3-8 | 9 | 5 or more, later season |
| Kansas City (KC) | 2011 | 13 | 14 | Todd Haley | Romeo Crennel | 5-8 | 3 | 3 to 4, later season |
| St. Louis (LA) | 2005 | 5 | 5 | Mike Martz | Joe Vitt | 2-3 | 6 | 1 to 2, later season |
| St. Louis (LA) | 2008 | 4 | 4 | Scott Linehan | Jim Haslett | 0-4 | 3 | 3 to 4, later season |
| Oakland (LV) | 2008 | 4 | 4 | Lane Kiffin | Tom Cable | 1-3 | 2 | 1 to 2, later season |
| Miami (MIA) | 2004 | 9 | 9 | Dave Wannstedt | Jim Bates | 1-8 | 5 | 5 or more, later season |
| Miami (MIA) | 2011 | 13 | 14 | Tony Sparano | Todd Bowles | 4-9 | 4 | 5 or more, later season |
| Minnesota (MIN) | 2010 | 10 | 11 | Brad Childress | Leslie Frazier | 3-7 | 5 | 3 to 4, later season |
| San Francisco (SF) | 2008 | 7 | 7 | Mike Nolan | Mike Singletary | 2-5 | 4 | 3 to 4, later season |
| San Francisco (SF) | 2010 | 15 | 16 | Mike Singletary | Jim Tomsula | 5-10 | 2 | 5 or more, later season |

Each row: **Confirmed** by pass 2. The game is the club's own game number; the week is the league week (a bye makes them differ).

## Pass 2: separate code

`scripts/research/verify_hc_inseason_hazard.py` shares no code with the builder. It reads the file by column position, orders each club's games by date rather than by week number, and finds a change from the last game the season's opening coach coached. Run on October 24, 2026 against the pinned file, it reported **no difference**:

1. **The change list.** The same seventeen changes, club, season, game, coaches and record, as pass 1; the same 351 club-seasons; every season of the window sixteen games long.
2. **Against the January table.** Each of the seventeen is a "changed" club-season in the January table: a different coach opened the club's next season, read from that next season's first game (all of them 2012 or earlier rows): Jim Mora (Atlanta 2004), Mike Smith (Atlanta 2008), Chan Gailey (Buffalo 2010), Romeo Crennel (Cleveland 2005), Jason Garrett (Dallas 2011), John Fox (Denver 2011), Rod Marinelli (Detroit 2006), Mike Mularkey (Jacksonville 2012), Romeo Crennel (Kansas City 2012), Scott Linehan (St. Louis 2006), Steve Spagnuolo (St. Louis 2009), Tom Cable (Oakland 2009), Nick Saban (Miami 2005), Joe Philbin (Miami 2012), Leslie Frazier (Minnesota 2011), Mike Singletary (San Francisco 2009) and Jim Harbaugh (San Francisco 2011). Each sits in a January cell, and its split cell, whose changed count covers it.
3. **The rates.** Every cell's at-risk club-games and changes, the overall rate, every smoothed rate and the whole conditional block below, recomputed and equal to the committed table.
4. **By eye.** It lists every club-season of the window with more than one coach in its rows: eighteen, the seventeen changes and New Orleans 2012 (Aaron Kromer games 1-6, Joe Vitt games 7-16), which is left out.

Both passes read one file from one publisher (nflverse's nfldata), so the second pass checks the parse and the definitions, not an independent observation of who coached each game. A second publisher was tried: Pro-Football-Reference's team-season pages, which name each season's coaches with their records, were refused by the session's network proxy (HTTP 403) on October 23, 2026, and no other host was tried.

## For step 6 only: the January table conditional on no in-season change

The season-end draw (step 6) uses the January table's chance of a change by the next opener. A club changed in season has already used its chance, so for a club not changed in season step 6 reads the January cells with the seventeen in-season club-seasons taken out, smoothed exactly as the January builder smooths (prior weight 5 toward the overall rate; a split cell toward its parent): 334 club-seasons, 56 changed, overall 0.1677 (the January table: 351, 73, 0.208). The cells that lose club-seasons:

| January cell | Club-seasons | Changed | In-season changes taken out | Conditional rate | January rate |
|---|--:|--:|--:|--:|--:|
| 0-4, 1st season | 16 | 4 | 1 | 0.2304 | 0.2745 |
| 0-4, 2nd-3rd | 17 | 12 | 2 | 0.5836 | 0.6267 |
| 0-4, 2nd-3rd, no recent playoffs | 10 | 7 | 2 | 0.6612 | 0.7137 |
| 0-4, 4th+ | 15 | 9 | 2 | 0.4919 | 0.5473 |
| 0-4, 4th+, no recent playoffs | 4 | 3 | 1 | 0.6066 | 0.6736 |
| 0-4, 4th+, recent playoffs | 11 | 6 | 1 | 0.5287 | 0.5727 |
| 5-6, 2nd-3rd | 24 | 9 | 3 | 0.3393 | 0.4075 |
| 5-6, 2nd-3rd, no recent playoffs | 18 | 9 | 3 | 0.4651 | 0.5399 |
| 5-6, 4th+ | 12 | 4 | 7 | 0.2846 | 0.5017 |
| 5-6, 4th+, no recent playoffs | 3 | 2 | 3 | 0.4279 | 0.6826 |
| 5-6, 4th+, recent playoffs | 9 | 2 | 4 | 0.2445 | 0.4727 |
| 7-8, 2nd-3rd | 26 | 2 | 1 | 0.0916 | 0.1262 |
| 7-8, 2nd-3rd, recent playoffs | 11 | 1 | 1 | 0.0911 | 0.1548 |
| 7-8, 4th+ | 29 | 4 | 1 | 0.1423 | 0.1726 |
| 7-8, 4th+, no recent playoffs | 8 | 2 | 1 | 0.2086 | 0.2759 |

The other eighteen cells keep their counts; their smoothed rates move a little with the lower overall rate (the table's `january_conditional` block holds every cell). Values: **Confirmed** by pass 2. The 2012 outcomes behind both tables: **Inherited** (read from the 2013 openers, as above). Which readings step 6 applies to the table (2013 counts as a recent playoff season; 11 wins without the playoffs is read as 9 or 10) is the season-end method's, not this record's.

## Honest limits

- **Seventeen events.** The first-season cells hold one change in 1,092 club-games; their rates come mostly from the smoothing. The cells are a labelled choice the user may change before the first draw; the user confirmed them as built on October 24, 2026.
- **No cause is modelled.** The table counts a coach who did not coach again that season. Whether the club fired him, he resigned or he fell ill is not in the file and not used.
- **Per game, not per week.** A club is at risk once per game it plays; a bye week carries no risk, as the weekly check draws no club on its bye.
- **No contract, owner or market input.** As the January table, the draw reads only the record and the coach's season with the club ([employment research](2014_jacksonville_employment_decision_research.md), section 1.8, item 2).

## What this file does not contain

- No 2013 or 2014 head-coach change, real or branch, and no real 2014 firing.
- No probability for any 2014 club: the weekly check computes each club's chance from the closed games when it runs.
- No number for Jacksonville or any club alone: every club is drawn from the same table.
