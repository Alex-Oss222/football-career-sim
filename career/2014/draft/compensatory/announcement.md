# 2014 compensatory picks: branch announcement

**Announced:** Monday, March 24, 2014 (ledger Entry 100). **Generated** by `python scripts/resolve_compensatory_picks.py` from [awards.json](awards.json); do not edit by hand.

The league awarded 32 compensatory picks for the 2014 draft, placed after rounds 3 to 7. They rest on each club's qualifying unrestricted free agents lost and signed in the **2013** league year of this branch. The NFL formula's weights are unpublished, so the branch used its own [method](method.json), version 2, on [recorded inputs](inputs.json). No real 2014 award list was read. The picks cannot be traded in 2014.

## How a free agent is valued

- **Salary (primary):** his new contract's average per year as a percentile of the 2013 league market (1477 contracts in force; median $0.81M). A $12.0M deal scores about 98; a $1.0M deal about 55.
- **Playing time:** branch 2013 games for his new club as a share of that club's games: 75 percent or more costs nothing, 50 to 75 percent costs 4 points, 25 to 50 percent 8, under 25 percent 12.
- **Honours:** the highest branch 2013 honour adds points: first-team All-Pro 6, second-team 4, Pro Bowl 3.
- **Round:** Round 3 at 90, Round 4 at 82, Round 5 at 74, Round 6 at 65, Round 7 at 55. Below 55 points a free agent neither earns nor cancels a pick.
- **Net loss:** each signing cancels a loss in the same round first, then the best lower-round loss, then the weakest higher-round loss. Remaining losses become picks, at most four per club. The league fills to 32 with Round 7 picks in 2014 draft order.

## Jacksonville

**No compensatory pick.** Jacksonville lost 2 qualifying free agents and signed 3, a net gain of 1.

- **Lost:** Derek Cox (JAX to SD, $5.00M a year, 84.1 points, Round 4); Terrance Knighton (JAX to DEN, $2.25M a year, 67.5 points, Round 6).
- **Signed:** Brent Grimes (ATL to JAX, $5.50M a year, 86.0 points, Round 4); Roy Miller (TB to JAX, $2.50M a year, 69.0 points, Round 6); Sen'Derrick Marks (TEN to JAX, $1.50M a year, 61.0 points, Round 7).
- **Cancellations:** Brent Grimes cancels Derek Cox; Roy Miller cancels Terrance Knighton; Sen'Derrick Marks had no loss left to cancel.
- Daryl Smith re-signed with Jacksonville, so he was not a loss. Rashean Mathis, Eben Britton, George Selvie and other departures have no 2013 contract value in the source and are not counted.

## The 32 picks

| Overall | Round | Club | Basis |
|---:|---:|---|---|
| 97 | 3 | Pittsburgh Steelers | Net loss of Mike Wallace ($12.00M a year, 98.0 points) |
| 98 | 3 | Green Bay Packers | Net loss of Greg Jennings ($9.00M a year, 95.7 points) |
| 99 | 3 | San Francisco 49ers | Net loss of Dashon Goldson ($8.25M a year, 94.0 points) |
| 100 | 3 | Baltimore Ravens | Net loss of Paul Kruger ($8.10M a year, 93.7 points) |
| 101 | 3 | New Orleans Saints | Net loss of Jermon Bushrod ($7.19M a year, 91.3 points) |
| 102 | 3 | Baltimore Ravens | Net loss of Dannell Ellerbe ($7.00M a year, 90.5 points) |
| 103 | 3 | Detroit Lions | Net loss of Gosder Cherilus ($7.00M a year, 90.5 points) |
| 136 | 4 | Houston Texans | Net loss of Connor Barwin ($6.00M a year, 87.8 points) |
| 137 | 4 | New York Jets | Net loss of LaRon Landry ($6.00M a year, 87.8 points) |
| 138 | 4 | Baltimore Ravens | Net loss of Cary Williams ($5.67M a year, 86.8 points) |
| 139 | 4 | New York Giants | Net loss of Martellus Bennett ($5.10M a year, 84.6 points) |
| 140 | 4 | Pittsburgh Steelers | Net loss of Keenan Lewis ($5.10M a year, 84.6 points) |
| 141 | 4 | New York Jets | Net loss of Mike Devito ($4.20M a year, 84.3 points) |
| 142 | 4 | Houston Texans | Net loss of Glover Quin ($4.70M a year, 83.0 points) |
| 175 | 5 | Green Bay Packers | Net loss of Erik Walden ($4.00M a year, 80.5 points) |
| 176 | 5 | New England Patriots | Net loss of Donald Thomas ($3.50M a year, 77.8 points) |
| 177 | 5 | New York Jets | Net loss of Shonn Greene ($3.33M a year, 76.2 points) |
| 178 | 5 | St. Louis Rams | Net loss of Brandon Gibson ($3.26M a year, 75.7 points) |
| 179 | 5 | Miami Dolphins | Net loss of Davone Bess ($2.94M a year, 74.9 points) |
| 212 | 6 | Cincinnati Bengals | Net loss of Manny Lawson ($3.00M a year, 72.7 points) |
| 213 | 6 | St. Louis Rams | Net loss of Bradley Fletcher ($2.62M a year, 70.0 points) |
| 214 | 6 | Pittsburgh Steelers | Net loss of Rashard Mendenhall ($2.50M a year, 69.0 points) |
| 215 | 6 | New England Patriots | Net loss of Patrick Chung ($3.33M a year, 68.2 points) |
| 248 | 7 | Cincinnati Bengals | Net loss of Pat Sims ($1.75M a year, 62.2 points) |
| 249 | 7 | New England Patriots | Net loss of Danny Woodhead ($1.75M a year, 62.2 points) |
| 250 | 7 | Washington Redskins | Net loss of Lorenzo Alexander ($1.54M a year, 61.3 points) |
| 251 | 7 | Cincinnati Bengals | Net loss of Dan Skuta ($1.50M a year, 61.0 points) |
| 252 | 7 | New Orleans Saints | Net loss of Jonathan Casillas ($1.40M a year, 60.6 points) |
| 253 | 7 | San Francisco 49ers | Fill pick: the formula produced fewer than 32 |
| 254 | 7 | Baltimore Ravens | Fill pick: the formula produced fewer than 32 |
| 255 | 7 | Cincinnati Bengals | Fill pick: the formula produced fewer than 32 |
| 256 | 7 | Houston Texans | Fill pick: the formula produced fewer than 32 |

