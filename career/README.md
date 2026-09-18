# Career instance data

Holds the actual played career — one subfolder per year, exactly the way the SCOTUS project's `terms/OT<year>/` holds one folder per term. `foundation/` and `state/` never accumulate season-by-season instance data; this folder is where it lives.

**Exception to "empty until initialization": the hiring search itself is tracked here too, starting immediately.** Document 1 §2 and Document 3 §12 already carve the hiring search out from the season/career initialization gate — it's the process that produces the team the gate needs, so it can't wait on it. The same logic applies to file-keeping: the search is a real, dated, multi-turn process, and per the lesson of the SCOTUS project, nothing real should live only in chat scrollback — it needs an actual file that survives the conversation, gets appended to turn by turn, and is still there if this project picks up in a new chat. That file is `career/2013/offseason/hiring_search.md` (2013 because that's the real year, known before the team is), updated in place as each turn happens. Once a team hire is finalized, `career/2013/` stops being just the hiring-search folder and becomes that team's actual 2013 folder per the layout below — the hiring-search file stays exactly where it is, now as that team's offseason record, and Document 3 §1.4 / Document 6 get updated with the concluded outcome.

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

A season folder is otherwise created only when that season is actually reached in play — never pre-built in advance, and never for a season with no career events yet. The hiring search is the one deliberate exception, per above.
