# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2014-FEB02-KERNEL-2014-2-STATE-46`
**Supersedes:** `JAX-2014-FEB02-KERNEL-2014-1-STATE-45`
**Snapshot effective:** February 2, 2014, after Super Bowl XLVIII (Buffalo 31, Minnesota 20); the 2013 season is complete and archived.
**Last reconciled:** September 28, 2026; season-ledger Entry 70.
**Global package checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.2 adopted (late-game recalibration)`

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `358ccf4feac40830055bae5e4cbd84151536ab9e` | Active foundation source |
| Document 2 | `ab790f6e935c99a901a6d39cf3bee5183cf4da3e` | Active foundation source |
| Document 3 | `38e0ce21e9cf1b62f8d4b9c281955facdaf07b57` | Active foundation source |
| Document 4 | `JAX-2014-FEB02-SEASON-CLOSE-REGISTER-34`; closed by Entry 67 | Controlled 53, all active, practice squad, roles and availability at the season's close |
| Document 6 | 2013 ledger through Entry 70 | 2013 season complete; phase archives in Entry 67; 2014 setup in Entry 68; kernels 2014.1 and 2014.2 in Entries 69-70 |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | February 2, 2014, after Super Bowl XLVIII |
| League/season | NFL, 2013 |
| Team / head coach | Jacksonville Jaguars / Alex Stone |
| Callers | Stone offense; Romeo Crennel defense; Alan Lowry special teams |
| Season phase | 2013 season complete; 2014 offseason |
| Preseason record | **2-2** |
| Regular-season record | **10-6 (final)** |
| Postseason record | **1-1 (eliminated)** |
| Last event | AFC Divisional: Tennessee 20, Jacksonville 13 (Entry 64) |
| Next competitive event | **2014 preseason (dates set by the 2014 schedule release, gated April 23, 2014)** |

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

Player birth dates and ages are in Document 4, the [roster](../career/2013/roster.md) and [league age view](../career/2013/player_ages.md). Ages are derived at the master date and checked on every repository validation; run `python scripts/render_player_ages.py` after a date or roster change. Entry 63 added identity metadata without advancing time or retiring anyone.

## 3. Availability

The Divisional game produced one Jacksonville injury: Ryan Davis (trunk, minor), cleared at his projected return (January 14, 2014). Montell Owens and Adam Thielen cleared their Wild Card injuries at their projections (January 5 and 6) and played in the Divisional game. Weeks 14-17 generated no Jacksonville injury. Paul Posluszny (Week 13, head/neck) is under an independent medical hold, long-term, projected return April 5, 2014; he is out for the regular season, and no reserve-list move has been made (a Caldwell transaction). Travis Kelce's Week 13 injury cleared at its projected return (December 3); he dressed in Week 14. Alan Ball cleared at his projected return (January 22, 2014). Rackley is limited (minor, no projected absence). C.J. Wilson cleared at his projected return (January 30, 2014). Pasztor and Mosley are available. Jacksonville has no further game this season.

## 4. Current football roles

- **QB:** Cousins QB1, Henne QB2, Wilson QB3 (a game-day numbers inactive in Weeks 5-8).
- **OL:** Monroe–Nwaneri–Brewster–Rackley–Johnson, with Brewster the starting center (confirmed Week 6). Meester reserve center; Bradfield swing tackle and sixth offensive lineman in 6OL; Asper interior depth; Pasztor available (Entry 46).
- **Skill:** Jones-Drew leads, Grimes RB2, Anderson RB3; Shorts WR1, Thielen WR2/H (the movable receiver), Blackmon WR3/outside Z (dressed from Week 8), Clemons WR4, Brown WR5; Lewis leads tight end, and Kelce is TE2 in the regular call structure.
- **Defense:** Edge order Babin, Mincey, Branch, Davis; Miller/Marks inside; Posluszny and Smith base linebackers (Posluszny out from Week 13; Russell Allen starts beside Smith from Week 14) with Smith the communication lead, Allen first off the bench, then Stanford, with Moore in Crennel's packages; Grimes and Mike Harris outside (Harris for the injured Ball from Week 11), Poyer nickel, Bouye first outside reserve (Week 13), Rutland next, Lowery/Rambo safety. C.J. Wilson and Ball cleared at their projections (Entry 67); Mosley available (Entry 46).
- **Teams:** Scobee/Anger/Cain specialists. Trawick, Rambo, Thielen, Anderson, Poyer, Prosinski, Allen and Bouye hold defined primary/backup coverage jobs.

Execution and observable effort remain separate. Protection losses were technique/physical evidence where assignments were identified; medical limitations are not effort findings. The kernel (2013.4 onward) turns this depth order into game usage, so each weekly TeamInput must carry it as explicit `depth` values.

## 5. Closed preseason block

All four preseason games were generated through `runtime.game_runner.run_game` from privately frozen event commitments. No historical score was imported and no result was rerun. Jacksonville beat Miami 33-17, lost at the Jets 24-17, lost to Philadelphia 31-20 and won at Atlanta 33-27. The preseason block is unaffected by the Week 1 void.

## 6. League position and statistics

**Postseason.** Jacksonville (AFC 5) beat Kansas City 38-14 in the Wild Card round (Entry 62) and lost 20-13 at Tennessee in the Divisional round (Entry 64). Wild Card: Dallas 40, New Orleans 10; Buffalo 33, Pittsburgh 30 in overtime; Philadelphia 30, Tampa Bay 20. Divisional: Minnesota 38, Dallas 10; Philadelphia 30, St. Louis 20; Buffalo 26, Jets 24 (E.J. Manuel injured, long-term). Conference championships (Entry 65): Buffalo 34, Tennessee 3; Minnesota 20, Philadelphia 7. Super Bowl XLVIII (Entry 67): Buffalo 31, Minnesota 20; Buffalo, the AFC's sixth seed, is the branch's 2013 champion. The eleven postseason receipts are in `career/2013/stats/postseason_receipts/`; the bracket is `career/2013/postseason/README.md`. No postseason awards are drawn.

The regular season is complete. Jacksonville finished 10-6, second in the AFC South: Tennessee also finished 10-6 and won the division on division record (4-2 against 3-3) after a 1-1 season split. Jacksonville was the AFC's fifth seed, a wild card, and won at fourth-seeded Kansas City (9-7) in the Wild Card round. AFC seeds: Jets, Tennessee, Pittsburgh, Kansas City, Jacksonville, Buffalo. NFC seeds: Minnesota, St. Louis, New Orleans, Philadelphia, Tampa Bay, Dallas (`career/2013/standings.md`). Two hundred fifty-six of two hundred fifty-six receipts are preserved; Week 14's are event generation 2 (Entry 57). Weeks 1-3 are the legacy kernel cohort, Weeks 4-8 are kernel 2013.6, Weeks 9-10 kernel 2013.7, Weeks 11-12 kernel 2013.8, Week 13 kernel 2013.9 and Week 14 onward kernel 2013.10, each audited as its own cohort. Every graded band-audit row is WITHIN and every ledger-coherence count is zero. The known field-position and downs gaps (Entries 39-45) produced impossible safeties in Weeks 5 and 6, San Diego's two-play touchdown drive in Week 7 and Jacksonville's short-field touchdown and a turnover on downs after an 18-yard gain in Week 8, none of which the coherence check can see. Kernels 2013.6-2013.10 gave the designated home team their small home term at a neutral site (Wembley, Weeks 4 and 8); kernel 2013.11 (Entry 66) removes it. Kernel 2013.7 (field position, real per-drive chains and sacks, carrier-true labels, late-game fourth-down partition) was adopted as documented by the user (Entry 48): its three OUTSIDE acceptance rows are registered known detections. Weeks 9-10 ran under it and Week 11 onward under kernel 2013.8 (Entry 51); Weeks 1-8 are never rerun.

League awards (`career/2013/awards/`): Weeks 1-8 and September backfilled (Entry 47); Week 9 and October drawn at the Week 9 close (Entry 49); Weeks 10-17, November and December at their close (Entries 50, 52, 53, 55 and 57-60). Every closed week's awards are required by `validate_repository.py`; December's are drawn after Week 17.

## 7. Immediate next step

The 2013 season is complete and archived (Entry 67): Jacksonville 10-6, 1-1 in the postseason; Buffalo won Super Bowl XLVIII. The next Jacksonville football event belongs to the 2014 offseason.

- **Held for the user:** end-of-season exit interviews (not run until the user asks).
- **2014 setup (Entry 68):** `career/2014/` holds the 2014 calendar with its gates, the generated draft order (Jacksonville 26th in each round; its second-round selection is Washington's), the derived opponents and the contract-status register (8 unrestricted, 3 restricted and 3 exclusive-rights free agents, 4 unresolved). The next league events are the tag window (February 17), the Combine (February 19-25) and the league year (March 11).
- **Engine:** kernel 2014.1 (Entry 69) tracks timeouts, conditions late draws on them, keeps kneel drives in their start zone and publishes goal-to-go distances. The two-minute warning and play clock remain embedded in real drive durations. Kernel 2014.2 (Entry 70) recalibrates the late-game draw: category weights conditioned on the start zone, and late cells borrowing feasible drives from the same need instead of masking a category; the late mix by score situation now tracks 2012.
- **Recorded gaps:** Pro Bowl, All-Pro and the AP season awards were not drawn (Entry 67).
