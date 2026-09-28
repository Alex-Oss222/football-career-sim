# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-NOV03-WEEK9-BYE-STATE-25`
**Supersedes:** `JAX-2013-OCT27-KERNEL-2013-7-STATE-24`
**Snapshot effective:** November 3, 2013, after Week 9 (Jacksonville bye).
**Last reconciled:** September 28, 2026; season-ledger Entry 49.
**Global package checkpoint:** `Canonical update - November 3, 2013 - Week 9 bye closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-NOV03-WEEK9-BYE-REGISTER-21`; closed by Entry 49 | Controlled 53, all active, practice squad, roles and availability after the Week 9 bye |
| Document 6 | 2013 ledger through Entry 49 | Week 9 bye closed; league slate under kernel 2013.7 |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | November 3, 2013, after the Week 9 bye |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 9 bye closed; Week 10 preparation |
| Preseason record | **2-2** |
| Regular-season record | **6-2** |
| Last event | Week 9 bye; trade deadline passed with no Jacksonville transaction (Entry 49) |
| Last game | Week 8: Jacksonville 20, San Francisco 13 (Entry 45) |
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

Through Week 9, Jacksonville is 6-2 (bye), first in the AFC South a game and a half ahead of 5-3 Tennessee, and the AFC's second seed behind the 7-2 Jets (`career/2013/standings.md`). One hundred thirty-three of one hundred thirty-three receipts are preserved. Weeks 1-3 are the legacy kernel cohort, Weeks 4-8 are kernel 2013.6 and Week 9 onward is kernel 2013.7, each audited as its own cohort. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernel 2013.6 also gives its small home term to the designated home team at a neutral site. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Every slate closed after Week 8 runs under it; Weeks 1-8 are never rerun. The neutral-site home term is unchanged in 2013.7.

League awards (`career/2013/awards/`): Weeks 1-8 and September backfilled (Entry 47); Week 9 and October drawn at the Week 9 close (Entry 49). Every closed week's awards are required by `validate_repository.py`; November's are drawn after Week 12.

## 7. Immediate next step

Play Week 10 at Tennessee only on an explicit `Run Week 10` instruction: `python scripts/build_week_inputs.py 10` freezes the slate and `python scripts/close_week.py 10 --close` closes it under the kernel then deployed. Stone's inputs needed:

- the Week 10 plan as a structured call sheet;
- the Week 10 inactive list (the Week 8 list, naming the now-available Pasztor and Mosley, carries forward unless replaced);
- Kernel 2013.7 fails closed on any call family not in `runtime/call_families.py`; a new family on the Week 10 sheet is declared from the active 2013 book before the build.

Week 10's league awards are drawn at its close (`scripts/league_awards.py week 10 --close`).

**Tennessee has not been simulated.**
