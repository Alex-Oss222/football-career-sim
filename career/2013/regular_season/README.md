# 2013 regular season - week index

One folder per week, named `week_NN_<away>_at_<home>`, with continuous numbering 1-17 and the Week 9 bye kept in sequence. Each holds one authoritative `output.md` that stays `NOT STARTED` until that week is played and, from the week's preparation, Stone's frozen `call_sheet.json`, which `python scripts/build_week_inputs.py N` requires before the draw.

## Weekly output owner

The complete Jacksonville head-coach weekly package is written **only** to that week's existing `output.md`, using:

`foundation/templates/regular_season_output_template.md`

For a played game week, that one file contains the full coach-facing turn: week/opponent setup, Stone's game preparation, pregame media Q&A, chronological generated game highlights, final score/box score, standouts, postgame media Q&A, coaching corrections and material roster/availability changes.

Do not create separate weekly prep, press-conference, recap or highlight files. The one exception is `call_sheet.json`, the machine-readable form of the call sheet in the week's `output.md`. Canonical dependent facts still update their existing owners (event records, roster/register, standings, medical/current state, cap/transactions when affected).

Dates, times and venues are historical schedule facts from `library/2013_jacksonville_master_calendar.md` section 5; scores, plays, injuries and results belong to the branch simulation and are never imported from the historical games.

