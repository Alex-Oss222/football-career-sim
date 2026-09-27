# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP15-WEEK2-STATE-15`
**Supersedes:** `JAX-2013-SEP08-WEEK1-STATE-14`
**Snapshot effective:** September 15, 2013, after Week 2 (Oakland 17, Jacksonville 13).
**Last reconciled:** September 27, 2026; season-ledger Entry 37.
**Global package checkpoint:** `Canonical update - September 15, 2013 - Week 2 at Oakland closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP15-WEEK2-REGISTER-13`; closed by Entry 37 | Controlled 53 (52 active, Blackmon on Reserve/Suspended), practice squad, roles and availability after Week 2 |
| Document 6 | 2013 ledger through Entry 37 | Blackmon ruling; Week 2 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 15, 2013, after Week 2 at Oakland |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 2 closed, Week 3 preparation |
| Preseason record | **2-2** |
| Regular-season record | **1-1** |
| Last event | Week 2: Oakland 17, Jacksonville 13 (Entry 37) |
| Next competitive event | **September 22, Week 3 at Seattle, 4:25 p.m. ET: NOT SIMULATED** |

## 2. Roster and finance

| Field | Current value |
|---|---|
| **Current Jacksonville controlled roster** | **53** |
| Active roster | **52**; Blackmon on Reserve/Suspended (Weeks 2-5); one open spot |
| Practice squad | **8; separate from active 53** |
| Current cap treatment | Regular-season accounting; Top-51 expired |
| Working room | Approximately **$6.2M-$6.6M** before weekly practice-squad charges; **$5.4M-$5.8M** comparable full-season exposure if the opening eight remain all season |
| Personnel/contracts/cap authority | David Caldwell |
| Football roles | Alex Stone within eligibility and medical limits |

## 3. Availability

Brad Meester is out after a Week 2 upper-extremity injury (projected return September 27). C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Justin Blackmon is on Reserve/Suspended for Weeks 2-5 and Stone's game-day inactive for Weeks 6-7. Every other status requires fresh Week 3 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3.
- **OL:** Monroe–Nwaneri–Meester–Rackley–Johnson; Bradfield swing tackle; Brewster/Asper interior depth; Pasztor only when cleared. Meester is out for Week 3; the replacement center is an open Stone decision.
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4 while Blackmon is unavailable; Lewis and Kelce lead tight end.
- **Defense:** Babin edge; Miller/Marks inside; Posluszny/Smith linebacker operation; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley and C.J. Wilson unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. Kernel 2013.4 turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 2, Jacksonville is 1-1, fourth in the AFC South (Tennessee 2-0; Indianapolis, Houston and Jacksonville 1-1) and eleventh in the AFC (`career/2013/standings.md`). Thirty-two of thirty-two receipts are preserved; the statbook is complete and every band-audit row is WITHIN.

## 7. Immediate next step

Play Week 3 at Seattle only on an explicit `Run Week 3` instruction. `python scripts/build_week_inputs.py 3` freezes the slate from canon (background units carried forward with branch injuries and pre-existing returns; Jacksonville from the roster, `career/2013/depth_chart.json` and the week's call sheet) and runs the gate; `python scripts/close_week.py 3 --close` closes it. Stone's inputs needed: the Week 3 plan as a structured call sheet; the starting center with Meester out; the edge rotation without C.J. Wilson; and inactives (the Week 2 list carries over otherwise). Meester's availability in `career/2013/roster.md` must be updated when medical clears him. **Seattle has not been simulated.**
