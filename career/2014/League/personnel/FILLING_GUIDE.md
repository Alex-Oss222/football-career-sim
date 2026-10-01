# League rails: what needs human input

The league research inventory is generated from public files. Do not hand-build 31 rosters. Start with [the coverage report](league_database_report.md), [the player table](league_players.csv) or [the exception queue](league_exceptions.csv).

## Three kinds of input

1. **A player the data cannot place.** Supply his name or GSIS ID, the conflicting or missing fact, and a dated source. The branch resolves the source correction and regenerates the affected views. Unknown does not mean unsigned, retired or unavailable.
2. **The four VERIFY retirements.** Nwaneri, Rackley, Owens and Rutland currently have **no dated source** for an exact public retirement date. If a public announcement is found, add the outlet, title, publication date and link to `retirements.md`. Leave VERIFY until the branch applies the supported date.
3. **A player Stone actually targets.** Give his name and position. The branch verifies his contract expiration, accrued service and any controlling tag/tender before pursuit. The nine February 2 targets already have sourced pending classifications in `free_agent_pool.md`; their contract money is researched at the prescribed draw date.

Most missing contracts can stay unresolved until a player matters. A seasons-of-experience estimate is not a legal eligibility ruling. Source statuses, stale contracts and missing rows do not settle a player's availability.

## Where updates belong

- Add verified target categories and citations above the generated block in `free_agent_pool.md`. Preserve the UFA/RFA/ERFA table format so the generator can read the evidence. A targeted player absent from the database needs a reviewed identity/source addition first.
- Put dated real moves for other clubs in the existing **Changes on the rails** table below the generated block in `clubs/<CODE>.md`. Include the real public date and source. A row takes effect only when an authorized closed event reaches its date.
- Put reviewed club, position, birth-date or contract-year corrections in `league_corrections.json`, keyed by GSIS ID, then rebuild. Include a note and dated sources, each with publisher, title, URL and publication date on or before February 2. For contract years, supply both `contract_start` and `contract_end`. Keep verified UFA/RFA/ERFA classifications and their citations in the manual free-agent section. Do not edit `league_players.json`, the generated CSVs, the compressed evidence snapshot or generated Markdown blocks by hand.
- Free-form club notes may go outside the generated markers. The builder preserves that text. The source snapshot and generated outputs were added for this authorized database build; further manual file structures are not needed.

## What the branch handles

- Database regeneration, identity joins, exception records and preservation of Jacksonville control.
- Free-agent draws at each pursued player's real signing date.
- Draft pairing at the May 8-10 draft.
- The other clubs' real 2014 Week 1 rosters before the season, with Jacksonville control, draft swaps and free agents won by Jacksonville reconciled again.
- Later retirements as their dates arrive.
- Jacksonville's roster, contracts, state, dated record, statistics and snapshot after actual branch events.

## Boundaries

Never add real 2014 game results, statistics, injuries, suspensions, awards or standings. Never import real coaching changes or real Jaguars transactions. Source roster status is historical evidence, not branch availability. Jacksonville has no generated club file.

The database build does not authorize editing `foundation/`, `state/`, dated event records or statistics. Those records change only through the normal event workflow. February 2, 2014 is this research database's baseline, not the current career clock; the current date belongs to [Document 5](../../../../state/05_Current_Season_State.md).

Rebuild with `python scripts/research/build_league_player_database.py`; verify with the same command plus `--check`. The legacy exporter is disabled. Generated club rows are alphabetized for lookup, while their old Week 1 slot labels remain reference information, not a new depth order.
