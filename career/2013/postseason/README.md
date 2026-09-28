# 2013 postseason - bracket and round index

The branch's own playoff field, built from the final regular-season standings (`career/2013/standings.md`, `runtime.standings.compute`). No real 2013 postseason pairing, score, winner or champion is imported.

## Format (`library/2013_postseason_format_and_schedule.md`)

- **Field.** Six clubs per conference: the four division winners (seeds 1-4) and two wild cards (seeds 5-6). A division winner is always seeded above a wild card.
- **Wild Card.** Seeds 1 and 2 have byes. Seed 3 hosts seed 6, and seed 4 hosts seed 5.
- **Divisional.** Reseeded: the 1 seed hosts the lowest surviving seed, and the 2 seed hosts the other survivor.
- **Conference championships.** The higher remaining seed hosts.
- **Super Bowl XLVIII.** A neutral site (MetLife Stadium). The AFC champion is the designated home team; from kernel 2013.11 (Entry 66) the designated home team receives no home edge at a neutral site.
- **Rules.** Postseason games cannot end tied: overtime runs in 15-minute periods, with modified sudden death, until someone wins (kernel 2013.8 onward). Game-day actives stay at 46.
- **No postseason weekly awards.** The league gave AFC/NFC Players of the Week for the regular season only, so none are drawn for the postseason.

## Slot rule

Each branch game takes the real 2013-14 date, kickoff and network of the slot with the same seed matchup and conference (for example, AFC 5 at 4 takes the Saturday 4:35 p.m. NBC slot). The rule is fixed before any postseason draw and never looks at a result. A round is built only after every game of the round before it has closed.

## Pipeline

- **Weeks.** Postseason weeks are numbered after the regular season: 18 Wild Card, 19 Divisional, 20 Conference, 21 Super Bowl.
- **Schedule.** `runtime/postseason.py` builds each round from the standings and the closed postseason receipts.
- **Build and close.** `build_week_inputs.py N` and `close_week.py N --close` run a postseason week exactly like a regular-season week.
- **Receipts.** They go in `career/2013/stats/postseason_receipts/`, so standings, the regular-season statbook, awards and the calibration audit stay regular-season only.
- **Jacksonville's folder.** Each Jacksonville playoff game has its own folder here, `week_NN_<away>_at_<home>/`, holding `output.md` and Stone's frozen `call_sheet.json`. The league roundup for each round goes in `career/2013/league_results/week_NN.md`.

## Seeds

| Seed | AFC | NFC |
|---:|---|---|
| 1 | New York Jets | Minnesota Vikings |
| 2 | Tennessee Titans | St. Louis Rams |
| 3 | Pittsburgh Steelers | New Orleans Saints |
| 4 | Kansas City Chiefs | Philadelphia Eagles |
| 5 | Jacksonville Jaguars | Tampa Bay Buccaneers |
| 6 | Buffalo Bills | Dallas Cowboys |

## Rounds

| Week | Round | Date / kickoff (ET) | Game | Status | Output |
|---:|---|---|---|---|---|
| 18 | AFC Wild Card (5 at 4) | Sat. Jan. 4, 4:35 p.m., NBC | Jacksonville at Kansas City | **Jacksonville 38**, Kansas City 14 (Entry 62) | [week_18_jacksonville_at_kansas_city/output.md](week_18_jacksonville_at_kansas_city/output.md) |
| 18 | NFC Wild Card (6 at 3) | Sat. Jan. 4, 8:10 p.m., NBC | Dallas at New Orleans | **Dallas 40**, New Orleans 10 | [roundup](../league_results/week_18.md) |
| 18 | AFC Wild Card (6 at 3) | Sun. Jan. 5, 1:05 p.m., CBS | Buffalo at Pittsburgh | **Buffalo 33**, Pittsburgh 30 (OT) | [roundup](../league_results/week_18.md) |
| 18 | NFC Wild Card (5 at 4) | Sun. Jan. 5, 4:40 p.m., FOX | Tampa Bay at Philadelphia | **Philadelphia 30**, Tampa Bay 20 | [roundup](../league_results/week_18.md) |
| 19 | NFC Divisional (6 at 1) | Sat. Jan. 11, 4:35 p.m., FOX | Dallas at Minnesota | **Minnesota 38**, Dallas 10 | [roundup](../league_results/week_19.md) |
| 19 | AFC Divisional (5 at 2) | Sat. Jan. 11, 8:15 p.m., CBS | Jacksonville at Tennessee | **Tennessee 20**, Jacksonville 13 (Entry 64); Jacksonville eliminated | [week_19_jacksonville_at_tennessee/output.md](week_19_jacksonville_at_tennessee/output.md) |
| 19 | NFC Divisional (4 at 2) | Sun. Jan. 12, 1:05 p.m., FOX | Philadelphia at St. Louis | **Philadelphia 30**, St. Louis 20 | [roundup](../league_results/week_19.md) |
| 19 | AFC Divisional (6 at 1) | Sun. Jan. 12, 4:40 p.m., CBS | Buffalo at New York Jets | **Buffalo 26**, New York Jets 24 | [roundup](../league_results/week_19.md) |
| 20 | AFC Championship (6 at 2) | Sun. Jan. 19, 3:00 p.m., CBS | Buffalo at Tennessee | **Buffalo 34**, Tennessee 3 | [roundup](../league_results/week_20.md) |
| 20 | NFC Championship (4 at 1) | Sun. Jan. 19, 6:30 p.m., FOX | Philadelphia at Minnesota | **Minnesota 20**, Philadelphia 7 | [roundup](../league_results/week_20.md) |
| 21 | Super Bowl XLVIII | Sun. Feb. 2, 2014, 6:30 p.m., FOX, MetLife Stadium (neutral) | Minnesota (NFC 1) vs. Buffalo (AFC 6, designated home) | Not started | - |

The Pro Bowl (Sun. Jan. 26, Aloha Stadium) falls in the off week between the conference round and the Super Bowl. It is not simulated.
