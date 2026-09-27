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
| Season honours (AP awards, All-Pro, Pro Bowl) | After the regular season | Method to be fixed before the end of the season |

Fan-voted sponsor awards (FedEx Air & Ground, Pepsi NEXT Rookie of the Week) are not generated. The league-wide Offensive and Defensive Rookie of the Month need a sourced rookie list for all 32 clubs, which the repository does not yet hold; they are not generated until one is built. Months are assigned by NFL week (September Weeks 1-4, October 5-8, November 9-12, December 13-17).

## Backfill

Awards for Weeks 1-8 were not generated when those weeks closed. At the user's instruction (September 27, 2026) they were drawn on the branch date of October 27, 2013, from the receipts of those weeks only, using the same method. Each backfilled period is marked as such, and no game result or statistic changed.
