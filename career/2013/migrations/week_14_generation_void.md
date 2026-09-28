# Week 14 generation-1 void (technical)

**Status:** CLOSED. Week 14 was replayed as event generation 2 (`2013-week14-...-g2`) and closed by ledger Entry 57.
**User authorization:** September 28, 2026. Offered "void and replay" or "keep the closed result" before any Week 14 result had been viewed; the user chose void and replay.
**Manifest:** [event_generations.json](event_generations.json).

## Defect

Stone's Week 14 plan dressed A.J. Bouye as first outside reserve corner; his Week 11 injury had cleared at its projected return (November 26). The Week 13 closure wrote his roster note as "No communicated restriction (Week 11 injury cleared November 26)". `runtime.week_inputs.roster_available` cleared only the exact note "No communicated restriction", so it treated the parenthetical as an undated hold. The generation-1 package (sha256 `3039f6e6...`) left Bouye unavailable and Jacksonville dressed 45, not 46. The build and the close were chained, so all sixteen generation-1 events closed before the squad was inspected.

## Blindness

No generation-1 receipt, score, standings or statistics view was opened. The receipts, the results cache and the re-rendered views were deleted from the working tree unread, and the committed views were restored. The void decision was the user's, made with no result known, and it replaces the whole slate, not only Jacksonville's game. The label-swap test holds: the defect removed a reserve player from one club, and the decision could not depend on a result nobody had seen.

## Replay

1. `runtime.week_inputs.roster_available` now accepts a clear note followed by an explanation, and fails the build on any note it cannot classify.
2. A new build gate fails when Jacksonville would dress fewer than 46 while healthy players sit on the inactive list, naming the unavailable players missing from Stone's list.
3. `career/2013/migrations/event_generations.json` sets Week 14 to generation 2; `runtime.week_inputs.event_id` appends `-g2`.
4. `python scripts/void_week_generation.py 14` recorded the sixteen generation-1 events as corrections in the private journal (append-only; nothing is deleted there).
5. The rebuilt package (sha256 `1b206955...`) differs from generation 1 in one place: Bouye available and active (45 to 46). It was committed with this record before any generation-2 draw.
6. All sixteen generation-2 events closed once each.
