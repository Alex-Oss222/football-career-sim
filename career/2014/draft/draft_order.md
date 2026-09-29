# 2014 NFL Draft: all seven rounds (branch)

**As of:** February 2, 2014; ledger Entry 81. **Draft:** May 8–10, 2014.
**Generated** by `python scripts/render_draft_order.py` from closed branch receipts and [pick_ownership.json](pick_ownership.json). Edit the underlying dated records, then regenerate; do not edit these tables by hand.
**Coverage:** all **224 ordinary selections**, with original club and recorded owner shown separately. Compensatory selections are still pending; this is not a final 256-pick execution list.
**Rules and sources:** [verification](../../../library/2014_draft_order_verification.md), [league rules §4](../../../library/2014_league_calendar_and_financial_rules.md#4-2014-draft-order-rules-applied-to-the-branchs-2013-season). Clubs tied on winning percentage rotate within their elimination group: first goes to last, the others move up. No real 2014 order or selection is imported.

## Jacksonville's current draft capital

**Corrected Cousins deal:** Jacksonville received Kirk Cousins **and Washington's original 2014 first**; Washington received Jacksonville's original **2014 and 2015 seconds**. Jacksonville retains its own first. [Completed trade](../../2013/trades/trades.md); [controlling correction, Entry 80](../../2013/ledger.md#entry-80-cousins-trade-and-draft-capital-reconciled).
**Historical exception:** real Washington had previously conveyed its 2014 first to St. Louis. The user expressly corrected this branch asset to Jacksonville after that conflict was disclosed. St. Louis does not also own No. 13; no compensating Rams deal is invented.

**Inherited asset restored (Entry 81):** Detroit's original fifth belongs to Jacksonville from the 2012 Mike Thomas trade. [League ownership audit](ownership_audit.md).

| Round | Original club | Slot in round | Overall pick | Current owner |
|---:|---|---|---|---|
| 1 | Washington Redskins | 13 | 13 | **Jacksonville Jaguars** |
| 1 | Jacksonville Jaguars | 26 | 26 | **Jacksonville Jaguars** |
| 2 | Jacksonville Jaguars | 26 | 58 | **Washington Redskins** |
| 3 | Jacksonville Jaguars | 26 | 90 | **Jacksonville Jaguars** |
| 4 | Jacksonville Jaguars | 26 | 122 + C3 | **Jacksonville Jaguars** |
| 5 | Detroit Lions | 11 | 139 + C3 + C4 | **Jacksonville Jaguars** |
| 5 | Jacksonville Jaguars | 26 | 154 + C3 + C4 | **Jacksonville Jaguars** |
| 6 | Jacksonville Jaguars | 26 | 186 + C3 + C4 + C5 | **Jacksonville Jaguars** |
| 7 | Jacksonville Jaguars | 26 | 218 + C3 + C4 + C5 + C6 | **Jacksonville Jaguars** |

Jacksonville currently owns **8 ordinary 2014 picks**: **13**; **26**; **90**; **122 + C3**; **139 + C3 + C4**; **154 + C3 + C4**; **186 + C3 + C4 + C5**; **218 + C3 + C4 + C5 + C6**. No prospect is selected by this inventory.

| Future asset already conveyed | Current owner | Overall pick | Authority |
|---|---|---|---|
| 2015 Round 2, Jacksonville Jaguars original | Washington Redskins | Unknown; future branch season | User-corrected Cousins trade; ledger Entry 80; unconditional, slot unknown |

## How to read pending fields

- **Coin flip resolved:** one RANDOM.ORG draw returned tails at 2026-09-29 01:42:47 UTC. The preassigned mapping gives **Indianapolis 14, Green Bay 15** in Round 1. That result is applied to every later rotation. [Receipt](coin_flip.json); [saved website result](coin_flip_2026-09-29.jpg).
- **Overall offsets:** C3, C4, C5 and C6 are the unknown numbers of compensatory picks appended to those rounds. An expression is not an exact overall number. Round 3 ordinary picks precede that round's compensatory additions.
- **Ownership audited:** all 224 ordinary assets have a current allocation. A **conditional hold** identifies a specific outstanding claim, not a second owner. Revis affects one of Tampa Bay's third/fourth; Benn is one claim against an undisclosed Philadelphia round; Rosario affects Chicago's seventh. [Terms, sources and branch exclusions](ownership_audit.md).
- **Execution gate:** resolve any conditional hold before spending that asset. `require_clear_ownership` rejects held or unaudited assets. Resolve compensatory numbering before executing affected selections, and reconcile any newly recorded forfeiture. The branch currently records no forfeited selection.
- **Existing package A:** the verified rotation puts Seattle's original second at No. 36; Stone's frozen memo also calls it No. 37. Reconcile that intended asset before executing the offer. No Seattle trade or amended offer is recorded here.

## Round 1

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 1 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick; Non-playoff; SOS 0.514 |
| 2 | 2 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick; Non-playoff; SOS 0.496 |
| 3 | 3 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick; Non-playoff; SOS 0.508 |
| 4 | 4 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick; Non-playoff; SOS 0.496 |
| 5 | 5 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick; Non-playoff; SOS 0.508 |
| 6 | 6 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick; Non-playoff; SOS 0.480 |
| 7 | 7 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick; Non-playoff; SOS 0.502 |
| 8 | 8 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick; Non-playoff; SOS 0.504 |
| 9 | 9 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick; Non-playoff; SOS 0.506 |
| 10 | 10 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick; Non-playoff; SOS 0.527 |
| 11 | 11 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick; Non-playoff; SOS 0.533 |
| 12 | 12 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick; Non-playoff; SOS 0.533 |
| 13 | 13 | Washington Redskins | Jacksonville Jaguars | 7-8-1 | User-corrected Cousins trade; ledger Entry 80; Non-playoff; SOS 0.490 |
| 14 | 14 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick; Non-playoff; SOS 0.479 |
| 15 | 15 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick; Non-playoff; SOS 0.479 |
| 16 | 16 | New York Giants | New York Giants | 8-8-0 | Retained original pick; Non-playoff; SOS 0.500 |
| 17 | 17 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick; Non-playoff; SOS 0.510 |
| 18 | 18 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick; Non-playoff; SOS 0.514 |
| 19 | 19 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick; Non-playoff; SOS 0.535 |
| 20 | 20 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick; Non-playoff; SOS 0.484 |
| 21 | 21 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick; Lost Wild Card; SOS 0.480 |
| 22 | 22 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick; Lost Wild Card; SOS 0.498 |
| 23 | 23 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick; Lost Wild Card; SOS 0.504 |
| 24 | 24 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick; Lost Wild Card; SOS 0.496 |
| 25 | 25 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick; Lost Divisional; SOS 0.527 |
| 26 | 26 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick; Lost Divisional; SOS 0.477 |
| 27 | 27 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick; Lost Divisional; SOS 0.445 |
| 28 | 28 | New York Jets | New York Jets | 12-4-0 | Retained original pick; Lost Divisional; SOS 0.494 |
| 29 | 29 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts.; Lost conference championship; SOS 0.506 |
| 30 | 30 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick; Lost conference championship; SOS 0.496 |
| 31 | 31 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick; Lost Super Bowl; SOS 0.453 |
| 32 | 32 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick; Won Super Bowl; SOS 0.525 |

## Round 2

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 33 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 34 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 35 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 36 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 5 | 37 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 6 | 38 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 39 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 8 | 40 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 9 | 41 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 10 | 42 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 11 | 43 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 12 | 44 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 13 | 45 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 46 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 15 | 47 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 16 | 48 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 17 | 49 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 18 | 50 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 19 | 51 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 20 | 52 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 53 | Kansas City Chiefs | San Francisco 49ers | 9-7-0 | Alex Smith: KC finished 9-7 in the branch; meets .500 escalation, third retained; Entry 81 |
| 22 | 54 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick |
| 23 | 55 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 24 | 56 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 57 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 58 | Jacksonville Jaguars | Washington Redskins | 10-6-0 | User-corrected Cousins trade; ledger Entry 80 |
| 27 | 59 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 60 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 61 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 62 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 63 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 64 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

## Round 3

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 65 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 66 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 67 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 68 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 5 | 69 | Seattle Seahawks | Minnesota Vikings | 6-10-0 | Percy Harvin: Consideration for accepted 2013 background acquisition; Entry 81 |
| 6 | 70 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 71 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 8 | 72 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 9 | 73 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 10 | 74 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 11 | 75 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 12 | 76 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 13 | 77 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 78 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 15 | 79 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 16 | 80 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 17 | 81 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 18 | 82 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 19 | 83 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 20 | 84 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 85 | Tampa Bay Buccaneers | Tampa Bay Buccaneers **conditional hold** | 9-7-0 | revis: One pick to NYJ: R3 if Revis remains on TB roster March 13, otherwise R4. Both alternatives reserved. |
| 22 | 86 | Pittsburgh Steelers | Cleveland Browns | 9-7-0 | Shamarko Thomas draft trade: Consideration for accepted 2013 draft acquisition; Entry 81 |
| 23 | 87 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 24 | 88 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 89 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 90 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 91 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 92 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 93 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 94 | Tennessee Titans | San Francisco 49ers | 10-6-0 | Justin Hunter draft trade: Consideration for accepted 2013 draft acquisition; Entry 81 |
| 31 | 95 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 96 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**After Round 3:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned.

## Round 4

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 97 + C3 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 98 + C3 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 99 + C3 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 100 + C3 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 5 | 101 + C3 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 6 | 102 + C3 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 103 + C3 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 8 | 104 + C3 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 9 | 105 + C3 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 10 | 106 + C3 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 11 | 107 + C3 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 12 | 108 + C3 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 13 | 109 + C3 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 110 + C3 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 15 | 111 + C3 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 16 | 112 + C3 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 17 | 113 + C3 | Indianapolis Colts | Cleveland Browns | 8-8-0 | Montori Hughes draft trade: Consideration for accepted 2013 draft acquisition; Entry 81 |
| 18 | 114 + C3 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 19 | 115 + C3 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 20 | 116 + C3 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 117 + C3 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 22 | 118 + C3 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 23 | 119 + C3 | Tampa Bay Buccaneers | Tampa Bay Buccaneers **conditional hold** | 9-7-0 | revis: One pick to NYJ: R3 if Revis remains on TB roster March 13, otherwise R4. Both alternatives reserved. |
| 24 | 120 + C3 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 121 + C3 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 122 + C3 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 123 + C3 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 124 + C3 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 125 + C3 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 126 + C3 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 127 + C3 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 128 + C3 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**After Round 4:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned.

## Round 5

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 129 + C3 + C4 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 130 + C3 + C4 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 131 + C3 + C4 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 132 + C3 + C4 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 5 | 133 + C3 + C4 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 6 | 134 + C3 + C4 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 135 + C3 + C4 | Oakland Raiders | Seattle Seahawks | 7-9-0 | Matt Flynn: Unconditional 2014 portion; 2015 condition not settled here; Entry 81 |
| 8 | 136 + C3 + C4 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 9 | 137 + C3 + C4 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 10 | 138 + C3 + C4 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 11 | 139 + C3 + C4 | Detroit Lions | Jacksonville Jaguars | 7-9-0 | Mike Thomas: Inherited pre-divergence consideration; Entry 81 |
| 12 | 140 + C3 + C4 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 13 | 141 + C3 + C4 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 142 + C3 + C4 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 15 | 143 + C3 + C4 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 16 | 144 + C3 + C4 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 17 | 145 + C3 + C4 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 18 | 146 + C3 + C4 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 19 | 147 + C3 + C4 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 20 | 148 + C3 + C4 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 149 + C3 + C4 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 22 | 150 + C3 + C4 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick |
| 23 | 151 + C3 + C4 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 24 | 152 + C3 + C4 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 153 + C3 + C4 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 154 + C3 + C4 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 155 + C3 + C4 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 156 + C3 + C4 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 157 + C3 + C4 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 158 + C3 + C4 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 159 + C3 + C4 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 160 + C3 + C4 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**After Round 5:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned.

## Round 6

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 161 + C3 + C4 + C5 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 162 + C3 + C4 + C5 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 163 + C3 + C4 + C5 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 164 + C3 + C4 + C5 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 5 | 165 + C3 + C4 + C5 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 6 | 166 + C3 + C4 + C5 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 167 + C3 + C4 + C5 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 8 | 168 + C3 + C4 + C5 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 9 | 169 + C3 + C4 + C5 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 10 | 170 + C3 + C4 + C5 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 11 | 171 + C3 + C4 + C5 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 12 | 172 + C3 + C4 + C5 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 13 | 173 + C3 + C4 + C5 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 174 + C3 + C4 + C5 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 15 | 175 + C3 + C4 + C5 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 16 | 176 + C3 + C4 + C5 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 17 | 177 + C3 + C4 + C5 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 18 | 178 + C3 + C4 + C5 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 19 | 179 + C3 + C4 + C5 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 20 | 180 + C3 + C4 + C5 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 181 + C3 + C4 + C5 | Tampa Bay Buccaneers | Chicago Bears | 9-7-0 | Gabe Carimi: Consideration for accepted 2013 background acquisition; Entry 81 |
| 22 | 182 + C3 + C4 + C5 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 23 | 183 + C3 + C4 + C5 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 24 | 184 + C3 + C4 + C5 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 185 + C3 + C4 + C5 | Dallas Cowboys | Kansas City Chiefs | 8-8-0 | Edgar Jones: 2014 sixth for Jones and KC seventh; Entry 81 |
| 26 | 186 + C3 + C4 + C5 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 187 + C3 + C4 + C5 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 188 + C3 + C4 + C5 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 189 + C3 + C4 + C5 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 190 + C3 + C4 + C5 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 191 + C3 + C4 + C5 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 192 + C3 + C4 + C5 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**After Round 6:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned.

## Round 7

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 193 + C3 + C4 + C5 + C6 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 194 + C3 + C4 + C5 + C6 | Baltimore Ravens | Indianapolis Colts | 5-11-0 | A.Q. Shipley: Roster condition met in accepted branch Week 1 lineup; Entry 81 |
| 3 | 195 + C3 + C4 + C5 + C6 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 196 + C3 + C4 + C5 + C6 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 5 | 197 + C3 + C4 + C5 + C6 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 6 | 198 + C3 + C4 + C5 + C6 | Arizona Cardinals | Oakland Raiders | 6-9-1 | Carson Palmer: Thirteen-start condition met; branch QB1 and sole passer in all sixteen games; Entry 81 |
| 7 | 199 + C3 + C4 + C5 + C6 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 8 | 200 + C3 + C4 + C5 + C6 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 9 | 201 + C3 + C4 + C5 + C6 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 10 | 202 + C3 + C4 + C5 + C6 | Chicago Bears | Chicago Bears **conditional hold** | 7-9-0 | rosario: Conditional seventh to DAL; playing-time threshold unverified. Branch appearances alone do not prove the clause. |
| 11 | 203 + C3 + C4 + C5 + C6 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 12 | 204 + C3 + C4 + C5 + C6 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 13 | 205 + C3 + C4 + C5 + C6 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 206 + C3 + C4 + C5 + C6 | Indianapolis Colts | St. Louis Rams | 8-8-0 | Josh Gordy: Inherited pre-divergence consideration; Entry 81 |
| 15 | 207 + C3 + C4 + C5 + C6 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 16 | 208 + C3 + C4 + C5 + C6 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 17 | 209 + C3 + C4 + C5 + C6 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 18 | 210 + C3 + C4 + C5 + C6 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 19 | 211 + C3 + C4 + C5 + C6 | Carolina Panthers | San Francisco 49ers | 8-8-0 | Pre-divergence Colin Jones trade, reported August 31, 2012 |
| 20 | 212 + C3 + C4 + C5 + C6 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 213 + C3 + C4 + C5 + C6 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 22 | 214 + C3 + C4 + C5 + C6 | Kansas City Chiefs | Dallas Cowboys | 9-7-0 | Edgar Jones: Counterpart of Dallas sixth in same Jones trade; Entry 81 |
| 23 | 215 + C3 + C4 + C5 + C6 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick |
| 24 | 216 + C3 + C4 + C5 + C6 | New Orleans Saints | San Francisco 49ers | 10-6-0 | Parys Haralson: Roster condition met in accepted branch Week 1 lineup; Entry 81 |
| 25 | 217 + C3 + C4 + C5 + C6 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 218 + C3 + C4 + C5 + C6 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 219 + C3 + C4 + C5 + C6 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 220 + C3 + C4 + C5 + C6 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 221 + C3 + C4 + C5 + C6 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 222 + C3 + C4 + C5 + C6 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 223 + C3 + C4 + C5 + C6 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 224 + C3 + C4 + C5 + C6 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**After Round 7:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned.

## Pending compensatory selections

The 2014 awards depend on qualifying **2013 free-agent losses and signings**, not the upcoming 2014 market. The announcement gate is **March 24, 2014**. Resolve branch eligibility and awards without importing the real recipients; the private formula's exact weights are not supplied by this generator. In 2014 these picks cannot be traded.

| Appended after | Count | Owner / overall numbering |
|---|---|---|
| Round 3 | C3: pending | Pending; no real award list imported |
| Round 4 | C4: pending | Pending; no real award list imported |
| Round 5 | C5: pending | Pending; no real award list imported |
| Round 6 | C6: pending | Pending; no real award list imported |
| Round 7 | C7: pending | Pending; no real award list imported |

The league's 32 supplemental choices are additional to the 224 ordinary allocations. Until their round distribution is reconciled, later overall pick expressions must retain their offsets. The ownership audit records the three specific open claims; there is no blanket outside-club ownership gap.
