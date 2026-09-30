# 2014 league rails

**Function:** the historical league rails workspace for the other 31 clubs. Jacksonville's roster and contracts come from the branch. Rules: AGENTS.md, Historical league rails; Document 2 §4.5; [method.md](method.md). Adopted in ledger Entry 78.

**Status:** the generated February 2, 2014 research database is built. It contains 2,208 distinct player identities, including Jacksonville's 61 controlled players. It replaces the partial contract export with an ID-linked inventory, coverage report and review queue. It is not a certified end-of-season roster or live TeamInput. The public files have coverage and status limitations documented in the report.

| Record | Purpose |
|---|---|
| [league_database_report.md](league_database_report.md) | Coverage, source hashes, uncertainty, branch protections and rebuild instructions |
| [league_players.json](league_players.json) | Full player records with identity, DOB evidence, college/draft history, source observations, branch control, contract estimates and FA evidence |
| [league_players.csv](league_players.csv) | Flat player table for filtering and review |
| [league_corrections.json](league_corrections.json) | Dated, reviewed club/position/DOB/contract-year corrections keyed by GSIS ID |
| [league_exceptions.csv](league_exceptions.csv) | Unresolved placement, status, identity and contract issues by player ID |
| [source_snapshot.json.gz](source_snapshot.json.gz) | Compressed, field-limited source and branch evidence for offline regeneration; no future outcomes or 2014 draft results |
| [clubs/](clubs) | 31 generated research inventories, with manually maintained dated move tables preserved below each generated block |
| [free_agent_pool.md](free_agent_pool.md) | Nine independently verified targets plus generated, explicitly estimated UFA/RFA/ERFA candidates |
| [retirements.md](retirements.md) | Meester applied; Allen applied at Arizona April 22; four VERIFY rows with no exact public retirement date found |
| [draft_pairing.md](draft_pairing.md) | Jacksonville's selections and swap partners, filled at the May 8-10 draft |
| [fa_draws.md](fa_draws.md) | Market draws at each pursued player's real signing date |
| [FILLING_GUIDE.md](FILLING_GUIDE.md) | The small amount of human input needed and where to put it |

**Rebuild:** `python scripts/research/build_league_player_database.py`. This runs offline and preserves the sourced target section and club text outside generated markers. Add `--check` to compare the generated outputs without writing. The old `build_league_rails_rosters.py` exporter now stops with a migration message; it cannot overwrite this research.

**Next work:** resolve exceptions when a player matters, retain dated retirement evidence, and verify targeted contract terms and accrued service. The branch handles market draws, the draft and 2014 Week 1 rosters at their prescribed dates. No hand-built league roster is required.

**Gate:** the baseline is February 2, 2014. Source status does not impose real injuries or suspensions on the branch. No new retirement, transaction, calendar event, state update or private snapshot advance is performed by this build.

<!-- folder-files -->
## Files in this folder

| File | What it contains |
|---|---|
| [FILLING_GUIDE.md](FILLING_GUIDE.md) | League rails: what needs human input. |
| [draft_pairing.md](draft_pairing.md) | 2014 draft pairing. |
| [fa_draws.md](fa_draws.md) | Free-agent market draws. |
| [free_agent_pool.md](free_agent_pool.md) | 2014 free-agent pool. |
| [league_corrections.json](league_corrections.json) | Structured league corrections used by the simulation. |
| [league_database_report.md](league_database_report.md) | League database: coverage, provenance and operation. |
| [league_exceptions.csv](league_exceptions.csv) | Supporting evidence for the records in this folder. |
| [league_players.csv](league_players.csv) | Supporting evidence for the records in this folder. |
| [league_players.json](league_players.json) | Structured league players used by the simulation. |
| [method.md](method.md) | Historical league rails: method. |
| [retirements.md](retirements.md) | Retirements on the rails. |
| [source_snapshot.json.gz](source_snapshot.json.gz) | Supporting evidence for the records in this folder. |
