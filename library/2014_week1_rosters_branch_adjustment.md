# 2014 Week 1 rosters: source and branch adjustment

**Function:** raw real 2014 Week 1 rosters for all 32 real clubs (source, user-supplied), plus a branch-adjusted copy with Jacksonville's controlled players removed from their real club and the offseason's traded-away players re-homed onto their actual destination. This is preparation for the other 31 clubs' real 2014 Week 1 rosters, whose gate is September (ledger Entry 114); it does not touch `state/`, the ledger, or `career/2014/league/personnel/` (the separate February 2, 2014 research database).

| File | Contents |
|---|---|
| [data/2014_week1_rosters_source.json](data/2014_week1_rosters_source.json) | Unmodified real 2014 Week 1 rosters, all 32 clubs, as supplied (schema: club → players, each with position, depth, slots, jersey, gsis_id, birth_date, headshot_url, page_url). |
| [data/2014_week1_rosters_branch_adjusted.json](data/2014_week1_rosters_branch_adjusted.json) | The same data with Jacksonville's real entry dropped (Jacksonville has no generated club file) and every Jacksonville-controlled player removed from whatever real club the source still listed them under. |

## Method

Jacksonville's current 84-name roster (`career/2014/team/roster/roster.md`) was matched against all 32 clubs by name **and birth date** — a name match alone produced two false positives (Baltimore's rookie LB "C.J. Mosley," born 1992, is not Jacksonville's DT "C.J. Mosley," born 1983; Minnesota's "Mike Harris," born 1988-12-05, is not Jacksonville's, born 1989-01-05). Both were correctly left on their real club.

**37 players removed** from their real 2014 club listing (full list: Dwight Lowery/ATL; Brynden Trawick, Daryl Smith, Eugene Monroe/BAL; Andrew Norwell, Trai Turner/CAR; Christian Jones, Jeremy Cain/CHI; Andrew Hawkins, Joel Bitonio, Jordan Poyer, Taylor Gabriel/CLE; Jeremy Mincey, Lavar Edwards/DAL; Aqib Talib, C.J. Anderson/DEN; C.J. Mosley, Cornelius Lucas, Montell Owens/DET; Corey Linsley, Davante Adams/GB; A.J. Bouye, Jonathan Grimes/HOU; Hakeem Nicks/IND; Travis Kelce/KC; Gator Hoskins/MIA; Adam Thielen/MIN; Malcolm Butler/NE; Kasim Edebali/NO; C.J. Wilson, Maurice Jones-Drew, Sio Moore/OAK; Antwon Blake/PIT; Aaron Donald/STL; Alterraun Verner/TB; Bacarri Rambo, Kirk Cousins/WAS).

**5 players Jacksonville traded away this offseason** (`career/2014/ledger.md` Entries 102, 104, 110) were re-homed onto their real branch destination rather than left on their real (or stale) club:

| Player | Real source showed | Branch destination | Data used |
|---|---|---|---|
| Jason Babin | NYJ | MIA | Full real record reused, club relabeled |
| Tyson Alualu | JAX (real) | HOU | Full real record reused, club relabeled |
| Cecil Shorts | JAX (real) | IND | Full real record reused, club relabeled |
| Justin Blackmon | *(none — real-world suspended, no 2014 roster row exists)* | IND | Position and birth date only, from `library/data/player_birth_dates.json` (corroborated). Jersey, depth and slot are genuinely unknown for Indianapolis and left `"Unknown"`, not invented. |
| Will Rackley | *(none — not on any real 2014 roster)* | SEA | Same: position/birth date only, jersey/depth/slot marked `"Unknown"`. |

Russell Allen (traded to Arizona, retired April 22) needed no correction — he doesn't appear on any real 2014 club's roster either, consistent with both realities.

**Not yet done:** the reverse direction (players the source correctly shows as traded elsewhere who might need Jacksonville added, e.g. any real 2014 move this branch diverges from beyond the six trades above) has not been swept — only Jacksonville's own controlled-player list was checked against the source. Flag if a specific other-club discrepancy turns up.
