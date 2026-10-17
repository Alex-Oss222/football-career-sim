# Free defensive data, 2006 to 2013

Built from nflverse releases (github.com/nflverse/nflverse-data): play-by-play, weekly depth charts, rosters, season player stats, players table, and 2013 snap counts. Regular season only. 2005 play-by-play and depth charts are read only to fill the prior-season columns for 2006. Nothing from 2014 or later is read or written.

## Files

- `defense_player_season_2006_2013.csv`: 7,850 rows, one per defender per club per season (DL, LB, DB). Traded players get one row per club.
- `defense_team_season_2006_2013.csv`: 256 rows, one per club-season. Outcome candidates (EPA allowed per dropback and per run, raw, neutral-situation and opponent-adjusted), unit indicators for pass rush, coverage and run defense, drive outcomes, prior-season lags, and starter continuity.
- `defense_unclassified_players_2006_2013.csv`: 191 rows for players credited with defensive stats who were offensive or special-teams players that season (e.g. Julian Edelman's 2011 snaps at DB). Kept out of the main file.
- `data_dictionary.csv`: every column, its definition and its season coverage.
- `build_defense_csvs.py`, `write_dictionary.py`: rebuild everything from the nflverse files (paths and file names in the script docstring).

## Checks run

- Player-summed sacks, interceptions, passes defensed and QB hits match nflverse season stats within 0.5% every season.
- Solo tackles and forced fumbles run about 15% below nflverse season totals by design: special-teams plays are excluded.
- Player sacks sum to the club's sacks within one sack for nearly every club-season.
- Sack leaders reproduce (Ware 20.0 in 2008, Allen 22.0 in 2011, Watt 20.5 in 2012, Mathis 19.5 in 2013), as do interception leaders.
- No duplicate keys; 32 clubs in each of the 8 seasons.

## Coverage gaps

- Snap counts: 2013 only. The nflverse 2012 snap-count file is header-only. PFR's team pages have 2012 snaps, but they were not scraped because Sports Reference's terms bar automated collection and use of its data with AI tools. The 2013 snap columns themselves originate from PFR via nflverse.
- Playing time for 2006 to 2012 comes from weekly depth charts (`depth_starter_share`). Some charts list 12 starters (a nickel back), and the number of weekly charts varies from 16 to 18, which is why the share column exists.
- QB hits are recorded from 2006; 2005 has none, so `qb_hit_or_sack_rate_prev` is blank for 2006.
- Official tackles for loss are missing for 2006 and 2007; `tackles_behind_los` is derived the same way in every season.
- Tackle recording changed in 2011: shared and assisted tackle credits drop sharply. `tackle_plays` (one per player per play) is the most consistent tackle count across the break.
- No free source records the defender in coverage on each target before PFR's 2018 charting, so coverage at player level is limited to passes defensed, interceptions, DPI and holding penalties, and tackles after completions.

## Not included

PFF grades (terms bar AI use and public distribution of derived data), PFR Approximate Value (built from the same box-score inputs scaled by team points allowed, and covered by the same Sports Reference terms), and anything from 2014 on.
