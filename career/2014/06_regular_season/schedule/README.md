# Jacksonville and league schedule, 2014

**Current state: released April 23, 2014, 8 p.m. ET ([ledger](../../ledger.md)).** The [career calendar](../../calendar.md) owns the year's dates and information gates. This folder has the complete historical opponent inventory and the frozen 256-game fixture release.

| Record | Purpose |
|---|---|
| [Jacksonville opponents](opponents.md) | Eight designated home and eight away games with their formula basis |
| [All 32 clubs](league_opponents.md) | Generated home/away lists and historical same-place pairings |
| [Opponent data](league_opponents.json) | 256 matchups, historical schedule order, source digests and fixed London dates |
| [Rotation inputs](rotation_2014.json) and [source checks](sources.md) | Historical home/away rotation and dated provenance, without real results or performance evidence |
| [Fixtures](fixtures.json) and [readable view](fixtures.md) | Frozen April 23 release: 256 dated games, byes, neutral London sites and dated amendments not yet applied |
| [Release plan](release_plan.md) | Acceptance checks and the April 23 gate |
| [Preseason](../../05_training_camp_and_preseason/02_preseason_games/README.md) | Four future game slots, with their public-date gates |
| [Regular season](../games/README.md) | All 17 planning windows and the weekly execution handoff |

Regenerate with `python scripts/render_2014_opponents.py`; check with `python scripts/render_2014_opponents.py --check`. Edit source inputs only after a sourced correction; never hand-edit generated files. Repository validation also checks them.

Fixture acceptance checks run in `tests/test_2014_fixtures.py`. No scores, team strengths or standings are created. The 2013 schedule remains exclusive to 2013; the game release gates still block 2014 execution. An undated opponent row must never be passed off as a scheduled game.

<!-- folder-files -->
## Files in this folder

| File | What it contains |
|---|---|
| [fixtures.json](fixtures.json) | Frozen machine-readable league fixtures, dates and venues. |
| [fixtures.md](fixtures.md) | 2014 league fixtures (April 23 release). |
| [league_opponents.json](league_opponents.json) | Structured league opponents used by the simulation. |
| [league_opponents.md](league_opponents.md) | 2014 league opponents (historical calendar). |
| [opponents.md](opponents.md) | Jacksonville 2014 opponents. |
| [release_plan.md](release_plan.md) | Release the historical 2014 schedule. |
| [rotation_2014.json](rotation_2014.json) | The historical opponent rotation used to verify the schedule. |
| [sources.md](sources.md) | 2014 opponent rotation: evidence and verification. |
