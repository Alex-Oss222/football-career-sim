"""2012-era calibration constants for the shared 2013 football kernel.

League-level inputs only. Provenance is in library/2012_game_calibration.md.
Weights are integerized so private packet resolution remains deterministic.
"""
DRIVE_WEIGHTS = {
    # Fit against 2012 PFR team-game anchors: 22.8 points, 347.2 yards,
    # 4.8 punts, 1.6 turnovers, 33.7% scoring-drive rate, 12.5% TO-drive rate.
    "td_methodical": 165,
    "td_explosive": 85,
    "field_goal": 87,
    "punt_short": 218,
    "punt_fieldflip": 218,
    "turnover_short": 70,
    "turnover_deep": 55,
    "turnover_on_downs": 35,
    "missed_field_goal": 35,
    "end_period": 30,
    "safety": 2,
}

PENALTY_WEIGHTS = {
    # 2012 league average was 6.3 accepted penalties per team-game.
    # Across roughly 11 offensive and 11 defensive possessions, this yields
    # about that burden without making every foul drive-defining.
    "none": 43,
    "offense": 29,
    "defense": 28,
}

TIER_ANCHORS = {
    "replacement-level": -2,
    "below-average": -1,
    "average": 0,
    "plus": 1,
    "elite": 2,
}

CALIBRATION_BANDS = {
    "points_per_team_game": (19.0, 27.0),
    "yards_per_team_game": (300.0, 395.0),
    "possessions_per_team_game": (9.0, 14.0),
    "turnovers_per_team_game": (0.8, 2.4),
    "punts_per_team_game": (3.0, 6.5),
    "penalties_per_team_game": (4.0, 9.0),
}
