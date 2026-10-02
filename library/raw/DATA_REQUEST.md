# Data request: what the user supplies, and how

Written October 2, 2026, for the 2010-2014 player-evidence policy the user adopted that day (real careers to 2012 carried forward on pooled aging curves, draft-slot priors, a recorded once-per-season swing, capped feedback from snaps, role and availability). This file lists only data that public sources do not already give the project. Anything not listed here is already covered and should not be uploaded.

## Already covered, do not upload

The public nflverse releases (pinned by sha256 in `library/data/`) already provide, for 2010-2014: play-by-play, weekly and season player statistics, QB hits and sacks by defender, draft picks, combine results, rosters, weekly injury reports, and snap counts from 2012 onward. Real 2013 and 2014 statistics are therefore not needed from the user.

## Do not upload anything from 2015 or later

Seasons after 2014 are the future inside the career. A season is added only when the career clock reaches it, with its public date, so no fit or evaluation can read it early (the no-hindsight rule).

## The public-repository problem

This repository is **public**. Paid data (PFF, Sports Info Solutions, Football Outsiders premium) is normally licensed for personal use and must not be committed to a public repository. Before uploading any paid data, choose one:

1. make the repository private (GitHub, Settings, General, Danger Zone, Change visibility), or
2. keep the paid files out of the repository and tell Claude; they would then be stored in the private Engine State service on Railway instead.

Free, redistributable data (for example Pro Football Reference exports, if their terms allow) can be committed as below.

## The requests, in priority order

### 1. Snap counts for 2010 and 2011 (highest value for player states)

What it unlocks: aging curves and the snap/role/availability feedback fitted on five seasons instead of three, for every position, especially offensive linemen and defensive backs.

One row per player per game (preferred) or per player per season:

| Column | Meaning |
|---|---|
| season | 2010 or 2011 |
| week | regular-season week (blank for a season row) |
| game_date | YYYY-MM-DD (blank for a season row) |
| team | team abbreviation the player played for |
| opponent | opponent abbreviation (blank for a season row) |
| player_name | full name as listed |
| player_id | the source's own player ID (PFF id, PFR id or gsis id) |
| position | position as listed |
| offense_snaps | count |
| offense_pct | share of team offensive snaps, 0-100 |
| defense_snaps | count |
| defense_pct | share, 0-100 |
| st_snaps | special-teams snaps |
| st_pct | share, 0-100 |

Likely source: PFF (snap counts go back to 2006). Pro Football Reference starts in 2012, which the project already has.

### 2. Pass-rush and pass-block charting, 2010-2014

What it unlocks: offensive linemen and pass rushers judged on their own work instead of honours and games started.

One row per player per season (per game if available):

| Column | Meaning |
|---|---|
| season, team, player_name, player_id, position | as above |
| pass_rush_snaps | snaps rushing the passer |
| pressures | total pressures |
| hurries, qb_hits, sacks | components |
| pass_block_snaps | snaps in pass protection |
| pressures_allowed | total |
| hurries_allowed, hits_allowed, sacks_allowed | components |
| run_block_snaps | if available |

Likely source: PFF premium statistics.

### 3. Coverage charting, 2010-2014

What it unlocks: defensive backs and linebackers judged in coverage.

One row per player per season:

| Column | Meaning |
|---|---|
| season, team, player_name, player_id, position | as above |
| coverage_snaps | snaps in coverage |
| targets, receptions_allowed, yards_allowed | when he was the primary defender |
| td_allowed, interceptions, passes_defended | |
| slot_snaps, wide_snaps, box_snaps | alignment, if available |

Likely source: PFF premium statistics.

### 4. Play-level defensive charting, 2010-2014 (the only route to defensive calls affecting results)

What it unlocks: a measured effect of coverage shell and pressure count on play outcomes. Without it, Stone's defensive calls are recorded on every snap but cannot change a result, because no effect size may be invented.

One row per play:

| Column | Meaning |
|---|---|
| season, week, game_date, home_team, away_team | game key |
| quarter, game_clock | MM:SS remaining in the quarter |
| down, distance, yardline | ball spot as the source records it |
| play_description | the source's text, so the play can be matched to nflverse play-by-play |
| offense_personnel, defense_personnel | for example 11, 12; 4-2-5 |
| pass_rushers | number who rushed |
| blitz | yes/no as the source defines it |
| coverage | Cover 0/1/2/3/4/6, man or zone, as the source names it |
| defenders_in_box | count |

Likely source: PFF or Sports Info Solutions play-level data (usually a paid API or data product).

### 5. Fallback if item 4 cannot be had: team-season defensive tendencies, 2010-2014

One row per team per season: blitz rate, average pass rushers, share of snaps in nickel and dime, and share in man coverage, with the source's definitions. Football Outsiders published several of these in its annual Almanac and pass-rush articles (archived copies may exist on archive.org). Weaker than item 4, but it can show whether any team-level effect exists.

## File format for every upload

- Plain CSV, UTF-8, comma-separated, one header row, one file per dataset per season.
- Missing values left blank, never typed as 0.
- Values exactly as the source gives them. No hand edits, no recalculations, no merged cells.
- Larger than about 25 MB: compress to `.csv.gz`.
- Folder and names: `library/raw/<source>/<dataset>_<season>.csv`, for example `library/raw/pff/snap_counts_2010.csv` or `library/raw/pff/pass_rush_2013.csv`.
- In each source folder, a `SOURCE.md` with: the source and product name, the URL, the date you downloaded it, the account or subscription used, the licence or terms (a link is enough), the source's definitions of each column (paste or link its glossary), and anything you changed (should be nothing).

On your computer the folder is `C:\Users\alexl\OneDrive\Desktop\Different LLM\Football\Repo\library\raw\` after you pull `main`. Upload through GitHub ("Add files via upload") the way you upload packets, or commit from your local clone.

## What happens after upload

Claude runs the project's two-pass check on each file: the first pass joins every player to the project's IDs and records the counts; a separate second pass rejoins from scratch and checks the totals against the public play-by-play wherever the two overlap. Unmatched players and mismatches are listed, never guessed. Only then does a file enter any fit.
