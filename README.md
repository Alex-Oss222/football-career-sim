# Football Career Simulation

An evidence-based NFL head-coaching career simulation centered on Alex-Lamar Stone. The user controls Stone's consequential decisions; the simulator resolves the independent football world under the established authority, chronology and no-hindsight rules.

## Start here

- [Current season state](state/05_Current_Season_State.md): the controlling current date, closed checkpoint, pending decisions and next event.
- [2013 Jacksonville career index](career/2013/README.md): phase records, roster, staff, cap, standings and season statistics.
- [2013 season statbook](career/2013/statbook.md): one front door for standings, Jacksonville stats, the comprehensive all-player ledger, league stats and leaderboards.
- [Game readiness](state/game_readiness.md): verified preparation and outstanding requirements before any game can be resolved.
- [Update workflow](docs/update_workflow.md): which records must change together and how to check them.
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
| [scripts](scripts/validate_repository.py) | Repository validation and game-readiness checks |
| [runtime](runtime/README.md) | Resolution-packet support and private-store interface; no private career state is committed here |

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
