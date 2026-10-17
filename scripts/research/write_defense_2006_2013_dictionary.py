import sys, csv
import pandas as pd

OUT = sys.argv[1]
P = "defense_player_season_2006_2013.csv"
T = "defense_team_season_2006_2013.csv"
U = "defense_unclassified_players_2006_2013.csv"

player = {
    "season": ("Regular season year", "all"),
    "team": ("Club, current nflverse code (LA = Rams, LAC = Chargers, LV = Raiders for every season)", "all"),
    "gsis_id": ("NFL GSIS player ID; joins to nflverse play-by-play and player tables", "all"),
    "pfr_id": ("Pro Football Reference player ID, for joining other sources", "all"),
    "player_name": ("Name from depth chart, else roster, else player table", "all"),
    "position": ("Defensive position from that season's depth chart, else roster, else player stats, else player table", "all"),
    "position_group": ("DL (DE, DT, NT), LB (OLB, ILB, MLB), DB (CB, S). 3-4 edge rushers listed as OLB fall in LB", "all"),
    "depth_position": ("Most frequent depth-chart slot that season (e.g. LDE, RCB, WLB)", "all; blank if never on chart"),
    "age_sept1": ("Age in years on 1 September of the season", "all"),
    "years_exp": ("Accrued seasons per nflverse roster", "all"),
    "draft_year": ("Draft year; blank = undrafted or unknown", "all"),
    "draft_round": ("Draft round; blank = undrafted or unknown", "all"),
    "draft_pick": ("Overall pick; blank = undrafted or unknown", "all"),
    "n_teams_season": ("Clubs the player has a row for that season; rows are per club", "all"),
    "team_games": ("Club regular-season games", "all"),
    "games_with_def_stat": ("Games in which the player was credited with any defensive stat on a scrimmage play (lower bound on games played)", "all"),
    "games_season_all_teams": ("Games played per nflverse season stats; total across clubs if traded", "all; blank if absent from that table"),
    "team_depth_charts": ("Weekly NFL depth charts published for the club that season (16 to 18)", "all"),
    "depth_weeks_listed": ("Weekly charts listing the player on defense at any depth", "all"),
    "depth_weeks_starter": ("Weekly charts listing the player as a defensive starter (depth 1)", "all"),
    "depth_starter_share": ("depth_weeks_starter / team_depth_charts; the playing-time proxy for 2006 to 2012", "all"),
    "def_snaps": ("Regular-season defensive snaps", "2013 only; nflverse 2012 file is empty"),
    "def_snap_pct": ("def_snaps / team_def_snaps", "2013 only"),
    "games_with_def_snap": ("Games with at least one defensive snap", "2013 only"),
    "team_def_snaps": ("Club defensive snaps, reconstructed from per-game snaps and percentages", "2013 only"),
    "sacks": ("Sacks, half sacks as 0.5", "all"),
    "sack_plays": ("Plays credited with a full or half sack", "all"),
    "qb_hits": ("Official QB hits; most sacks also carry a QB hit", "2006 on"),
    "qb_hits_non_sack": ("QB hits on plays that were not sacks", "2006 on"),
    "pressure_plays": ("Distinct plays with a sack, half sack or QB hit credit; the free pass-rush proxy, not PFF pressures", "2006 on"),
    "roughing_passer_pen": ("Roughing-the-passer penalties", "all"),
    "tackle_plays": ("Scrimmage plays with any tackle credit (solo, shared or assist), counted once per play. Special teams excluded", "all"),
    "tackles_solo": ("Solo tackles on scrimmage plays", "all"),
    "tackles_with_assist": ("Shared tackles credited as primary (nflverse tackle_with_assist); recording drops sharply from 2011", "all"),
    "tackle_assists": ("Assisted tackles on scrimmage plays; recording convention shifts in 2011", "all"),
    "run_tackle_plays": ("Tackle credits on designed runs", "all"),
    "run_stops": ("Tackle credits on designed runs the offense failed to make successful (nflverse success = 0)", "all"),
    "run_tackle_yards_mean": ("Mean yards gained on runs the player tackled; lower is better", "all; blank if none"),
    "run_tackle_epa_mean": ("Mean offensive EPA on runs the player tackled; lower is better", "all; blank if none"),
    "tackles_behind_los": ("Tackle credits on non-sack plays that lost yards; consistent substitute for TFL across all seasons", "all"),
    "tfl_official": ("Official tackles for loss", "2008 on; blank 2006-2007 (not recorded)"),
    "pass_tackle_plays": ("Tackle credits on completed passes; rough indicator of who was near the catch, not targets allowed", "all"),
    "pass_stops": ("Tackle credits on completions that were not successful for the offense", "all"),
    "pass_tackle_yards_mean": ("Mean yards gained on completions the player tackled", "all; blank if none"),
    "pass_tackle_epa_mean": ("Mean offensive EPA on completions the player tackled", "all; blank if none"),
    "passes_defensed": ("Passes defensed", "all"),
    "interceptions": ("Interceptions", "all"),
    "dpi": ("Defensive pass interference penalties", "all"),
    "dpi_yards": ("Yards on DPI penalties", "all"),
    "holding_contact_pen": ("Defensive holding, illegal contact and illegal use of hands penalties", "all"),
    "forced_fumbles": ("Forced fumbles on scrimmage plays", "all"),
    "fumble_recoveries": ("Opponent fumbles recovered on scrimmage plays", "all"),
    "def_penalties": ("All defensive penalties charged to the player on scrimmage downs, including nullified plays", "all"),
    "def_penalty_yards": ("Yards on those penalties", "all"),
    "pre_snap_pen": ("Defensive offside, encroachment and neutral zone infractions", "all"),
}

