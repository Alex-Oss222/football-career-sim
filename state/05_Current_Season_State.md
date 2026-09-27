# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-OCT20-WEEK7-STATE-21`
**Supersedes:** `JAX-2013-OCT13-WEEK6-STATE-20`
**Snapshot effective:** October 20, 2013, after Week 7 (Jacksonville 30, San Diego 24).
**Last reconciled:** September 27, 2026; season-ledger Entry 44.
**Global package checkpoint:** `Canonical update - October 20, 2013 - Week 7 vs San Diego closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-OCT20-WEEK7-REGISTER-18`; closed by Entry 44 | Controlled 53, all active, practice squad, roles and availability after Week 7 |
| Document 6 | 2013 ledger through Entry 44 | Week 7 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | October 20, 2013, after Week 7 vs San Diego |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 7 closed, Week 8 preparation |
| Preseason record | **2-2** |
| Regular-season record | **5-2** |
| Last event | Week 7: Jacksonville 30, San Diego 24 (Entry 44) |
| Next competitive event | **October 27, Week 8 vs San Francisco at Wembley Stadium, London (Jacksonville designated home), 1 p.m. ET: NOT SIMULATED** |
| Next deadline | Trade deadline, October 29, 4 p.m. ET |

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

Week 7 generated no Jacksonville injury. Will Rackley has a minor injury, limited with no projected absence. C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor remains on an independent medical hold after the August 17 simulated head/neck injury. C.J. Mosley remains medically unavailable after the August 29 simulated upper-extremity injury. Justin Blackmon is on the active 53; Stone's game-day inactive period (Weeks 6-7) is complete and he is eligible from Week 8. Every other status requires fresh Week 8 medical communication.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-7).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor only when cleared.
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4; Blackmon active, eligible from Week 8 with his role Stone's decision; Lewis leads tight end, and Kelce is TE2 with a development emphasis.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. Mosley and C.J. Wilson unavailable.
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 7, Jacksonville is 5-2, first in the AFC South (Tennessee also 5-2; record in common games) and first in the AFC (`career/2013/standings.md`). One hundred seven of one hundred seven receipts are preserved. Weeks 1-3 are the legacy kernel cohort, and Weeks 4-7 are kernel 2013.6. Every graded band-audit row is WITHIN except field-goal accuracy under 30 yards (investigated, no defect found, Entry 44), and every ledger-coherence count is zero. The known field-position gap (Entries 39-44) produced impossible safeties in Weeks 5 and 6 and San Diego's two-play touchdown drive in Week 7, none of which the coherence check can see. Kernel 2013.7, in development, addresses it.

## 7. Immediate next step

Play Week 8 vs San Francisco only on an explicit `Run Week 8` instruction. `python scripts/build_week_inputs.py 8` freezes the slate, and `python scripts/close_week.py 8 --close` closes it under the kernel then deployed. Stone's inputs needed:

- the Week 8 plan as a structured call sheet;
- the Week 8 inactive list. The Week 7 list in `depth_chart.json` still names Blackmon, whose inactive period is over, and it carries forward unless Stone replaces it.

**San Francisco has not been simulated.**
