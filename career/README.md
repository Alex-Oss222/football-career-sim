# Career instance data

This directory holds dated simulation history. The project has one deliberate pre-initialization exception: the head-coaching search that determines Stone's first permanent job.

## Lifecycle

1. **PRE-HIRE SEARCH** — career is not initialized. Only `career/<year>/offseason/hiring_search.md` and its user-authored brief may contain dated simulated search activity.
2. **HIRED / INITIALIZATION BUILD** — an offer has been accepted by the user or by an exact pre-authorized standing instruction. The accepted search result is reconciled into Documents 2–6, the roster/staff baseline is built, and the engine is made ready.
3. **READY** — all initialization gates reconcile, but season play has not begun.
4. **ACTIVE CAREER** — the user explicitly initializes the career. Normal roster, staff, transaction, media, practice, and game events may begin.

The pre-hire search ledger exists because team, contract, and start date are outputs of the search and therefore cannot be prerequisites to it. This does not authorize other season or career events before initialization.

## Pre-hire files

```
career/
  2013/
    offseason/
      hiring_search.md
      hiring_search_brief/
        README.md
        [user-authored team/strategy files]
```

During PRE-HIRE SEARCH, `hiring_search.md` is the authorized ex-ante decision ledger for the search. It records frozen organization criteria, the user's relevant standing instructions, organization-side developments, offers, unresolved user decisions, and the final search status. Document 6 remains free of simulated events until the initialization build.

## Layout after initialization

```
career/
  <year>/
    ledger.md
    league_results/
      week_01.md
      ...
    preseason/
      bulk_report.md
    regular_season/
      weeks/
        week_01.md
        ...
    postseason/
      wild_card.md
      divisional.md
      conference.md
      championship.md
    offseason/
      closeout.md
      hiring_search.md
      hiring_search_brief/
      draft/
        draft_board.md
        results.md
      free_agency/
        plan.md
        results.md
```

Only rounds and phase files actually reached in play should be created. Do not pre-build future seasons.

`state/04_Roster_and_Staff_Register.md` and `state/05_Current_Season_State.md` hold the current snapshot. `career/` holds dated history. `foundation/` holds stable rules and canon structure, not accumulating season history.