team = {
    "team": ("Club, current nflverse code", "all"),
    "season": ("Regular season year", "all"),
    "games": ("Regular-season games", "all"),
    "plays": ("Opponent dropbacks plus designed runs with valid EPA (nflverse pass==1 or rush==1); includes penalty plays", "all"),
    "dropbacks": ("Opponent dropbacks, including sacks and scrambles", "all"),
    "pass_attempts": ("Opponent pass attempts, excluding sacks and scrambles", "all"),
    "rushes": ("Opponent designed runs, excluding scrambles", "all"),
    "epa_per_play": ("Mean offensive EPA allowed per play; lower is better for the defense", "all"),
    "epa_per_dropback": ("EPA allowed per dropback (pass rush plus coverage)", "all"),
    "epa_per_pass_att": ("EPA allowed per pass attempt, sacks and scrambles excluded (coverage-leaning)", "all"),
    "epa_per_rush": ("EPA allowed per designed run", "all"),
    "success_dropback": ("Offensive success rate allowed on dropbacks", "all"),
    "success_rush": ("Offensive success rate allowed on runs", "all"),
    "epa_per_dropback_neutral": ("As epa_per_dropback, win probability 10% to 90% and outside the last two minutes of each half", "all"),
    "epa_per_rush_neutral": ("As epa_per_rush, same neutral filter", "all"),
    "epa_per_dropback_adj": ("Opponent-adjusted: each play's EPA minus that offense's mean against all other defenses that season, re-centred on the league mean", "all"),
    "epa_per_rush_adj": ("Opponent-adjusted EPA per run, same method", "all"),
    "sack_rate": ("Sacks per dropback", "all"),
    "qb_hit_or_sack_rate": ("Dropbacks with a QB hit or sack per dropback", "all"),
    "int_rate": ("Interceptions per pass attempt", "all"),
    "pass_defensed_rate": ("Pass attempts with a pass defensed or interception per attempt", "all"),
    "completion_rate_allowed": ("Completions per pass attempt", "all"),
    "explosive_pass_rate": ("Pass attempts gaining 20+ yards per attempt", "all"),
    "explosive_run_rate": ("Runs gaining 10+ yards per run", "all"),
    "run_stuff_rate": ("Runs gaining 0 or fewer yards per run", "all"),
    "yards_per_rush": ("Yards allowed per designed run", "all"),
    "def_penalties_per_game": ("Defensive penalties on scrimmage downs per game, including declined and offsetting where recorded", "all"),
    "dpi_count": ("Defensive pass interference penalties; blank = none", "all"),
    "dpi_yards": ("DPI yards; blank = none", "all"),
    "drives_faced": ("Opponent drives (nflverse fixed_drive)", "all"),
    "td_per_drive": ("Share of opponent drives ending in an offensive touchdown; the old outcome measure, for comparison", "all"),
    "fg_per_drive": ("Share ending in a made field goal", "all"),
    "turnover_per_drive": ("Share ending in a turnover", "all"),
    "punt_per_drive": ("Share ending in a punt", "all"),
    "points_per_drive_approx": ("(7 x TD drives + 3 x FG drives) / drives", "all"),
    "points_allowed_per_game": ("Points allowed per game from final scores, including return and defensive scores by the opponent", "all"),
    "prev_starter_weeks_share_returning": ("Share of last season's defensive starter-weeks belonging to players on this season's week-1 defensive depth chart (known before kickoff)", "all"),
    "wk1_starters_returning": ("Week-1 defensive starters who started at least 4 weeks for the club last season", "all"),
}
for c in ["epa_per_play", "epa_per_dropback", "epa_per_pass_att", "epa_per_rush", "epa_per_dropback_adj",
          "epa_per_rush_adj", "success_dropback", "success_rush", "sack_rate", "qb_hit_or_sack_rate",
          "int_rate", "td_per_drive", "points_per_drive_approx"]:
    cov = "2007 on (2005 pbp has no QB hits)" if c == "qb_hit_or_sack_rate" else "all (2006 lags use 2005 data)"
    team[c + "_prev"] = (f"Prior-season value of {c} for the same club", cov)

unclassified = {
    "season": ("Regular season year", "all"), "team": ("Club", "all"), "gsis_id": ("GSIS ID", "all"),
    "pfr_id": ("PFR ID", "all"), "player_name": ("Name", "all"),
    "roster_position": ("Roster position", "all"), "stats_position": ("nflverse stats position", "all"),
    "depth_position": ("Defensive depth slot if any", "all"),
    "tackle_plays": ("As in player file", "all"), "sacks": ("As in player file", "all"),
    "qb_hits": ("As in player file", "all"), "passes_defensed": ("As in player file", "all"),
    "interceptions": ("As in player file", "all"), "forced_fumbles": ("As in player file", "all"),
    "def_penalties": ("As in player file", "all"),
}

rows = []
for fname, spec in [(P, player), (T, team), (U, unclassified)]:
    cols = pd.read_csv(f"{OUT}/{fname}", nrows=1).columns.tolist()
    missing = [c for c in cols if c not in spec]
    extra = [c for c in spec if c not in cols]
    assert not missing and not extra, (fname, missing, extra)
    for c in cols:
        rows.append({"file": fname, "column": c, "definition": spec[c][0], "coverage": spec[c][1]})
with open(f"{OUT}/data_dictionary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["file", "column", "definition", "coverage"])
    w.writeheader()
    w.writerows(rows)
print("dictionary rows", len(rows))
