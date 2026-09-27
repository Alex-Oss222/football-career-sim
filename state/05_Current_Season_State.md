# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP08-WEEK1-STATE-14`
**Supersedes:** `JAX-2013-SEP04-WEEK1-VOID-STATE-13`
**Snapshot effective:** September 8, 2013, after Week 1 (Jacksonville 31, Kansas City 13).
**Last reconciled:** September 27, 2026; season-ledger Entry 35.
**Global package checkpoint:** `Canonical update - September 8, 2013 - Week 1 vs Kansas City closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP08-WEEK1-REGISTER-12`; closed by Entry 35 | Active 53, practice squad, roles and availability after Week 1 |
| Document 6 | 2013 ledger through Entry 35 | Week 1 closed as generation 3 under kernel 2013.4 |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 8, 2013, after Week 1 vs Kansas City |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 1 closed, Week 2 preparation |
| Preseason record | **2-2** |
| Regular-season record | **1-0** |
| Last event | Week 1: Jacksonville 31, Kansas City 13 (Entry 35) |
| Next competitive event | **September 15, Week 2 at Oakland, 4:25 p.m. ET: NOT SIMULATED** |

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

Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Week 1 generated no Jacksonville injury. No other active player has a communicated football restriction; every status requires fresh Week 2 medical communication.

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

Through Week 1, Jacksonville is 1-0, second in the AFC South (all four clubs 1-0) and the No. 5 AFC seed if the season ended today (`career/2013/standings.md`). Sixteen of sixteen Week 1 receipts are preserved; the statbook is complete and every band-audit row is WITHIN.

## 7. Immediate next step

Play Week 2 at Oakland only on an explicit `Run Week 2` instruction. The path is built and gated: `python scripts/build_week_inputs.py 2` freezes all 16 TeamInputs (background clubs carried forward from the sourced Week 1 units with branch injuries and pre-existing returns applied; Jacksonville from the roster, `career/2013/depth_chart.json` and the week's call sheet) and runs the exclusivity and game-day gate; `python scripts/close_week.py 2 --close` closes the games and generates receipts, stats and standings. The one missing input is Stone's Week 2 plan, frozen as the Week 2 `call_sheet.json`. Game-day inactives default to the Week 1 list unless Stone sets new ones. **Oakland has not been simulated.**
