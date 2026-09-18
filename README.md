# Football Career Simulation

An LLM-first, choice-driven NFL head-coaching career simulation centered on Alex-Lamar Stone. The user controls Stone's consequential choices. The simulator controls the football world, independent organizations and people, and the consequences of those choices under the repository's evidence, authority, and anti-favoritism rules.

## Current status

The project is in **PRE-HIRE SEARCH** at a January 14, 2013 reference date.

- Alex Stone's established biography and demonstrated coaching record are resolved.
- No 2013 head-coaching hire has occurred.
- The hiring search has not started yet.
- Full career initialization has not occurred.
- Team, contract, staff, active roster, and post-hire coaching identity remain unset.
- The game engine design is approved but is not runtime-ready until its era calibration is completed and a private Engine State store is instantiated for the hired team.

The lifecycle is:

`PRE-HIRE SEARCH -> HIRED / INITIALIZATION BUILD -> READY -> ACTIVE CAREER`

The hiring search is the one permitted simulated phase before full career initialization because team, contract, and starting organization are outputs of that search. No games, roster moves, staff construction, practices, press conferences, or other post-hire team events begin until the later initialization build is complete and the user explicitly starts ACTIVE CAREER play.

## Repository structure

```
foundation/   stable runtime rules, canon structure, engine design, and output templates
state/        mutable current snapshots
career/       dated simulation history, including the one pre-initialization hiring-search ledger
library/      supporting research and non-authoritative reference
archive/      historical, superseded, or quarantined material that is never runtime authority
```

### Foundation

- **`foundation/01_Project_Instructions.md`** — highest-level operating rules: user control, authority boundaries, evidence, fog of war, real-person handling, protagonist-blind resolution, lifecycle, and continuity procedure.
- **`foundation/02_League_Era_and_Sourcebook.md`** — authoring sourcebook for league, era, calendar, rules, labor, roster, financial, and draft structure. It remains an authoring master until a team is hired and an active-only edition can be built.
- **`foundation/03_Head_Coach_Organization_and_Authority_Canon.md`** — Stone's stable background, the hiring-search procedure, contract/authority structure, and initialization gate.
- **`foundation/06_Chronology_Game_Ledger_and_Handoff.md`** — ledger, audit, correction, and handoff protocol. During PRE-HIRE SEARCH, simulated search events stay in the dedicated hiring ledger rather than Document 6.
- **`foundation/07_Game_Simulation_and_Resolution_Engine.md`** — game-resolution design and private Engine State contract. Design approved, runtime not ready until initialization/calibration requirements are satisfied.
- **`foundation/templates/hiring_search_output_template.md`** — pre-hire search turns.
- **`foundation/templates/offseason_output_template.md`** — post-hire offseason turns.
- **`foundation/templates/season_output_template.md`** — in-season turns.

The rebuild audit is historical reference and lives at **`archive/00_Audit_Migration_and_Stress_Test_Report.md`**, not in the runtime rulebook.

### State

- **`state/04_Roster_and_Staff_Register.md`** — remains uninitialized until a team is hired.
- **`state/05_Current_Season_State.md`** — current PRE-HIRE SEARCH snapshot at January 14, 2013. It tracks the current lifecycle/date without pretending a team, roster, or active career already exists.

### Career

- **`career/2013/offseason/hiring_search.md`** — authorized pre-initialization decision ledger for the 2013 search. It stores organization criteria freezes, user instructions relied on, search developments, offers, and unresolved user decisions.
- **`career/2013/offseason/hiring_search_brief/`** — user-authored priorities, terms, concessions, walk-away conditions, and any exact standing acceptance/rejection rules.

After a hire, `career/2013/` becomes the normal season-history directory and gains the season ledger and only the phase files actually reached.

### Library

Runtime tasks must read only the library files permitted for their phase.

- **`library/alex_stone_character_dossier_pre_hire.md`** — factual pre-hire Stone reference. It does not decide his philosophy, motives, future staff, interview answers, or 2013 outcome.
- **`library/2013_coaching_market_pre_hire.md`** — clean opening-of-January-14 hiring-market view used by the search resolver, with events cut off at 11:59 PM ET on January 13 so later hiring outcomes cannot leak backward.
- **`library/2013_coaching_market.md`** — quarantined hindsight/comparator research. It contains actual future outcomes and must not be loaded while resolving Stone's 2013 search.
- **`library/2013_league_calendar_and_financial_rules.md`** — sourced 2013 calendar/CBA/cap research.
- **`library/2013_draft_class.md`** — final pre-selection scouting snapshot, loadable in full only at the April 25 pre-draft cutoff.
- **`library/2013_draft_information_gates.md`** — controls when declarations, combine information, pro days, medical/workout updates, and final boards become available in-world.
- **`library/2013_draft_pool_registry.md`** — eligibility/pool coverage, including the NFL's complete 73-player special-eligibility list and the conservative senior-pool rule.

Library files do not override canonical ownership in `foundation/` or `state/`.

### Archive

`archive/` contains historical or discarded material that normal runtime tasks do not load. Nothing there is active canon.

## How to run the project

For the current pre-hire phase:

1. Read Document 1.
2. Read Document 3 §10 and the hiring-search template.
3. Use `library/alex_stone_character_dossier_pre_hire.md` for Stone's established record.
4. Use only `library/2013_coaching_market_pre_hire.md` for team-side January 14 context.
5. Freeze all in-scope organizations' documented criteria before reading Stone's user-authored search brief.
6. Resolve organization-side actions without using real future hires as an answer key.
7. Stop for any consequential Stone choice not already covered by an exact user standing instruction.
8. Persist the search in `career/2013/offseason/hiring_search.md`.

If an offer is accepted, stop at **HIRED / INITIALIZATION BUILD**. Reconcile Documents 2–7, roster/staff state, contract/authority, engine state, and the audited search closure. Only after the package reaches READY and the user explicitly initializes the career does normal season/offseason play begin.

## Batch tasks

`AGENTS.md` defines bounded tasks for external coding/agent workflows. The 2013 hiring resolver is allowed only within the pre-hire control rules above. Background-game simulation is disabled until Document 7 is runtime-ready. Agents may never invent an uncovered consequential choice for Stone.
