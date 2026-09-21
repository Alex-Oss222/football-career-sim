# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP09-WEEK2-READY-STATE-12`
**Supersedes:** `JAX-2013-SEP09-WEEK1-HANDOFF-STATE-11`
**Snapshot effective:** September 9, 2013, after the published generation-2 Week 1 slate, completed attribution audit and Week 2 generation-readiness reconciliation.
**Last reconciled:** September 20, 2026; season-ledger Entry 33.
**Global package checkpoint:** `Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP09-WEEK1-RESET-STATE-10`; closed by Entry 31 | Active 53, practice squad, roles and availability; no owned fact changed in Entries 32-33 |
| Document 6 | 2013 ledger through Entry 33 | Week 1 attribution audit completion / Week 2 readiness correction |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 9, 2013, after Week 1 postgame and league closure |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 1 complete |
| Preseason record | **2-2** |
| **Current Jacksonville controlled roster** | **53** |
| Regular-season record | **1-0** |
| Last event | Jacksonville defeated Kansas City 34-13; Week 1 generation-2 slate published; completed attribution/readiness correction closed without rerun |
| Next competitive event | **September 15 at Oakland, 4:25 p.m. — NOT SIMULATED** |

## 2. Roster and finance

Jacksonville controls 53 active-roster players and eight practice-squad players. No transaction, contract, reserve-list or cap event occurred in Week 1. Regular-season accounting remains approximately **$6.2M-$6.6M** before weekly practice-squad charges, subject to the existing worksheet limitations.

## 3. Availability

Montell Owens is out pending reassessment after a generated minor trunk injury. Bacarri Rambo is medically unavailable after a generated short-term trunk injury; the first reassessment is due four days after the game and the generated return horizon extends beyond Week 2. Austin Pasztor remains on independent medical hold and C.J. Mosley remains medically unavailable. Week 1 inactive designations expired after the game; Week 2 requires fresh medical and game-day communication.

## 4. Current football roles and Week 1 evidence

- **QB:** Cousins remains QB1, Henne QB2 and Wilson QB3. Isolated backup series occurred without a generated quarterback injury; Stone ended ordinary multi-quarterback usage.
- **OL:** Monroe-Nwaneri-Meester-Rackley-Johnson remains the starting five; Jacksonville allowed one sack, charged to a generated leverage loss by Monroe.
- **Skill:** Jones-Drew continues to lead Anderson/Grimes. Grimes produced 61 scrimmage yards and two touchdowns; Kelce led receivers with 47 yards and a touchdown. Owens is unavailable pending reassessment.
- **Defense:** Jacksonville recorded five interceptions and two sacks. Kansas City still gained 489 yards and converted 13 third downs, preserving a clear correction need. Rambo is medically unavailable.
- **Teams:** Scobee made both field goals and all four extra points; Anger punted five times.

Jacksonville gained 431 yards, committed one turnover and won 34-13. No one-game result automatically changes an underlying qualitative tier.

## 5. League position

The full Week 1 slate is closed in `career/2013/league_results/week_01.md`. Jacksonville is 1-0 in the AFC South; Indianapolis, Houston and Tennessee are 0-1. `career/2013/standings.md` owns the complete tables. All 16 team-result receipts preserve complete scores and team totals. The completed branch-control audit corrected ten impossible historical-team player identities across seven receipts; Jacksonville's player attribution remains complete, while exact player attribution for nine affected non-Jacksonville clubs is partial. Formal league player rankings are withheld rather than reassigned by guesswork.

## 6. Immediate next step

The repository/statbook layer has passed the Week 2 generation-readiness audit in `career/2013/migrations/week_02_generation_readiness.md`. Week 2 at Oakland is ready for a new explicit `Run Week 2` instruction and Stone's weekly plan. Before any Week 2 game event closes, build the full weekly TeamInput package, obtain fresh qualified-medical communication, and pass both ordinary game readiness and the branch-exclusivity gate. Cousins carries forward as QB1 with no ordinary multi-quarterback rotation. **Oakland has not been simulated.**
