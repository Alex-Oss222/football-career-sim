# 2014 league rails

**Function:** the working folder for the historical league rails rule: the other 31 clubs' rosters follow real history, while Jacksonville's come only from the branch. Rule: AGENTS.md, "Historical league rails"; Document 2 §4.5. Method: [method.md](method.md). Adopted in ledger Entry 78.
**Status:** DRAFT. The structure is built and pre-filled; the user is completing rosters and contracts.

| Record | What it holds | Status |
|---|---|---|
| [method.md](method.md) | The rules: gates, Jacksonville control, the free-agent market draw, retirements, the draft pairing, Week 1 charts | Adopted |
| [clubs/](clubs/) | One file per club (31): the branch's 2013 Week 1 unit with contract years from Over The Cap data, a 2014 status column for the user, and a dated rails table | Draft: 316 players have no contract in the data; every end year is unverified |
| [free_agent_pool.md](free_agent_pool.md) | Players whose latest contract in the data ends with 2013 (413) | Draft: status (UFA, RFA, ERFA) not separated |
| [retirements.md](retirements.md) | Real retirements by real date, league-wide, Jacksonville included | Empty: fill by date |
| [draft_pairing.md](draft_pairing.md) | Jacksonville's selections, real availability and the swap partner | Empty until the draft (May 8-10, 2014) |
| [fa_draws.md](fa_draws.md) | Each market draw for a free agent Jacksonville pursues | Empty until March 11, 2014 |
| [FILLING_GUIDE.md](FILLING_GUIDE.md) | What the user fills, what the branch fills, and what never to enter | Read first |

**Builder:** `scripts/research/build_league_rails_rosters.py` (reads the downloaded `historical_contracts.csv.gz` from nflverse; only contracts signed in 2013 or earlier). Re-running it overwrites the club files, so rerun it only before the user edits them.

**Gate reminder:** nothing in the rails tables applies until the career clock passes its real date. The branch is at February 2, 2014.
