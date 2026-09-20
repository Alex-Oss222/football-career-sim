# 2013 regular season - week index

One folder per week, named `week_NN_<away>_at_<home>`, with continuous numbering 1-17 and the Week 9 bye kept in sequence. Each holds one authoritative `output.md` that stays `NOT STARTED` until that week is played.

## Weekly output owner

The complete Jacksonville head-coach weekly package is written **only** to that week's existing `output.md`, using:

`foundation/templates/season_output_template.md`

For a played game week, that one file contains the full coach-facing turn: week/opponent setup, Stone's game preparation, pregame media Q&A, chronological generated game highlights, final score/box score, standouts, postgame media Q&A, coaching corrections and material roster/availability changes.

Do not create separate weekly prep, press-conference, recap or highlight files. Canonical dependent facts still update their existing owners (ledger, roster/register, standings, medical/current state, cap/transactions when affected).

Dates, times and venues are historical schedule facts from `library/2013_jacksonville_master_calendar.md` section 5; scores, plays, injuries and results belong to the branch simulation and are never imported from the historical games.

| Week | Date | Kickoff (ET) | Matchup | Jacksonville | Output file |
|---:|---|---|---|---|---|
| 1 | Sun. Sep. 8 | 1:00 p.m. ET | Kansas City Chiefs at Jacksonville | Home | `week_01_kansas_city_at_jacksonville/output.md` |
| 2 | Sun. Sep. 15 | 4:25 p.m. ET | Jacksonville at Oakland Raiders | Away | `week_02_jacksonville_at_oakland/output.md` |
| 3 | Sun. Sep. 22 | 4:25 p.m. ET | Jacksonville at Seattle Seahawks | Away | `week_03_jacksonville_at_seattle/output.md` |
| 4 | Sun. Sep. 29 | 1:00 p.m. ET | Indianapolis Colts at Jacksonville | Home | `week_04_indianapolis_at_jacksonville/output.md` |
| 5 | Sun. Oct. 6 | 1:00 p.m. ET | Jacksonville at St. Louis Rams | Away | `week_05_jacksonville_at_st_louis/output.md` |
| 6 | Sun. Oct. 13 | 4:05 p.m. ET | Jacksonville at Denver Broncos | Away | `week_06_jacksonville_at_denver/output.md` |
| 7 | Sun. Oct. 20 | 1:00 p.m. ET | San Diego Chargers at Jacksonville | Home | `week_07_san_diego_at_jacksonville/output.md` |
| 8 | Sun. Oct. 27 | 1:00 p.m. ET (5:00 p.m. UK local) | San Francisco 49ers at Jacksonville | Home | `week_08_san_francisco_at_jacksonville/output.md` |
| 9 | Sun. Nov. 3 | - | **BYE** | - | `week_09_bye/output.md` |
| 10 | Sun. Nov. 10 | 1:00 p.m. ET | Jacksonville at Tennessee Titans | Away | `week_10_jacksonville_at_tennessee/output.md` |
| 11 | Sun. Nov. 17 | 1:00 p.m. ET | Arizona Cardinals at Jacksonville | Home | `week_11_arizona_at_jacksonville/output.md` |
| 12 | Sun. Nov. 24 | 1:00 p.m. ET | Jacksonville at Houston Texans | Away | `week_12_jacksonville_at_houston/output.md` |
| 13 | Sun. Dec. 1 | 1:00 p.m. ET | Jacksonville at Cleveland Browns | Away | `week_13_jacksonville_at_cleveland/output.md` |
| 14 | Thu. Dec. 5 | 8:25 p.m. ET | Houston Texans at Jacksonville | Home | `week_14_houston_at_jacksonville/output.md` |
| 15 | Sun. Dec. 15 | 1:00 p.m. ET | Buffalo Bills at Jacksonville | Home | `week_15_buffalo_at_jacksonville/output.md` |
| 16 | Sun. Dec. 22 | 1:00 p.m. ET | Tennessee Titans at Jacksonville | Home | `week_16_tennessee_at_jacksonville/output.md` |
| 17 | Sun. Dec. 29 | 1:00 p.m. ET | Jacksonville at Indianapolis Colts | Away | `week_17_jacksonville_at_indianapolis/output.md` |

The rest of the league's games each week are recorded in `../league_results/week_NN.md`. The current league, conference and division standings live in `../standings.md`; update that file whenever final scores change records.

Every closed game also feeds the season statbook in `../stats/`. Preserve the public stat receipt at game closure, then refresh the current Jacksonville player stats, league player stats and league-leader view from receipts. Do not hand-carry cumulative totals from one weekly output to the next.
