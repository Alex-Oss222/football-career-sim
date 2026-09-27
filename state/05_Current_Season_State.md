# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-OCT06-WEEK5-STATE-19`
**Supersedes:** `JAX-2013-SEP29-WEEK4-STATE-18`
**Snapshot effective:** October 6, 2013, after Week 5 (St. Louis 26, Jacksonville 24).
**Last reconciled:** September 27, 2026; season-ledger Entry 41.
**Global package checkpoint:** `Canonical update - October 6, 2013 - Week 5 at St. Louis closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-OCT06-WEEK5-REGISTER-16`; closed by Entry 41 | Controlled 53 (52 active, Blackmon on Reserve/Suspended), practice squad, roles and availability after Week 5 |
| Document 6 | 2013 ledger through Entry 41 | Week 5 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | October 6, 2013, after Week 5 at St. Louis |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 5 closed, Week 6 preparation |
| Preseason record | **2-2** |
| Regular-season record | **3-2** |
| Last event | Week 5: St. Louis 26, Jacksonville 24 (Entry 41) |
| Next dated event | **October 7: Blackmon reinstated from Reserve/Suspended** (Entry 36) |
| Next competitive event | **October 13, Week 6 at Denver, 4:05 p.m. ET: NOT SIMULATED** |

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

Adam Thielen is out after a Week 5 upper-extremity injury (projected return October 9, before Week 6). Will Rackley has a minor injury, limited with no projected absence. Paul Posluszny is available and returned in Week 5. C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Justin Blackmon's league suspension ended with Week 5. His reinstatement from Reserve/Suspended is due October 7, and Stone's game-day inactive applies for Weeks 6 and 7. Every other status requires fresh Week 6 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (inactive in Week 5 as a numbers decision).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson in Weeks 3 to 5. Meester is reserve center, and Stone evaluates the center weekly. Bradfield is swing tackle and the sixth offensive lineman in 6OL; Asper interior depth; Pasztor only when cleared.
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4 while Blackmon is unavailable; Lewis and Kelce lead tight end.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley and C.J. Wilson unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 5, Jacksonville is 3-2, first in the AFC South on a three-way tie with Tennessee and Indianapolis (conference record), and second in the AFC (`career/2013/standings.md`). Seventy-seven of seventy-seven receipts are preserved. Weeks 1-3 are the legacy kernel cohort, and Weeks 4-5 are kernel 2013.6. Every ledger-coherence count is zero. One graded band row, field-goal accuracy under 30 yards, reads OUTSIDE; it was investigated as chance, not a defect (Entry 41). The known field-position gap (Entries 39-41) produced an impossible safety in Week 5 that the coherence check cannot see.

## 7. Immediate next step

Play Week 6 at Denver only on an explicit `Run Week 6` instruction. `python scripts/build_week_inputs.py 6` freezes the slate from canon, and `python scripts/close_week.py 6 --close` closes it under kernel 2013.6. Before the build, Blackmon's October 7 reinstatement moves him from Reserve/Suspended to the active roster, filling the 53rd spot. `career/2013/roster.md` and Document 4 change accordingly, and he joins the Week 6 inactive list under Stone's ruling. Stone's inputs needed:

- the Week 6 plan as a structured call sheet;
- the center;
- seven game-day inactives including Blackmon (the Week 5 list carries forward otherwise);
- Thielen's role, since his projection clears October 9.

**Denver has not been simulated.**
