# 2013 NFL standings - league, conference and division

**Status:** PRE-SEASON. No regular-season game has been played; every record is 0-0-0 and no seed exists.
**Through:** nothing played. Update this line to `Through Week N (date)` each time results are entered.
**Scope:** all 32 clubs. Regular-season games only; preseason results never count.

## How this file is kept current

This is the single current-standings file for the whole league. It is rewritten in place after every regular-season week, in the same commit as the results that change it (`AGENTS.md`, atomic progression rule).

- **Inputs:** Jacksonville's game comes from `regular_season/week_NN_*/output.md`; every other game comes from `league_results/week_NN.md`. Both must be final before this file changes.
- **Weekly history:** each `league_results/week_NN.md` carries its own header snapshot of these tables, so past weeks stay recoverable. This file holds only the current state.
- **Tiebreakers:** apply the NFL procedure in `foundation/02_League_Era_and_Sourcebook.md` section 5.3, never a guess. Until a tie is broken by that procedure, mark it `TIE - unbroken` rather than ordering the clubs by feel.
- **Playoff field:** six clubs per conference (four division winners as seeds 1-4, two wild cards as seeds 5-6). Seeds are entered only once the tiebreak inputs are known.
- **Draft order:** computed from these standings by the rules in Document 2 section 12; never copied from real history.
- **Column meaning:** Div, Conf, Home and Away are W-L-T. Streak is `W3` or `L2` style. PF/PA are points for and against.

## 1. Division standings

Ordered by record within each division; tied clubs stay alphabetical and marked unbroken until the tiebreak procedure resolves them.
### AFC East

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Buffalo Bills | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Miami Dolphins | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| New England Patriots | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| New York Jets | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### AFC North

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Baltimore Ravens | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Cincinnati Bengals | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Cleveland Browns | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Pittsburgh Steelers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### AFC South

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Houston Texans | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Indianapolis Colts | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| **Jacksonville Jaguars** | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Tennessee Titans | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### AFC West

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Denver Broncos | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Kansas City Chiefs | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Oakland Raiders | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| San Diego Chargers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### NFC East

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Dallas Cowboys | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| New York Giants | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Philadelphia Eagles | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Washington Redskins | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### NFC North

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Chicago Bears | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Detroit Lions | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Green Bay Packers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Minnesota Vikings | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### NFC South

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Atlanta Falcons | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Carolina Panthers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| New Orleans Saints | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Tampa Bay Buccaneers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

### NFC West

| Team | W | L | T | Pct | PF | PA | Diff | Div | Conf | Home | Away | Streak |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|
| Arizona Cardinals | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| St. Louis Rams | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| San Francisco 49ers | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |
| Seattle Seahawks | 0 | 0 | 0 | .000 | 0 | 0 | 0 | 0-0-0 | 0-0-0 | 0-0-0 | 0-0-0 | - |

## 2. Conference standings and playoff seeding

Seed order follows the NFL rule: the four division winners ranked by record take seeds 1-4, then the two best remaining clubs take wild-card seeds 5-6. Pre-season, no seed is assigned.

### AFC

| Seed | Team | Division | W | L | T | Pct | Conf | Status |
|---:|---|---|--:|--:|--:|--:|---|---|
| 1 | - | - | - | - | - | - | - | not yet seeded |
| 2 | - | - | - | - | - | - | - | not yet seeded |
| 3 | - | - | - | - | - | - | - | not yet seeded |
| 4 | - | - | - | - | - | - | - | not yet seeded |
| 5 | - | - | - | - | - | - | - | not yet seeded |
| 6 | - | - | - | - | - | - | - | not yet seeded |

Out of the field, in current order: none ranked yet.

### NFC

| Seed | Team | Division | W | L | T | Pct | Conf | Status |
|---:|---|---|--:|--:|--:|--:|---|---|
| 1 | - | - | - | - | - | - | - | not yet seeded |
| 2 | - | - | - | - | - | - | - | not yet seeded |
| 3 | - | - | - | - | - | - | - | not yet seeded |
| 4 | - | - | - | - | - | - | - | not yet seeded |
| 5 | - | - | - | - | - | - | - | not yet seeded |
| 6 | - | - | - | - | - | - | - | not yet seeded |

Out of the field, in current order: none ranked yet.

## 3. League-wide standings

All 32 clubs ranked by overall record. Pre-season, clubs are listed alphabetically because every record is 0-0-0.

| Rank | Team | Conf | Division | W | L | T | Pct | PF | PA | Diff | Streak |
|---:|---|---|---|--:|--:|--:|--:|--:|--:|--:|---|
| 1 | Arizona Cardinals | NFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 2 | Atlanta Falcons | NFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 3 | Baltimore Ravens | AFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 4 | Buffalo Bills | AFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 5 | Carolina Panthers | NFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 6 | Chicago Bears | NFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 7 | Cincinnati Bengals | AFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 8 | Cleveland Browns | AFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 9 | Dallas Cowboys | NFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 10 | Denver Broncos | AFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 11 | Detroit Lions | NFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 12 | Green Bay Packers | NFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 13 | Houston Texans | AFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 14 | Indianapolis Colts | AFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 15 | **Jacksonville Jaguars** | AFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 16 | Kansas City Chiefs | AFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 17 | Miami Dolphins | AFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 18 | Minnesota Vikings | NFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 19 | New England Patriots | AFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 20 | New Orleans Saints | NFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 21 | New York Giants | NFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 22 | New York Jets | AFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 23 | Oakland Raiders | AFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 24 | Philadelphia Eagles | NFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 25 | Pittsburgh Steelers | AFC | North | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 26 | San Diego Chargers | AFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 27 | San Francisco 49ers | NFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 28 | Seattle Seahawks | NFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 29 | St. Louis Rams | NFC | West | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 30 | Tampa Bay Buccaneers | NFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 31 | Tennessee Titans | AFC | South | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
| 32 | Washington Redskins | NFC | East | 0 | 0 | 0 | .000 | 0 | 0 | 0 | - |
