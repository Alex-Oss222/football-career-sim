# Football Career Simulation

An evidence-based NFL head-coaching career simulation centered on Alex-Lamar Stone. The user controls Stone's consequential decisions; the simulator resolves the independent football world under the established authority, chronology and no-hindsight rules.

## Start here

- [2014 work in order](career/2014/README.md): current team, finances, offseason, games and annual handoff.
- [Player cap and organization finances](career/finances/README.md): separate accounting areas and contract history.
- [2014 setup and readiness](career/2014/readiness.md): current handoff, prepared folders and requirements before execution.
- [2014 operating baseline](career/2014/operating_baseline.md): offseason work and year-owner transition.
- [Living coaching profiles](career/coaching_profiles/README.md): Stone and the staff after the full 2013 season.

- [Current season state](state/05_Current_Season_State.md): the controlling current date, closed checkpoint, pending decisions and next event.
- [2013 Jacksonville career index](career/2013/README.md): archived phase records, checkpoint views, standings and season statistics.
- [2013 season statbook](career/2013/statbook.md): one front door for standings, Jacksonville stats, the comprehensive all-player ledger, league stats and leaderboards.
- [Player ages](career/2014/player_ages.md): sourced DOBs and ages at the current simulation date, including Jacksonville's practice squad.
- [Game readiness](state/game_readiness.md): verified preparation and outstanding requirements before any game can be resolved.
- [Update workflow](docs/update_workflow.md): which records must change together and how to check them.
- [Run-week prompt](docs/run_week.md): the handoff for a regular-season week and the inputs Stone supplies first.
- [Agent instructions](AGENTS.md): task-specific execution rules.

Current status is maintained in the linked state files. This index deliberately carries no independent date, roster count, cap balance or readiness declaration.

## Repository ownership

| Folder | Purpose |
|---|---|
| [foundation](foundation/01_Project_Instructions.md) | Stable operating rules, active sourcebook, authority, ledger protocol, engine specification and templates |
| [state](state/05_Current_Season_State.md) | Current coach-known register and compact resume snapshot |
| [career](career/README.md) | Season-specific plans, dated results, ledger and readable current views |
| [library](library/2013_jacksonville_master_calendar.md) | Sourced research; each file states its permitted information date |
| [archive](archive/README.md) | Superseded or quarantined material, excluded from ordinary runtime reads |
| [docs](docs/update_workflow.md) | File ownership, dependencies and maintenance procedure |
| [scripts](scripts/validate_repository.py) | Validation, readiness, weekly input build and close, generated views and private-snapshot advance |
| [runtime](runtime/README.md) | Shared game kernel (2013.x), authenticated private-service interface and public statbook; no private career state is committed here |

## Work on the repository

Use a branch and pull request. Run:

```sh
python scripts/validate_repository.py
python -m unittest discover -s tests -v
python scripts/check_game_readiness.py
```

Repository validation and game readiness are separate checks. A clean file structure does not authorize a game. Readiness exits unsuccessfully while a required calibration, rule, runtime or private-store requirement remains unresolved.

## Resume the career

Read the current-state file first, then the relevant authority, calendar, phase plan, active playbook and latest event records. Follow only the playbook iterations permitted for the in-simulation year. Keep the user's decisions, medical authority and verified historical information boundaries intact.

The hiring search is preserved as completed history in [its ledger](career/2013/offseason/hiring_search.md). It is not the current entry point.