## Club summary

Only clubs with a qualifying loss or signing are listed. Net loss is losses minus signings; a negative number is a net gain.

| Club | Qualifying losses | Qualifying signings | Net loss | Picks |
|---|---:|---:|---:|---:|
| San Francisco 49ers | 4 | 3 | 1 | 2 |
| Baltimore Ravens | 3 | 0 | 3 | 4 |
| Cincinnati Bengals | 3 | 0 | 3 | 4 |
| Houston Texans | 3 | 1 | 2 | 3 |
| Seattle Seahawks | 2 | 2 | 0 | 0 |
| Arizona Cardinals | 0 | 3 | -3 | 0 |
| Denver Broncos | 1 | 4 | -3 | 0 |
| Cleveland Browns | 2 | 5 | -3 | 0 |
| Detroit Lions | 4 | 3 | 1 | 1 |
| Chicago Bears | 2 | 2 | 0 | 0 |
| Oakland Raiders | 4 | 5 | -1 | 0 |
| Miami Dolphins | 5 | 4 | 1 | 1 |
| Washington Redskins | 1 | 0 | 1 | 1 |
| Indianapolis Colts | 3 | 5 | -2 | 0 |
| Green Bay Packers | 2 | 0 | 2 | 2 |
| New York Giants | 2 | 1 | 1 | 1 |
| New England Patriots | 4 | 1 | 3 | 3 |
| Atlanta Falcons | 2 | 2 | 0 | 0 |
| Carolina Panthers | 1 | 1 | 0 | 0 |
| San Diego Chargers | 1 | 5 | -4 | 0 |
| Pittsburgh Steelers | 3 | 0 | 3 | 3 |
| Kansas City Chiefs | 1 | 5 | -4 | 0 |
| Tampa Bay Buccaneers | 2 | 2 | 0 | 0 |
| New Orleans Saints | 3 | 1 | 2 | 2 |
| Dallas Cowboys | 0 | 1 | -1 | 0 |
| Jacksonville Jaguars | 2 | 3 | -1 | 0 |
| St. Louis Rams | 4 | 2 | 2 | 2 |
| New York Jets | 3 | 0 | 3 | 3 |
| Philadelphia Eagles | 2 | 6 | -4 | 0 |
| Tennessee Titans | 2 | 3 | -1 | 0 |
| Minnesota Vikings | 0 | 1 | -1 | 0 |
| Buffalo Bills | 2 | 2 | 0 | 0 |

## Adjustments and limits

- **Honours applied:** Sean Smith (+3); Mike Devito (+3); Reggie Bush (+3); Davone Bess (+3); Vance Walker (+3); Justin Durant (+4).
- **Playing time applied:** Patrick Chung (8 of 19 games, -8).
- **Below the minimum value:** 12 moves: Alan Ball, Antonio Johnson, D.J. Moore, Donnie Jones, Geoff Schwartz, Kellen Winslow, Matt Shaughnessy, Matt Slauson, Quintin Demps, Rashad Jennings, Ropati Pitoitua, Tony McDaniel.
- **Coverage:** 85 valued moves (including Jacksonville's four branch signings) and 177 club changes that do not qualify or could not be valued. Most of the unvalued moves are near-minimum deals missing from the source.
- **Not applied:** the league's post-draft signing deadline (no signing dates in the source) and the unverified real fill order (the branch fills in 2014 first-round order). Playing time is games, not snaps.
- **Values:** contract APYs are Over The Cap reconstructions via nflverse, not certified league figures; Jacksonville's four signings use its branch contracts.
