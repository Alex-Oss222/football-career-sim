"""2012-era calibration constants for the shared 2013 football kernel.

These are league-level inputs, not player ratings. Source/provenance lives in
library/2012_game_calibration.md and library/data/2012_nfl_aggregate_baseline.json.
"""
DRIVE_WEIGHTS = {
    "td_methodical": 150,
    "td_explosive": 80,
    "field_goal": 130,
    "punt_short": 190,
    "punt_fieldflip": 190,
    "turnover_short": 70,
    "turnover_deep": 55,
    "turnover_on_downs": 45,
    "missed_field_goal": 55,
    "end_period": 33,
    "safety": 2,
}

# Fixed qualitative anchor points. Internal use only; never coach-facing.
TIER_ANCHORS = {
    "replacement-level": -2,
    "below-average": -1,
    "average": 0,
    "plus": 1,
    "elite": 2,
}

# 2012 regular-season league anchors used as validation bands, not exact targets.
CALIBRATION_BANDS = {
    "points_per_team_game": (19.0, 27.0),
    "possessions_per_team_game": (9.0, 14.0),
    "turnovers_per_team_game": (0.8, 2.4),
    "punts_per_team_game": (3.0, 6.5),
}
