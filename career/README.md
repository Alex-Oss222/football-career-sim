# Career instance data

This directory holds dated simulation history and explicitly identified current views. Start with the [2013 career index](2013/README.md) and [current state](../state/05_Current_Season_State.md). The lifecycle below describes transitions; it does not declare the present phase.

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
    calendar.md                 <- branch-facing full-season calendar: camps, preseason, games, roster/cap deadlines and conditional postseason gates
    coaching_staff.md          <- clean current staff list, no process narrative; the hiring process itself lives in offseason/staff_building/hires.md
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
      initial_cap_sheet.md       <- historical starting financial baseline for that inherited roster
      current_cap_worksheet.md   <- current branch accounting after transactions; Top-51/full-roster effects and current planning room
      roster_evaluation.md       <- Stone's own dated evaluation of the inherited roster and his approach across the offseason calendar -- his recommendation; actual roster cuts/outcomes are not assumed from it
      the_prowl_program_identity.md            <- Stone's user-established coaching identity ("The Prowl"), full text; Document 3 SS2.1 carries only the summary and points here
      the_prowl_player_readiness_standard.md   <- companion file: the physical/psychological/financial/family player-readiness system
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
        plan.md
        output.md
        standouts.md
      otas/
        plan.md
        output.md
        standouts.md           <- who stood out and why, with evidence -- practice performance is evidence, never a hidden true-ability reveal (Document 1 SS6.3)
      mandatory_minicamp/
        plan.md
        output.md
        standouts.md
      training_camp/
        plan.md
        output.md
        standouts.md
        position_battles.md    <- evidence-based open competitions
        roster_decisions.md   <- dated decisions; state/04 holds the current result
    standings.md                <- the single current league / conference / division standings file (all 32 clubs); updated after each final regular-season result; a closed weekly snapshot is kept in league_results/week_NN.md
    preseason/
      README.md                 <- game index (date, kickoff, matchup, home/away)
      game_1_miami_at_jacksonville/output.md      <- one folder per game, named game_N_<away>_at_<home>; resolved as one bulk turn per Document 7 SS5.1
      game_2_jacksonville_at_ny_jets/output.md
      game_3_philadelphia_at_jacksonville/output.md
      game_4_jacksonville_at_atlanta/output.md
      final_roster_cuts.md
    regular_season/
      README.md                 <- week index (date, kickoff, matchup, home/away)
      week_01_kansas_city_at_jacksonville/
        output.md               <- season_output_template.md; a bye week uses the same slot with no game, per SS below
      ...                       <- folders are named week_NN_<away>_at_<home>; Week 9 is week_09_bye
      week_17_jacksonville_at_indianapolis/
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

Only phases and rounds actually reached in play get created — never pre-built ahead of when the career actually gets there, and never for a season with no career events yet. **Exception, at the user's request (2026-09-19):** the 2013 `standings.md`, `preseason/` game folders and `regular_season/` week folders were pre-built as `NOT STARTED` stubs from the verified master calendar so the schedule and standings are easy to find; the approved repository repair also creates training-camp record stubs, explicitly `NOT STARTED`. The conditional `postseason/` folders and `league_results/` files are still created only when reached. Detailed field-by-field formats for a new file type (e.g. `draftees.md`, `standouts.md`, a closeout file) get written as a dedicated template in `foundation/templates/` the same way the three current templates were, when that phase is actually about to be reached — not invented in advance of need.

**A year folder is the NFL season being built and played, not a calendar year.** `career/2013/postseason/` holds the playoffs that conclude the 2013 season even though they're played in January/February 2014; `career/2013/closeouts/` closes out the 2013 season before `career/2014/offseason/` opens. This resolves what would otherwise be a real ambiguity once the league year and the calendar year diverge.

**Bye week:** still gets its own `regular_season/week_NN_bye/output.md`, so the week numbering stays one continuous sequence — it just carries no game, and covers practice, recovery, self-scout, and anything material that happened instead.

**Trades aren't confined to one phase** — they can happen at the draft, in free agency, or around the real in-season trade deadline — so `trades/` sits at the year level rather than nested under `offseason/`, and gets a dated entry in `trades.md` whenever one actually closes, whatever the calendar says. The procedure is Document 7 SS6.2's free-agency pattern (coach's plan, autonomous market pressure from other clubs, one consolidated outcome report, immediate cap/roster accounting), applied to trades — see Document 7 SS6.2a.

**A new head coach's voluntary veteran minicamp** (a real, separate 2013 offseason-program allowance beyond the standard OTA/mandatory-minicamp structure) is covered inside `otas/output.md` unless something in it is material enough to earn its own record — it doesn't need a dedicated folder.

`state/04_Roster_and_Staff_Register.md` and `state/05_Current_Season_State.md` hold the current snapshot. `career/` holds dated history — the plan file for a phase is never rewritten to match its own outcome after the fact. `foundation/` holds stable rules and canon structure, not accumulating season history.

## Dependency checks

[Update workflow](../docs/update_workflow.md) and [file map](../docs/repository_map.json) define the closure requirements. Run `python scripts/validate_repository.py` before committing. Calendar links, source hashes, summaries and current-state checkpoints are checked; an unchanged financial record may retain its last financial-event date.
