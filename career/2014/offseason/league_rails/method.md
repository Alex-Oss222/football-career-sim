# Historical league rails: method

**Adopted:** September 28, 2026, by the user (AGENTS.md, "Historical league rails"; Document 2 §§4.3a and 4.5; ledger Entry 77).
**Purpose:** keep the branch's league the same league of players the real NFL had from 2014, while Jacksonville's roster and contracts come only from the branch.

## 1. What rides the rails

For the 31 clubs other than Jacksonville, real player movement:
- free-agent signings and re-signings;
- trades and releases;
- retirements;
- draft selections and undrafted signings;
- each season's real Week 1 depth chart.

Game results, statistics, injuries, suspensions, awards, standings, the draft order, and coaching and front-office changes are never rails. Players ride the rails whatever coaches the branch gave their clubs (the coaching carousel, ledger Entry 75, stands).

## 2. Information gate

A rail is used only once the career clock reaches its real public date.
- Each club file's "Changes on the rails" table is filled with the real date of each move. A move enters the branch only when a closed event passes that date.
- No rail may inform an evaluation, a board or a decision by Stone, Caldwell or any club before its date.
- Real contract terms for a free agent Jacksonville pursues are read only at that player's draw (§4).

## 3. Jacksonville control

- Jacksonville's roster, contracts, cap and transactions come from branch decisions only, under Caldwell's authority (Document 3). A real move involving a Jacksonville-controlled player does not apply. The one exception is retirement (§5).
- A move the real Jaguars made and the branch did not never happens. A player the real Jaguars signed as a free agent stays available to Jacksonville; if Jacksonville never signs him, he is unplaced, as in 2013.
- A player who leaves Jacksonville (not re-signed, released or traded) follows his real next move only if it was the same kind of move in the same window, for example a free-agent signing in March after his contract ran out. Otherwise he is an unplaced free agent.

## 4. Free agents Jacksonville pursues: the market draw

One private draw per player, at his real signing date. Caldwell's best offer made by that date is compared with the contract the player really signed.

- **Money index:** m = 0.5 x (Jacksonville's average per year / real average per year) + 0.5 x (Jacksonville's guarantee / real guarantee). If the real contract had no guarantee, m uses the average per year alone.
- **Chance Jacksonville signs him:**

| Money index m | Chance |
|---|---|
| Below 0.80 | 0 |
| 0.80 to 1.00 | Rises in a straight line from 0 to 0.50 |
| 1.00 to 1.25 | Rises in a straight line from 0.50 to 0.90 |
| Above 1.25 | 0.90 |

  At parity the chance is even, because the player chose his real club for reasons beyond money. It never passes 0.90.
- **Timing:** an offer counts only if it was legal on its date. Agents could negotiate from noon March 8, 2014; signing was allowed from 4 p.m. March 11. A player who really signed before Jacksonville made an offer is gone.
- **Restricted, exclusive-rights and tagged players:** the original club's right to match or to hold the player is decided by its real action. A club that really kept the player matches.
- **Result:** if Jacksonville wins, he leaves his real 2014 club and the next man up takes his depth slot. If it loses, he goes to his real club on his real terms and date.
- The draw goes through the private service, with this method committed before the first draw. Each draw is recorded in `fa_draws.md`.
- **Label swap:** only the two contracts and the dates are inputs.

The weights are the branch's modelling choice; no source supplies them. The user may change them before the first draw, never after.

## 5. Retirements

Every real retirement applies on its real public date, league-wide, Jacksonville included, because retirement is the player's own choice. For a Jacksonville player:
- the ledger records the date and any contract and cap effect;
- a retirement dated before a branch event that depends on the player is applied first.

Recorded in `retirements.md`.

## 6. Draft

- **Order:** Jacksonville's order is computed from branch standings (Document 2 §12); it picks 26th in each round in 2014, and its second-round pick went to Washington for Cousins.
- **Other clubs:** their selections are their real selections.
- **Availability:** a prospect is available at Jacksonville's branch overall pick N only if his real selection was pick N or later, or he went undrafted, and Jacksonville has not already taken him.
- **Swaps:** Jacksonville's k-th selection pairs with the real Jaguars' k-th selection.
  - The real Jaguars' player goes to the club that really drafted Jacksonville's player, and takes the depth slot he really held on his Week 1 chart.
  - If Jacksonville's player went undrafted in reality, the real Jaguars' player goes to the club where Jacksonville's player really signed as an undrafted free agent.
  - A real Jaguars' selection with no partner is unplaced.
  - Recorded in `draft_pairing.md`.
- **Undrafted players Jacksonville signs:** they leave their real clubs, and the next man up takes the slot.

## 7. Week 1 depth charts

Each season, the 31 clubs' TeamInputs start from their real Week 1 depth charts, built when those charts are public, as `library/2013_week1_depth_charts.md` was for 2013. The build applies:
- Jacksonville-controlled players removed;
- draft swaps;
- free agents lost to Jacksonville;
- rail retirements.

Later weeks carry forward with branch-generated availability.

## 8. Work split

- **Built by the branch:**
  - the rule and this method;
  - draft club rosters from the 2013 Week 1 units and Over The Cap contract data (`clubs/`, `free_agent_pool.md`);
  - the draw, pairing and retirement records.
- **The user completes:**
  - full rosters, including players off the Week 1 charts and practice squads;
  - confirmed contract years and 2014 status;
  - the real dated moves in each club's rails table, as the clock reaches them.
