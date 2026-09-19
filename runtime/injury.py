"""Period-calibrated injury occurrence helpers.

The rates are derived from published 2012-2014 NFL injury-report epidemiology.
They are simulation inputs only and must never be presented as a player's hidden
health score.
"""
POSITION_RISK = {
    "WR": 30.28, "TE": 27.44, "DB": 23.60, "RB": 21.90, "LB": 21.48,
    "DL": 15.88, "OL": 12.85, "QB": 12.09, "K": 4.88, "P": 4.88,
}
SEVERITY_WEIGHTS = {
    "practice_limited": 45,
    "short_absence": 30,
    "multi_week": 20,
    "long_term": 5,
}

def relative_position_weight(position):
    return POSITION_RISK.get(position, 15.0)

def football_status(severity):
    return {
        "practice_limited": "LIMITED",
        "short_absence": "OUT_SHORT",
        "multi_week": "OUT_MULTI_WEEK",
        "long_term": "OUT_LONG_TERM",
    }[severity]
