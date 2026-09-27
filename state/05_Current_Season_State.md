# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-SEP22-WEEK3-STATE-16`
**Supersedes:** `JAX-2013-SEP15-WEEK2-STATE-15`
**Snapshot effective:** September 22, 2013, after Week 3 (Jacksonville 16, Seattle 13).
**Last reconciled:** September 27, 2026; season-ledger Entry 38.
**Global package checkpoint:** `Canonical update - September 22, 2013 - Week 3 at Seattle closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-SEP22-WEEK3-REGISTER-14`; closed by Entry 38 | Controlled 53 (52 active, Blackmon on Reserve/Suspended), practice squad, roles and availability after Week 3 |
| Document 6 | 2013 ledger through Entry 38 | Week 3 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | September 22, 2013, after Week 3 at Seattle |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 3 closed, Week 4 preparation |
| Preseason record | **2-2** |
| Regular-season record | **2-1** |
| Last event | Week 3: Jacksonville 16, Seattle 13 (Entry 38) |
| Next competitive event | **September 29, Week 4 vs Indianapolis, 1 p.m. ET: NOT SIMULATED** |

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

Paul Posluszny is out after a Week 3 upper-extremity injury (projected return October 2), which covers the Week 4 game. Brad Meester's Week 2 upper-extremity projection clears September 27. C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Justin Blackmon is on Reserve/Suspended for Weeks 2-5 and Stone's game-day inactive for Weeks 6-7. Every other status requires fresh Week 4 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3.
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson in Week 3, Brewster at center for Meester; Bradfield swing tackle; Asper interior reserve; Pasztor only when cleared. Meester's role is starting center when available; the Week 4 center is an open Stone decision.
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4 while Blackmon is unavailable; Lewis and Kelce lead tight end.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny/Smith linebacker operation, with Posluszny's Week 4 replacement an open decision; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley and C.J. Wilson unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 3, Jacksonville is 2-1, third in the AFC South (Tennessee, Indianapolis and Jacksonville 2-1; Houston 1-2) and ninth in the AFC (`career/2013/standings.md`). Forty-eight of forty-eight receipts are preserved; the statbook is complete and every band-audit row is WITHIN.

## 7. Immediate next step

Play Week 4 vs Indianapolis only on an explicit `Run Week 4` instruction. `python scripts/build_week_inputs.py 4` freezes the slate from canon: background units are carried forward with branch injuries and pre-existing returns, each dressing 46 from its depth order, and Jacksonville is built from the roster, `career/2013/depth_chart.json` and the week's call sheet. The build runs the gate, and `python scripts/close_week.py 4 --close` closes the slate under kernel 2013.5. Stone's inputs needed:

- the Week 4 plan as a structured call sheet;
- the center: Meester's projection clears September 27, but he is on the carried-over Week 3 inactive list and Brewster heads the center depth;
- Posluszny's replacement in the linebacker order;
- the inactive list.

**Indianapolis has not been simulated.**
