"""Period-calibrated injury occurrence helpers.

Position incidence comes from Lawrence et al., 2012-2014 NFL injury-report
epidemiology. Values are injuries per 100 team-game player exposures. They are
private simulation inputs, never player-facing hidden health grades.
"""
POSITION_RISK = {
    "WR": 30.28, "TE": 27.44, "DB": 23.60, "CB": 23.60, "S": 23.60,
    "RB": 21.90, "FB": 21.90, "LB": 21.48,
    "DL": 15.88, "DE": 15.88, "DT": 15.88,
    "OL": 12.85, "OT": 12.85, "OG": 12.85, "C": 12.85,
    "QB": 12.09, "K": 4.88, "P": 4.88, "LS": 4.88,
}
SEVERITY_WEIGHTS = {
    # Bounded football-status classes. The public record receives the medical
    # status only after the medical layer communicates it, not a private draw.
    "practice_limited": 45,
    "short_absence": 30,
    "multi_week": 20,
    "long_term": 5,
}

def relative_position_weight(position):
    return POSITION_RISK.get(position, 15.0)

def occurrence_weights(position, exposure):
    if not 0.0 <= float(exposure) <= 1.0:
        raise ValueError("exposure must be in [0,1]")
    risk_bps = round(relative_position_weight(position) * 100 * float(exposure))
    risk_bps = max(0, min(9500, risk_bps))
    return {"injury": risk_bps, "none": 10000 - risk_bps}

def football_status(severity):
    return {
        "practice_limited": "LIMITED",
        "short_absence": "OUT_SHORT",
        "multi_week": "OUT_MULTI_WEEK",
        "long_term": "OUT_LONG_TERM",
    }[severity]
