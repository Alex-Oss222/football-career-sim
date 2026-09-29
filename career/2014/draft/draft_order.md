# 2014 NFL Draft: all seven rounds (branch)

**As of:** March 24, 2014; ledger Entry 100 (compensatory awards announced). **Draft:** May 8–10, 2014.
**Generated** by `python scripts/render_draft_order.py` from closed branch receipts and [pick_ownership.json](pick_ownership.json). Edit the underlying dated records, then regenerate; do not edit these tables by hand.
**Coverage:** all **256 selections**: 224 ordinary picks, with original club and recorded owner shown separately, and the 32 branch compensatory picks announced March 24. Overall numbers are exact.
**Rules and sources:** [verification](../../../library/2014_draft_order_verification.md), [league rules §4](../../../library/2014_league_calendar_and_financial_rules.md#4-2014-draft-order-rules-applied-to-the-branchs-2013-season). Clubs tied on winning percentage rotate within their elimination group: first goes to last, the others move up. No real 2014 order or selection is imported.

## Jacksonville's current draft capital

**Corrected Cousins deal:** Jacksonville received Kirk Cousins **and Washington's original 2014 first**; Washington received Jacksonville's original **2014 and 2015 seconds**. Jacksonville retains its own first. [Completed trade](../../2013/trades/trades.md); [controlling correction, Entry 80](../../2013/ledger.md#entry-80-cousins-trade-and-draft-capital-reconciled).
**Historical exception:** real Washington had previously conveyed its 2014 first to St. Louis. The user expressly corrected this branch asset to Jacksonville after that conflict was disclosed. St. Louis does not also own No. 13; no compensating Rams deal is invented.

**Inherited asset restored (Entry 81):** Detroit's original fifth belongs to Jacksonville from the 2012 Mike Thomas trade. [League ownership audit](ownership_audit.md).

| Round | Original club | Slot in round | Overall pick | Current owner |
|---:|---|---|---|---|
| 1 | Washington Redskins | 13 | 13 | **Jacksonville Jaguars** |
| 1 | Jacksonville Jaguars | 26 | 26 | **Jacksonville Jaguars** |
| 2 | Arizona Cardinals | 6 | 38 | **Jacksonville Jaguars** |
| 2 | Jacksonville Jaguars | 26 | 58 | **Washington Redskins** |
| 3 | Jacksonville Jaguars | 26 | 90 | **Jacksonville Jaguars** |
| 4 | Jacksonville Jaguars | 26 | 129 | **Jacksonville Jaguars** |
| 5 | Detroit Lions | 11 | 153 | **Jacksonville Jaguars** |
| 5 | Jacksonville Jaguars | 26 | 168 | **Jacksonville Jaguars** |
| 6 | Jacksonville Jaguars | 26 | 205 | **Jacksonville Jaguars** |
| 7 | Jacksonville Jaguars | 26 | 241 | **Jacksonville Jaguars** |

Jacksonville currently owns **9 ordinary 2014 picks**: **13**; **26**; **38**; **90**; **129**; **153**; **168**; **205**; **241**. Jacksonville received **0 compensatory picks**; see [Compensatory selections](#compensatory-selections). No prospect is selected by this inventory.

| Future asset already conveyed | Current owner | Overall pick | Authority |
|---|---|---|---|
| 2015 Round 2, Jacksonville Jaguars original | Washington Redskins | Unknown; future branch season | User-corrected Cousins trade; ledger Entry 80; unconditional, slot unknown |
| 2015 Round 1, Jacksonville Jaguars original | Arizona Cardinals | Unknown; future branch season | Package I trade with Arizona, March 20, 2014; ledger Entry 99 |
| 2015 Round 4, Jacksonville Jaguars original | Arizona Cardinals | Unknown; future branch season | Package I trade with Arizona, March 20, 2014; ledger Entry 99 |
| 2016 Round 5, Jacksonville Jaguars original | Arizona Cardinals | Unknown; future branch season | Package I trade with Arizona, March 20, 2014; ledger Entry 99 |

## How to read the order

- **Coin flip resolved:** one RANDOM.ORG draw returned tails at 2026-09-29 01:42:47 UTC. The preassigned mapping gives **Indianapolis 14, Green Bay 15** in Round 1. That result is applied to every later rotation. [Receipt](coin_flip.json); [saved website result](coin_flip_2026-09-29.jpg).
- **Overall numbers:** each round's compensatory picks follow its ordinary picks, so every later overall number includes the earlier rounds' compensatory counts (Round 3: 7, Round 4: 7, Round 5: 5, Round 6: 4, Round 7: 9).
- **Ownership audited:** all 224 ordinary assets have a current allocation. A **conditional hold** identifies a specific outstanding claim, not a second owner. Revis affects one of Tampa Bay's third/fourth; Benn is one claim against an undisclosed Philadelphia round; Rosario affects Chicago's seventh. [Terms, sources and branch exclusions](ownership_audit.md).
- **Execution gate:** resolve any conditional hold before spending that asset. `require_clear_ownership` rejects held or unaudited assets. Compensatory picks cannot be traded in 2014. Reconcile any newly recorded forfeiture. The branch currently records no forfeited selection.
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
| 6 | 38 | Arizona Cardinals | Jacksonville Jaguars | 6-9-1 | Package I trade with Arizona, March 20, 2014; ledger Entry 99 |
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

**Compensatory picks after Round 3:**

| Overall pick | Club | Basis | Note |
|---|---|---|---|
| 97 | Pittsburgh Steelers | Net loss of Mike Wallace | Not tradeable |
| 98 | Green Bay Packers | Net loss of Greg Jennings | Not tradeable |
| 99 | San Francisco 49ers | Net loss of Dashon Goldson | Not tradeable |
| 100 | Baltimore Ravens | Net loss of Paul Kruger | Not tradeable |
| 101 | New Orleans Saints | Net loss of Jermon Bushrod | Not tradeable |
| 102 | Baltimore Ravens | Net loss of Dannell Ellerbe | Not tradeable |
| 103 | Detroit Lions | Net loss of Gosder Cherilus | Not tradeable |

## Round 4

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 104 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 105 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 106 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 107 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 5 | 108 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 6 | 109 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 110 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 8 | 111 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 9 | 112 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 10 | 113 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 11 | 114 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 12 | 115 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 13 | 116 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 117 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 15 | 118 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 16 | 119 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 17 | 120 | Indianapolis Colts | Cleveland Browns | 8-8-0 | Montori Hughes draft trade: Consideration for accepted 2013 draft acquisition; Entry 81 |
| 18 | 121 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 19 | 122 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 20 | 123 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 124 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 22 | 125 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 23 | 126 | Tampa Bay Buccaneers | Tampa Bay Buccaneers **conditional hold** | 9-7-0 | revis: One pick to NYJ: R3 if Revis remains on TB roster March 13, otherwise R4. Both alternatives reserved. |
| 24 | 127 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 128 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 129 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 130 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 131 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 132 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 133 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 134 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 135 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**Compensatory picks after Round 4:**

| Overall pick | Club | Basis | Note |
|---|---|---|---|
| 136 | Houston Texans | Net loss of Connor Barwin | Not tradeable |
| 137 | New York Jets | Net loss of LaRon Landry | Not tradeable |
| 138 | Baltimore Ravens | Net loss of Cary Williams | Not tradeable |
| 139 | New York Giants | Net loss of Martellus Bennett | Not tradeable |
| 140 | Pittsburgh Steelers | Net loss of Keenan Lewis | Not tradeable |
| 141 | New York Jets | Net loss of Mike Devito | Not tradeable |
| 142 | Houston Texans | Net loss of Glover Quin | Not tradeable |

## Round 5

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 143 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 144 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 145 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 146 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 5 | 147 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 6 | 148 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 149 | Oakland Raiders | Seattle Seahawks | 7-9-0 | Matt Flynn: Unconditional 2014 portion; 2015 condition not settled here; Entry 81 |
| 8 | 150 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 9 | 151 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 10 | 152 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 11 | 153 | Detroit Lions | Jacksonville Jaguars | 7-9-0 | Mike Thomas: Inherited pre-divergence consideration; Entry 81 |
| 12 | 154 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 13 | 155 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 156 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 15 | 157 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 16 | 158 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 17 | 159 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 18 | 160 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 19 | 161 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 20 | 162 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 163 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 22 | 164 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick |
| 23 | 165 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 24 | 166 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 167 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 168 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 169 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 170 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 171 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 172 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 173 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 174 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**Compensatory picks after Round 5:**

| Overall pick | Club | Basis | Note |
|---|---|---|---|
| 175 | Green Bay Packers | Net loss of Erik Walden | Not tradeable |
| 176 | New England Patriots | Net loss of Donald Thomas | Not tradeable |
| 177 | New York Jets | Net loss of Shonn Greene | Not tradeable |
| 178 | St. Louis Rams | Net loss of Brandon Gibson | Not tradeable |
| 179 | Miami Dolphins | Net loss of Davone Bess | Not tradeable |

## Round 6

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 180 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 181 | Baltimore Ravens | Baltimore Ravens | 5-11-0 | Retained original pick |
| 3 | 182 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 183 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 5 | 184 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 6 | 185 | Arizona Cardinals | Arizona Cardinals | 6-9-1 | Retained original pick |
| 7 | 186 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 8 | 187 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 9 | 188 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 10 | 189 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 11 | 190 | Chicago Bears | Chicago Bears | 7-9-0 | Retained original pick |
| 12 | 191 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 13 | 192 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 193 | Carolina Panthers | Carolina Panthers | 8-8-0 | Retained original pick |
| 15 | 194 | Indianapolis Colts | Indianapolis Colts | 8-8-0 | Retained original pick |
| 16 | 195 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 17 | 196 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 18 | 197 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 19 | 198 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 20 | 199 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 200 | Tampa Bay Buccaneers | Chicago Bears | 9-7-0 | Gabe Carimi: Consideration for accepted 2013 background acquisition; Entry 81 |
| 22 | 201 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 23 | 202 | Kansas City Chiefs | Kansas City Chiefs | 9-7-0 | Retained original pick |
| 24 | 203 | New Orleans Saints | New Orleans Saints | 10-6-0 | Retained original pick |
| 25 | 204 | Dallas Cowboys | Kansas City Chiefs | 8-8-0 | Edgar Jones: 2014 sixth for Jones and KC seventh; Entry 81 |
| 26 | 205 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 206 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 207 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 208 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 209 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 210 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 211 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**Compensatory picks after Round 6:**

| Overall pick | Club | Basis | Note |
|---|---|---|---|
| 212 | Cincinnati Bengals | Net loss of Manny Lawson | Not tradeable |
| 213 | St. Louis Rams | Net loss of Bradley Fletcher | Not tradeable |
| 214 | Pittsburgh Steelers | Net loss of Rashard Mendenhall | Not tradeable |
| 215 | New England Patriots | Net loss of Patrick Chung | Not tradeable |

## Round 7

| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |
|---|---|---|---|---|---|
| 1 | 216 | San Francisco 49ers | San Francisco 49ers | 2-13-1 | Retained original pick |
| 2 | 217 | Baltimore Ravens | Indianapolis Colts | 5-11-0 | A.Q. Shipley: Roster condition met in accepted branch Week 1 lineup; Entry 81 |
| 3 | 218 | Cincinnati Bengals | Cincinnati Bengals | 5-10-1 | Retained original pick |
| 4 | 219 | Houston Texans | Houston Texans | 6-10-0 | Retained original pick |
| 5 | 220 | Seattle Seahawks | Seattle Seahawks | 6-10-0 | Retained original pick |
| 6 | 221 | Arizona Cardinals | Oakland Raiders | 6-9-1 | Carson Palmer: Thirteen-start condition met; branch QB1 and sole passer in all sixteen games; Entry 81 |
| 7 | 222 | Denver Broncos | Denver Broncos | 7-9-0 | Retained original pick |
| 8 | 223 | Cleveland Browns | Cleveland Browns | 7-9-0 | Retained original pick |
| 9 | 224 | Detroit Lions | Detroit Lions | 7-9-0 | Retained original pick |
| 10 | 225 | Chicago Bears | Chicago Bears **conditional hold** | 7-9-0 | rosario: Conditional seventh to DAL; playing-time threshold unverified. Branch appearances alone do not prove the clause. |
| 11 | 226 | Oakland Raiders | Oakland Raiders | 7-9-0 | Retained original pick |
| 12 | 227 | Miami Dolphins | Miami Dolphins | 7-9-0 | Retained original pick |
| 13 | 228 | Washington Redskins | Washington Redskins | 7-8-1 | Retained original pick |
| 14 | 229 | Indianapolis Colts | St. Louis Rams | 8-8-0 | Josh Gordy: Inherited pre-divergence consideration; Entry 81 |
| 15 | 230 | Green Bay Packers | Green Bay Packers | 8-8-0 | Retained original pick |
| 16 | 231 | New York Giants | New York Giants | 8-8-0 | Retained original pick |
| 17 | 232 | New England Patriots | New England Patriots | 8-8-0 | Retained original pick |
| 18 | 233 | Atlanta Falcons | Atlanta Falcons | 8-8-0 | Retained original pick |
| 19 | 234 | Carolina Panthers | San Francisco 49ers | 8-8-0 | Pre-divergence Colin Jones trade, reported August 31, 2012 |
| 20 | 235 | San Diego Chargers | San Diego Chargers | 8-6-2 | Retained original pick |
| 21 | 236 | Pittsburgh Steelers | Pittsburgh Steelers | 9-7-0 | Retained original pick |
| 22 | 237 | Kansas City Chiefs | Dallas Cowboys | 9-7-0 | Edgar Jones: Counterpart of Dallas sixth in same Jones trade; Entry 81 |
| 23 | 238 | Tampa Bay Buccaneers | Tampa Bay Buccaneers | 9-7-0 | Retained original pick |
| 24 | 239 | New Orleans Saints | San Francisco 49ers | 10-6-0 | Parys Haralson: Roster condition met in accepted branch Week 1 lineup; Entry 81 |
| 25 | 240 | Dallas Cowboys | Dallas Cowboys | 8-8-0 | Retained original pick |
| 26 | 241 | Jacksonville Jaguars | Jacksonville Jaguars | 10-6-0 | Retained original pick |
| 27 | 242 | St. Louis Rams | St. Louis Rams | 11-5-0 | Retained original pick |
| 28 | 243 | New York Jets | New York Jets | 12-4-0 | Retained original pick |
| 29 | 244 | Philadelphia Eagles | Philadelphia Eagles **conditional hold** | 8-8-0 | benn: One conditional compensation claim to TB; round and trigger undisclosed. Scope hold until terms verified; not seven debts. |
| 30 | 245 | Tennessee Titans | Tennessee Titans | 10-6-0 | Retained original pick |
| 31 | 246 | Minnesota Vikings | Minnesota Vikings | 13-3-0 | Retained original pick |
| 32 | 247 | Buffalo Bills | Buffalo Bills | 9-7-0 | Retained original pick |

**Compensatory picks after Round 7:**

| Overall pick | Club | Basis | Note |
|---|---|---|---|
| 248 | Cincinnati Bengals | Net loss of Pat Sims | Not tradeable |
| 249 | New England Patriots | Net loss of Danny Woodhead | Not tradeable |
| 250 | Washington Redskins | Net loss of Lorenzo Alexander | Not tradeable |
| 251 | Cincinnati Bengals | Net loss of Dan Skuta | Not tradeable |
| 252 | New Orleans Saints | Net loss of Jonathan Casillas | Not tradeable |
| 253 | San Francisco 49ers | Fill pick to reach 32 | Not tradeable |
| 254 | Baltimore Ravens | Fill pick to reach 32 | Not tradeable |
| 255 | Cincinnati Bengals | Fill pick to reach 32 | Not tradeable |
| 256 | Houston Texans | Fill pick to reach 32 | Not tradeable |

## Compensatory selections

Announced **March 24, 2014**. The 32 picks rest on each club's qualifying **2013** free-agent losses and signings in the branch. The NFL formula's weights are unpublished, so the branch applies its own [adopted method](compensatory/method.json) to [recorded inputs](compensatory/inputs.json); no real award list is imported. [Announcement and club-by-club detail](compensatory/announcement.md); [awards receipt](compensatory/awards.json).

| Round | Picks | Overall numbers |
|---|---:|---|
| 3 | 7 | 97-103 |
| 4 | 7 | 136-142 |
| 5 | 5 | 175-179 |
| 6 | 4 | 212-215 |
| 7 | 9 | 248-256 |

Compensatory picks cannot be traded in the 2014 draft. The ownership audit records the three specific open claims on ordinary picks; there is no blanket outside-club ownership gap.
