# League rails: what to fill, and what not to

**For:** the user, before editing anything in this folder. **Rule source:** AGENTS.md, "Historical league rails"; [method.md](method.md).

## The short version

Most of the 31 club files do **not** need filling. When the 2014 regular season is near, the branch builds every other club's Week 1 roster from the real 2014 Week 1 depth charts (the same data source as 2013), then applies Jacksonville's moves. That brings in every real signing, trade, release, retirement and draft pick automatically. Hand-filling full rosters would be redone by that build.

What actually needs you is small:

| Needed | When | Where | What to enter |
|---|---|---|---|
| **1. The four VERIFY retirements** | Any time | `retirements.md` | For Nwaneri, Rackley, Owens and Rutland: a dated public source (outlet, title, date, link). If none exists, write "no dated source" and leave it. Do not remove the word VERIFY; the branch does that when it applies the row. |
| **2. Contract status for Stone's free-agent targets** | Before March 11, 2014 | `free_agent_pool.md` (add a row if the player is missing) | For each player on the February 2 memo's free-agency board: his 2013 club, position, and whether he is unrestricted, restricted or exclusive-rights. Nothing else. |
| **3. Any player Stone wants who is not on the memo's board** | Before March 11, 2014 | Tell the branch, or add him to the memo | Name and position. Adding him to a club file is not needed. |

Everything else is optional.

## What the branch fills (do not fill these)

| Record | Filled by the branch when |
|---|---|
| `fa_draws.md` | At each target's real signing date: his real contract terms, Caldwell's offer, the chance and the draw |
| `draft_pairing.md` | At the draft (May 8-10, 2014) |
| Other clubs' 2014 Week 1 rosters | Before the 2014 season, from the real Week 1 depth charts |
| Retirement rows other than the four VERIFY rows | As real dates are reached |
| Jacksonville's roster, register, Document 4 and 5, ledger, stats, standings | Every closed event |

## Never enter

- Game results, statistics, injuries, suspensions, awards or standings from real 2014. These are never rails.
- Coaching or front-office changes. The branch's own carousel (Entry 75) stands.
- Any real move by the Jaguars, or by a Jacksonville-controlled player, in a club file. Jacksonville's moves come only from Stone and Caldwell's decisions, and Jacksonville has no club file.
- New files or folders here. If something seems to need one, ask first.
- Edits to `foundation/`, `state/`, the ledger, or anything under `career/2013/stats/`. The branch updates those.

## If you do fill a club file (optional)

Only if you want a club's picture now instead of waiting for the Week 1 build:
- **Contract column:** fix a wrong end year, or fill "not in the contract data". Use a source dated before March 11, 2014, such as a team or league transaction page.
- **2014 status column:** one of *Under contract*, *Pending UFA*, *Pending RFA*, *Pending ERFA*, *Released (date)*, *Retired (date)*.
- **Changes on the rails table:** one row per real move, with its real date and a source. It takes effect only when the branch clock passes that date.
- Do not add stats, grades or opinions, and do not reorder the depth column.

## Order of work, if you want one

1. The four VERIFY retirements.
2. Contract status for the memo's free-agency targets: Verner, Talib, Tate, Hardy, Te'o-Nesheim, Jared Allen, Hawkins, Edelman and Sanders.
3. Nothing else is needed until the calendar moves.
