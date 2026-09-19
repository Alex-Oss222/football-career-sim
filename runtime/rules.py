"""Executable subset of the 2013 NFL rules required by the game kernel."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Rules2013:
    quarter_seconds: int = 900
    halftime_seconds: int = 720
    play_clock_seconds: int = 40
    play_clock_admin_seconds: int = 25
    timeouts_per_half: int = 3
    regulation_periods: int = 4
    regular_ot_seconds: int = 900
    preseason_ot_seconds: int = 900
    postseason_ot_seconds: int = 900
    challenge_count: int = 2
    earned_third_challenge: bool = True
    roster_limit: int = 53
    active_limit: int = 46
    kickoff_yard_line: int = 35
    kickoff_touchback_yard_line: int = 20
    pat_snap_yard_line: int = 2

RULES = Rules2013()

def overtime_ends(scores, possession_complete, game_type="regular"):
    """2012-forward modified sudden death; postseason cannot end tied."""
    home, away = scores
    if home == away:
        return False
    return possession_complete

def review_authority(*, seconds_left, scoring=False, turnover=False):
    if scoring or turnover or seconds_left <= 120:
        return "booth"
    return "coach"
