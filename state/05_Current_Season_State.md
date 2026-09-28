# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-DEC22-WEEK16-STATE-35`
**Supersedes:** `JAX-2013-DEC15-WEEK15-STATE-34`
**Snapshot effective:** December 22, 2013, after Week 16 (Jacksonville 38, Tennessee 27).
**Last reconciled:** September 28, 2026; season-ledger Entry 59.
**Global package checkpoint:** `Canonical update - December 22, 2013 - Week 16 vs Tennessee closed`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2013-DEC22-WEEK16-REGISTER-28`; closed by Entry 59 | Controlled 53, all active, practice squad, roles and availability after Week 16 |
| Document 6 | 2013 ledger through Entry 59 | Week 16 closed |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | December 22, 2013, after Week 16 vs Tennessee |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | Regular season; Week 16 closed; Week 17 preparation |
| Preseason record | **2-2** |
| Regular-season record | **10-5** |
| Last event | Week 16: Jacksonville 38, Tennessee 27 (Entry 59) |
| Next competitive event | **December 29, Week 17 at Indianapolis, 1 p.m. ET: NOT SIMULATED** |

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

Weeks 14-16 generated no Jacksonville injury. Paul Posluszny (Week 13, head/neck) is under an independent medical hold, long-term, projected return April 5, 2014; he is out for the regular season, and no reserve-list move has been made (a Caldwell transaction). Travis Kelce's Week 13 injury cleared at its projected return (December 3); he dressed in Week 14. Alan Ball is out (Week 10; projected return January 22, 2014); no reserve-list move has been made. Rackley is limited (minor, no projected absence). C.J. Wilson is out (projected return January 30, 2014). Pasztor and Mosley are available. Every other status requires fresh medical communication before Week 17.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-8).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor available (Entry 46).
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2/H (the movable receiver), Blackmon WR3/outside Z (dressed from Week 8), Clemons WR4, Brown WR5; Lewis leads tight end, and Kelce is TE2 in the regular call structure.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers (Posluszny out from Week 13; Russell Allen starts beside Smith from Week 14) with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes and Mike Harris outside (Harris for the injured Ball from Week 11), Poyer nickel, Bouye first outside reserve (Week 13), Rutland next, Lowery/Rambo safety. C.J. Wilson unavailable; Mosley available (Entry 46).
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

Through Week 16, Jacksonville is 10-5 and first in the AFC South, a game ahead of 9-6 Tennessee (season series 1-1); a Week 17 win clinches the division. Jacksonville is the AFC's second seed behind the 11-4 Jets (`career/2013/standings.md`). Two hundred forty of two hundred forty receipts are preserved; Week 14's are event generation 2 (Entry 57). Weeks 1-3 are the legacy kernel cohort, Weeks 4-8 are kernel 2013.6, Weeks 9-10 kernel 2013.7, Weeks 11-12 kernel 2013.8, Week 13 kernel 2013.9 and Week 14 onward kernel 2013.10, each audited as its own cohort. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernel 2013.6 also gives its small home term to the designated home team at a neutral site. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Weeks 9-10 ran under it and Week 11 onward under kernel 2013.8 (Entry 51); Weeks 1-8 are never rerun. The neutral-site home term is unchanged in 2013.7.

League awards (`career/2013/awards/`): Weeks 1-8 and September backfilled (Entry 47); Week 9 and October drawn at the Week 9 close (Entry 49); Weeks 10-16 and November at their close (Entries 50, 52, 53, 55 and 57-59). Every closed week's awards are required by `validate_repository.py`; December's are drawn after Week 17.

## 7. Immediate next step

Play Week 17 at Indianapolis (Sunday, December 29) only on an explicit `Run Week 17` instruction: `python scripts/build_week_inputs.py 17` freezes the slate and `python scripts/close_week.py 17 --close` closes it under kernel 2013.10. Stone's inputs needed:

- the Week 17 plan as a structured call sheet (new families are declared in `runtime/call_families.py` from the active 2013 book before the build);
- the Week 17 inactive list (the Week 16 list carries forward unless replaced).

Week 17 closes the regular season: December's Players of the Month (Weeks 13-17) are drawn at its close, and the postseason field is set from the final standings.

**Indianapolis has not been simulated.**
