# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-NOV10-WEEK10-STATE-26`
**Supersedes:** `JAX-2013-NOV03-WEEK9-BYE-STATE-25`
**Snapshot effective:** November 10, 2013, after Week 10 (Tennessee 41, Jacksonville 11).
**Last reconciled:** September 28, 2026; season-ledger Entry 50.
**Global package checkpoint:** `Canonical update - November 10, 2013 - Week 10 at Tennessee closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-NOV10-WEEK10-REGISTER-22`; closed by Entry 50 | Controlled 53, all active, practice squad, roles and availability after Week 10 |
| Document 6 | 2013 ledger through Entry 50 | Week 10 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | November 10, 2013, after Week 10 at Tennessee |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 10 closed; Week 11 preparation |
| Preseason record | **2-2** |
| Regular-season record | **6-3** |
| Last event | Week 10: Tennessee 41, Jacksonville 11 (Entry 50) |
| Next competitive event | **November 17, Week 11 vs Arizona, 1 p.m. ET: NOT SIMULATED** |

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

Week 10 generated one Jacksonville injury: cornerback Alan Ball (trunk, long-term; out, projected return January 22, 2014, beyond the regular season). No reserve-list move has been made; that is Caldwell's, and the repository holds no sourced 2013 injured-reserve rules. Will Rackley is limited with a minor injury and no projected absence. C.J. Wilson is out (projected return January 30, 2014). Pasztor and Mosley are available (Entry 46); Pasztor dressed as the interior reserve in Week 10 and Mosley was inactive. Every other status requires fresh medical communication before Week 11.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-8).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor available (Entry 46).
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2/H (the movable receiver), Blackmon WR3/outside Z (dressed from Week 8), Clemons WR4, Brown WR5; Lewis leads tight end, and Kelce is TE2 in the regular call structure.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes and Ball outside until Ball's Week 10 injury (the replacement is Stone's decision), Poyer nickel, Lowery/Rambo safety. C.J. Wilson unavailable; Mosley available (Entry 46).
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 10, Jacksonville is 6-3, second in the AFC South behind 6-3 Tennessee on head-to-head, and the AFC's fifth seed (`career/2013/standings.md`). One hundred forty-seven of one hundred forty-seven receipts are preserved. Weeks 1-3 are the legacy kernel cohort, Weeks 4-8 are kernel 2013.6 and Weeks 9-10 are kernel 2013.7, each audited as its own cohort. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernel 2013.6 also gives its small home term to the designated home team at a neutral site. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Every slate closed after Week 8 runs under it; Weeks 1-8 are never rerun. The neutral-site home term is unchanged in 2013.7.

League awards (`career/2013/awards/`): Weeks 1-8 and September backfilled (Entry 47); Week 9 and October drawn at the Week 9 close (Entry 49); Week 10 at its close (Entry 50). Every closed week's awards are required by `validate_repository.py`; November's are drawn after Week 12.

## 7. Immediate next step

Play Week 11 vs Arizona only on an explicit `Run Week 11` instruction: `python scripts/build_week_inputs.py 11` freezes the slate and `python scripts/close_week.py 11 --close` closes it under kernel 2013.7. Stone's inputs needed:

- the Week 11 plan as a structured call sheet (new families are declared in `runtime/call_families.py` from the active 2013 book before the build);
- the Week 11 inactive list and the starting corner in Ball's place (the Week 10 list carries forward unless replaced).

Week 11's league awards are drawn at its close; November's after Week 12.

**Arizona has not been simulated.**
