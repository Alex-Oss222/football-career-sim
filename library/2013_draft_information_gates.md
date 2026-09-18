# Library: 2013 NFL Draft Information Gates

**Status:** Runtime date-gating companion for the 2013 draft class  
**Purpose:** Prevent later pre-draft information from leaking backward into earlier simulation dates.

This file controls **when** the research in `library/2013_draft_class.md` may become available. The main scouting file is a final pre-selection snapshot, not a January sourcebook.

## Core rule

Never load the full final scouting snapshot merely because it exists in the repository.

At any simulation date, use only information that had become public by that date. A later board, combine result, pro-day result, medical update, or declaration decision stays unavailable until its real publication/event date.

## January 14, 2013

At the current pre-hire project date:

- the 2012 college season and bowl results already exist;
- ordinary senior eligibility can be researched from the player's actual college status;
- the underclassman declaration process is **not yet closed**;
- the deadline for underclassmen to declare is January 15, 2013;
- the final list of 73 players granted special eligibility is not yet public;
- no February combine results, March/April pro-day results, or April final boards are available.

**Runtime consequence:** do not load `library/2013_draft_class.md` in full on January 14. If a specific prospect becomes relevant before the declaration deadline, use only dated pre-January-15 evidence for that prospect.

## January 15-19: declaration window closes

NFL.com tracked announced underclassman intentions through the January 15 deadline. The league subsequently announced the 73 players granted special eligibility.

After the official special-eligibility announcement, the complete 73-player underclassman list in `library/2013_draft_pool_registry.md` becomes eligible runtime information.

Source:
https://www.nfl.com/news/seventy-three-players-granted-special-eligibility-for-nfl-draft-0ap1000000128329

## February: combine invitations and testing

NFL.com published the 333-player combine invitation list on February 6, 2013. Invitation status becomes public from that date.

Combine measurements and drill results become available only after the relevant player actually measures or works out. Do not preload final combine numbers before the event.

Source:
https://www.nfl.com/news/manti-te-o-heads-list-of-nfl-scouting-combine-invitees-0ap1000000136883

## March-April: pro days and medical/workout updates

A pro-day result, private/public workout result, or public medical update becomes usable only on or after its dated event/report.

Examples already sourced in the main scouting file include:

- D.J. Hayden: March 18.
- Star Lotulelei: March 20.
- Jarvis Jones: March 21.
- Keenan Allen: April 9.
- Eddie Lacy: April 11.
- Tank Carradine: April 20.

The dates above are gates, not guarantees of evaluation quality. Team doctors and private club information remain separate from public reporting.

## Final public boards

- April 18: Mike Mayock final position rankings.
- April 19: Mayock Top 100.
- April 24: Gil Brandt Hot 100 + 25.

Those rankings are unavailable before their publication dates.

## Final hard cutoff

The 2013 NFL Draft begins Thursday, April 25, 2013 at **8:00 PM ET**.

At any point before 8:00 PM ET, only pre-selection information already public by that time may be used. Once the first selection begins, the real draft itself becomes quarantined history and must not be imported into the simulation's selection process.

Source:
https://espnpressroom.com/press-release/espn-and-the-2013-nfl-draft/

## Runtime loading rule

- January 14: use this gate file plus prospect-specific evidence dated on or before January 14.
- After the special-eligibility announcement: add the underclassman pool registry.
- After the combine: add only completed combine information.
- After each pro day/workout: add that dated information.
- April 18-24: add the corresponding final public boards as they publish.
- April 25 before 8:00 PM ET: the complete `2013_draft_class.md` final snapshot may be loaded.
- After 8:00 PM ET: resolve the simulation draft from simulation state only. Never consult the real selection order or destinations.
