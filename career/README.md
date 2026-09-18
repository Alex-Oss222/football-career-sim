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

Adopted 2026-09-18, replacing an earlier, flatter version of this layout. The change is structural only — every existing rule in this file and in Document 7 still applies unchanged; this just gives each phase its own plan-file/result-file pair and its own dated record, the same separation `hiring_search_brief/` already established for the search itself.

```
career/
  <year>/
    ledger.md
    league_results/
      week_01.md
      ...
      week_17.md              <- the rest of the league; real season length per Document 2 (Document 7 SS5.3)
    trades/
      trade_targets.md        <- Stone's own dated plan: what he'd move, what he wants, acceptable cost -- not rewritten after the outcome is known
      trade_offers.md         <- inbound: real proposals from other clubs under discussion, dated, before any is accepted or declined
      trades.md               <- history: only trades that actually closed, both sides, date, draft-capital/cap effect -- completing one here updates state/04's roster/staff register and Document 4's cap reconciliation in the same turn, per Document 7 SS6.3's immediate-update rule
    offseason/
      hiring_search.md
      hiring_search_brief/
      initial_roster.md          <- built once, right after a hire closes: the real inherited roster, sourced -- players/positions/experience only, no contract figures
      initial_cap_sheet.md       <- the full financial breakdown for that same roster: contract terms, cap hits, dead money, cap space (AGENTS.md's roster/cap-sheet task); both kept here rather than library/ so they're found with the rest of that year's record
      staff_building/
        staff_plan.md          <- who Stone is pursuing/considering, and why
        hires.md               <- who actually signed on, in what role, when
      free_agency/
        player_board.md        <- dated plan: needs, targets, own free agents, acceptable terms, priorities
        signings.md            <- history: who signed, terms, date, competing-market result, cap effect
      draft/
        player_draft_board.md  <- evolves as scouting information becomes legally available (date-gated, per library/2013_draft_information_gates.md's pattern)
        draftees.md            <- the simulation's own actual selections; never a real 2013 destination (Document 2 SS12)
      rookie_minicamp/
        output.md
      otas/
        output.md
        standouts.md           <- who stood out and why, with evidence -- practice performance is evidence, never a hidden true-ability reveal (Document 1 SS6.3)
      mandatory_minicamp/
        output.md
        standouts.md
    training_camp/
      camp_output.md
      standouts.md
      position_battles.md      <- each open competition, tracked on evidence, not a secret score
      roster_decisions.md      <- why a roster/depth-chart change happened; state/04 holds only the current result
    preseason/
      preseason_output.md      <- all preseason games in one bulk report, per Document 7 SS5.1's exception
      final_roster_cuts.md
    regular_season/
      week_01/
        output.md               <- season_output_template.md; a bye week uses the same slot with no game, per SS below
      ...
      week_17/
        output.md
    postseason/
      wild_card/
        output.md
      divisional/
        output.md
      conference_championship/
        output.md
      super_bowl/
        output.md
    closeouts/
      player_closeout.md       <- one concise entry per rostered player: role, availability, evaluation, contract/2014 status
      team_closeout.md         <- final record, unit-by-unit assessment, transactions, unresolved issues
      coach_closeout.md        <- Stone's own record/decisions/relationships -- only what was actually established, never his feelings invented for him
      season_closeout.md       <- short administrative bridge: final ledger checkpoint, roster/contract/cap snapshot, next phase
```

Only phases and rounds actually reached in play get created — never pre-built ahead of when the career actually gets there, and never for a season with no career events yet. Detailed field-by-field formats for a new file type (e.g. `draftees.md`, `standouts.md`, a closeout file) get written as a dedicated template in `foundation/templates/` the same way the three current templates were, when that phase is actually about to be reached — not invented in advance of need.

**A year folder is the NFL season being built and played, not a calendar year.** `career/2013/postseason/` holds the playoffs that conclude the 2013 season even though they're played in January/February 2014; `career/2013/closeouts/` closes out the 2013 season before `career/2014/offseason/` opens. This resolves what would otherwise be a real ambiguity once the league year and the calendar year diverge.

**Bye week:** still gets its own `regular_season/week_NN/output.md`, so the week numbering stays one continuous sequence — it just carries no game, and covers practice, recovery, self-scout, and anything material that happened instead.

**Trades aren't confined to one phase** — they can happen at the draft, in free agency, or around the real in-season trade deadline — so `trades/` sits at the year level rather than nested under `offseason/`, and gets a dated entry in `trades.md` whenever one actually closes, whatever the calendar says. The procedure is Document 7 SS6.2's free-agency pattern (coach's plan, autonomous market pressure from other clubs, one consolidated outcome report, immediate cap/roster accounting), applied to trades — see Document 7 SS6.2a.

**A new head coach's voluntary veteran minicamp** (a real, separate 2013 offseason-program allowance beyond the standard OTA/mandatory-minicamp structure) is covered inside `otas/output.md` unless something in it is material enough to earn its own record — it doesn't need a dedicated folder.

`state/04_Roster_and_Staff_Register.md` and `state/05_Current_Season_State.md` hold the current snapshot. `career/` holds dated history — the plan file for a phase is never rewritten to match its own outcome after the fact. `foundation/` holds stable rules and canon structure, not accumulating season history.
