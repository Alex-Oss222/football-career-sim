# 2013 NFL regular-season schedule

**Research date:** September 27, 2026. **Status: VERIFIED** for weeks, dates, kickoff times, clubs, home/away designation and site. No score, result or game statistic is recorded.

**Machine artifact:** [data/2013_schedule.json](data/2013_schedule.json), 256 games. **Builder:** `scripts/research/build_2013_schedule.py`. **Used by:** `runtime/week_inputs.py` for each week's slate, event identifiers and injury-return dates.

## Source

nflverse [games.csv](https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv), 2013 regular season. The builder reads only the schedule columns: week, date, weekday, kickoff (ET), away and home club, site and stadium. The file also carries real scores, results, betting lines, starting quarterbacks, coaches, officials and weather; none of those columns is read.

## Verification

- **Jacksonville:** all sixteen Jacksonville games match the separately sourced [Jacksonville master calendar](2013_jacksonville_master_calendar.md) (opponent, home/away, date and kickoff), including the Week 8 London game and the Week 14 Thursday game.
- **Week 1:** the sixteen Week 1 pairings match the Week 1 migration manifest, built earlier from its own source.
- **Structure:** every club plays once in each week in which it has no bye; byes fall in Weeks 4 through 12.

## Neutral sites

Three games were played away from the designated home club's stadium: Pittsburgh vs Minnesota (Week 4, Wembley Stadium), San Francisco vs Jacksonville (Week 8, Wembley Stadium) and Atlanta vs Buffalo (Week 13, Rogers Centre). The designated home club is kept for standings; the game packet records a neutral venue.
