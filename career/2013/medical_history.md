# Jacksonville medical history: recovered records and season-end returns

These are previously closed simulation decisions. The original injury reports remain with their games; this file preserves the later availability changes that would otherwise lose their dated owner. A projected return, an applied availability change and an actual practice appearance are recorded separately.

## October 27, 2013: Pasztor and Mosley availability corrected

Austin Pasztor sustained a simulated head/neck injury with an independent medical hold in the [August 17 preseason game](preseason/game_2_jacksonville_at_ny_jets/output.md). C.J. Mosley sustained a simulated upper-extremity injury and was unavailable after the [August 29 preseason game](preseason/game_4_jacksonville_at_atlanta/output.md). The original reports omitted their generated return projections. Neither preseason input packet had been preserved, so an exact replay could not recover the missing fields.

The user authorized a single audited recovery for each missing projection. The [recovery record](migrations/injury_projection_recovery.json) preserves the procedure, precommitted packet and model digests, result references and both recovered projections. Pasztor's result was a minor injury with a two-day projection, August 19; Mosley's was a minor injury with a one-day projection, August 30. These were recovered simulation fields, not new medical examinations.

Both projections preceded the regular season, but the missing dates had left both players unavailable through Weeks 1–8. Their availability was restored prospectively at the October 27 checkpoint. Their missed games were not rewritten, no game was replayed, and neither player received a role or an automatic game-day activation. The Week 8 inactive list remained in place until Stone changed it. Their first recorded practice after the correction was during the [Week 9 bye](regular_season/week_09_bye/output.md).

## January 19, 2014: Ryan Davis's return applied

Davis sustained a minor trunk injury in the [January 11 Divisional game](postseason/week_19_jacksonville_at_tennessee/output.md), with a projected return of January 14. The January 19 postseason handoff explicitly applied that elapsed projection under the branch's standard return rule and recorded him available. The source does not supply a separate examination, clearance conversation or practice appearance on January 14. No other Jacksonville availability changed in that handoff.

## February 2, 2014: Ball and C.J. Wilson returns reconciled

Alan Ball's long-term trunk injury in the [November 10 game at Tennessee](regular_season/week_10_jacksonville_at_tennessee/output.md) carried a January 22 return projection. C.J. Wilson's trunk injury in the [September 15 game at Oakland](regular_season/week_02_jacksonville_at_oakland/output.md) carried a January 30 projection. The February 2 season-close reconciliation recorded both cleared at those projected returns under the same branch rule. It did not record new examinations or football participation on either date.

At that close, Paul Posluszny remained unavailable on the independent medical hold originating in the [December 1 Cleveland game](regular_season/week_13_jacksonville_at_cleveland/output.md), with an April 5, 2014 projection. Will Rackley remained limited with a minor injury. These were the February 2 statuses, not a replacement for the current roster or later medical decisions.

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - October 27, 2013 - Pasztor and Mosley injury projections recovered", "original_close": "Commit closed - Canonical correction - October 27, 2013 - Pasztor and Mosley injury projections recovered - canonical through October 27, after Week 8", "sequence": 46, "through": "2013-10-27"}, "date": "2013-10-27", "id": "2013-10-27-pasztor-and-mosley-injury-projections-recovered", "kind": "technical", "status": "closed", "summary": "Missing preseason injury projections were recovered and prospective availability corrected."} -->
