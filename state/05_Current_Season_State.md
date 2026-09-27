# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP04-WEEK1-VOID-STATE-13`
**Supersedes:** `JAX-2013-SEP09-WEEK2-READY-STATE-12` and every September 9 Week 1 snapshot
**Snapshot effective:** September 4, 2013, after regular-season cap compliance; Week 1 voided and awaiting replay under kernel 2013.4.
**Last reconciled:** September 27, 2026; season-ledger Entry 34.
**Global package checkpoint:** `Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP04-WEEK1-VOID-REGISTER-11`; closed by Entry 34 | September 4 active 53, practice squad, roles and availability restored |
| Document 6 | 2013 ledger through Entry 34 | Week 1 void and kernel 2013.4 restart |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 4, 2013, after regular-season cap compliance |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular-season preparation; Week 1 void and not yet replayed |
| Preseason record | **2-2** |
| Regular-season record | **0-0** |
| Last event | Week 1 void (Entry 34); canon restored to the September 4 roster/cap transition |
| Next competitive event | **September 8 vs Kansas City, 1:00 p.m. — NOT SIMULATED** (replay under kernel 2013.4, event generation 3) |

## 2. Roster and finance

| Field | Current value |
|---|---|
| **Current Jacksonville controlled roster** | **53** |
| Practice squad | **8; separate from active 53** |
| Current cap treatment | Regular-season accounting; Top-51 expired |
| Working room | Approximately **$6.2M-$6.6M** before weekly practice-squad charges; **$5.4M-$5.8M** comparable full-season exposure if the opening eight remain all season |
| Personnel/contracts/cap authority | David Caldwell |
| Football roles | Alex Stone within eligibility and medical limits |

## 3. Availability

Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Daryl Smith cleared his short restriction before this checkpoint. No other active player has a communicated football restriction; all statuses require fresh Week 1 medical communication. The voided Week 1 injuries to Montell Owens and Bacarri Rambo never occurred in current canon.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3.
- **OL:** Monroe–Nwaneri–Meester–Rackley–Johnson; Bradfield swing tackle; Brewster/Asper interior depth; Pasztor only when cleared.
- **Skill:** Jones-Drew leads Anderson/Grimes; Shorts and Blackmon lead with Thielen WR3; Lewis and Kelce lead tight end.
- **Defense:** Babin edge; Miller/Marks inside; Posluszny/Smith linebacker operation; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. Kernel 2013.4 turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

No regular-season game is canon. `career/2013/standings.md` shows every club 0-0-0, and every `career/2013/stats/` view is empty until the replayed Week 1 receipts close.

## 7. Immediate next step

Replay Week 1 vs Kansas City only on an explicit `Run Week 1` instruction, under kernel 2013.4, following `career/2013/migrations/week_01_kernel_2013_4_restart.md`. Prerequisites: the private runtime redeployed at kernel 2013.4; `ENGINE_RUNTIME_URL` and `ENGINE_API_TOKEN` available; generations 1 and 2 marked in the private journal by `scripts/mark_week1_generations_void.py`; all 32 depth-ordered TeamInputs passing `scripts/check_week1_reset_ready.py`; and `scripts/check_game_readiness.py` passing. **Kansas City has not been simulated.**
