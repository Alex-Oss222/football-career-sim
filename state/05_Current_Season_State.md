# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP04-REGULAR-STATE-8`
**Supersedes:** `JAX-2013-AUG08-WALKTHROUGH-STATE-7`
**Snapshot effective:** September 4, 2013, after regular-season cap compliance.
**Last reconciled:** September 19, 2026; season-ledger Entry 29.
**Global package checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP04-REGULAR-STATE-8`; closed by Entry 29 | Active 53, practice squad, roles and availability |
| Document 6 | 2013 ledger through Entry 29 | September 4 preseason/cutdown/cap closure |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 4, 2013, after regular-season cap compliance |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular-season preparation |
| Preseason record | **2-2** |
| Regular-season record | **0-0** |
| Last event | September 4 regular-season roster/cap transition |
| Next competitive event | **September 8 vs Kansas City, 1:00 p.m. — NOT SIMULATED** |

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

Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Daryl Smith cleared his short restriction before this checkpoint. No other active player has a communicated football restriction; all statuses require fresh Week 1 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3.
- **OL:** Monroe–Nwaneri–Meester–Rackley–Johnson; Bradfield swing tackle; Brewster/Asper interior depth; Pasztor only when cleared.
- **Skill:** Jones-Drew leads Anderson/Grimes; Shorts and Blackmon lead with Thielen WR3; Lewis and Kelce lead tight end.
- **Defense:** Babin edge; Miller/Marks inside; Posluszny/Smith linebacker operation; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27.

## 6. Immediate next step

Begin September 8 Week 1 vs Kansas City preparation/game flow only on a new explicit instruction and after the game-readiness gate. **Kansas City has not been simulated.**
