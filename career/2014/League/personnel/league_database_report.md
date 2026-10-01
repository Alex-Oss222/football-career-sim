# League database: coverage, provenance and operation

**Research baseline:** 2014-02-02. **Source capture checked:** 2026-09-28. Generated deterministically from the committed, field-limited `source_snapshot.json.gz`. No runtime or calendar mutation.

## Coverage

- 2208 distinct GSIS identities; 61 Jacksonville-controlled players, including reserve/retired and practice squad.
- 1709 identities observed in Week 17 or the playoffs; 176 additional identities have no 2013 roster observation.
- 204 identities have no resolved inventory club. All remain in the database.
- 5 missing-ID source rows quarantined: Braden Wilson, Dick Conn, Ryan Swope, Terry Hawthorne.
- Sources do not establish a complete final 53 plus eight practice-squad players and every reserve list for each club. Seasonal rosters add no new IDs to the weekly feed in this capture. Annual/weekly/depth agreement is a same-provider consistency check, not independent verification.
- Players seen earlier in 2013, draft-only identities, existing branch identities and players with contract estimates spanning 2013 are retained. Absence after an earlier week does not prove release, retirement or unsigned status. Players absent from all these sources may still be missing.
- The register is used only for identity, birth date, college, OTC/PFR IDs and pre-2014 draft fields. Current status, current team, career totals and later outcomes are excluded. The draft file is projected to selection/identity fields before storage, with all 2014+ selections excluded.
- Existing reviewed DOB evidence takes precedence. New birthdays are single-provider data unless independently verified. A conflict becomes an exception rather than a guessed date.

## Free agency and contract limits

Nine targeted statuses retain the two-pass evidence in `free_agent_pool.md`. Elsewhere `years_exp + 1` is only an experience proxy for the completed 2013 season. It is not a verified accrued-season count. Four or more maps to estimated UFA, three to estimated RFA, fewer to estimated ERFA, and missing experience stays unknown.

An accrued season depends on qualifying regular-season service. Practice-squad time, credited experience, holdouts and reserve designations prevent treating the proxy as legal eligibility. Check the actual accrued service, expiration and any tag or tender for each pursued player. Rule cross-check: Tennessee Titans, [2014 NFL Free Agency Questions & Answers](https://www.tennesseetitans.com/news/2014-nfl-free-agency-questions-answers-salary-cap-set-at-133-million-12709412), March 8, 2014. Only the established free-agency definitions are used, not later player actions.

Contracts join by OTC ID from the GSIS-linked player register and matching historical club. Full-name and slash-separated club codes are normalized. Retrospective OTC club strings are limited to clubs observed for the player in 2013; later destinations are stripped. There is no name-only or wrong-club fallback. Invalid zero years, post-2013 signings and nonpositive lengths are excluded. Conflicting latest-year terms remain unresolved. Start + length - 1 is explicitly an estimate: extensions may list only added years, and release/option/restructure history is incomplete. Contract-only entries do not prove club membership. No contract dollars or future terms are imported.

| Contract evidence | Players |
|---|---|
| ambiguous_same_year_terms | 51 |
| branch_register_controls | 61 |
| club_unresolved | 168 |
| estimated_not_verified | 1165 |
| missing_otc_id | 13 |
| no_matching_club_contract | 33 |
| no_pre_2014_contract | 698 |
| sourced_correction | 2 |
| stale_contract | 17 |

Two spot checks exposed false expiry candidates: Ben Roethlisberger and Rob Gronkowski. Dated club reports and independent corroboration are recorded in `league_corrections.json`; they remain under contract rather than being classified as 2014 free agents. These corrections do not certify the remaining contract estimates.

## Branch protection and date gates

Jacksonville control comes from the current branch roster, including Reserve/Retired and practice squad, using reviewed GSIS identities. Existing 2013 trades and draft swaps are preserved. A real Jaguars player with no branch placement stays unplaced; he is never silently added to Jacksonville or another club. Existing unnamed waiver claimants remain unresolved. Real source statuses never set branch injuries, suspensions or availability.

The builder accepts only this February 2 baseline. It cannot advance the clock, resolve an offer or draw, apply a retirement, or construct 2014 Week 1 TeamInputs. Future dated moves still belong in the club rails tables; draft pairing remains at the draft. The later Week 1 build must reconcile branch control and swaps afresh. The four VERIFY retirement rows are untouched.

## Rebuild and review

- Run `python scripts/research/build_league_player_database.py` for a fully offline rebuild from the committed snapshot.
- Run `python scripts/research/build_league_player_database.py --check` to verify generated JSON, CSV, exceptions, club blocks, report and pool sections without writing.
- To recapture sources, download the six files below into a scratch directory and run `python scripts/research/build_league_player_database.py --source-dir SOURCE_DIR --capture --checked-on YYYY-MM-DD`. Review source hashes, coverage and the diff before committing. Never use later-season files under these names.
- Resolve a dated club, position, birth-date or contract-year correction in `league_corrections.json`, keyed by GSIS ID, with `note` and a `sources` list. Each source requires publisher, title, HTTPS URL and an ISO published date no later than February 2. These corrections cannot change Jacksonville control or existing branch placements. Use paired contract_start and contract_end fields for sourced term corrections. Free-agent-category confirmations belong in the sourced target section.
- Edit the verified section and source receipt in `free_agent_pool.md`, not generated candidate rows. Rebuilds preserve that section. Club text outside the generated markers, including dated moves, is also preserved. Reviewed club/position/DOB/contract-year corrections belong in `league_corrections.json` before rebuilding; do not hand-edit generated outputs.
- `league_exceptions.csv` is the full row-level review queue. Missing or ambiguous contracts need attention when a player is pursued, not a manual cleanup of the whole league. The existing retired-player research remains in `retirements.md`.

## Input hashes

| Input | Raw rows | SHA-256 |
|---|---|---|
| [depth_charts_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2013.csv) | 37066 | `68a48cb5c3488aa505c2612c21797353c794c9ce5094e5071cc866373e71fd71` |
| [draft_picks.csv](https://github.com/nflverse/nflverse-data/releases/download/draft_picks/draft_picks.csv) | 12927 | `2c286fc7892b3178819c846e8c9bdd7be8689bbdd1cbe56cf5e0de318231abf8` |
| [historical_contracts.csv.gz](https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.csv.gz) | 31893 | `000916029c2b41127034346c978f001d30b3e25efb0106fd43816accd9d59c3f` |
| [players.csv](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv) | 24833 | `40677127536c7e6c9d36840cd4dbea07a0d231def170d925f403fe05f7a59c26` |
| [roster_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv) | 2137 | `abf73c2b1ef10914af78f6b7397338508bd0c9f0372d2f0667a630e06a4484ed` |
| [roster_weekly_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2013.csv) | 31901 | `76c47a629075ffd75f9c4ee49fadb6dad45396be486af897078fee5722969781` |

Status-code reference: [nflreadr roster status dictionary](https://nflreadr.nflverse.com/articles/dictionary_roster_status.html). The source status codes are retained verbatim, not interpreted as dated transactions.
