# 2013 league awards

**Function:** the branch's own league honours, generated from branch results only. No real 2013 award result is used anywhere.
**Structure source:** [`library/2013_nfl_awards_structure.md`](../../../library/2013_nfl_awards_structure.md) (categories and calendar only).
**Method:** [`methodology.json`](methodology.json), committed before any winner was drawn.
**Record:** [`weekly_and_monthly.md`](weekly_and_monthly.md) (generated), with every draw in [`results.json`](results.json).

## How winners are chosen

Each award has one scoring formula, applied identically to every player from the closed game receipts. The club a player belongs to plays no part except to place him in the AFC or NFC. The top three in each conference make the shortlist. The private Engine State service commits the award packet (period, shortlist, panel weights and the methodology digest), then supplies the entropy for a weighted panel pick of 6:3:1 among the shortlist. This mirrors how the league office chose from its leading candidates, without letting anyone choose by feel.

## Awards generated

| Award | Periods | Status |
|---|---|---|
| AFC and NFC Offensive, Defensive and Special Teams Player of the Week | Each regular-season week | Weeks 1-8 backfilled; generated with each later week |
| AFC and NFC Offensive, Defensive and Special Teams Player of the Month | Each month, on the league's calendar | Generated when the month's weeks close |
| Season honours (AP awards, All-Pro, Pro Bowl) | After the regular season | Completed retroactively: [season_honours.md](season_honours.md), method [season_honours_method.json](season_honours_method.json) |
| Super Bowl XLVIII MVP | The Super Bowl | Completed retroactively: C.J. Spiller, Buffalo; [super_bowl_mvp.json](super_bowl_mvp.json), method [super_bowl_mvp_method.json](super_bowl_mvp_method.json) |
| Pro Bowl need players, draft and game | January 21-26, 2014 | Completed retroactively: [../pro_bowl/README.md](../pro_bowl/README.md) |

Fan-voted sponsor awards (FedEx Air & Ground, Pepsi NEXT Rookie of the Week) are not generated. The league-wide Offensive and Defensive Rookie of the Month need a sourced rookie list for all 32 clubs, which the repository does not yet hold; they are not generated until one is built. Months are assigned by NFL week (September Weeks 1-4, October 5-8, November 9-12, December 13-17).

## Season selection record

The season methods were fixed before the draws. AP ballots used regular-season Weeks 1 to 17, while the Pro Bowl vote used Weeks 1 to 16 because voting closed December 26. The line evaluation used team output for verified starters and limited each club to one lineman per position, a rule fixed before selection and applied to every club. The author had already seen the completed branch season; the formula and eligibility rules were applied uniformly. No Jacksonville player made either All-Pro team. Marcedes Lewis replaced Buffalo's Scott Chandler in the Pro Bowl; Sen'Derrick Marks was the first defensive-tackle alternate. The Rams and Jets supplied the Pro Bowl staffs. The two special-teamer slots remained unfilled because the 2013 receipts supplied no coverage-unit evidence.

The [Super Bowl MVP receipt](super_bowl_mvp.json) records the winning-club shortlist of C.J. Spiller, Leodis McKelvin and Jeff Tuel and the completed selection of Spiller. The separate [Pro Bowl record](../pro_bowl/README.md) owns the January 21 and 22 draft and January 26 game. Its exhibition receipt counts toward no regular-season or postseason statistic, standing, award or calibration band. These are preserved outcomes; reading or reorganizing this page does not authorize another draw.

## Backfill

Awards for Weeks 1-8 were not generated when those weeks closed. At the user's instruction (September 27, 2026) they were drawn on the branch date of October 27, 2013, from the receipts of those weeks only, using the same method. Each backfilled period is marked as such, and no game result or statistic changed.

<!-- event-record: {"closure": {"checkpoint": "Canonical update - October 27, 2013 - League awards backfilled", "original_close": "Commit closed - Canonical update - October 27, 2013 - League awards backfilled - canonical through October 27, after Week 8", "sequence": 47, "through": "2013-10-27"}, "date": "2013-10-27", "id": "2013-10-27-league-awards-record-created-weeks-1-8-and-september-backfilled", "kind": "technical", "status": "closed", "summary": "Weekly and monthly league awards were backfilled from completed games."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical update - February 2, 2014 - 2013 season honours drawn (retroactive)", "sequence": 71, "through": "2014-02-02"}, "date": "2014-02-02", "id": "2014-02-02-2013-season-honours-completed", "season": 2013, "status": "closed", "summary": "The 2013 season honours were completed retroactively; Maurice Jones-Drew won Comeback Player of the Year."} -->

<!-- event-record: {"closure": {"checkpoint": "Canonical update - February 2, 2014 - Super Bowl MVP and Pro Bowl drawn (retroactive)", "sequence": 73, "through": "2014-02-02"}, "date": "2014-02-02", "id": "2014-02-02-super-bowl-mvp", "season": 2013, "status": "closed", "summary": "Buffalo\u2019s C.J. Spiller was selected Super Bowl XLVIII MVP from the closed game receipt."} -->
