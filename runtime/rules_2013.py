"""Runtime subset of verified 2013 NFL game rules.

Full provenance is recorded in library/2013_game_rules.md and the era sourcebook.
"""
RULES = {
    "regulation_quarters": 4,
    "quarter_seconds": 900,
    "regulation_seconds": 3600,
    "timeouts_per_half": 3,
    "regular_season_overtime_seconds": 900,
    "regular_season_ot_can_tie": True,
    "opening_ot_touchdown_ends_game": True,
    "opening_ot_field_goal_guarantees_reply_possession": True,
    "overtime_coach_challenges": False,
    "turnovers_automatically_reviewed": True,
    "scoring_plays_automatically_reviewed": True,
    "coach_challenges": 2,
    "third_challenge_after_two_successful": True,
    "roster_limit": 53,
    "game_day_active_limit": 46,
    "pat_kick_spot_yard_line": 2,
    "touchback_yard_line": 20,
}
