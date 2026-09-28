# 2014 league rails

**Function:** the working folder for the historical league rails rule: the other 31 clubs' rosters follow real history, while Jacksonville's come only from the branch. Rule: AGENTS.md, "Historical league rails"; Document 2 §4.5. Method: [method.md](method.md). Adopted in ledger Entry 78.
**Status:** The nine-player February 2 free-agency board is classified and sourced; the four requested retirement checks are recorded as **no dated source**, with VERIFY preserved. The wider contract inventory remains a draft. Responsibilities and limits are in [FILLING_GUIDE.md](FILLING_GUIDE.md).

| Record | What it holds | Status |
|---|---|---|
| [method.md](method.md) | The rules: gates, Jacksonville control, the free-agent market draw, retirements, the draft pairing, Week 1 charts | Adopted |
| [clubs/](clubs/) | One file per club (31): the branch's 2013 Week 1 unit, draft contract data and a dated rails table | Optional contract research only: 316 players have no contract in the data; every end year is unverified. The branch builds the real 2014 Week 1 rosters before the season |
| [free_agent_pool.md](free_agent_pool.md) | Nine verified board targets, separated into pending UFA/RFA/ERFA sections, plus 406 unverified contract candidates | Target classifications complete: eight pending UFA, one pending RFA, no targeted ERFA. The remaining candidates are not an eligibility list |
| [retirements.md](retirements.md) | Real retirements by real date, league-wide, Jacksonville included | Meester applied; Allen scheduled for April 22; four VERIFY rows researched with no exact public retirement date found |
| [draft_pairing.md](draft_pairing.md) | Jacksonville's selections, real availability and the swap partner | Empty until the draft (May 8-10, 2014) |
| [fa_draws.md](fa_draws.md) | Each market draw for a free agent Jacksonville pursues | Empty until March 11, 2014 |
| [FILLING_GUIDE.md](FILLING_GUIDE.md) | What the user fills, what the branch fills, and what never to enter | Read first |

**Builder:** `scripts/research/build_league_rails_rosters.py` (reads the downloaded `historical_contracts.csv.gz` from nflverse; only contracts signed in 2013 or earlier). It overwrites the club files and `free_agent_pool.md`. Do not rerun it over this researched version.

**Next work:** the branch maintains free-agent draws at each player's real signing date, draft pairings at the May 8-10 draft, the other clubs' Week 1 rosters before the season, and Jacksonville/state records after actual branch events. No full-club roster completion is required from the user. An additional target needs his name and position, then the same status check before pursuit.

**Gate reminder:** nothing in the rails tables applies until the career clock passes its real date. The branch is at February 2, 2014.
