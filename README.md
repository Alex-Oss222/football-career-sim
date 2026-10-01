# Football Career Simulation

An evidence-based NFL head-coaching career simulation centered on Alex-Lamar Stone. The user controls Stone's consequential decisions; the simulator resolves the independent football world under the established authority, chronology and no-hindsight rules.

## Start here

**[Open the 2014 season](career/2014/README.md)** — the season in calendar order, from early offseason to the handoff into 2015.

[Team and roster](career/2014/00_Team_Operations/Team/README.md) · [Depth chart](career/2014/00_Team_Operations/Team/Depth_Chart/README.md) · [Finances](career/2014/00_Team_Operations/Finances/README.md) · [Calendar](career/2014/Calendar.md) · [Trades](career/2014/00_Team_Operations/Trades/README.md)

- [Current state](state/05_Current_Season_State.md): live date, latest closed event and next decisions.
- [Player cards](career/2014/00_Team_Operations/Team/Player_Cards/README.md): current personnel assessments and each player’s annual statistics.
- [2013 season](career/2013/README.md): completed season, player sheets, statistics and history.
- [Career](career/README.md): seasons, coaching profiles and playbooks.
- [How the folders work](docs/season_structure.md): what lives in a season and what carries to the next.
- [Report templates](foundation/templates/README.md): training, games, assessments, interviews and the file that owns each completed report.

## Repository ownership

| Folder | Purpose |
|---|---|
| [foundation](foundation/01_Project_Instructions.md) | Stable operating rules, active sourcebook, authority, event-record protocol, engine specification and templates |
| [state](state/05_Current_Season_State.md) | Current coach-known register and compact resume snapshot |
| [career](career/README.md) | Season-specific plans, dated results, annual event indexes and readable current views |
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
