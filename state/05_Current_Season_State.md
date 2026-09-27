# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-OCT13-WEEK6-STATE-20`
**Supersedes:** `JAX-2013-OCT06-WEEK5-STATE-19`
**Snapshot effective:** October 13, 2013, after Week 6 (Jacksonville 26, Denver 10).
**Last reconciled:** September 27, 2026; season-ledger Entry 43.
**Global package checkpoint:** `Canonical update - October 13, 2013 - Week 6 at Denver closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-OCT13-WEEK6-REGISTER-17`; closed by Entry 43 | Controlled 53, all active (Blackmon activated October 7), practice squad, roles and availability after Week 6 |
| Document 6 | 2013 ledger through Entry 43 | Blackmon reinstated and activated; Week 6 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | October 13, 2013, after Week 6 at Denver |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 6 closed, Week 7 preparation |
| Preseason record | **2-2** |
| Regular-season record | **4-2** |
| Last event | Week 6: Jacksonville 26, Denver 10 (Entry 43) |
| Next competitive event | **October 20, Week 7 vs San Diego, 1 p.m. ET: NOT SIMULATED** |

## 2. Roster and finance

| Field | Current value |
|---|---|
| **Current Jacksonville controlled roster** | **53** |
| Active roster | **53**; Blackmon reinstated and activated October 7 (Entry 42) |
| Practice squad | **8; separate from active 53** |
| Current cap treatment | Regular-season accounting; Top-51 expired |
| Working room | Approximately **$6.2M-$6.6M** before weekly practice-squad charges; **$5.4M-$5.8M** comparable full-season exposure if the opening eight remain all season |
| Personnel/contracts/cap authority | David Caldwell |
| Football roles | Alex Stone within eligibility and medical limits |

## 3. Availability

Week 6 generated no Jacksonville injury, and Adam Thielen returned from his Week 5 injury. Will Rackley has a minor injury, limited with no projected absence. C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Justin Blackmon is on the active 53 and is Stone's game-day inactive for Week 7; he is eligible from Week 8. Every other status requires fresh Week 7 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5 and 6).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor only when cleared.
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4; Blackmon active and inactive through Week 7; Lewis leads tight end, and Kelce is TE2 with a development emphasis.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley and C.J. Wilson unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 6, Jacksonville is 4-2, first in the AFC South (Tennessee also 4-2; conference record) and first in the AFC (`career/2013/standings.md`). Ninety-two of ninety-two receipts are preserved. Weeks 1-3 are the legacy kernel cohort, and Weeks 4-6 are kernel 2013.6. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position gap (Entries 39-43) produced impossible safeties in Weeks 5 and 6 that the coherence check cannot see. Kernel 2013.7, in development, addresses it.

## 7. Immediate next step

Play Week 7 vs San Diego only on an explicit `Run Week 7` instruction. `python scripts/build_week_inputs.py 7` freezes the slate, and `python scripts/close_week.py 7 --close` closes it under the kernel then deployed. Stone's inputs needed:

- the Week 7 plan as a structured call sheet;
- the inactive list (the Week 6 list, including Blackmon, carries forward otherwise).

**San Diego has not been simulated.**
