# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-NOV24-KERNEL-2013-9-STATE-30`
**Supersedes:** `JAX-2013-NOV24-WEEK12-STATE-29`
**Snapshot effective:** November 24, 2013, after Week 12 (Houston 38, Jacksonville 6).
**Last reconciled:** September 28, 2026; season-ledger Entry 54.
**Global package checkpoint:** `Canonical update - November 24, 2013 - Kernel 2013.9 adopted (spike seating)`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-NOV24-WEEK12-REGISTER-24`; closed by Entry 53 | Controlled 53, all active, practice squad, roles and availability after Week 12 |
| Document 6 | 2013 ledger through Entry 54 | Week 12 closed; kernel 2013.9 adopted |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | November 24, 2013, after Week 12 at Houston |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 12 closed; Week 13 preparation |
| Preseason record | **2-2** |
| Regular-season record | **7-4** |
| Last event | Week 12: Houston 38, Jacksonville 6 (Entry 53) |
| Next competitive event | **December 1, Week 13 at Cleveland, 1 p.m. ET: NOT SIMULATED** |

## 2. Roster and finance

| Field | Current value |
|---|---|
| **Current Jacksonville controlled roster** | **53** |
| Active roster | **53** |
| Practice squad | **8; separate from active 53** |
| Current cap treatment | Regular-season accounting; Top-51 expired |
| Working room | Approximately **$6.2M-$6.6M** before weekly practice-squad charges; **$5.4M-$5.8M** comparable full-season exposure if the opening eight remain all season |
| Personnel/contracts/cap authority | David Caldwell |
| Football roles | Alex Stone within eligibility and medical limits |

## 3. Availability

Week 12 generated no injury. A.J. Bouye (Week 11, lower extremity) is projected to return November 26, before Week 13; his status needs fresh medical communication. Alan Ball is out (Week 10; projected return January 22, 2014); no reserve-list move has been made. Rackley is limited (minor, no projected absence). C.J. Wilson is out (projected return January 30, 2014). Pasztor and Mosley are available and dressed in Weeks 11-12. Every other status requires fresh medical communication before Week 13.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-8).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor available (Entry 46).
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2/H (the movable receiver), Blackmon WR3/outside Z (dressed from Week 8), Clemons WR4, Brown WR5; Lewis leads tight end, and Kelce is TE2 in the regular call structure.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes and Mike Harris outside (Harris for the injured Ball from Week 11), Poyer nickel, Rutland first outside reserve (Week 12, with Bouye out), Lowery/Rambo safety. C.J. Wilson unavailable; Mosley available (Entry 46).
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 12, Jacksonville is 7-4, first in the AFC South a game ahead of 6-5 Tennessee, and the AFC's third seed behind the 8-3 Jets and 7-4 Pittsburgh (`career/2013/standings.md`). One hundred seventy-six of one hundred seventy-six receipts are preserved. Weeks 1-3 are the legacy kernel cohort, Weeks 4-8 are kernel 2013.6, Weeks 9-10 kernel 2013.7, Weeks 11-12 kernel 2013.8 and Week 13 onward kernel 2013.9, each audited as its own cohort. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernel 2013.6 also gives its small home term to the designated home team at a neutral site. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Weeks 9-10 ran under it and Week 11 onward under kernel 2013.8 (Entry 51); Weeks 1-8 are never rerun. The neutral-site home term is unchanged in 2013.7.

League awards (`career/2013/awards/`): Weeks 1-8 and September backfilled (Entry 47); Week 9 and October drawn at the Week 9 close (Entry 49); Weeks 10-12 and November at their close (Entries 50, 52 and 53). Every closed week's awards are required by `validate_repository.py`; December's are drawn after Week 17.

## 7. Immediate next step

Play Week 13 at Cleveland only on an explicit `Run Week 13` instruction: `python scripts/build_week_inputs.py 13` freezes the slate and `python scripts/close_week.py 13 --close` closes it under kernel 2013.9 (spike seating; Entry 54). Stone's inputs needed:

- the Week 13 plan as a structured call sheet (new families are declared in `runtime/call_families.py` from the active 2013 book before the build);
- the Week 13 inactive list and Bouye's role once his status is communicated (the Week 12 list carries forward unless replaced).

Week 14 (Houston, Thursday, December 5) follows on a short week; the rematch notes are in `career/2013/regular_season/week_12_jacksonville_at_houston/houston_rematch_notes.md`.

**Cleveland has not been simulated.**
