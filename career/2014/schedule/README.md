# Jacksonville and league schedule, 2014

**Current state: opponents prepared; dated league schedule not yet released.** The [career calendar](../calendar.md) owns the year's dates and information gates. This folder now has the complete branch opponent inventory, not only Jacksonville's list.

| Record | Purpose |
|---|---|
| [Jacksonville opponents](opponents.md) | Eight designated home and eight away games with their formula basis |
| [All 32 clubs](league_opponents.md) | Generated home/away lists and branch same-place pairings |
| [Opponent data](league_opponents.json) | 256 matchups, branch division order, source digests and fixed London dates |
| [Rotation inputs](rotation_2014.json) and [source checks](sources.md) | Historical home/away rotation and dated provenance, without real standings or results |
| [Release plan](release_plan.md) | Build and validate the dated 256-game slate when April 23 arrives |
| [Preseason](../preseason/README.md) | Four future game slots, with their public-date gates |
| [Regular season](../regular_season/README.md) | All 17 planning windows and the weekly execution handoff |

Regenerate with `python scripts/render_2014_opponents.py`; check with `python scripts/render_2014_opponents.py --check`. Edit source inputs only after a sourced correction; never hand-edit generated files. Repository validation also checks them.

No scores, team strengths, byes, ordinary kickoff slots or standings are created. The 2013 schedule remains the 2013 runtime input until a season-aware 2014 fixture path is implemented and validated. An undated opponent row must never be passed off as a scheduled game.
