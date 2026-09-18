# Career instance data

Empty until the user completes Document 1's initialization gate. This folder holds the actual played career — one subfolder per season, exactly the way the SCOTUS project's `terms/OT<year>/` holds one folder per term. `foundation/` and `state/` never accumulate season-by-season instance data; this folder is where it lives.

## Layout, once initialized

```
career/
  2013/
    ledger.md                  <- this season's slice of the Document 6 append-only ledger (schema/format defined in foundation/06_..., not here)
    preseason/
      bulk_report.md           <- the single bulk turn per Document 7 §5.1
    regular_season/
      weeks/
        week_01.md              <- one file per week, in season_output_template.md's format
        week_02.md
        ...
    postseason/
      wild_card.md
      divisional.md
      conference.md
      championship.md          <- only the rounds actually reached
    offseason/
      closeout.md               <- offseason_output_template.md's format, front-office + self-assessment
      draft/
        draft_board.md
        results.md
      free_agency/
        plan.md
        results.md
  2014/
    ...
```

Why per-season, not one continuously growing file: the same reason SCOTUS splits per term instead of one file for the whole Court's history — a multi-year coaching career's week-by-week record would otherwise become one unmanageable file. `state/04_Roster_and_Staff_Register.md` and `state/05_Current_Season_State.md` always hold only the CURRENT snapshot (updated in place, per Document 7 §6.3); this folder holds the full history those snapshots were built from.

A season folder is created only when that season is actually reached in play — never pre-built in advance, and never for a season with no career events yet.
