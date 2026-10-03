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


# ---- possession sequencing (kernel 2014.6, batch B8) -----------------------------------------------------

# Engine bound, not a football rule: a sequence of kickoffs in which every
# kick is returned for a touchdown (each scorer kicking off again) is laid
# out on one chain of at most this many kicks; the kernel fails closed if
# it is ever exhausted (never observed; plan B9).
KICK_CHAIN_BOUND = 8
# How a possession began after a kick the kicking club kept (a recovery of
# the receiving club's fumble or muff, R12 layer C; an onside recovery, R9).
RETAINED_START_KINDS = ("kickoff_retained", "free_kick_retained", "punt_retained")
SCORE_POINTS = {"touchdown": 6, "field_goal": 3, "safety": 2}


def possession_score(p, opponent=None):
    """The score a possession produced, as (kind, scoring club, points), or
    None.

    Read from the possession record or a receipt's drive row: a touchdown
    (6 plus the try), a made field goal (3), a safety (2 to the opponent,
    ``opponent`` when known). A non-offensive score recorded on the drive
    (``non_offensive_score``: {"kind", "team", "points"}, written by the
    kernel for a defensive touchdown, batch B9) takes precedence: the scorer
    is the club it names, never the offense.
    """
    non_offensive = p.get("non_offensive_score")
    if isinstance(non_offensive, dict) and non_offensive.get("kind"):
        return (non_offensive["kind"], non_offensive.get("team"),
                int(non_offensive.get("points", SCORE_POINTS[non_offensive["kind"]])))
    category = p.get("category")
    if category == "touchdown":
        return ("touchdown", p.get("team"), 6 + (1 if p.get("xp_made") else 0))
    if category == "field_goal_attempt" and p.get("fg_made"):
        return ("field_goal", p.get("team"), 3)
    if category == "safety":
        return ("safety", opponent, 2)
    return None


def kick_score(kick):
    """The score a kick record or kicks-summary row produced, as (kind,
    scoring club, points), or None: a kick returned for a touchdown (the
    receiving club, 6 plus the try; batch B9 R15)."""
    if kick.get("touchdown") or kick.get("outcome") == "returned_touchdown":
        team = kick.get("scoring_team") or kick.get("receiving")
        points = kick.get("points")
        if points is None:
            points = 6 + (1 if kick.get("xp_made") else 0)
        return ("touchdown", team, int(points))
    return None


def kick_try_made(kick):
    """Whether the try after a kick's touchdown was made: the record's
    ``xp_made`` (None when there was no try), or on a summary row read from
    its points (7 made; 6 missed or no try, which the row cannot tell apart,
    so None)."""
    if "xp_made" in kick:
        return kick.get("xp_made")
    points = kick.get("points")
    if points is None:
        return None
    return True if points == 7 else None


def kicking_club(kind, scoring_team, opponent):
    """The club that kicks off after a score: the scorer after a touchdown
    or field goal; after a safety the club scored upon free-kicks."""
    return opponent if kind == "safety" else scoring_team


def ot_history(possessions, kicks=()):
    """The overtime possession history ``ot_status`` reads, built from the
    overtime possessions and the overtime kicks (kick records or a
    receipt's kicks summary), in game order.

    One entry per overtime possession: {"team", "score"} with the kind of
    score the possession produced (None when it did not score). A
    defensive touchdown during a possession is that possession's score
    ("touchdown", the entry also naming ``scoring_team``), which ends the
    game under the rule exactly as the offense's touchdown would. A kick
    returned for a touchdown is the returning club's entry (it scored on
    its opportunity to possess), so an overtime whose opening kickoff is
    returned for a touchdown has a complete history with zero possessions.
    A kickoff the kicking club keeps before the receiving club's first
    possession gives the receiving club a scoreless entry: it is considered
    to have had its opportunity to possess (library rule R4), so the
    kicking club's possession that follows is a sudden-death possession.
    Kicks are ordered before the possession whose number they carry
    (``drive``), by kick number.
    """
    history = []
    by_drive = {}
    for kick in kicks:
        if kick.get("half") != "OT":
            continue
        by_drive.setdefault(kick.get("drive"), []).append(kick)
    for group in by_drive.values():
        group.sort(key=lambda k: k.get("kick_no", 0))

    def possessed(team):
        return any(entry["team"] == team for entry in history)

    def kick_entries(group):
        for kick in group:
            score = kick_score(kick)
            if score is not None:
                history.append({"team": score[1], "score": "touchdown", "kick": kick.get("kick_no")})
            elif kick.get("outcome") == "retained" and not possessed(kick.get("receiving")):
                history.append({"team": kick.get("receiving"), "score": None, "kick": kick.get("kick_no"),
                                "opportunity": "kicking-club recovery (R4)"})

    overtime = [p for p in possessions if p.get("half") == "OT"]
    for p in overtime:
        kick_entries(by_drive.pop(p.get("number"), ()))
        score = possession_score(p)
        entry = {"team": p.get("team"), "score": score[0] if score else None}
        if score and score[1] is not None and score[1] != p.get("team"):
            entry["scoring_team"] = score[1]
        history.append(entry)
    for number in sorted(k for k in by_drive if k is not None):
        kick_entries(by_drive[number])
    return history