| Week | Date | Kickoff (ET) | Matchup | Jacksonville | Status / result | Output file |
|---:|---|---|---|---|---|---|
| 1 | Sun. Sep. 8 | 1:00 p.m. ET | Kansas City Chiefs at Jacksonville | Home | Closed: W 31-13 ([2013 Kansas City game report](week_01_kansas_city_at_jacksonville/output.md)) | [week_01_kansas_city_at_jacksonville/output.md](week_01_kansas_city_at_jacksonville/output.md) |
| 2 | Sun. Sep. 15 | 4:25 p.m. ET | Jacksonville at Oakland Raiders | Away | Closed: L 13-17 ([2013 Oakland game report](week_02_jacksonville_at_oakland/output.md)) | [week_02_jacksonville_at_oakland/output.md](week_02_jacksonville_at_oakland/output.md) |
| 3 | Sun. Sep. 22 | 4:25 p.m. ET | Jacksonville at Seattle Seahawks | Away | Closed: W 16-13 ([2013 Seattle game report](week_03_jacksonville_at_seattle/output.md)) | [week_03_jacksonville_at_seattle/output.md](week_03_jacksonville_at_seattle/output.md) |
| 4 | Sun. Sep. 29 | 1:00 p.m. ET | Indianapolis Colts at Jacksonville | Home | Closed: W 31-10 ([2013 Indianapolis home game report](week_04_indianapolis_at_jacksonville/output.md)) | [week_04_indianapolis_at_jacksonville/output.md](week_04_indianapolis_at_jacksonville/output.md) |
| 5 | Sun. Oct. 6 | 1:00 p.m. ET | Jacksonville at St. Louis Rams | Away | Closed: L 24-26 ([2013 St. Louis game report](week_05_jacksonville_at_st_louis/output.md)) | [week_05_jacksonville_at_st_louis/output.md](week_05_jacksonville_at_st_louis/output.md) |
| 6 | Sun. Oct. 13 | 4:05 p.m. ET | Jacksonville at Denver Broncos | Away | Closed: W 26-10 ([2013 Denver game report](week_06_jacksonville_at_denver/output.md)) | [week_06_jacksonville_at_denver/output.md](week_06_jacksonville_at_denver/output.md) |
| 7 | Sun. Oct. 20 | 1:00 p.m. ET | San Diego Chargers at Jacksonville | Home | Closed: W 30-24 ([2013 San Diego game report](week_07_san_diego_at_jacksonville/output.md)) | [week_07_san_diego_at_jacksonville/output.md](week_07_san_diego_at_jacksonville/output.md) |
| 8 | Sun. Oct. 27 | 1:00 p.m. ET (5:00 p.m. UK local) | San Francisco 49ers at Jacksonville | Home | Closed: W 20-13 ([2013 San Francisco game report](week_08_san_francisco_at_jacksonville/output.md)) | [week_08_san_francisco_at_jacksonville/output.md](week_08_san_francisco_at_jacksonville/output.md) |
| 9 | Sun. Nov. 3 | - | **BYE** | - | Closed: bye ([2013 bye-week report](week_09_bye/output.md)) | [week_09_bye/output.md](week_09_bye/output.md) |
| 10 | Sun. Nov. 10 | 1:00 p.m. ET | Jacksonville at Tennessee Titans | Away | Closed: L 11-41 ([2013 Tennessee away game report](week_10_jacksonville_at_tennessee/output.md)) | [week_10_jacksonville_at_tennessee/output.md](week_10_jacksonville_at_tennessee/output.md) |
| 11 | Sun. Nov. 17 | 1:00 p.m. ET | Arizona Cardinals at Jacksonville | Home | Closed: W 29-7 ([2013 Arizona game report](week_11_arizona_at_jacksonville/output.md)) | [week_11_arizona_at_jacksonville/output.md](week_11_arizona_at_jacksonville/output.md) |
| 12 | Sun. Nov. 24 | 1:00 p.m. ET | Jacksonville at Houston Texans | Away | Closed: L 38-6 ([2013 Houston away game report](week_12_jacksonville_at_houston/output.md)) | [week_12_jacksonville_at_houston/output.md](week_12_jacksonville_at_houston/output.md) |
| 13 | Sun. Dec. 1 | 1:00 p.m. ET | Jacksonville at Cleveland Browns | Away | Closed: W 22-19 OT ([2013 Cleveland game report](week_13_jacksonville_at_cleveland/output.md)) | [week_13_jacksonville_at_cleveland/output.md](week_13_jacksonville_at_cleveland/output.md) |
| 14 | Thu. Dec. 5 | 8:25 p.m. ET | Houston Texans at Jacksonville | Home | Closed: W 21-20 ([2013 Houston home game report](week_14_houston_at_jacksonville/output.md)) | [week_14_houston_at_jacksonville/output.md](week_14_houston_at_jacksonville/output.md) |
| 15 | Sun. Dec. 15 | 1:00 p.m. ET | Buffalo Bills at Jacksonville | Home | Closed: L 45-16 ([2013 Buffalo game report](week_15_buffalo_at_jacksonville/output.md)) | [week_15_buffalo_at_jacksonville/output.md](week_15_buffalo_at_jacksonville/output.md) |
| 16 | Sun. Dec. 22 | 1:00 p.m. ET | Tennessee Titans at Jacksonville | Home | Closed: W 38-27 ([2013 Tennessee home game report](week_16_tennessee_at_jacksonville/output.md)) | [week_16_tennessee_at_jacksonville/output.md](week_16_tennessee_at_jacksonville/output.md) |
| 17 | Sun. Dec. 29 | 1:00 p.m. ET | Jacksonville at Indianapolis Colts | Away | Closed: L 23-22 ([2013 Indianapolis away game report](week_17_jacksonville_at_indianapolis/output.md)) | [week_17_jacksonville_at_indianapolis/output.md](week_17_jacksonville_at_indianapolis/output.md) |

The rest of the league's games each week are recorded in `../league_results/week_NN.md`.

Every closed game preserves a public stat receipt in `../stats/game_receipts/`. From those receipts:

- the week's box score is generated into its `output.md` with `python scripts/render_box_score.py --write <output.md>`;
- `../standings.md` is regenerated with `python scripts/render_standings.py 2013`;
- the season statbook in `../stats/` is regenerated with `python scripts/render_season_stats.py 2013 --team "Jacksonville Jaguars"`.

Never hand-carry a statistic or record from one weekly output to the next.
