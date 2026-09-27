# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-OCT27-KERNEL-2013-7-STATE-24`
**Supersedes:** `JAX-2013-OCT27-INJURY-RECOVERY-STATE-23`
**Snapshot effective:** October 27, 2013, after Week 8 (Jacksonville 20, San Francisco 13, Wembley Stadium) the recovery of Pasztor's and Mosley's injury projections, the backfilled league awards and the adoption of kernel 2013.7.
**Last reconciled:** September 27, 2026; season-ledger Entry 48.
**Global package checkpoint:** `Canonical update - October 27, 2013 - League awards backfilled; kernel 2013.7 adopted`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-OCT27-INJURY-RECOVERY-REGISTER-20`; closed by Entry 46 | Controlled 53, all active, practice squad, roles and availability after Week 8 and the projection recovery |
| Document 6 | 2013 ledger through Entry 48 | Week 8 closed; projections recovered; awards backfilled (Entry 47); kernel 2013.7 adopted (Entry 48) |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | October 27, 2013, after Week 8 vs San Francisco at Wembley Stadium, London |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 8 closed; Week 9 bye next |
| Preseason record | **2-2** |
| Regular-season record | **6-2** |
| Last event | Week 8: Jacksonville 20, San Francisco 13 (Entry 45); injury-projection recovery (Entry 46) |
| Next deadline | Trade deadline, Tuesday, October 29, 4 p.m. ET; no trade proposal is open |
| Next week | Week 9 bye (November 3) |
| Next competitive event | **November 10, Week 10 at Tennessee, 1 p.m. ET: NOT SIMULATED** |

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

Week 8 generated no Jacksonville injury. Will Rackley has a minor injury, limited with no projected absence. C.J. Wilson is out after a Week 2 trunk injury (projected return January 30, 2014); no reserve-list move has been made. Austin Pasztor (August 17 head/neck hold) and C.J. Mosley (August 29 upper-extremity injury) are available. Their preseason projections were never recorded, so each was redrawn once through the private service from the injury model every club uses (Entry 46): Pasztor minor, 2 days (projected return August 19); Mosley minor, 1 day (August 30). On the rule applied to every club they would have returned before Week 1; they were held through Week 8 by the recording defect, and those results stand. The Week 8 inactive list, which names both, carries forward unless Stone changes it. Every other status requires fresh medical communication before Week 10.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-8).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor available (Entry 46).
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2/H (the movable receiver), Blackmon WR3/outside Z (dressed from Week 8), Clemons WR4, Brown WR5; Lewis leads tight end, and Kelce is TE2 in the regular call structure.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes/Ball outside, Poyer nickel, Lowery/Rambo safety. C.J. Wilson unavailable; Mosley available (Entry 46).
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 8, Jacksonville is 6-2, first in the AFC South (5-2 Tennessee had a bye) and first in the AFC, ahead of the 6-2 Jets on conference record (`career/2013/standings.md`). One hundred twenty of one hundred twenty receipts are preserved. Weeks 1-3 are the legacy kernel cohort, and Weeks 4-8 are kernel 2013.6. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernel 2013.6 also gives its small home term to the designated home team at a neutral site. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Every slate closed after Week 8 runs under it; Weeks 1-8 are never rerun. The neutral-site home term is unchanged in 2013.7.

League awards (`career/2013/awards/`): Weeks 1-8 and September were backfilled by the registered method (Entry 47); October's awards are drawn on the league's October 31 date, during Week 9.

## 7. Immediate next step

October's Players of the Month are drawn on October 31 (`python scripts/league_awards.py month October --close`). The trade deadline (Tuesday, October 29, 4 p.m. ET) passes with no open proposal unless Stone and Caldwell open one. Week 9 is the bye; its output is written only on an explicit instruction and records practice, recovery and self-scout without inventing events. Play Week 10 at Tennessee only on an explicit `Run Week 10` instruction: `python scripts/build_week_inputs.py 10` freezes the slate and `python scripts/close_week.py 10 --close` closes it under the kernel then deployed. Stone's inputs needed:

- the Week 10 plan as a structured call sheet;
- the Week 10 inactive list (the Week 8 list carries forward unless replaced).

**Tennessee has not been simulated.**
