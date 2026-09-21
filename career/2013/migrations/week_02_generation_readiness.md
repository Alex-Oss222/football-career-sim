# Week 2 generation readiness audit

**Audit date:** September 20, 2026
**Canonical effective date:** September 9, 2013, after Week 1 and before Week 2 preparation
**Status:** REPOSITORY AND STATBOOK READY FOR WEEK 2 INPUT BUILD. This audit does not itself close a Week 2 game or replace the live game-readiness and weekly TeamInput gates.
**Simulation boundary:** Oakland has not been simulated.

## Week 1 receipt reconciliation

The generation-2 Week 1 slate has sixteen closed-game receipts covering all thirty-two teams. Jacksonville-Kansas City retains full detail; the other fifteen receipts use `compact_stats`. Every receipt's final-score values reconcile to the corresponding team `points` values. The receipt set remains the durable statistical authority.

The season cache in `../stats/season_totals.json` is rebuilt from those receipts. Team scores and team statistical totals remain complete.

## Completed branch-control attribution audit

The pre-Week-2 audit found ten historical-team player identities that conflicted with Jacksonville branch control. Exact replacement attribution is unknowable, so each invalid line is preserved under an explicit pseudo/unattributed player ID instead of being reassigned by guesswork.

Affected receipts:

- Baltimore-Denver: Brynden Trawick on Baltimore and C.J. Anderson on Denver.
- Tennessee-Pittsburgh: Antwon Blake on Pittsburgh.
- Miami-Cleveland: Brent Grimes on Miami.
- Minnesota-Detroit: C.J. Mosley on Detroit.
- Green Bay-San Francisco: C.J. Wilson on Green Bay.
- Philadelphia-Washington: Jordan Poyer, Kirk Cousins and Bacarri Rambo across the affected historical-team rails.
- Kansas City-Jacksonville: Tyler Bray on Kansas City.

The correction affects exact player attribution for nine non-Jacksonville clubs across seven receipts. It changes no final score, team total, standing, Jacksonville Week 1 player line, generated medical event or game outcome. Jacksonville remains 1-0 after the 34-13 Week 1 win over Kansas City.

Because exact player attribution is partial for those corrected clubs, `../stats/league_leaders.md` continues to withhold formal league rankings. Known named-player lines remain available in the league stat views.

## Reproducibility controls

`scripts/render_season_stats.py` is the only supported rebuild path for the current season-stat cache and readable stat views. Its correction-aware version labels now match the checked-in generated files.

`scripts/validate_repository.py` now rebuilds the stat cache and all generated stat Markdown views in memory from the closed-game receipts. Validation fails if:

- a receipt's final score disagrees with its team points;
- `season_totals.json` is stale relative to the receipts; or
- a generated stat Markdown view differs from the renderer output.

The continuity test suite contains explicit failure cases for all three conditions.

## Week 2 close gates

Before any Week 2 event closes:

1. Obtain fresh qualified-medical communication for the existing carry-forward medical cases.
2. Build the complete Week 2 league TeamInput slate before any game draw.
3. Run `scripts/check_week_input_exclusivity.py` against that frozen slate and Jacksonville's current controlled roster.
4. Pass ordinary `scripts/check_game_readiness.py` against the canonical merged checkout and private runtime.
5. Close the week only after those gates pass. Do not import Oakland's real historical Week 2 result or use future roster knowledge.

This report establishes repository/statbook readiness only. It does not pre-resolve Week 2 inputs, live private-runtime readiness, medical communication or the Oakland result.
