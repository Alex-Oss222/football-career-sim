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
    # Sourced in library/2013_nfl_playing_rules_for_simulation.md (kernel 2013.8).
    two_minute_warning_seconds: int = 120
    safety_kick_yard_line: int = 20
    scrimmage_kick_touchback_yard_line: int = 20
    two_point_snap_yard_line: int = 2
    regular_ot_timeouts: int = 2
    # Kernel 2014.1 (Unverified for 2013, labelled inference): postseason
    # overtime periods are played as halves of two periods, each club with
    # three timeouts per such half.
    postseason_ot_timeouts_per_half: int = 3
    postseason_ot_intermission_seconds: int = 120
    # Engine bound, not a football rule: postseason overtime is untimed in
    # the sense that periods continue until a score. The kernel lays the
    # periods on one continuous timeline of this many periods and fails
    # closed if it is ever exhausted.
    postseason_ot_period_bound: int = 10
    # Preseason game-day unit: the 46-player active list applies to regular
    # season and postseason games; in a preseason game every player on the
    # club's roster may dress (2013-2014 offseason roster limit 90, cut to 75
    # then 53 at the dated deadlines, which the roster file itself carries).
    preseason_roster_limit: int = 90
    # 2014 preseason extra-point experiment (approved by the clubs May 20,
    # 2014; NFL communications, "NFL to experiment with longer extra points
    # in preseason"): in preseason Weeks 1 and 2 the try was snapped from
    # the 15-yard line, which the league described as a 33-yard kick; from
    # preseason Week 3 and in the regular season the 2-yard line applied.
    # The experiment belongs to 2014 only; two-point tries were unchanged.
    preseason_2014_pat_snap_yard_line: int = 15
    preseason_2014_pat_distance: int = 33
    preseason_2014_pat_window: tuple = ("2014-08-07", "2014-08-17")

RULES = Rules2013()
PRESEASON = "preseason"
GAME_TYPES = ("regular", "postseason", "pro_bowl", PRESEASON)


def active_limit(game_type="regular"):
    """Game-day actives a club may dress: 46, or the whole roster in preseason."""
    return RULES.preseason_roster_limit if game_type == PRESEASON else RULES.active_limit


def extra_point_rule(game_type="regular", game_date=None):
    """The try rule for a game, or None when the ordinary extra point applies.

    Only a 2014 preseason game dated inside the experiment window gets the
    15-yard-line try, resolved on the field-goal distance model at 33 yards.
    Every other game, every regular-season and postseason game included,
    returns None and keeps the kernel's extra-point rate unchanged.
    """
    if game_type != PRESEASON or not game_date:
        return None
    if not isinstance(game_date, str) or len(game_date) != 10:
        raise ValueError("game_date must be an ISO date string YYYY-MM-DD")
    first, last = RULES.preseason_2014_pat_window
    if first <= game_date <= last:
        return {"snap_yard_line": RULES.preseason_2014_pat_snap_yard_line,
                "distance": RULES.preseason_2014_pat_distance, "model": "field_goal_distance",
                "basis": "2014 preseason Weeks 1-2 experiment"}
    return {"snap_yard_line": RULES.pat_snap_yard_line, "distance": None,
            "model": "extra_point_rate", "basis": "ordinary try"}

DIVISION_TIEBREAKERS=("head_to_head","division_record","common_games","conference_record",
    "strength_of_victory","strength_of_schedule","conference_combined_rank",
    "league_combined_rank","net_common_points","net_all_points","net_touchdowns","coin_toss")
WILD_CARD_TIEBREAKERS=("head_to_head_if_applicable","conference_record","common_games_minimum_four",
    "strength_of_victory","strength_of_schedule","conference_combined_rank","league_combined_rank",
    "net_conference_points","net_all_points","net_touchdowns","coin_toss")
PLAYOFF_SEEDS={"division_champions":(1,2,3,4),"wild_cards":(5,6)}

def review_authority(*, seconds_left, scoring=False, turnover=False, overtime=False):
    """2013: the replay official initiates every review inside two minutes of
    either half, throughout overtime, and of every scoring play and turnover;
    otherwise a coach's challenge is required."""
    if scoring or turnover or overtime or seconds_left <= RULES.two_minute_warning_seconds:
        return "booth"
    return "coach"


def ot_status(history, game_type="regular", expired=False):
    """2012-forward modified sudden death as a pure function.

    ``history`` lists the overtime possessions in order, each a mapping with
    ``team`` and ``score`` (None, "touchdown", "field_goal" or "safety").
    Returns "end" or "continue". A first-possession touchdown or a safety at
    any time ends the game. A first-possession field goal gives the opponent
    one possession: its touchdown wins, its field goal leads to sudden death
    and no score means the field-goal team wins. A scoreless first possession
    leads to sudden death. When the period expires (``expired``), a regular
    season game ends (tied or not); a postseason game continues.
    """
    scores = [entry.get("score") for entry in history]
    if "safety" in scores:
        return "end"
    rest = None
    if scores:
        first = scores[0]
        if first == "touchdown":
            return "end"
        if first == "field_goal":
            if len(scores) >= 2:
                second = scores[1]
                if second != "field_goal":
                    return "end"
                rest = scores[2:]
        else:
            rest = scores[1:]
    if rest is not None and any(rest):
        return "end"
    if expired and game_type != "postseason":
        return "end"
    return "continue"
