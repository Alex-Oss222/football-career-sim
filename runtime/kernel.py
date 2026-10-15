"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict, replace
import hashlib, json, math, random

from . import KERNEL_VERSION
from . import calibration
from . import calibration_base
from . import injury_model
from . import participation
from . import rotation
from .rules import (GAME_TYPES, KEPT_KICK_OUTCOMES, KICK_CHAIN_BOUND, PRESEASON, RULES, kicking_club,
                    ot_history, ot_status, try_rule)
from . import chains as chain_walk
from . import drive_model
from . import field_position
from . import strength as unit_strength
from . import player_state
from . import usage
from . import scoring_decisions as scoring
from .player_evidence import empty_player_stats, normalize_players, observation
from .profiles import Profile, profile_for
from .play_detail import (
    KICKOFF_DETAIL_TAG, PUNT_BLOCKED_TD, PUNT_RETURN_TD, apply_drive_detail, apply_kickoff_detail, canonical_call_sheet, check_ledger,
    has_chain_ledger, return_touchdown_distance_errors, scoring_events, seat_try, try_fields, try_row, two_point_row,
    _period_clock, _stream,
)


@dataclass(frozen=True)
class TeamInput:
    team_id: str
    active_players: tuple
    offense_anchor: float = 2.0
    defense_anchor: float = 2.0
    special_teams_anchor: float = 2.0
    scheme: str = "balanced"
    plan: str = "balanced"
    roster: tuple = ()
    personnel_packages: tuple = ()
    rotation_plan: tuple = ()
    # Public, week-specific offensive calls. Entries may be strings or dicts
    # with name/family/type/personnel/formation/motion/protection/tags.
    offensive_call_sheet: tuple = ()
    # Kernel 2014.4 (E1, runtime/strength.py): the club's dated honours
    # evidence per player id, built by runtime.strength.team_strength. None
    # keeps the legacy anchor path; a record with no honoured player is still
    # scored (a unit with none sits below the study's centre). Omitted from
    # the outcome packet when None, so legacy packets are unchanged.
    strength: dict | None = None
    # Kernel 2014.6 batch B9 (R8, R9): the club's standing two-point and
    # onside decisions (call_sheet.json decisions.two_point and
    # decisions.kickoff; runtime.scoring_decisions.policy_errors). Any club
    # may carry them; each is omitted from the outcome packet when None and
    # enters it through scoring_decisions.canonical_policy (id and source
    # text stay with the frozen sheet), so legacy packets are unchanged.
    try_policy: dict | None = None
    kickoff_policy: dict | None = None


POLICY_FIELDS = ("try_policy", "kickoff_policy")


def outcome_policies(data):
    """Drop None policies from a TeamInput's dict form and canonicalise the
    rest (scoring_decisions.canonical_policy, the one stripper both packet
    builders use)."""
    for name in POLICY_FIELDS:
        if data.get(name) is None:
            data.pop(name, None)
        else:
            data[name] = scoring.canonical_policy(data[name])
    return data


def installed_profile():
    """The profile production resolves with: runtime.KERNEL_VERSION's, as
    read by this module (resolve_game and runtime.game_runner.run_game)."""
    return profile_for(KERNEL_VERSION)


def decision_block_errors(home, away, *, profile, game_type, management_mode="autonomous", controlled_team=None):
    """The batch B9 decision-block refusals of one game ([] when it may
    proceed), all decidable from the inputs before any draw. The production
    runner applies them before the private event is journaled
    (runtime.game_runner.run_game, with installed_profile()); the kernel
    applies them again, before its first draw, as the second line:

    - a block for a kind the resolving ``profile`` does not decide;
    - any block in a preseason or Pro Bowl game;
    - a malformed block (scoring_decisions.policy_errors);
    - ``otherwise: ask`` on any club but the controlling coach's in a
      user-controlled game (a live answer has no one to give it);
    - U6 (unanswered): the controlled club of a user-controlled regular or
      postseason game without a block (a standing rule, a delegation or
      ``otherwise: ask``) for every kind the profile decides.

    A rule reads only the inputs and the controlled-club designation, never
    a club's identity; the same block on either side is refused or accepted
    alike."""
    errors = []
    kinds = scoring.profile_kinds(profile)
    user_controlled = management_mode == "user_controlled"
    if user_controlled and controlled_team not in (home.team_id, away.team_id):
        return ["user-controlled management requires the controlled club's team_id"]
    present = {}
    for team in (home, away):
        for field, kind in (("try_policy", "two_point"), ("kickoff_policy", "kickoff")):
            block = getattr(team, field, None)
            if block is None:
                continue
            present[(team.team_id, kind)] = True
            if kind not in kinds:
                errors.append("%s carries a %s decision block; profile %s does not resolve one"
                              % (team.team_id, kind, profile.kernel_version))
                continue
            if game_type in (PRESEASON, PRO_BOWL):
                errors.append("%s carries a %s decision block in a %s game" % (team.team_id, kind, game_type))
                continue
            faults = scoring.policy_errors(block, kind)
            if faults:
                errors.append("%s decision block: %s" % (team.team_id, "; ".join(faults)))
                continue
            if block.get("otherwise") == "ask" and not (user_controlled and team.team_id == controlled_team):
                errors.append("%s asks for a live %s decision; only the controlling coach's club in a "
                              "user-controlled game can answer one" % (team.team_id, kind))
    if user_controlled and game_type in ("regular", "postseason"):
        missing = [kind for kind in kinds if (controlled_team, kind) not in present]
        if missing:
            errors.append("U6: %s has no %s decision block (a standing rule, a delegation or otherwise: ask); "
                          "the user-controlled game fails closed" % (controlled_team, " or ".join(missing)))
    return errors


def _outcome_team(team):
    data = asdict(team)
    if data.get("strength") is None:
        data.pop("strength", None)
    return outcome_policies(data)


def _rng(seed, packet):
    digest = hashlib.sha256(
        seed + json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    ).digest()
    return random.Random(int.from_bytes(digest, "big"))


def _merge_call_stats(target, source):
    for name, line in source.items():
        row = target.setdefault(
            name,
            {
                "family": line.get("family", name),
                "snaps": 0,
                "runs": 0,
                "dropbacks": 0,
                "pass_attempts": 0,
                "completions": 0,
                "yards": 0,
                "touchdowns": 0,
                "turnovers": 0,
                "sacks": 0,
            },
        )
        for field in (
            "snaps", "runs", "dropbacks", "pass_attempts", "completions",
            "yards", "touchdowns", "turnovers", "sacks",
        ):
            row[field] += line.get(field, 0)


def _append_evidence(evidence, drive_ledger, offense_players, defense_players, outcome):
    offense_by_id = {p.player_id: p for p in offense_players}
    defense_by_id = {p.player_id: p for p in defense_players}

    for play in drive_ledger:
        if play.get("sack") and play.get("blocker"):
            # Kernel 2014.3: the lineman facing the rusher is named; which one
            # is an even draw, so no technique finding is asserted.
            blocker = offense_by_id.get(play["blocker"])
            if blocker:
                evidence.append(
                    observation(
                        blocker,
                        unit="offense",
                        role="pass protection",
                        responsibility="protect assigned gap/edge",
                        situation="generated passing down",
                        physical_execution="sacked from his side of the line",
                    )
                )
        if play.get("play_type") == "punt" and play.get("cover_player"):
            # Kernel 2014.3: named only when he made the tackle on a return.
            cover = offense_by_id.get(play["cover_player"])
            if cover:
                evidence.append(
                    observation(
                        cover,
                        unit="special teams",
                        role="punt coverage",
                        responsibility="maintain coverage lane and leverage",
                        situation="returned punt",
                        special_teams_responsibility="tackle made on the return",
                    )
                )
        if play.get("turnover"):
            if play.get("turnover_type") == "interception" and play.get("passer"):
                passer = offense_by_id.get(play["passer"])
                if passer:
                    evidence.append(
                        observation(
                            passer,
                            unit="offense",
                            role="passer",
                            responsibility="protect the football",
                            situation="turnover play",
                            processing="decision resulted in an interception",
                        )
                    )
            elif play.get("runner"):
                runner = offense_by_id.get(play["runner"])
                if runner:
                    evidence.append(
                        observation(
                            runner,
                            unit="offense",
                            role="ball carrier",
                            responsibility="secure the football",
                            situation="turnover play",
                            physical_execution="fumble lost",
                        )
                    )

    if outcome != "turnover":
        # Kernel 2014.6 batch B9: a two-point try row names a target but is
        # not a scrimmage snap, so it is never route evidence (earlier ledgers
        # have no such row, so their evidence is unchanged).
        route = next((p for p in drive_ledger if p.get("target") and p.get("play_type") != "two_point"), None)
        if route:
            receiver = offense_by_id.get(route["target"])
            if receiver:
                evidence.append(
                    observation(
                        receiver,
                        unit="offense",
                        role="route participant",
                        responsibility="execute assigned route",
                        situation=f"{outcome} drive",
                        assignment="assignment held",
                        observable_effort="sustained route responsibility through the rep",
                    )
                )


def _split_yards(total, weight_pass, weight_rush):
    """Split an integer total by weight with largest-remainder rounding."""
    denom = weight_pass + weight_rush
    exact_pass = total * weight_pass / denom
    exact_rush = total - exact_pass
    passing, rushing = math.floor(exact_pass), math.floor(exact_rush)
    leftover = total - passing - rushing
    if leftover:
        if exact_pass - passing >= exact_rush - rushing:
            passing += leftover
        else:
            rushing += leftover
    return passing, rushing


def _start_kind(kick_record):
    """How a possession began after a kick: free_kick, kickoff or kickoff_touchback,
    or (kernel 2014.6 batch B8) free_kick_retained / kickoff_retained when the
    kicking club kept the ball (outcome "retained"), or (batch B9, R9)
    onside_recovery / onside_lost after an onside kick."""
    if kick_record.get("outcome") in scoring.ONSIDE_START:
        return scoring.ONSIDE_START[kick_record["outcome"]]
    retained = kick_record.get("outcome") == "retained"
    if kick_record["free_kick"]:
        return "free_kick_retained" if retained else "free_kick"
    if retained:
        return "kickoff_retained"
    return "kickoff_touchback" if kick_record["touchback"] else "kickoff"


# Kernel 2014.6 batch B8: the test-only scoring hook's shape. ``kicks`` maps a
# kick number to the branch forced on that kick ("retained": the kicking club
# keeps the ball on a real retained record; "touchdown": the receiving club
# returns it for a touchdown), ``drives`` a possession number to
# "defensive_touchdown" (applied only when the drawn drive is a turnover).
# The hook exercises the sequencing before batches B9 and B10 add the sourced
# mechanisms; the production runner cannot pass it (game_runner.architecture_errors).
_SCORING_KICK_BRANCHES = ("retained", "touchdown")
_SCORING_DRIVE_BRANCHES = ("defensive_touchdown",)


# Batch B9 adds the R9 onside outcomes, the R15 punt and field-goal returns,
# and forced tries: ``tries`` maps "drive:N" or "kick:K" to {"decision": "go"
# or "kick", "made": bool} (either key may be left out). With the B9 flags a
# forced "touchdown" kick or "defensive_touchdown" drive runs the sourced R15
# path (a real return record), not the B8 placeholder.
_SCORING_KICK_BRANCHES_B9 = ("onside_recovered", "onside_lost")
_SCORING_DRIVE_BRANCHES_B9 = ("punt_return_td", "blocked_punt_td", "blocked_fg_td")
# Batch B9 team counters (append-only, kernel 2014.6 field group).
SCORING_TEAM_FIELDS = ("two_point_attempts", "two_point_conversions", "defensive_touchdowns",
                       "special_teams_touchdowns", "onside_kicks", "onside_recoveries")


def _scoring_hook(forced, sequencing, scoring_on=False):
    if forced is None:
        return {"kicks": {}, "drives": {}, "tries": {}}
    if not sequencing:
        raise ValueError("_test_scoring requires a profile holding possession_sequencing")
    if not isinstance(forced, dict) or set(forced) - {"kicks", "drives", "tries"}:
        raise ValueError("_test_scoring must be {'kicks': {...}, 'drives': {...}, 'tries': {...}}")
    kicks = dict(forced.get("kicks") or {})
    drives = dict(forced.get("drives") or {})
    tries = dict(forced.get("tries") or {})
    kick_branches = _SCORING_KICK_BRANCHES + (_SCORING_KICK_BRANCHES_B9 if scoring_on else ())
    drive_branches = _SCORING_DRIVE_BRANCHES + (_SCORING_DRIVE_BRANCHES_B9 if scoring_on else ())
    if any(v not in kick_branches for v in kicks.values()):
        raise ValueError("unknown forced kick branch")
    if any(v not in drive_branches for v in drives.values()):
        raise ValueError("unknown forced drive branch")
    if tries and not scoring_on:
        raise ValueError("forced tries need a profile holding two_point_tries")
    for key, spec in tries.items():
        if not isinstance(spec, dict) or set(spec) - {"decision", "made"} or spec.get("decision", "go") not in (
                "go", "kick"):
            raise ValueError("forced try %s must be {'decision': 'go'|'kick', 'made': bool}" % key)
    return {"kicks": kicks, "drives": drives, "tries": tries}


def _edge(team, defense, home, venue="home", off_view=(), def_view=(), passer=None):
    """The drive's matchup edge (runtime/strength.drive_edge).

    Kernel 2013.11: the designated home team gets the home term only at a
    home venue; at a neutral site neither team does. Kernel 2014.4 (E1): the
    home term is 0.023, the clamp +/-0.12, and a club with a strength record
    is scored from the drive's actual lineup; without one it keeps its
    anchor."""
    return unit_strength.drive_edge(team, defense, off_view, def_view, passer,
                                    team is home and venue != "neutral")[0]


def _blank_team_stats(players):
    return {
        "points": 0,
        "touchdowns": 0,
        "field_goals": 0,
        "punts": 0,
        "turnovers": 0,
        "sacks_allowed": 0,
        "penalties": 0,
        "penalty_yards": 0,
        "passing_yards": 0,
        "rushing_yards": 0,
        "first_downs": 0,
        "third_down_attempts": 0,
        "third_down_conversions": 0,
        "time_of_possession": 0,
        "kick_returns": 0,
        "punt_returns": 0,
        "field_goal_attempts": 0,
        "extra_point_attempts": 0,
        "extra_points_made": 0,
        "safeties": 0,
        "turnovers_on_downs": 0,
        "clock_expired_drives": 0,
        "kickoffs": 0,
        "drives": 0,
        "players": empty_player_stats(players),
    }


CLOCK_REASON = {1: "end_of_half", 2: "end_of_game", "OT": "end_of_overtime"}
# Kernel 2014.3 Pro Bowl (library/2013_super_bowl_mvp_and_pro_bowl_procedure.md
# section 3; branch readings in career/2013/pro_bowl/method.json): no kickoffs,
# the ball at the 25 to start every quarter and after every score, and a
# possession that ends when any quarter ends.
PRO_BOWL = "pro_bowl"
PRO_BOWL_SPOT = 75
QUARTER_REASON = {1: "end_of_quarter", 2: "end_of_half", 3: "end_of_quarter", 4: "end_of_game"}
SCORE_KIND = {"touchdown": "touchdown", "field_goal_attempt": "field_goal", "safety": "safety"}
# Kernel 2014.4 phase 2: resample attempts for a drive with no legal layout.
LAYOUT_RESAMPLE_LIMIT = 8
LEGACY_OUTCOME = {
    "touchdown": "touchdown", "field_goal_attempt": "field_goal", "punt": "punt",
    "interception": "turnover", "fumble_lost": "turnover", "downs": "downs",
    "safety": "safety",
}


# ---- Kernel 2014.4 E2: in-game removal, consequential substitutions, pause.
# A player whose removal needs the controlling coach (E2 "important
# substitution"): a quarterback, the designated caller, a featured role, or a
# removal that changes the legal package. Anything else follows the club's
# depth order (the approved contingency).
CALLER_ROLES = frozenset({"caller", "play_caller", "signal_caller", "designated_caller",
                          "defensive_caller", "green_dot"})
# Specialists' emergency replacements, in order (the punter kicks, the kicker
# punts, a lineman snaps).
SPECIALIST_SPARES = {"K": ("P",), "P": ("K",), "LS": ("OL",)}


def _featured(team):
    """Player ids the TeamInput rotation plan marks as featured, if any.

    Accepted entries: {"player"|"player_id": id, "featured": true} or with
    "role"/"status" "featured". Other entries are ignored."""
    ids = set()
    for entry in getattr(team, "rotation_plan", ()) or ():
        if isinstance(entry, dict):
            pid = entry.get("player_id", entry.get("player"))
            if pid and (entry.get("featured") is True or "featured" in (entry.get("role"), entry.get("status"))):
                ids.add(pid)
    return ids


class _Paused(Exception):
    def __init__(self, partial):
        super().__init__("paused for a consequential substitution")
        self.partial = partial


def _partial_result(event_id, game_type, opening_receiver, stats, possessions, kickoffs,
                    play_ledger, injuries, substitutions, history, pause, kernel_version=KERNEL_VERSION):
    """E2 step 4: completed events only. No final score, no team or player
    totals, no later draw; the continuation token binds a decision to it."""
    snapshot = json.loads(json.dumps({
        "possessions": possessions, "kickoffs": kickoffs, "play_ledger": play_ledger,
        "injuries": injuries, "substitutions": substitutions, "history": history, "pause": pause,
    }, default=str))
    return {
        "kernel_version": kernel_version,
        "event_id": event_id,
        "game_type": game_type,
        "opening_receiver": opening_receiver,
        "score": {tid: s["points"] for tid, s in stats.items()},
        "possessions": snapshot["possessions"],
        "kickoffs": snapshot["kickoffs"],
        "play_ledger": snapshot["play_ledger"],
        "injuries": snapshot["injuries"],
        "substitutions": snapshot["substitutions"],
        "pauses": snapshot["history"] + [snapshot["pause"]],
        "paused": True,
        "terminated": False,
    }


def resolve_game(home, away, *, seed, event_id, venue="home", weather="normal", game_type="regular",
                 management_mode="autonomous", controlled_team=None, continuation=None, game_date=None,
                 _test_onsets=None, _test_profile=None, _test_strength_receipt=None, _test_scoring=None):
    """Resolve one game, or return a genuine partial result at an E2 pause.

    Kernel 2014.4 (E2): ``management_mode="user_controlled"`` with a
    ``controlled_team`` stops before the next event after a consequential
    in-game removal on that club and returns a partial result (no final
    score, no later draws). ``continuation={"decisions": [...]}`` resumes it:
    the game is re-run from the same seed, so the prefix and the frozen injury
    reproduce exactly, and each decision is checked against the digest of the
    partial state it answers. ``_test_onsets`` forces onsets for tests only;
    the production runner (runtime/game_runner.run_game) cannot pass it.

    ``game_date`` (ISO date) is read only for ``game_type="preseason"``,
    where runtime.rules.extra_point_rule decides the try (the 2014 preseason
    Weeks 1-2 experiment). It is omitted from the outcome packet when None,
    so every regular-season and postseason packet and draw is unchanged.

    Kernel 2014.6 plumbing (batch B1): the game resolves with the frozen
    Profile of runtime.KERNEL_VERSION (runtime.profiles), whose calibration
    base is bound once here. ``_test_profile`` resolves with another Profile
    (tests and acceptance scripts only); the production runner cannot pass
    it (runtime.game_runner.architecture_errors).

    Kernel 2014.6 (batch B7): under the player-state strength model the
    result carries no per-possession strength block (the drawn values are
    hidden). ``_test_strength_receipt``, a list, receives each drive's
    receipt for tests and acceptance scripts only.

    Kernel 2014.6 (batch B8): ``_test_scoring`` forces a sequencing branch
    (a kick the kicking club keeps, a kick returned for a touchdown, a
    defensive touchdown) for tests only, under a profile holding
    possession_sequencing; the production runner cannot pass it.
    """
    if _test_profile is not None and not isinstance(_test_profile, Profile):
        raise TypeError("_test_profile must be a runtime.profiles.Profile")
    profile = _test_profile if _test_profile is not None else installed_profile()
    if _test_strength_receipt is not None and not isinstance(_test_strength_receipt, list):
        raise TypeError("_test_strength_receipt must be a list")
    try:
        return _resolve_game(home, away, seed=seed, event_id=event_id, venue=venue, weather=weather,
                             game_type=game_type, management_mode=management_mode,
                             controlled_team=controlled_team, continuation=continuation,
                             game_date=game_date, _test_onsets=_test_onsets, profile=profile,
                             _test_strength_receipt=_test_strength_receipt, _test_scoring=_test_scoring)
    except _Paused as paused:
        return paused.partial


def _resolve_game(
    home,
    away,
    *,
    seed,
    event_id,
    venue="home",
    weather="normal",
    game_type="regular",
    management_mode="autonomous",
    controlled_team=None,
    continuation=None,
    game_date=None,
    _test_onsets=None,
    profile,
    _test_strength_receipt=None,
    _test_scoring=None,
):
    if not isinstance(seed, bytes) or len(seed) < 32:
        raise ValueError("private seed required")
    if game_type not in GAME_TYPES:
        raise ValueError("unknown game type")
    # The try rule is fixed before the first draw; None keeps the fixed rate
    # (runtime.rules.try_rule, the 2015 seam; through 2014 its extra-point
    # rule is extra_point_rule's).
    xp_rule = try_rule(game_type, game_date)["extra_point"]
    if management_mode not in ("autonomous", "user_controlled"):
        raise ValueError("unknown management mode")
    if management_mode == "user_controlled" and controlled_team not in (home.team_id, away.team_id):
        raise ValueError("user-controlled management requires the controlled club's team_id")
    if continuation is not None and management_mode != "user_controlled":
        raise ValueError("a continuation applies only to a user-controlled game")
    if continuation is not None and not (isinstance(continuation, dict)
                                         and isinstance(continuation.get("decisions", []), list)):
        raise ValueError("continuation must be an object with a decisions list")
    decisions = list((continuation or {}).get("decisions", []))

    home_players, away_players = normalize_players(home), normalize_players(away)
    if not home_players or not away_players:
        raise ValueError("active participants required")

    home_outcome = _outcome_team(home)
    away_outcome = _outcome_team(away)
    home_outcome["offensive_call_sheet"] = canonical_call_sheet(home)
    away_outcome["offensive_call_sheet"] = canonical_call_sheet(away)
    packet = {
        "event_id": event_id,
        "home": home_outcome,
        "away": away_outcome,
        "venue": venue,
        "weather": weather,
        "game_type": game_type,
    }
    if game_date is not None:
        packet["game_date"] = game_date
    rng = _rng(seed, packet)
    packet_digest = hashlib.sha256(
        json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    # Kernel 2014.6 plumbing (batch B1): the profile's calibration base is
    # bound once per game. Its sha256 pins and partition counts are verified
    # (once per base object) before any of its data is used, and an invalid
    # aggregate or usage baseline raises CalibrationBaseError (formerly an
    # assert, which python -O would skip).
    cbase = profile.calibration_base()
    cbase.require()
    cal = cbase.aggregate()
    # Kernel 2014.6 (batch B5): usage shares (credit only) and the injury
    # block come from the bound base under usage_2014_6 and injury_2014_6,
    # else from the 2012 base (every kernel up to 2014.5 is bound to it).
    ubase = profile.usage_base(cbase)
    # The chain layout's run-value shapes (the negative-run rate and loss
    # distribution) are a yardage rule, not a credit share: they stay the
    # 2012 base's until R16 owns the yard split (batch B13), so the usage
    # block changes credit only. Kernels up to 2014.5 read their own base.
    usage_values = (cbase if cbase.legacy_2012() else calibration_base.BASE_2012).usage()["values"]
    dm = cbase.drive_model()
    fpm = cbase.field_position()
    injury_params = profile.injury_base(cbase).injury_parameters()
    strength_params = unit_strength.parameters(profile.strength)
    # Kernel 2014.6 (B7): a profile on the player-state model resolves only
    # records of that model, and only with every drawable player's latent
    # value present (fails closed); a profile on honours-production-v3 never
    # reads a player-state record.
    hidden_strength = strength_params.model == unit_strength.PLAYER_STATE_MODEL
    for team in (home, away):
        if team.strength and team.strength.get("model") != strength_params.model:
            raise ValueError("%s strength record is model %s; profile %s resolves %s"
                             % (team.team_id, team.strength.get("model"), profile.kernel_version,
                                strength_params.model))
        missing = player_state.latent_errors(team.strength)
        if missing:
            raise ValueError("%s player-state record cannot resolve: %s" % (team.team_id, "; ".join(missing[:5])))
    # The base's yardage numbers (runtime.calibration.kernel_rates; the 2012
    # schema keeps its exact expressions). The per-play penalty counter stays
    # the 2012 base's factor until R11 owns it (batch B11).
    rates = calibration.kernel_rates(cal, None if cbase.legacy_2012() else calibration_base.BASE_2012.aggregate())
    yards_per_attempt = rates["yards_per_attempt"]
    yards_per_carry = rates["yards_per_carry"]
    completion_rate = rates["completion_rate"]
    penalty_per_play = rates["penalty_per_play"]
    xp_rate = dm.rate("extra_point")
    regimes_v3 = profile.has("regimes_v3")
    # Kernel 2014.6 batch B6: the drive-internal record mechanisms, each by
    # its profile flag (runtime.profiles), each needing a schema-3 base for
    # its constants (fails closed on the 2012 base).
    early_fg_v2 = profile.has("early_fg_v2")
    clock_detail = profile.has("clock_detail_v1")
    substitution_record = profile.has("substitution_record")
    if (early_fg_v2 or clock_detail) and not hasattr(fpm, "early_fg_ok"):
        raise ValueError("profile %s holds a batch B6 flag on a base without the W3/W5a constants"
                         % profile.kernel_version)
    # Kernel 2014.6 batch B8: possession sequencing and its append-only
    # records; the test-only hook needs it (fails closed otherwise).
    sequencing = profile.has("possession_sequencing")
    # Kernel 2014.6 batch B9: the scoring decisions (R8 two-point tries, R15
    # defensive and return touchdowns, R9 onside kicks), each by its flag,
    # each on the possession sequencing and the base's scoring artifact
    # (fails closed otherwise). The Pro Bowl takes none of the try or kick
    # branches (no kickoffs; the try stays the kick); R15's turnover, punt
    # and field-goal returns apply in every game type.
    try_v1 = profile.has("two_point_tries")
    returns_v1 = profile.has("return_touchdowns")
    onside_v1 = profile.has("onside_kicks")
    scoring_on = try_v1 or returns_v1 or onside_v1
    if scoring_on and not sequencing:
        raise ValueError("profile %s holds a batch B9 scoring flag without possession_sequencing"
                         % profile.kernel_version)
    smodel = cbase.scoring() if scoring_on else None
    forced_scoring = _scoring_hook(_test_scoring, sequencing, scoring_on)
    pro_bowl_game = game_type == PRO_BOWL
    # The decision blocks (R8, R9) and U6 (unanswered: the controlled club's
    # two-point and onside decisions come from Stone, a standing rule or
    # delegation on the frozen sheet or a live answer, otherwise: ask) fail
    # closed before any draw; the production runner has already refused the
    # same inputs before journaling the event (decision_block_errors).
    faults = decision_block_errors(home, away, profile=profile, game_type=game_type,
                                   management_mode=management_mode, controlled_team=controlled_team)
    if faults:
        raise ValueError("; ".join(faults))
    policies = {team.team_id: {kind: scoring.canonical_policy(getattr(team, field, None))
                               for field, kind in (("try_policy", "two_point"), ("kickoff_policy", "kickoff"))}
                for team in (home, away)}
    T = fpm.T

    teams = {home.team_id: home, away.team_id: away}
    rosters = {home.team_id: home_players, away.team_id: away_players}
    stats = {t.team_id: _blank_team_stats(rosters[t.team_id]) for t in (home, away)}
    if scoring_on:
        # Batch B9 team counters (append-only; absent from earlier results).
        for line in stats.values():
            for field in SCORING_TEAM_FIELDS:
                line[field] = 0
    # Preseason unit rotation (runtime/rotation.py): a tracker per club, from
    # its plan or the documented default. Any other game type has none, and a
    # rotation block in such a game fails closed before any draw.
    trackers = None
    if game_type == PRESEASON:
        trackers = {}
        for team_id, team in teams.items():
            blocks, plan_errors = rotation.parse(team, rosters[team_id])
            if plan_errors:
                raise ValueError("rotation plan: " + "; ".join(plan_errors))
            trackers[team_id] = rotation.Tracker(team_id, blocks, rosters[team_id])
    else:
        plan_errors = [e for team in (home, away) for e in rotation.plan_errors(team, None, game_type)]
        if plan_errors:
            raise ValueError("rotation plan: " + "; ".join(plan_errors))
    # Kernel 2014.3: the five linemen on the field start the game (credit only).
    for team_id, players in rosters.items():
        opening = players
        if trackers and trackers[team_id].blocks["offense"]:
            opening = rotation.apply(trackers[team_id].blocks["offense"][0], players)[0]
        for lineman in usage.protection_front(opening).values():
            stats[team_id]["players"][lineman.player_id]["line_starts"] += 1
    play_call_stats = {home.team_id: {}, away.team_id: {}}
    evidence = []
    possessions = []
    play_ledger = []
    kickoffs = []
    diagnostics = {"yard_split_count_fallback": 0, "td_split_fitted": 0, "interior_clock_redirected": 0,
                   "sack_losses_fitted": 0, "fallback_need_union": 0, "fallback_clock_tuple": 0,
                   "fallback_zero_tuple": 0, "h2_neutral_into_late": 0, "ot_leading_offense": 0,
                   "prefix_order_repaired": 0, "prefix_order_failed": 0,
                   # Kernel 2014.1: timeout-ladder levels and the end-of-half fit fallback.
                   "timeout_level_0": 0, "timeout_level_1": 0, "timeout_level_2": 0,
                   "timeout_level_3": 0, "h1_fit_fallback": 0, "timeout_tuple_widened": 0,
                   # Kernel 2014.4: no time-feasible first-half final for the
                   # window, a late/overtime fit drive, a zero-play clock
                   # expiry inside the allowance.
                   "h1_final_infeasible": 0, "fallback_fit_drive": 0, "clock_expiry_zero": 0,
                   # Kernel 2014.4 phase 2: a drive whose snaps admitted no legal
                   # chain layout was replaced by another real drive of the same
                   # category and rung (chain_layout_resampled), or none was
                   # available (chain_layout_resample_exhausted).
                   "chain_layout_resampled": 0, "chain_layout_resample_exhausted": 0}
    # Kernel 2014.1: charged timeouts left, per club; reset at each half and
    # at the start of overtime (and every two postseason overtime periods).
    timeouts = {home.team_id: RULES.timeouts_per_half, away.team_id: RULES.timeouts_per_half}
    # Kernel 2014.4 (Tier 1 item 4, E2): the live available roster per club.
    # A removed player leaves it at the end of his injury drive, so every
    # later role (passer, front, skill, defense, returns, coverage, snapper,
    # specialists) is re-derived from the players still available. The
    # passer is chosen per drive; legacy inputs without a QB keep the first
    # available player.
    baseline = {tid: participation.group_counts(players) for tid, players in rosters.items()}
    current = {tid: list(players) for tid, players in rosters.items()}
    original_index = {tid: {p.player_id: i for i, p in enumerate(players)} for tid, players in rosters.items()}
    removed = {}
    vacated = {}
    onset_players = set()
    injuries = []
    substitutions = []
    exposure = {tid: {} for tid in rosters}
    accumulator = {}
    forced = dict(_test_onsets or {})
    pause_state = {"pending": None, "history": []}

    # The last emergency filler of each group per club and side (October 1,
    # 2026): he keeps the job while available (participation.emergency_view).
    fills = {tid: {"offense": {}, "defense": {}} for tid in rosters}

    def lineup(team_id, side, quarter=None, number=None):
        view, notes = participation.emergency_view(current[team_id], baseline[team_id], side,
                                                   prefer=fills[team_id][side])
        fills[team_id][side] = {n["group"]: n["filled_by"] for n in notes if n.get("filled_by")}
        block = None
        if trackers is not None:
            # Preseason: the active rotation block's unit leads the depth order.
            view, block = trackers[team_id].view(side, view, quarter, number)
        return view, notes, block

    def live_rosters():
        return {tid: tuple(players) for tid, players in current.items()}

    def pure_lineup(team_id, players):
        """Batch B6 (W2a): the club's on-field slots from `players` through
        the pure path: emergency_view with the kept fillers (never written
        back), the preseason tracker's current block applied without
        selecting or recording, then participation.slot_lineup. No draw, no
        state change; the kernel's lineup() is never called here."""
        views = {}
        for side in ("offense", "defense"):
            view, notes = participation.emergency_view(players, baseline[team_id], side,
                                                       prefer=fills[team_id][side])
            if trackers is not None:
                tracker = trackers[team_id]
                blocks = tracker.blocks[side]
                if blocks:
                    view, _ = rotation.apply(blocks[tracker.index[side]], view)
                st_blocks = tracker.blocks["special_teams"]
                if st_blocks:
                    specialists = {g: ids for g, ids in st_blocks[tracker.index["special_teams"]]["players"].items()
                                   if g in rotation.SPECIALISTS}
                    if specialists:
                        view, _ = rotation.apply({"players": specialists}, view)
            views[side] = (view, notes)
        off_view, off_notes = views["offense"]
        def_view, def_notes = views["defense"]
        passer = usage.game_passer(off_view) or off_view[0]
        front = usage.protection_front(off_view)
        lineup_now = participation.slot_lineup(off_view, def_view, passer, front)
        kicker = usage.kicking_specialist(players, "K", "placekicker")
        punter = usage.kicking_specialist(players, "P", "punt")
        snapper = usage.long_snapper(players, front)
        return {
            "slots": {side: participation.slot_map(lineup_now, side) for side in ("offense", "defense")},
            "emergency": off_notes + def_notes,
            "specialists": {"K": kicker.player_id if kicker else None, "P": punter.player_id if punter else None,
                            "LS": snapper.player_id if snapper else None},
            "returners": {role: (r.player_id if r else None) for role, r in
                          (("kick_return", usage.club_returner(players, "kick_return")),
                           ("punt_return", usage.club_returner(players, "punt_return")))},
        }

    def substitution_detail(before, after, removed_id):
        """Batch B6 (W2a): the record of one removal from the pure lineups
        before and after it: the entrant (on the field after, not before, on
        the removed player's side; else any side), the vacated and entering
        slots, slot moves (labels only, no shares), the emergency fills after
        the removal and every specialist or returner change."""
        vacated = [{"side": side, "slot": before["slots"][side][removed_id]} for side in ("offense", "defense")
                   if removed_id in before["slots"][side]]
        sides = [v["side"] for v in vacated] or ["offense", "defense"]
        entrant, entering = None, []
        for side in sides:
            new = [pid for pid in after["slots"][side] if pid not in before["slots"][side]]
            for pid in new:
                entering.append({"side": side, "slot": after["slots"][side][pid], "player": pid})
                if entrant is None:
                    entrant = pid
        moves = []
        for side in ("offense", "defense"):
            for pid, slot in after["slots"][side].items():
                was = before["slots"][side].get(pid)
                if was is not None and was != slot:
                    moves.append({"side": side, "player": pid, "from": was, "to": slot})
        specialists = {role: {"from": before["specialists"][role], "to": after["specialists"][role]}
                       for role in before["specialists"] if before["specialists"][role] != after["specialists"][role]}
        returners = {role: {"from": before["returners"][role], "to": after["returners"][role]}
                     for role in before["returners"] if before["returners"][role] != after["returners"][role]}
        return {"entrant": entrant, "vacated_slots": vacated, "entering_slots": entering, "moves": moves,
                "emergency": list(after["emergency"]), "specialists": specialists, "returners": returners}

    # W2a: the pure lineup before each removal, kept so a coach's choice
    # (apply_decision) can recompute the record against the same baseline.
    lineup_before = {}

    def add_exposure(team_id, snaps):
        for pid, count in snaps.items():
            exposure[team_id][pid] = exposure[team_id].get(pid, 0) + count

    def eligible_for(team_id, player):
        """Available replacements for a removed player's place, best first."""
        players = current[team_id]
        grp = usage.group(player.position)
        ordered = list(usage.depth_order(players, grp)) if grp else []
        for spare in SPECIALIST_SPARES.get(grp, ()):
            ordered += usage.depth_order(players, spare)
        if not ordered:
            for source in participation.EMERGENCY_FROM.get(grp, ()):
                ordered += usage.depth_order(players, source)[usage.MINIMUM_GAME_DAY.get(source, 0):]
        if not ordered and grp in ("K", "P", "LS"):
            ordered = list(players)
        seen, out = set(), []
        for p in ordered:
            if p.player_id not in seen:
                seen.add(p.player_id)
                out.append(p.player_id)
        return out

    def consequential(team_id, player, counts_after):
        """E2: why this removal needs the controlling coach, else None."""
        grp = usage.group(player.position)
        tags = set(player.roles) | set(player.responsibilities)
        if grp == "QB":
            return "quarterback"
        if tags & CALLER_ROLES:
            return "designated_caller"
        if "featured" in tags or player.player_id in _featured(teams[team_id]):
            return "featured_role"
        need = min(usage.MINIMUM_GAME_DAY.get(grp, 0), baseline[team_id].get(grp, 0))
        if counts_after.get(grp, 0) < need or (grp in ("K", "P", "LS") and not counts_after.get(grp)):
            return "package_change"
        return None

    def end_of_drive(drive_no, clock, half):
        """Draw this interval's onsets for both clubs, then apply removals."""
        boundary = []
        for team in (home, away):
            tid = team.team_id
            snaps = exposure[tid]
            for player in rosters[tid]:
                pid = player.player_id
                count = snaps.get(pid, 0)
                key = (drive_no, pid)
                if pid in onset_players:
                    if key in forced:
                        raise ValueError("forced onset for a player already injured this game")
                    continue
                stream = _stream(injury_model.ONSET_TAG, seed, event_id, drive_no, tid, pid)
                if key in forced:
                    if count <= 0:
                        raise ValueError("forced onset for a player with no exposure in that interval")
                    spec = dict(forced.pop(key))
                    injury = injury_model.disposition(stream, spec.get("injury_class"), spec.get("severity"),
                                                      params=injury_params)
                    if "removed" in spec:
                        injury["removed"] = bool(spec["removed"]) or injury["injury_class"] == "head_neck"
                else:
                    injury = injury_model.draw(stream, player.position, count, params=injury_params)
                if injury is None:
                    continue
                onset_players.add(pid)
                entry = {"team": tid, "player": pid, **injury, "onset": "end_of_drive",
                         "drive": drive_no, "half": half, "period": clock[0], "clock": clock[1],
                         "snaps_in_interval": count}
                injuries.append(entry)
                boundary.append((tid, player, entry))
            exposure[tid] = {}
        decisions_due = []
        for tid, player, entry in boundary:
            if not entry["removed"]:
                continue
            pid = player.player_id
            grp = usage.group(player.position)
            live = current[tid]
            live_player = next(p for p in live if p.player_id == pid)
            before = usage.depth_order(live, grp) if grp else []
            rank = next((i for i, p in enumerate(before) if p.player_id == pid), None)
            pure_before = pure_lineup(tid, live) if substitution_record else None
            current[tid] = [p for p in live if p.player_id != pid]
            removed[pid] = entry
            vacated[pid] = live_player
            after = usage.depth_order(current[tid], grp) if grp else []
            successor = after[rank].player_id if rank is not None and rank < len(after) else None
            if grp == "OL":
                # The lineman who now completes the protection front.
                seated = {p.player_id for p in usage.protection_front(live).values()}
                entering = [p.player_id for p in usage.protection_front(current[tid]).values()
                            if p.player_id not in seated]
                successor = entering[0] if entering else None
            record = {"drive": drive_no, "team": tid, "removed": pid, "group": grp,
                      "basis": "depth_order", "replacement": successor}
            if substitution_record:
                # Batch B6 (W2a, append-only): several removals at one
                # boundary are applied in sequence, each against the lineup
                # the previous one left.
                lineup_before[(tid, pid)] = pure_before
                record.update(substitution_detail(pure_before, pure_lineup(tid, current[tid]), pid))
            substitutions.append(record)
        if management_mode != "user_controlled":
            return
        counts_after = participation.group_counts(current[controlled_team])
        for tid, player, entry in boundary:
            if tid != controlled_team or not entry["removed"]:
                continue
            reason = consequential(tid, vacated[player.player_id], counts_after)
            if reason:
                eligible = eligible_for(tid, vacated[player.player_id])
                if not eligible:
                    raise participation.NoLegalPersonnel(
                        "no available replacement for %s" % player.player_id)
                decisions_due.append({"slot": player.player_id, "group": usage.group(player.position),
                                      "reason": reason, "eligible": eligible, "default": eligible[0]})
        if not decisions_due:
            return
        score = {tid: stats[tid]["points"] for tid in stats}
        availability = {tid: {"removed": {pid: removed[pid]["restriction"] for pid in removed
                                          if removed[pid]["team"] == tid},
                              "available": [p.player_id for p in current[tid]]} for tid in current}
        pause = {"trigger": "consequential_substitution", "team": controlled_team, "drive": drive_no,
                 "half": half, "period": clock[0], "clock": clock[1], "score": score,
                 "injuries": [dict(e) for _, _, e in boundary], "decisions": decisions_due,
                 "availability": availability}
        pause["continuation_token"] = hashlib.sha256(json.dumps(
            {"packet": packet_digest, "index": len(pause_state["history"]), "pause": pause,
             "possessions": possessions, "kickoffs": kickoffs, "play_ledger": play_ledger,
             "injuries": injuries, "prior": pause_state["history"]},
            sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        pause_state["pending"] = pause

    def apply_decision(pause, decision):
        """E2 step 5: validate the continuation decision, then promote."""
        if not isinstance(decision, dict) or decision.get("token") != pause["continuation_token"]:
            raise ValueError("stale or tampered continuation decision")
        choices = decision.get("choices")
        slots = {d["slot"]: d for d in pause["decisions"]}
        if not isinstance(choices, dict) or set(choices) != set(slots):
            raise ValueError("continuation must choose exactly the pending replacements")
        if len(set(choices.values())) != len(choices):
            raise ValueError("duplicate replacement in continuation")
        for slot, choice in choices.items():
            if choice not in slots[slot]["eligible"]:
                raise ValueError("replacement %r is not an eligible available player" % (choice,))
        tid = pause["team"]
        order = original_index[tid]
        for slot, choice in sorted(choices.items(), key=lambda item: order[item[0]]):
            gone = vacated[slot]
            live = current[tid]
            chosen = next(p for p in live if p.player_id == choice)
            promoted = replace(chosen, position=gone.position, depth=gone.depth,
                               rotation_status=gone.rotation_status)
            rest = [p for p in live if p.player_id != choice]
            at = next((i for i, p in enumerate(rest) if order[p.player_id] > order[slot]), len(rest))
            current[tid] = rest[:at] + [promoted] + rest[at:]
            for sub in substitutions:
                if sub["removed"] == slot and sub["team"] == tid:
                    sub.update({"basis": "coach_choice", "replacement": choice})
                    if substitution_record and (tid, slot) in lineup_before:
                        # W2a: the record recomputed after the coach's choice.
                        sub.update(substitution_detail(lineup_before[(tid, slot)], pure_lineup(tid, current[tid]),
                                                       slot))
        pause_state["history"].append({"drive": pause["drive"], "team": tid,
                                       "continuation_token": pause["continuation_token"],
                                       "choices": dict(choices)})

    def checkpoint():
        """Before the next event: apply the pending decision or pause."""
        pause = pause_state["pending"]
        if pause is None:
            return
        index = len(pause_state["history"])
        if index < len(decisions):
            apply_decision(pause, decisions[index])
            pause_state["pending"] = None
            return
        raise _Paused(_partial_result(event_id, game_type, opening_receiver, stats, possessions, kickoffs,
                                      play_ledger, injuries, substitutions, pause_state["history"], pause,
                                      kernel_version=profile.kernel_version))

    def other(team_id):
        return away.team_id if team_id == home.team_id else home.team_id

    ot_half = [0]

    def _reset_postseason_ot_timeouts(window):
        """Postseason overtime: periods 1-2, 3-4, ... are halves; each club
        gets three timeouts at the start of each such half (labelled
        inference, library/2013_nfl_playing_rules_for_simulation.md R6)."""
        total = RULES.postseason_ot_period_bound * RULES.postseason_ot_seconds
        elapsed = total - window
        half_index = int(elapsed // (2 * RULES.postseason_ot_seconds))
        if half_index != ot_half[0]:
            ot_half[0] = half_index
            for team_id in timeouts:
                timeouts[team_id] = RULES.postseason_ot_timeouts_per_half

    def append_rows(rows):
        for row in rows:
            row["sequence"] = len(play_ledger) + 1
            play_ledger.append(row)

    def try_after(scorer_id, line, available, *, walk_off, u=None):
        """The try after a non-offensive touchdown (R8 placeholder: the
        ordinary extra point on the fixed rate, or the dated 2014 preseason
        rule; one draw, the same as a drive's try). Returns xp_made (None for
        a walk-off touchdown, which has no try). Batch B9: ``u`` (the keyed
        try substream's result uniform) replaces the possession-stream draw
        in the Pro Bowl, which takes no try decision."""
        if walk_off:
            return None
        line["extra_point_attempts"] += 1
        xp_prob = xp_rate
        if xp_rule is not None and xp_rule.get("distance"):
            # 2014 preseason Weeks 1-2: the try is a 33-yard kick on
            # the field-goal distance model, with the kicker's own
            # term as for any field goal. Same single draw.
            xp_prob = dm.fg_make_prob_at(xp_rule["distance"])
            scorer = teams[scorer_id]
            if scorer.strength:
                kicker = usage.kicking_specialist(available, "K", "placekicker")
                kick_shift, _ = unit_strength.kicker_adjustment(scorer.strength, kicker, params=strength_params)
                xp_prob = min(strength_params.fg_prob_ceiling,
                              max(strength_params.fg_prob_floor, xp_prob + kick_shift))
        xp_made = (rng.random() if u is None else u) < xp_prob
        if xp_made:
            line["extra_points_made"] += 1
        return xp_made

    # ---- Kernel 2014.6 batch B9: scoring decisions ------------------------------------------

    def coach_choice(trigger, team_id, slot, eligible, info):
        """A live decision of the controlling coach (a policy's ``otherwise:
        ask``; U6), through the E2 pause machinery: the game returns a
        genuine partial result (completed events only) with the decision
        ``slot``, its ``eligible`` answers and only the public situation
        (``info``: clock, score, margin; never a probability); the
        continuation's answer is checked against the digest of that state.
        Any other club, or autonomous mode, fails closed: such an ask is
        refused before any draw (decision_block_errors) and here again."""
        if management_mode != "user_controlled" or team_id != controlled_team:
            raise ValueError("%s asks for a live %s decision; only the controlling coach's club in a "
                             "user-controlled game can answer one" % (team_id, trigger))
        index = len(pause_state["history"])
        pause = {"trigger": trigger, "team": team_id, **info,
                 "decisions": [{"slot": slot, "eligible": list(eligible)}]}
        pause["continuation_token"] = hashlib.sha256(json.dumps(
            {"packet": packet_digest, "index": index, "pause": pause,
             "possessions": possessions, "kickoffs": kickoffs, "play_ledger": play_ledger,
             "injuries": injuries, "prior": pause_state["history"]},
            sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        if index < len(decisions):
            decision = decisions[index]
            if not isinstance(decision, dict) or decision.get("token") != pause["continuation_token"]:
                raise ValueError("stale or tampered continuation decision")
            choices = decision.get("choices")
            if not isinstance(choices, dict) or set(choices) != {slot} or choices[slot] not in eligible:
                raise ValueError("continuation must answer %s with one of %s" % (slot, ", ".join(eligible)))
            pause_state["history"].append({"trigger": trigger, "drive": info.get("drive"), "team": team_id,
                                           "continuation_token": pause["continuation_token"],
                                           "choices": dict(choices)})
            return choices[slot]
        raise _Paused(_partial_result(event_id, game_type, opening_receiver, stats, possessions, kickoffs,
                                      play_ledger, injuries, substitutions, pause_state["history"], pause,
                                      kernel_version=profile.kernel_version))

    def side_view(team_id, side, quarter=None):
        """A club's side as it lines up now, by the pure path (no filler
        written back, a preseason block viewed with record=False): the
        scorer's offense and the other club's defense on a try after a
        non-offensive or return touchdown."""
        view, _notes = participation.emergency_view(current[team_id], baseline[team_id], side,
                                                    prefer=fills[team_id][side])
        if trackers is not None:
            view, _ = trackers[team_id].view(side, view, quarter, len(possessions) + 1, record=False)
        return view

    def kick_try_prob(scorer_id, view):
        """The extra point's probability: the base's rate, or in the dated
        2014 preseason window the 33-yard kick with the kicker's term."""
        prob = xp_rate
        if xp_rule is not None and xp_rule.get("distance"):
            prob = dm.fg_make_prob_at(xp_rule["distance"])
            if teams[scorer_id].strength:
                kicker = usage.kicking_specialist(view, "K", "placekicker")
                shift, _ = unit_strength.kicker_adjustment(teams[scorer_id].strength, kicker, params=strength_params)
                prob = min(strength_params.fg_prob_ceiling, max(strength_params.fg_prob_floor, prob + shift))
        return prob

    def resolve_try(scorer_id, *, anchor, at, view, edge=0.0, result_rng=None):
        """R8: one try's decision and result. The decision uniform is drawn on
        the keyed scoring-try-v1 substream (event and anchor; no team id) in
        every case, so a policy never shifts a later draw. The scorer's
        policy rule decides (policy:i), its delegation or the league chart
        cell of the try row's own stamp and the margin after the touchdown
        (delegated:league, league), or the controlling coach live. The
        result uniform is ``result_rng``'s next draw (an offensive
        touchdown's: the possession stream at the extra point's position)
        or the substream's second uniform (a non-offensive touchdown's).
        Counts the club's attempt; returns the try record."""
        opponent = other(scorer_id)
        key = ("drive", anchor["drive"]) if "drive" in anchor else ("kick", anchor["kick"])
        stream = _stream(scoring.TRY_TAG, seed, event_id, *key)
        u_dec, u_res = stream.random(), stream.random()
        seconds = scoring.try_seconds(at["period"], at["game_clock"])
        diff = stats[scorer_id]["points"] + 6 - stats[opponent]["points"]
        cell = smodel.try_cell(seconds, diff)
        pair = smodel.p_go(cell)
        state = {"period": at["period"], "diff": diff, "seconds": seconds}
        decision, basis = scoring.decide(policies[scorer_id]["two_point"], "two_point", state, u_dec, pair)
        forced = forced_scoring["tries"].get("%s:%s" % key, {})
        if "decision" in forced:
            decision = forced["decision"]
        if decision is None:
            score = {tid: stats[tid]["points"] for tid in stats}
            score[scorer_id] += 6
            decision = coach_choice("two_point", scorer_id, "try", scoring.TRY_DECISIONS,
                                    {"drive": at["drive"], "anchor": dict(anchor), "period": at["period"],
                                     "clock": at["game_clock"], "score": score,
                                     "situation": {"margin_after_touchdown": diff}})
        u = result_rng.random() if result_rng is not None else u_res
        line = stats[scorer_id]
        if decision == "kick":
            made = u < kick_try_prob(scorer_id, view)
        else:
            made = u < smodel.two_point_success(edge)
        if "made" in forced:
            made = bool(forced["made"])
        if decision == "kick":
            line["extra_point_attempts"] += 1
            line["extra_points_made"] += int(made)
            points = int(made)
        else:
            line["two_point_attempts"] += 1
            line["two_point_conversions"] += int(made)
            points = 2 * int(made)
        return {"decision": decision, "basis": basis, "cell": cell, "p_go": list(pair), "made": made,
                "points": points, "type": "kick" if decision == "kick" else None}

    def try_rows(record, scorer_id, *, anchor, at, off_view, def_view, passer=None):
        """The try's ledger row after a non-offensive or return touchdown (or
        an offensive touchdown's two-point row): an anchored extra_point row
        (play_detail.try_row) or a two_point row (play_detail.two_point_row,
        credit on its own keyed stream). A two-point snap credits one
        offensive and one defensive slot-lineup snap
        (participation.try_snap) and joins the next injury draw's exposure;
        an extra point's unit is credited by the caller from the row's own
        offense."""
        opponent = other(scorer_id)
        if record["decision"] == "kick":
            return try_row(at, scoring=teams[scorer_id], opponent=opponent, available=off_view, stats=stats,
                           made=record["made"], seed=seed, event_id=event_id, anchor=anchor, decision=record)
        passer = passer or usage.game_passer(off_view) or off_view[0]
        row = two_point_row(at, scoring=teams[scorer_id], opponent=opponent, available=off_view, stats=stats,
                            made=record["made"], seed=seed, event_id=event_id, anchor=anchor, passer=passer,
                            decision=record, pass_share=smodel.pass_share, usage_base=ubase)
        record["type"] = row["try_type"]
        hazard = {}
        snaps = participation.try_snap(accumulator, scorer_id, opponent, off_view, def_view, passer,
                                       usage.protection_front(off_view), row, hazard_out=hazard)
        participation.credit(stats, scorer_id, snaps[scorer_id], "offense")
        participation.credit(stats, opponent, snaps[opponent], "defense")
        for tid in (scorer_id, opponent):
            add_exposure(tid, hazard[tid])
        return row

    def kick(kicking, receiving, *, free_kick, half, remaining, ot_label="OT", chain=1, after_drive=None):
        """One real kickoff (or safety free kick) record: one randrange.

        Kernel 2014.6 batch B8 (under possession_sequencing): the record also
        carries its chain position, the possession it followed, its basis and
        the scoring fields; a forced test branch may make it a kick the
        kicking club keeps or a return touchdown.

        Kernel 2014.6 batch B9: in a fixed order on the keyed
        scoring-kick-v1 substream (event and kick number; no team id; two
        uniforms always drawn): the onside decision (R9; a kickoff from the
        35 only, never a free kick), then for an onside kick its recovery (the
        expected or surprise rate) and a real onside record of the recovering
        side, else the deep kick's return-touchdown test (R15) and a real
        return record. The base pool draw is taken first in every case and
        discarded when a branch replaces it."""
        def kick_returner_value(number):
            """The returner socket's input on a deep kick: the receiving
            club's kick returner's tier value (the existing returner term's),
            from the live roster through the preseason tracker's current block
            without recording it; 0 without a strength record. No draw."""
            strength = teams[receiving].strength
            if not strength:
                return 0.0
            players = live_rosters()[receiving]
            if trackers is not None:
                players = trackers[receiving].view("special_teams", players,
                                                   rotation.quarter_of_remaining(remaining, half == "OT"),
                                                   number, record=False)[0]
            return unit_strength.returner_adjustment(strength, usage.club_returner(players, "kick_return"), "KR",
                                                     params=strength_params)[1]["value"]

        checkpoint()
        kick_no = len(kickoffs) + 1
        drawn = fpm.free_kick(rng) if free_kick else fpm.kickoff(rng)
        branch = forced_scoring["kicks"].get(kick_no)
        onside = None
        b9_touchdown = False
        if scoring_on and not pro_bowl_game:
            ks = _stream(scoring.KICK_TAG, seed, event_id, kick_no)
            u0, u1 = ks.random(), ks.random()
            margin = stats[kicking]["points"] - stats[receiving]["points"]
            overtime = half == "OT"
            opening = chain == 1 and after_drive is None
            period = None if overtime else (4 if half == 2 and remaining <= RULES.quarter_seconds else
                                            _period_clock(remaining)[0])
            if onside_v1 and not free_kick:
                cell = smodel.onside_cell(seconds_left=remaining, period=period, overtime=overtime, opening=opening,
                                          diff=margin)
                pair = smodel.p_onside(cell)
                state = {"period": "OT" if overtime else period, "diff": margin, "seconds": remaining,
                         "opening": opening}
                decision, basis = scoring.decide(policies[kicking]["kickoff"], "kickoff", state, u0, pair)
                if branch in ("onside_recovered", "onside_lost"):
                    decision = "onside"
                if decision is None:
                    score = {tid: stats[tid]["points"] for tid in stats}
                    decision = coach_choice("onside", kicking, "kickoff", scoring.KICKOFF_DECISIONS,
                                            {"drive": len(possessions) + 1, "kick": kick_no, "half": half,
                                             "period": "OT" if overtime else period,
                                             "clock": _period_clock(remaining, overtime=ot_label if overtime else False)[1],
                                             "score": score, "situation": {"margin": margin, "opening_kick": opening}})
                onside = {"onside": decision == "onside", "cell": cell, "p_onside": list(pair), "basis": basis}
            if onside and onside["onside"]:
                label = smodel.recovery_class(seconds_left=remaining, period=period, overtime=overtime, diff=margin)
                # The onside kicking and hands unit sockets (slope 0) have no
                # input: strength v4 defines no special-teams unit composite,
                # so both read 0 until one is specified (runtime/README.md).
                p_recover = smodel.p_recover(label, kicking_unit=0.0, hands_unit=0.0)
                recovered = u1 < p_recover
                if branch in ("onside_recovered", "onside_lost"):
                    recovered = branch == "onside_recovered"
                side = "kicking" if recovered else "receiving"
                pool = smodel.spot_records[side]
                r = pool[ks.randrange(len(pool))]
                drawn = {"touchback": False, "next_start": int(r["next_start"]), "kick_yards": int(r["kick_yards"]),
                         "return_yards": int(r["return_yards"]), "enforcement": int(r["enforcement"]),
                         "outcome": scoring.ONSIDE_RECOVERED if recovered else scoring.ONSIDE_LOST, "kick_spot": 35}
                onside.update(recovery_class=label, p_recover=[smodel.recovery[label][0], smodel.recovery[label][1]])
            elif returns_v1 and not free_kick and (u1 < smodel.p_return(smodel.kickoff,
                                                                        returner=kick_returner_value(kick_no))
                                                   or branch == "touchdown"):
                # R15: a deep kick from the 35 returned for a touchdown, on a
                # real record (kick yards and the return from the receiving
                # club's goal line, 35 + kick yards).
                records = smodel.records["kickoff_return_td"]
                r = records[ks.randrange(len(records))]
                drawn = dict(drawn, touchback=False, outcome="returned_touchdown", kick_yards=int(r["kick_yards"]),
                             return_yards=int(r["return_yards"]), enforcement=0, next_start=None)
                b9_touchdown = True
        if branch == "retained":
            # The base draw is taken and discarded; a real retained record of
            # the kick kind stands in (the first in the artifact's list).
            pool = fpm.data["retained_kick_pools"]["free_kick" if free_kick else "kickoff"]
            if not pool:
                raise ValueError("no retained %s record in the base" % ("free kick" if free_kick else "kickoff"))
            K = fpm.KICK
            r = pool[0]
            drawn = {"touchback": False, "next_start": r[K["next_start"]], "kick_yards": r[K["kick_yards"]],
                     "return_yards": r[K["return_yards"]], "enforcement": r[K["enforcement"]],
                     "outcome": "retained", "kick_spot": 20 if free_kick else 35}
        elif branch == "touchdown" and not b9_touchdown:
            # The drawn kick is run back to the goal line (R15 placeholder).
            spot = 20 if free_kick else 35
            drawn = dict(drawn, touchback=False, outcome="returned_touchdown",
                         return_yards=max(0, 100 - spot - int(drawn["kick_yards"] or 0)), next_start=None)
        retained = drawn["outcome"] == "retained"
        touchdown = drawn["outcome"] == "returned_touchdown"
        onside_kick = drawn["outcome"] in (scoring.ONSIDE_RECOVERED, scoring.ONSIDE_LOST)
        live = live_rosters()
        kick_quarter = None
        if trackers is not None:
            # Preseason: each club's special-teams block (or depth order).
            kick_quarter = rotation.quarter_of_remaining(remaining, half == "OT")
            live = {tid: trackers[tid].view("special_teams", live[tid], kick_quarter, kick_no)[0]
                    for tid in (kicking, receiving)}
        if teams[receiving].strength and not drawn["touchback"] and not (retained or touchdown or onside_kick):
            # Kernel 2014.4 phase 2: the returner's term (slope 0 in this
            # candidate); no draw is consumed. Batch B9: an onside kick has
            # no returner term.
            returner = usage.club_returner(live[receiving], "kick_return")
            ret_shift, ret_receipt = unit_strength.returner_adjustment(teams[receiving].strength, returner, "KR",
                                                                       params=strength_params)
            drawn = fpm.adjust_return(drawn, ret_shift)
            drawn["returner"] = ret_receipt
        returned = not drawn["touchback"] and not retained and not onside_kick
        stats[kicking]["kickoffs"] += 1
        if returned:
            stats[receiving]["kick_returns"] += 1
        record = {
            "kick_no": kick_no, "kicking": kicking, "receiving": receiving,
            "returned": returned, "free_kick": free_kick, "half": half,
            "drive": len(possessions) + 1,
            "next_start": drawn["next_start"], "touchback": drawn["touchback"],
            "kick_yards": drawn["kick_yards"], "return_yards": drawn["return_yards"],
            "enforcement": drawn["enforcement"], "outcome": drawn["outcome"],
        }
        if "return_adjust" in drawn:
            record["return_adjust"] = drawn["return_adjust"]
            record["returner_term"] = drawn.get("returner")
        xp_made = None
        try_record = None
        if sequencing:
            # Batch B8 (append-only): the kick's place in its chain, the
            # possession it followed, the decision basis (a league draw; a
            # policy basis arrives with R9) and the scoring fields.
            record.update(remaining=remaining, chain=chain, after_drive=after_drive, basis="league",
                          touchdown=touchdown, scoring_team=receiving if touchdown else None)
            if onside is not None:
                # Batch B9 (R9, append-only): the onside decision, its basis,
                # the chart cell and its onside/kicks pair, and for an onside
                # kick the recovery class and its recovered/kicks pair.
                record["basis"] = onside["basis"]
                record.update({k: v for k, v in onside.items() if k != "basis"})
                if onside_kick:
                    stats[kicking]["onside_kicks"] += 1
                    stats[kicking]["onside_recoveries"] += int(drawn["outcome"] == scoring.ONSIDE_RECOVERED)
            if touchdown:
                line = stats[receiving]
                line["touchdowns"] += 1
                if scoring_on:
                    line["special_teams_touchdowns"] += 1
                walk_off = half == "OT" and ot_status(
                    ot_history(possessions, kickoffs + [record]), game_type) == "end"
                if try_v1:
                    if not walk_off:
                        at = {"drive": record["drive"], "period": _period_clock(remaining)[0],
                              "game_clock": _period_clock(remaining)[1]}
                        try_record = resolve_try(receiving, anchor={"kick": kick_no}, at=at, view=live[receiving])
                        xp_made = try_record["made"] if try_record["decision"] == "kick" else None
                        record["try"] = try_record
                    record["xp_made"] = xp_made
                    record["points"] = 6 + (try_record["points"] if try_record else 0)
                else:
                    xp_made = try_after(receiving, line, live[receiving], walk_off=walk_off)
                    record["xp_made"] = xp_made
                    record["points"] = 6 + (1 if xp_made else 0)
                line["points"] += record["points"]
        kickoffs.append(record)
        rows = apply_kickoff_detail(
            seed=seed, event_id=event_id, kick_no=kick_no,
            kicking=teams[kicking], receiving=teams[receiving], rosters=live,
            stats=stats, returned=returned, free_kick=free_kick,
            remaining=remaining, overtime=ot_label if half == "OT" else False, drive=record["drive"],
            record=record,
        )
        if retained:
            # The receiving club lost the ball to the kicking club (R12 layer
            # C / R9 own the credit); the row says so, no returner is credited.
            rows[0].update(touchback=False, turnover=True, outcome="retained", next_start=drawn["next_start"])
        if onside_kick:
            # Batch B9 (R9): an onside kick; the recovering player is named
            # evenly from the recovering club's kick unit on a keyed
            # kickoff-detail substream (a credit-only convention, never
            # player evidence: attribution group_draw). No return and no
            # returner term on a kicking-club recovery.
            recovering = kicking if drawn["outcome"] == scoring.ONSIDE_RECOVERED else receiving
            rows[0].update(touchback=False, outcome=drawn["outcome"], next_start=drawn["next_start"], onside=True)
            unit = participation.kick(rows[0], kicking, receiving, live[kicking], live[receiving])[recovering]
            if unit:
                pick = _stream(KICKOFF_DETAIL_TAG, seed, event_id, kick_no, "onside")
                rows[0]["recovered_by"] = unit[pick.randrange(len(unit))]
                rows[0]["attribution"] = scoring.GROUP_DRAW
        if touchdown:
            rows[0]["touchdown"] = True
            rows[0]["scoring_team"] = receiving
            if scoring_on and rows[0].get("returner"):
                line = stats[receiving]["players"].get(rows[0]["returner"])
                if line is not None:
                    line["kick_return_touchdowns"] = line.get("kick_return_touchdowns", 0) + 1
            if try_record is not None:
                at = {"drive": record["drive"], "period": rows[0]["period"], "game_clock": rows[0]["game_clock"]}
                quarter = rotation.quarter_of_remaining(remaining, False) if trackers is not None else None
                off = live[receiving] if try_record["decision"] == "kick" else side_view(receiving, "offense", quarter)
                rows.append(try_rows(try_record, receiving, anchor={"kick": kick_no}, at=at, off_view=off,
                                     def_view=side_view(kicking, "defense", quarter)))
            elif xp_made is not None:
                rows.append(try_row(rows[0], scoring=teams[receiving], opponent=kicking, available=live[receiving],
                                    stats=stats, made=xp_made, seed=seed, event_id=event_id,
                                    anchor={"kick": kick_no}))
        append_rows(rows)
        # Kernel 2014.4: the kick's units join the next drive's exposure.
        # Batch B9: each row's units by its own offense (a try row after a
        # return touchdown is the scorer's unit).
        views = {kicking: live[kicking], receiving: live[receiving]}
        for row in rows:
            if row.get("play_type") in participation.KICK_TYPES:
                kicking_id, receiving_id = (row["offense"], row["defense"]) if scoring_on else (kicking, receiving)
                units = participation.kick(row, kicking_id, receiving_id, views[kicking_id], views[receiving_id])
                for team_id, ids in units.items():
                    add_exposure(team_id, participation.credit(stats, team_id, dict.fromkeys(ids, 1),
                                                               "special_teams"))
        if trackers is not None:
            for tid in (kicking, receiving):
                trackers[tid].kicked(kick_quarter)
        return record

    def possess(offense, window, half, spot, start_kind, ot_history=None, ot_label="OT", quarter=None):
        checkpoint()
        team = teams[offense]
        # Pro Bowl quarters are their own windows: the first three draw as a
        # first-half window ending the possession, the fourth as the second
        # half's last fifteen minutes (runtime/README.md, kernel 2014.3).
        draw_half = half if quarter is None else (2 if quarter == 4 else 1)
        defense = teams[other(offense)]
        drive_no = len(possessions) + 1
        # Kernel 2014.4: this drive's lineups from the live rosters (after
        # every removal so far; no draw is used), and E1: the matchup edge
        # from those lineups' composites (runtime/strength.py).
        period = rotation.quarter_of(half, window, quarter)
        off_view, off_notes, off_block = lineup(offense, "offense", period, drive_no)
        def_view, def_notes, def_block = lineup(defense.team_id, "defense", period, drive_no)
        passer = usage.game_passer(off_view) or off_view[0]
        edge, strength_receipt = unit_strength.drive_edge(
            team, defense, off_view, def_view, passer, team is home and venue != "neutral", params=strength_params)
        # Kernel 2014.4 phase 2: the interception-share and sack-probability
        # shifts of the matchup ride with the draw (zero on the legacy path).
        draw_extra = {"int": strength_receipt.get("int_edge", 0.0), "sack": strength_receipt.get("sack_shift", 0.0)}
        score_diff = stats[offense]["points"] - stats[other(offense)]["points"]
        if regimes_v3:
            # Kernel 2014.6 (B5): per-game context rides with the draw (no
            # module state): the overtime history (R14 ot_first/ot_sudden)
            # and whether a made field goal now would end the game.
            draw_extra["ot_history_empty"] = half == "OT" and not ot_history
            draw_extra["walk_off_fg"] = bool(half == "OT" and ot_history is not None and ot_status(
                ot_history + [{"team": offense, "score": "field_goal"}], game_type) == "end")
        if early_fg_v2:
            # Batch B6 (W3): the clock filters admit a field-goal tuple that
            # kicked before fourth down only when the kick is early or a
            # fourth-down layout exists at the spot (FieldPositionModelV3).
            draw_extra["early_fg_v2"] = True

        # 1-3. Game-state cell, category and a real 2012 drive feasible from
        # the start spot (runtime/field_position.py, possession stream).
        if half == "OT" and game_type == "postseason":
            _reset_postseason_ot_timeouts(window)
        timeouts_before = (timeouts[offense], timeouts[other(offense)])
        drawn = fpm.draw_drive(rng, spot, draw_half, window, score_diff, edge, diagnostics,
                                          timeouts_before, extra=draw_extra)

        def lay_out(drawn, draw_rng, scratch):
            """Steps 4-6b for one drawn drive: its snap counts, the sack
            losses and yard split (on `draw_rng`) and the chain layout (its
            diagnostics in `scratch`, merged only for the adopted drive)."""
            category, row = drawn.category, drawn.tuple
            net, end_spot = fpm.adapt(category, row, spot)
            plays = int(row[T["plays"]])
            runs, attempts, sacks = int(row[T["runs"]]), int(row[T["attempts"]]), int(row[T["sacks"]])
            kneel_yards = list(row[T["kneel_yards"]])
            spikes = int(row[T["spikes"]])

            # 4. Real per-drive snap counts: the drive's own runs, attempts,
            # sacks, kneels and spikes, and its own scoring kind. No Bernoulli
            # decides a pass or a sack, so no sack is converted to an attempt.
            td_type = row[T["td_kind"]] if category == "touchdown" else None
            turnover_type = category if category in drive_model.TURNOVER_CATEGORIES else None
            free, kneel_sum, terminal_value, open_sacks = fpm.fixed_yardage(category, row)
            safety_terminal = None
            if category == "safety":
                safety_terminal = (row[T["safety_term_kind"]], terminal_value)

            # 5. Sack losses (possession stream). With no free snap, the sacks
            # carry the drive's yardage: their losses are fitted to the net.
            if free > 0:
                sack_losses = [draw_rng.randint(3, 10) for _ in range(open_sacks)]
                if category == "touchdown" and free == 1 and sum(sack_losses) > 99 - spot:
                    # Only fixed snaps precede the scoring snap: their losses must
                    # keep the ball out of the own end zone.
                    while sum(sack_losses) > 99 - spot:
                        big = max(range(len(sack_losses)), key=lambda i: (sack_losses[i], -i))
                        sack_losses[big] -= 1
                    scratch["sack_losses_fitted"] = scratch.get("sack_losses_fitted", 0) + 1
            else:
                required = kneel_sum + terminal_value - net
                base, extra = divmod(required, open_sacks) if open_sacks else (0, 0)
                sack_losses = [base + (1 if i < extra else 0) for i in range(open_sacks)]
                if open_sacks:
                    scratch["sack_losses_fitted"] = scratch.get("sack_losses_fitted", 0) + 1
            fixed_sum = kneel_sum - sum(sack_losses) + terminal_value
            free_total = net - fixed_sum

            # 6. Gross passing/rushing yardage over the free snaps.
            usable = attempts - (1 if category == "interception" else 0)
            free_runs = runs - (1 if safety_terminal and safety_terminal[0] == "run" else 0)
            weight_pass = max(0.0, draw_rng.gauss(usable * yards_per_attempt, max(6, usable * 3))) if usable else 0.0
            weight_rush = max(0.0, draw_rng.gauss(free_runs * yards_per_carry, max(4, free_runs * 2))) if free_runs else 0.0
            if usable + free_runs == 0:
                pass_yards = rush_free = 0
            elif not usable:
                pass_yards, rush_free = 0, free_total
            elif not free_runs:
                pass_yards, rush_free = free_total, 0
            else:
                if weight_pass + weight_rush <= 0:
                    scratch["yard_split_count_fallback"] = scratch.get("yard_split_count_fallback", 0) + 1
                    weight_pass, weight_rush = usable, free_runs
                pass_yards, rush_free = _split_yards(free_total, weight_pass, weight_rush)
            if td_type == "pass" and pass_yards < 1 and free_runs:
                rush_free -= 1 - pass_yards
                pass_yards = 1
            elif td_type == "rush" and rush_free < 1 and usable:
                pass_yards -= 1 - rush_free
                rush_free = 1
            if td_type and usable and free_runs:
                # Feasibility, not calibration: the non-scoring kind's yards plus
                # the fixed snaps keep the ball in the field before the scoring
                # snap (running spot in [1, 99]); any excess moves to the scoring
                # kind, whose total then lies in [1, 99].
                before = rush_free if td_type == "pass" else pass_yards
                fitted = min(max(before, spot - 99 - fixed_sum), spot - 1 - fixed_sum)
                if fitted != before:
                    scratch["td_split_fitted"] = scratch.get("td_split_fitted", 0) + 1
                    if td_type == "pass":
                        rush_free, pass_yards = fitted, pass_yards + before - fitted
                    else:
                        pass_yards, rush_free = fitted, rush_free + before - fitted

            # 6b. Kernel 2014.4 (defect register item 3): the drive's ordered
            # snaps and their chain walk, on the kernel-owned chain-layout stream
            # (runtime/chains.py; the possession stream is not consumed). Down,
            # distance, first downs and third/fourth-down counts come from that
            # walk; only the real drive's penalty first downs (no ledger rows)
            # stay a counter, chains[1], less any walked scrimmage first downs
            # beyond the real scrimmage count (chains.penalty_first_downs). When the split above admits no legal
            # order the layout returns an alternative split or sack-loss draw
            # (same net), which the drive then publishes.
            fg_down = None
            if early_fg_v2 and category == "field_goal_attempt" and not fpm.early_fg_ok(
                    row, window, half == "OT", drawn.consumes_window, draw_extra.get("walk_off_fg", False)):
                # Batch B6 (W3): the kick comes on fourth down in every tier;
                # the closable last fallback admits the real down, counted.
                fg_down = 4
            layout = chain_walk.drive_layout(
                seed=seed, event_id=event_id, drive_no=drive_no, offense=offense, category=category,
                td_type=td_type, runs=runs, attempts=attempts, sacks=sacks, kneel_yards=kneel_yards,
                spikes=spikes, pass_yards=pass_yards, rush_free=rush_free, losses=sack_losses,
                safety_terminal=safety_terminal, net=net, spot=spot, completion_rate=completion_rate,
                targets=list(row[T["chains"]]), term_down=row[T["term_down"]], diagnostics=scratch,
                usage_values=usage_values, fg_down=fg_down)
            return dict(net=net, end_spot=end_spot, plays=plays, runs=runs, attempts=attempts, sacks=sacks,
                        kneel_yards=kneel_yards, spikes=spikes, td_type=td_type, turnover_type=turnover_type,
                        kneel_sum=kneel_sum, terminal_value=terminal_value, safety_terminal=safety_terminal,
                        layout=layout)

        scratch = {}
        laid = lay_out(drawn, rng, scratch)
        layout_resample = None
        if not laid["layout"]["ok"]:
            # Kernel 2014.4 phase 2 (register item 3, last fallback): no plan
            # legalised this real drive's snaps, so another real drive of the
            # same category and rung stands in, drawn on the drive's own
            # layout-resample stream (never the possession stream); the
            # original tuple is recorded. A closed week cannot abort on one
            # drive; when the rung has no other legal drive the original
            # keeps its unconstrained order and the audit flags it, as before.
            resample_rng = chain_walk.resample_stream(seed, event_id, drive_no, offense)
            original = drawn
            tried = [drawn.tuple]
            for attempt in range(1, LAYOUT_RESAMPLE_LIMIT + 1):
                alt = (fpm.resample_drive(resample_rng, original, spot, window, exclude=tried,
                                          timeouts=timeouts_before, extra=draw_extra) if regimes_v3
                       else fpm.resample_drive(resample_rng, original, spot, window, exclude=tried))
                if alt is None:
                    break
                tried.append(alt.tuple)
                alt_scratch = {}
                candidate = lay_out(alt, resample_rng, alt_scratch)
                if candidate["layout"]["ok"]:
                    drawn, laid, scratch = alt, candidate, alt_scratch
                    layout_resample = {
                        "resamples": attempt,
                        "pool": list(original.pool_id) if original.pool_id else None,
                        "original": {"locator": fpm.tuple_locator(original.category, original.tuple),
                                     "tuple": list(original.tuple[:5])},
                        "final": {"locator": fpm.tuple_locator(alt.category, alt.tuple),
                                  "tuple": list(alt.tuple[:5])},
                    }
                    if original.match_width is not None:
                        # Kernel 2014.6 (append-only): the R17 time-match width.
                        layout_resample["match_width"] = original.match_width
                    if regimes_v3 and (alt.pool_id != original.pool_id or alt.match_width != original.match_width):
                        # Kernel 2014.6 (append-only): the wider pool the
                        # resample drew from (FieldPositionModelV3._resample_rungs).
                        layout_resample["final_pool"] = list(alt.pool_id)
                        layout_resample["final_match_width"] = alt.match_width
                        diagnostics["chain_layout_resample_widened"] = \
                            diagnostics.get("chain_layout_resample_widened", 0) + 1
                    diagnostics["chain_layout_resampled"] += 1
                    break
            if layout_resample is None:
                diagnostics["chain_layout_resample_exhausted"] += 1
        for name, count in scratch.items():
            diagnostics[name] = diagnostics.get(name, 0) + count
        category, row, seconds = drawn.category, drawn.tuple, drawn.seconds
        # The real drive's charged timeouts, capped at what each club holds.
        timeouts_used = (min(timeouts_before[0], row[T["off_timeouts_used"]] or 0),
                         min(timeouts_before[1], row[T["def_timeouts_used"]] or 0))
        timeouts[offense] -= timeouts_used[0]
        timeouts[other(offense)] -= timeouts_used[1]
        half_final = drawn.consumes_window
        net, end_spot, plays = laid["net"], laid["end_spot"], laid["plays"]
        runs, attempts, sacks = laid["runs"], laid["attempts"], laid["sacks"]
        kneel_yards, spikes, td_type, turnover_type = laid["kneel_yards"], laid["spikes"], laid["td_type"], laid["turnover_type"]
        kneel_sum, terminal_value, safety_terminal, layout = laid["kneel_sum"], laid["terminal_value"], laid["safety_terminal"], laid["layout"]
        pass_yards, rush_free, sack_losses = layout["pass_yards"], layout["rush_free"], layout["losses"]
        walked = layout["walk"]["chains"]
        real_chains = row[T["chains"]]
        chains = [walked[0], chain_walk.penalty_first_downs(real_chains[0], real_chains[1], walked[0]),
                  walked[1], walked[2], walked[3], walked[4]]

        rush_yards = rush_free + kneel_sum + (terminal_value if safety_terminal and safety_terminal[0] == "run" else 0)
        sack_total = sum(sack_losses) + (-terminal_value if safety_terminal and safety_terminal[0] == "sack" else 0)

        s = stats[offense]
        d = stats[defense.team_id]
        s["passing_yards"] += pass_yards
        s["rushing_yards"] += rush_yards
        s["sacks_allowed"] += sacks

        # 7. Penalties (counters only) and the drive's chains.
        pens = sum(rng.random() < penalty_per_play for _ in range(plays))
        s["penalties"] += pens
        s["penalty_yards"] += pens * rng.randint(5, 10) if pens else 0
        s["first_downs"] += chains[0] + chains[1]
        s["third_down_attempts"] += chains[2]
        s["third_down_conversions"] += chains[3]

        terminal = category
        if category == "clock":
            terminal = QUARTER_REASON[quarter] if quarter else CLOCK_REASON[half]
        if half == "OT":
            start_clock, end_clock = window, window - seconds
        else:
            base = (4 - quarter) * RULES.quarter_seconds if quarter else (1800 if half == 1 else 0)
            start_clock, end_clock = base + window, base + window - seconds
        overtime_label = ot_label if half == "OT" else False
        # Batch B9 (R8): the try row's own stamp, with its scoring snap at the
        # drive's own end, never after the clock-expiry leg (the extra-point
        # row's stamp since kernel 2014.4); the try state reads it.
        own_used = seconds if drawn.own_seconds is None else max(0, min(int(drawn.own_seconds), seconds))
        own_end = start_clock - own_used
        try_period, try_clock = _period_clock(own_end, closing=own_end <= end_clock, overtime=overtime_label)
        try_at = {"drive": drive_no, "period": try_period, "game_clock": try_clock, "snap_in_drive": plays + 1}

        # 8. Terminal scoring, then the transition to the next possession.
        points = 0
        score_kind = None
        scoring_team = None
        xp_made = None
        fg_made = None
        fg_distance = None
        next_start = None
        next_kind = None
        next_offense = defense.team_id
        non_offensive_score = None
        punt_record = None
        turnover_record = None
        try_record = None
        # Batch B9 (R15): (source, return yards) when this possession's
        # turnover, punt or missed field goal is returned for a touchdown,
        # and the keyed scoring-return-v1 substream (event and drive; no team
        # id) its one uniform is drawn on at every such event.
        defensive_td = None
        return_stream = None
        forced_drive = forced_scoring["drives"].get(drive_no)

        def unit_input(side, unit):
            """The E1 socket input of one of this drive's unit composites: the
            composite of the drive's actual lineup less its strength term's
            centre (runtime.strength), 0 for a side with no strength record.
            Read for the slope-0 return and blocked-kick sockets; no draw."""
            units = (strength_receipt.get("units") or {}).get(side)
            if not units:
                return 0.0
            centre = next((term["centre"] for term in strength_params.terms
                           if term["side"] == side and term["unit"] == unit), None)
            if centre is None:
                raise ValueError("profile %s has no %s %s strength term for its scoring socket"
                                 % (profile.kernel_version, side, unit))
            return units[unit]["composite"] - centre

        def returned(unit, los, **inputs):
            """The R15 test of this possession's turnover, punt or missed field
            goal, with its E1 socket inputs (``returner``/``coverage`` for a
            return, ``protection``/``rush`` for a blocked kick; slope 0)."""
            nonlocal return_stream
            return_stream = _stream(scoring.RETURN_TAG, seed, event_id, drive_no)
            u = return_stream.random()
            pair = smodel.missed_fg if unit == "missed_field_goal" else smodel.return_rate(unit, los)
            prob = (smodel.p_blocked(pair, **inputs) if unit == "missed_field_goal"
                    else smodel.p_return(pair, **inputs))
            return u < prob

        if category == "touchdown":
            points = 6
            s["touchdowns"] += 1
            score_kind, scoring_team = "touchdown", offense
            walk_off = ot_history is not None and ot_status(
                ot_history + [{"team": offense, "score": "touchdown"}], game_type) == "end"
            if not walk_off and try_v1 and not pro_bowl_game:
                # Batch B9 (R8): go or kick by the club's policy, a live
                # answer or the league chart; the result on the possession
                # stream at the extra point's position (one draw, as before).
                try_record = resolve_try(offense, anchor={"drive": drive_no}, at=try_at, view=off_view, edge=edge,
                                         result_rng=rng)
                points += try_record["points"]
                if try_record["decision"] == "kick":
                    xp_made = try_record["made"]
            elif not walk_off:
                s["extra_point_attempts"] += 1
                xp_prob = xp_rate
                if xp_rule is not None and xp_rule.get("distance"):
                    # 2014 preseason Weeks 1-2: the try is a 33-yard kick on
                    # the field-goal distance model, with the kicker's own
                    # term as for any field goal. Same single draw.
                    xp_prob = dm.fg_make_prob_at(xp_rule["distance"])
                    if team.strength:
                        kicker = usage.kicking_specialist(off_view, "K", "placekicker")
                        kick_shift, _ = unit_strength.kicker_adjustment(team.strength, kicker, params=strength_params)
                        xp_prob = min(strength_params.fg_prob_ceiling,
                                      max(strength_params.fg_prob_floor, xp_prob + kick_shift))
                xp_made = rng.random() < xp_prob
                if xp_made:
                    points += 1
                    s["extra_points_made"] += 1
        elif category == "field_goal_attempt":
            s["field_goal_attempts"] += 1
            fg_distance = int(row[T["fg_distance"]])
            # Kernel 2014.4 phase 2: the distance model (register item 18)
            # and the kicker's own term (special teams; slope 0 in this
            # candidate) on the same single draw.
            fg_prob = dm.fg_make_prob_at(fg_distance)
            if team.strength:
                kicker = usage.kicking_specialist(off_view, "K", "placekicker")
                kick_shift, kick_receipt = unit_strength.kicker_adjustment(team.strength, kicker, params=strength_params)
                fg_prob = min(strength_params.fg_prob_ceiling, max(strength_params.fg_prob_floor, fg_prob + kick_shift))
            fg_made = rng.random() < fg_prob
            if fg_made:
                points = 3
                s["field_goals"] += 1
                score_kind, scoring_team = "field_goal", offense
            else:
                next_start, next_kind = fpm.missed_fg_start(fg_distance), "missed_fg"
                if returns_v1 and (returned("missed_field_goal", end_spot, protection=unit_input("offense", "protection"),
                                            rush=unit_input("defense", "rush"))
                                   or forced_drive == "blocked_fg_td"):
                    # Batch B9 (R15): a blocked kick returned for a touchdown
                    # (every sourced one was a block), from the line of
                    # scrimmage to the goal line.
                    defensive_td = ("blocked_field_goal", 100 - end_spot)
        elif category == "punt":
            s["punts"] += 1
            punt_record = fpm.punt(rng, end_spot)
            # Kernel 2014.4 phase 2: the punter's net term on the kicking
            # club's record and the returner's term on the receiving club's
            # (returner slope 0 in this candidate); no draw is consumed.
            if team.strength:
                punter = usage.kicking_specialist(off_view, "P", "punt")
                punt_shift, punt_receipt = unit_strength.punter_adjustment(team.strength, punter, params=strength_params)
                punt_record = fpm.adjust_punt(punt_record, punt_shift)
                punt_record["punter"] = punt_receipt
            if defense.strength and punt_record["outcome"] == "returned":
                returner = usage.club_returner(def_view, "punt_return")
                ret_shift, ret_receipt = unit_strength.returner_adjustment(defense.strength, returner, "PR",
                                                                           params=strength_params)
                punt_record = fpm.adjust_return(punt_record, ret_shift)
                punt_record["returner"] = ret_receipt
            punt_returner = 0.0
            if returns_v1 and defense.strength:
                # The returner socket's input: the receiving club's punt
                # returner's tier value (the existing returner term's).
                punt_returner = unit_strength.returner_adjustment(
                    defense.strength, usage.club_returner(def_view, "punt_return"), "PR",
                    params=strength_params)[1]["value"]
            if returns_v1 and (returned("punt", end_spot, returner=punt_returner)
                               or forced_drive in ("punt_return_td", "blocked_punt_td")):
                # Batch B9 (R15): a punt returned or blocked for a touchdown,
                # on a real record of the punt's bin feasible from this line
                # (the base record is taken and discarded).
                records = smodel.punt_records(end_spot)
                if forced_drive in ("punt_return_td", "blocked_punt_td"):
                    blocked = forced_drive == "blocked_punt_td"
                    records = [r for r in records if bool(r["blocked"]) == blocked] or [
                        r for r in smodel.records["punt_return_or_block_td"]
                        if bool(r["blocked"]) == blocked and (blocked or r["gross"] <= end_spot + 9)]
                if records:
                    r = records[return_stream.randrange(len(records))]
                    blocked = bool(r["blocked"])
                    gross = 0 if blocked else int(r["gross"])
                    ry = 100 - end_spot + gross
                    punt_record = {"los": end_spot, "outcome": PUNT_BLOCKED_TD if blocked else PUNT_RETURN_TD,
                                   "gross": gross, "return_yards": ry, "enforcement": 0, "next_start": None,
                                   "touchback": False, "record_los": int(r["los"])}
                    defensive_td = ("blocked_punt" if blocked else "punt_return", ry)
                else:
                    diagnostics["return_td_without_record"] = diagnostics.get("return_td_without_record", 0) + 1
            d["punt_returns"] += int(punt_record["outcome"] in ("returned", PUNT_RETURN_TD))
            next_start, next_kind = punt_record["next_start"], "punt"
            if punt_record.get("possession") == "kicking":
                # Batch B8: the kicking club kept the ball (R12 layer C).
                next_kind, next_offense = "punt_retained", offense
        elif category in drive_model.TURNOVER_CATEGORIES:
            s["turnovers"] += 1
            turnover_record = fpm.turnover(rng, category, end_spot)
            next_start, next_kind = turnover_record["next_start"], category
            if returns_v1:
                # Batch B9 (R15): the turnover returned for a touchdown at its
                # line-of-scrimmage bin's sourced rate (the fumbled snap's line
                # for a fumble); a pick-six's return covers 100 - (LOS - air
                # yards) of a real pick-six record of the bin, a fumble's
                # 100 - the fumble spot.
                forced = forced_drive == "defensive_touchdown"
                coverage = unit_input("defense", "coverage")
                if category == "interception":
                    if returned("interception", end_spot, coverage=coverage) or forced:
                        records = smodel.interception_records(end_spot)
                        r = records[return_stream.randrange(len(records))]
                        defensive_td = ("interception", 100 - (end_spot - int(r["air_yards"])))
                else:
                    fumbled_los = end_spot + int(layout["values"][-1])
                    if returned("fumble_lost", fumbled_los, coverage=coverage) or forced:
                        defensive_td = ("fumble", 100 - end_spot)
                if defensive_td is not None:
                    turnover_record = dict(turnover_record, return_yards=defensive_td[1], next_start=None)
            elif forced_drive == "defensive_touchdown":
                # Batch B8 test branch (R15 placeholder): the defense returns
                # the turnover for a touchdown and kicks off to this offense.
                score_kind, scoring_team = "touchdown", defense.team_id
                d["touchdowns"] += 1
                walk_off = ot_history is not None and ot_status(
                    ot_history + [{"team": offense, "score": "touchdown"}], game_type) == "end"
                d_xp = try_after(defense.team_id, d, def_view, walk_off=walk_off)
                non_offensive_score = {"kind": "touchdown", "team": defense.team_id,
                                       "points": 6 + (1 if d_xp else 0), "xp_made": d_xp}
                d["points"] += non_offensive_score["points"]
                next_start, next_kind = None, None
        elif category == "downs":
            s["turnovers_on_downs"] += 1
            next_start, next_kind = fpm.downs_start(end_spot), "downs"
        elif category == "safety":
            d["points"] += 2
            d["safeties"] += 1
            score_kind, scoring_team = "safety", defense.team_id
        elif category == "clock":
            s["clock_expired_drives"] += 1
        if defensive_td is not None:
            # Batch B9 (R15): the defense (or the punt or field-goal return
            # unit) scores. The possession keeps its category and its
            # counters; the score is the drive's non_offensive_score, its try
            # R8's (the scorer's policy and margin), and no next start is
            # published: the scorer kicks off when time remains.
            source, ry = defensive_td
            score_kind, scoring_team = "touchdown", defense.team_id
            d["touchdowns"] += 1
            d[scoring.SOURCES[source]] += 1
            walk_off = ot_history is not None and ot_status(
                ot_history + [{"team": offense, "score": "touchdown"}], game_type) == "end"
            non_offensive_score = {"kind": "touchdown", "team": defense.team_id, "source": source,
                                   "return_yards": ry, "points": 6, "xp_made": None}
            if not walk_off and try_v1 and not pro_bowl_game:
                try_record = resolve_try(defense.team_id, anchor={"drive": drive_no}, at=try_at, view=def_view)
                non_offensive_score["try"] = try_record
                non_offensive_score["points"] += try_record["points"]
                if try_record["decision"] == "kick":
                    non_offensive_score["xp_made"] = try_record["made"]
            elif not walk_off:
                # The Pro Bowl (no try decision): the kick, on the keyed
                # substream's result uniform (2014.5 had no draw here).
                stream = _stream(scoring.TRY_TAG, seed, event_id, "drive", drive_no)
                stream.random()
                d_xp = try_after(defense.team_id, d, def_view, walk_off=False, u=stream.random())
                non_offensive_score["xp_made"] = d_xp
                non_offensive_score["points"] += int(bool(d_xp))
            d["points"] += non_offensive_score["points"]
            next_start, next_kind = None, None
        s["drives"] += 1
        s["points"] += points
        s["time_of_possession"] += seconds

        fourth_down = None
        if category in field_position.FOURTH_DOWN_CATEGORIES:
            clock_s = window - seconds
            # Kernel 2014.4: the ledger's own state before the kick (after the
            # last scrimmage snap) or, on downs, before the failed fourth-down
            # snap (its line of scrimmage, not the spot where it ended).
            state = chain_walk.terminal_state(category, spot, layout["values"])
            fourth_down = {
                "down": state["down"],
                "ydstogo": state["ydstogo"],
                "goal_to_go": state["goal_to_go"],
                "los": state["los"],
                "clock_s": clock_s, "clock_bucket": fpm.terminal_bucket(clock_s) if draw_half == 2 else None,
                "half": draw_half, "score_diff": score_diff, "need": fpm.need(score_diff),
                "decision_zone": fpm.decision_zone(end_spot), "cell": drawn.cell,
                "tuple_terminal_bucket": row[T["term_bucket"]],
                "action": {"punt": "punt", "field_goal_attempt": "field_goal", "downs": "go"}[category],
            }
            if clock_detail:
                # Batch B6 (W5a, append-only): the fourth-down action is the
                # replayed drive's, a league-model decision, never a coach's.
                fourth_down["decision_source"] = "league_model"

        drive_ledger, drive_calls = apply_drive_detail(
            calibration_base=cbase,
            usage_base=ubase,
            seed=seed,
            event_id=event_id,
            drive_no=drive_no,
            team=team,
            defense=defense,
            available=off_view,
            defenders=def_view,
            offense_stats=s,
            defense_stats=d,
            runs=runs,
            attempts=attempts,
            sacks=sacks,
            kneel_yards=kneel_yards,
            spikes=spikes,
            pass_yards=pass_yards,
            rush_free=rush_free,
            category=terminal,
            td_type=td_type,
            turnover_type=turnover_type,
            sack_losses=sack_losses,
            safety_terminal=safety_terminal,
            fg_made=fg_made,
            fg_distance=fg_distance,
            xp_made=xp_made,
            net_yards=net,
            start_spot=spot,
            start_clock=start_clock,
            end_clock=end_clock,
            own_seconds=drawn.own_seconds,
            overtime=ot_label if half == "OT" else False,
            punt_record=punt_record,
            turnover_record=turnover_record,
            fourth_down=fourth_down,
            passer=passer,
            diagnostics=diagnostics,
            layout=layout,
            # Kernel 2014.5: label-stream inputs only (the situational menus
            # and the opening sequence); no draw reads them.
            score_diff=score_diff,
            start_kind=start_kind,
            game_ledger=play_ledger,
            # Kernel 2014.6 batch B6 (W5a): clock stamps, timeout and
            # two-minute-warning rows (records only).
            clock_detail=clock_detail,
            timeouts_used=timeouts_used,
            game_type=game_type,
            kernel_version=profile.kernel_version,
        )
        chain_walk.annotate(drive_ledger, layout["walk"], fourth_down)
        if try_record is not None and score_kind == "touchdown" and scoring_team == offense:
            # Batch B9 (R8): the offensive try row, anchored to this drive and
            # naming its scorer; a two-point row sits right after the
            # scoring snap, where the extra-point row would.
            anchor = {"drive": drive_no}
            if try_record["decision"] == "kick":
                xp_row = next(r for r in drive_ledger if r.get("play_type") == "extra_point")
                xp_row.update(try_fields(try_record), anchor=anchor, scoring_team=offense)
            else:
                # (Not `row`: that name is the drawn drive tuple below.)
                try_line = try_rows(try_record, offense, anchor=anchor, at=try_at, off_view=off_view,
                                    def_view=def_view, passer=passer)
                drive_ledger.insert(seat_try(drive_ledger, try_line, overtime_label), try_line)
        if defensive_td is not None:
            # Batch B9 (R15): the scoring row. A turnover row carries
            # touchdown and turnover both, the scorer the defense (the
            # interceptor or the recoverer already named); a punt return's
            # row its returner; a blocked punt's or field goal's row the
            # player credited by an even draw from the defense's unit on that
            # row (a labelled convention, attribution group_draw, never
            # player evidence).
            source, ry = defensive_td
            if source in ("interception", "fumble"):
                scored = [r for r in drive_ledger if r.get("play_type") in ("pass", "run")][-1]
                credit = scored.get("tackler")
            else:
                scored = next(r for r in drive_ledger if r.get("play_type") in ("punt", "field_goal"))
                credit = scored.get("returner") if source == "punt_return" else None
                if source != "punt_return":
                    unit = participation.kick(scored, offense, defense.team_id, off_view, def_view)[defense.team_id]
                    credit = unit[return_stream.randrange(len(unit))] if unit else None
                    scored.update(blocked=True, scorer=credit, attribution=scoring.GROUP_DRAW)
            scored.update(touchdown=True, scoring_team=defense.team_id, return_yards=ry)
            if credit is not None:
                line = d["players"][credit]
                field = scoring.PLAYER_TD_FIELD[source]
                line[field] = line.get(field, 0) + 1
            if try_record is not None:
                quarter_now = period if trackers is not None else None
                scorer_view = def_view if try_record["decision"] == "kick" else side_view(defense.team_id, "offense",
                                                                                          quarter_now)
                drive_ledger.append(try_rows(try_record, defense.team_id, anchor={"drive": drive_no}, at=try_at,
                                             off_view=scorer_view,
                                             def_view=side_view(offense, "defense", quarter_now)))
            elif non_offensive_score.get("xp_made") is not None:
                drive_ledger.append(try_row(try_at, scoring=defense, opponent=offense, available=def_view, stats=stats,
                                            made=non_offensive_score["xp_made"], seed=seed, event_id=event_id,
                                            anchor={"drive": drive_no}))
        elif non_offensive_score is not None and non_offensive_score.get("xp_made") is not None:
            # Batch B8: the defense's try, anchored to this possession, after
            # the drive's own rows (the terminal snap is the turnover).
            period, game_clock = _period_clock(end_clock, closing=True, overtime=ot_label if half == "OT" else False)
            drive_ledger.append(try_row({"drive": drive_no, "period": period, "game_clock": game_clock,
                                         "snap_in_drive": plays}, scoring=defense, opponent=offense,
                                        available=def_view, stats=stats, made=non_offensive_score["xp_made"],
                                        seed=seed, event_id=event_id, anchor={"drive": drive_no}))
        append_rows(drive_ledger)
        _merge_call_stats(play_call_stats[offense], drive_calls)
        _append_evidence(
            evidence,
            drive_ledger,
            off_view,
            def_view,
            "turnover" if turnover_type else LEGACY_OUTCOME.get(category, "other"),
        )

        record = {
            "number": drive_no,
            "team": offense,
            "half": half,
            "start_clock": start_clock,
            "end_clock": end_clock,
            "seconds": seconds,
            "scrimmage_plays": plays,
            "outcome": LEGACY_OUTCOME.get(category, terminal),
            "category": terminal,
            "points": points,
            "td_type": td_type,
            "turnover_type": turnover_type,
            "net_yards": net,
            "sack_loss_total": sack_total,
            "fg_distance": fg_distance,
            "fg_made": fg_made,
            "xp_made": xp_made,
            "half_final": half_final,
            "kickoff_after": None,
            # Kernel 2013.7 field position (append-only).
            "start_spot": spot,
            "start_kind": start_kind,
            "end_spot": end_spot,
            "next_start": next_start,
            "score_diff": score_diff,
            "cell": drawn.cell,
            "tuple_terminal_bucket": row[T["term_bucket"]],
            "chains": chains,
            "fourth_down": fourth_down,
            "kneels": len(kneel_yards),
            "spikes": spikes,
            # Kernel 2014.1 (append-only): [offense before, defence before,
            # offense used, defence used] and the timeout-ladder level.
            "timeouts": [timeouts_before[0], timeouts_before[1], timeouts_used[0], timeouts_used[1]],
            "timeout_level": drawn.timeout_level,
            # Kernel 2014.4 (append-only): the drive's own scaled seconds and
            # the clock-expiry leg after its last snap (seconds = own +
            # expiry; expiry is 0 unless the drive ends its window).
            "own_seconds": drawn.own_seconds,
            "expiry_seconds": drawn.expiry_seconds,
            # Kernel 2014.4 (append-only): the drive's passer.
            "passer": passer.player_id,
            # Kernel 2014.4 (append-only): chains and fourth_down are walked
            # from this drive's own snap ledger (runtime/chains.py).
            "chain_model": chain_walk.CHAIN_MODEL,
        }
        if off_notes or def_notes:
            record["emergency"] = off_notes + def_notes
        if (team.strength or defense.strength) and not hidden_strength:
            # Kernel 2014.4 E1 (append-only): the drive's composites, their
            # contributors and the edge they produced. Not under the
            # player-state model (B7): the contributors would publish the
            # drawn values.
            record["strength"] = strength_receipt
        if _test_strength_receipt is not None:
            _test_strength_receipt.append({"drive": drive_no, "team": offense, **strength_receipt})
        # Kernel 2014.4 phase 2 (append-only): the field-goal probability the
        # make was drawn against, the punt transition as adjusted, and the
        # layout resample when one stood in for the drawn drive.
        if category == "field_goal_attempt":
            record["fg_prob"] = fg_prob
            if team.strength:
                record["fg_kicker"] = kick_receipt
        if punt_record is not None:
            record["punt"] = {k: punt_record[k] for k in ("outcome", "gross", "return_yards", "enforcement",
                                                          "touchback", "next_start") if k in punt_record}
            for key in ("adjust", "return_adjust", "punter", "returner"):
                if key in punt_record:
                    record["punt"][key] = punt_record[key]
        if layout_resample is not None:
            record["layout_resample"] = layout_resample
        if regimes_v3 and spikes:
            # Kernel 2014.6 (append-only): the window seconds left at the
            # drive's last spike (the R14 spike rule's quantity).
            record["last_spike_seconds_left"] = window - drawn.own_seconds + int(fpm.value(row, "last_spike_to_end"))
        if half == "OT":
            record["period"] = _period_clock(start_clock, overtime=ot_label)[0]
        if quarter:
            record["quarter"] = quarter
        if non_offensive_score is not None:
            # Batch B8 (append-only): the score the defense made during this
            # possession (runtime.rules.possession_score); batch B9 (R15)
            # writes it with its source, return yards and try.
            record["non_offensive_score"] = non_offensive_score
        if try_record is not None and scoring_team == offense:
            # Batch B9 (R8, append-only): the offensive touchdown's try.
            record["try"] = try_record
        possessions.append(record)
        # Kernel 2014.4: record this drive's participants, then draw injury
        # onsets for both clubs at the end of the drive (E2 step 1).
        front = usage.protection_front(off_view)
        # The recorded snap line keeps the named-player uplift; the injury
        # exposure is the slot model alone (participation.scrimmage), so the
        # attribution tilt (item 19) cannot move an onset draw.
        hazard = {}
        scrimmage = participation.scrimmage(accumulator, offense, defense.team_id, off_view, def_view,
                                            passer, front, drive_ledger, hazard_out=hazard)
        for team_id, side in ((offense, "offense"), (defense.team_id, "defense")):
            participation.credit(stats, team_id, scrimmage[team_id], side)
            add_exposure(team_id, hazard[team_id])
        views = {offense: off_view, defense.team_id: def_view}
        for row in drive_ledger:
            if row.get("play_type") in participation.KICK_TYPES:
                # Batch B9: a row's units by its own offense (the defense's
                # try after its touchdown is its unit; unchanged otherwise).
                units = participation.kick(row, row["offense"], row["defense"], views[row["offense"]],
                                           views[row["defense"]])
                for team_id, ids in units.items():
                    add_exposure(team_id, participation.credit(stats, team_id, dict.fromkeys(ids, 1),
                                                               "special_teams"))
                if trackers is not None:
                    for team_id in (offense, defense.team_id):
                        trackers[team_id].kicked(period)
        if trackers is not None:
            # Preseason: the blocks that played this drive advance their counts.
            scrimmage_snaps = sum(1 for r in drive_ledger if r.get("play_type") in participation.SCRIMMAGE_TYPES)
            trackers[offense].played("offense", off_block, period, scrimmage_snaps)
            trackers[defense.team_id].played("defense", def_block, period, scrimmage_snaps)
        end_of_drive(drive_no, _period_clock(end_clock, closing=True, overtime=overtime_label), half)
        # Batch B8: the possession reports what ended it (the score, with its
        # scorer) and, when it did not score, who possesses next (the
        # defense, or this offense after a kick it kept) and how.
        score = {"kind": score_kind, "team": scoring_team} if score_kind else None
        return record, score, next_kind, next_offense

    def kick_sequence(kicking, receiving, *, free_kick, half, window, ot_label="OT", after_drive=None):
        """Kernel 2014.6 batch B8: the chain of kicks between two possessions.

        A kick returned for a touchdown is followed by the scorer's kickoff on
        the same chain (kicks take no game clock), until a kick is taken over:
        by the receiving club, or by the kicking club when it keeps the ball.
        In overtime a return touchdown may end the game (rules.ot_history and
        ot_status), which closes the chain with no possessor. Bounded by
        KICK_CHAIN_BOUND, failing closed. Returns (spot, start_kind, next
        possessor or None, the last kick record, whether the game ended)."""
        chain = 0
        while True:
            chain += 1
            if chain > KICK_CHAIN_BOUND:
                raise RuntimeError("kick chain exceeded the engine's %d-kick bound" % KICK_CHAIN_BOUND)
            remaining = window + (1800 if half == 1 else 0)
            kicked = kick(kicking, receiving, free_kick=free_kick, half=half, remaining=remaining,
                          ot_label=ot_label, chain=chain, after_drive=after_drive)
            if kicked.get("touchdown"):
                if half == "OT" and ot_status(ot_history(possessions, kickoffs), game_type) == "end":
                    return None, None, None, kicked, True
                kicking, receiving, free_kick = receiving, kicking, False
                continue
            retained = kicked["outcome"] in KEPT_KICK_OUTCOMES
            if retained and half == "OT" and ot_status(ot_history(possessions, kickoffs), game_type) == "end":
                # Batch B9 (R9, library rule R4): a kick the kicking club keeps
                # before the receiving club's first overtime possession gives
                # the receiver its opportunity; checked at once (after an
                # opening field goal, the recovery ends the game).
                return None, None, None, kicked, True
            return kicked["next_start"], _start_kind(kicked), kicking if retained else receiving, kicked, False

    def kicked_after(record, score, window, half, ot_label="OT"):
        """The kick(s) after a scoring possession: the scorer kicks off (the
        club scored upon free-kicks after a safety). Returns (spot,
        start_kind, next possessor, retained flag, game ended)."""
        kicker = kicking_club(score["kind"], score["team"], other(score["team"]))
        spot, start_kind, offense, kicked, ended = kick_sequence(
            kicker, other(kicker), free_kick=score["kind"] == "safety", half=half, window=window,
            ot_label=ot_label, after_drive=record["number"])
        record["kickoff_after"] = {"returned": kicked["returned"], "free_kick": kicked["free_kick"],
                                   "next_start": kicked["next_start"], "touchback": kicked["touchback"],
                                   "enforcement": kicked["enforcement"]}
        record["next_start"] = kicked["next_start"]
        return spot, start_kind, offense, kicked["outcome"] in KEPT_KICK_OUTCOMES, ended

    def placed(record, score):
        """Pro Bowl: the next possession starts at the 25 (no kickoff), taken
        by the club that would have received the kick (the club scored upon
        after a touchdown or field goal, the scorer after a safety)."""
        record["next_start"] = PRO_BOWL_SPOT
        return PRO_BOWL_SPOT, "placement", other(kicking_club(score["kind"], score["team"], other(score["team"])))

    # Regulation: two clock-bounded halves; a possession never crosses one.
    opening_receiver = away.team_id if rng.random() < 0.5 else home.team_id
    pro_bowl = game_type == PRO_BOWL
    for quarter in ((1, 2, 3, 4) if pro_bowl else ()):
        # Possession alternates at the start of each quarter from the
        # opening coin toss; timeouts reset at each half.
        half = 1 if quarter <= 2 else 2
        offense = opening_receiver if quarter in (1, 3) else other(opening_receiver)
        window = RULES.quarter_seconds
        if quarter in (1, 3):
            for team_id in timeouts:
                timeouts[team_id] = RULES.timeouts_per_half
        spot, start_kind = PRO_BOWL_SPOT, "placement"
        while window > 0:
            record, score, next_kind, next_offense = possess(offense, window, half, spot, start_kind, quarter=quarter)
            window -= record["seconds"]
            if score and window > 0:
                spot, start_kind, offense = placed(record, score)
            else:
                spot, start_kind, offense = record["next_start"], next_kind, next_offense
    for half in (() if pro_bowl else (1, 2)):
        receiver = opening_receiver if half == 1 else other(opening_receiver)
        window = RULES.quarter_seconds * 2
        for team_id in timeouts:
            timeouts[team_id] = RULES.timeouts_per_half
        spot, start_kind, offense, _opened, _ended = kick_sequence(other(receiver), receiver, free_kick=False,
                                                                  half=half, window=window)
        while window > 0:
            record, score, next_kind, next_offense = possess(offense, window, half, spot, start_kind)
            window -= record["seconds"]
            if score and window > 0:
                spot, start_kind, offense, _retained, _ended = kicked_after(record, score, window, half)
            else:
                spot, start_kind, offense = record["next_start"], next_kind, next_offense

    total = RULES.quarter_seconds * 4
    overtime_seconds = 0
    if stats[home.team_id]["points"] == stats[away.team_id]["points"]:
        # Kernel 2013.8 overtime (library/2013_nfl_playing_rules_for_simulation.md).
        # A new coin toss decides the receiver; possessions alternate on a
        # real clock, each drive using its own seconds; modified sudden death
        # (runtime.rules.ot_status) decides when a score ends the game.
        # Regular season and preseason: one 15-minute period; when it expires
        # the game ends, tied if still level. Postseason: 15-minute periods
        # laid on one continuous countdown, so a possession carries across a
        # period break and the game never ends tied.
        offense = home.team_id if rng.random() < 0.5 else away.team_id
        postseason = game_type == "postseason"
        if postseason:
            periods = RULES.postseason_ot_period_bound
            ot_label = ("OT", periods, RULES.postseason_ot_seconds)
            window = periods * RULES.postseason_ot_seconds
        else:
            ot_label = "OT"
            window = RULES.regular_ot_seconds
        for team_id in timeouts:
            timeouts[team_id] = (RULES.postseason_ot_timeouts_per_half if postseason
                                 else RULES.regular_ot_timeouts)
        ot_half[0] = 0
        # Batch B8: the overtime history is rebuilt from the possessions and
        # kicks after every event (rules.ot_history), so a kick the kicking
        # club keeps or returns for a touchdown enters it as the rule says.
        ot_start = len(possessions)
        ot_kicks_from = len(kickoffs)

        def history_now():
            return ot_history(possessions[ot_start:], kickoffs[ot_kicks_from:])

        ended = False
        if pro_bowl:
            spot, start_kind = PRO_BOWL_SPOT, "placement"
        else:
            spot, start_kind, offense, _opened, ended = kick_sequence(other(offense), offense, free_kick=False,
                                                                     half="OT", window=window, ot_label=ot_label)
        while not ended:
            record, score, next_kind, next_offense = possess(offense, window, "OT", spot, start_kind, history_now(),
                                                             ot_label)
            window -= record["seconds"]
            overtime_seconds += record["seconds"]
            history = history_now()
            if ot_status(history, game_type) == "end":
                break
            if window <= 0:
                if ot_status(history, game_type, expired=True) == "end":
                    break
                raise RuntimeError("postseason overtime exceeded the engine's %d-period bound"
                                   % RULES.postseason_ot_period_bound)
            if score:
                if pro_bowl:
                    spot, start_kind, offense = placed(record, score)
                else:
                    spot, start_kind, offense, _retained, ended = kicked_after(record, score, window, "OT", ot_label)
            else:
                spot, start_kind, offense = record["next_start"], next_kind, next_offense
        total += overtime_seconds

    # The game is over: a removal at its last boundary affects no later play.
    pause_state["pending"] = None
    if len(pause_state["history"]) < len(decisions):
        raise ValueError("continuation names a decision for a pause the game never reached")

    result = {
        "kernel_version": profile.kernel_version,
        "event_id": event_id,
        "game_type": game_type,
        "opening_receiver": opening_receiver,
        "final_score": {k: v["points"] for k, v in stats.items()},
        "possessions": possessions,
        "kickoffs": kickoffs,
        "play_ledger": play_ledger,
        "play_call_stats": play_call_stats,
        "team_stats": stats,
        "player_evidence": evidence,
        "injuries": injuries,
        "substitutions": substitutions,
        "pauses": pause_state["history"],
        "diagnostics": diagnostics,
        "terminated": True,
    }
    if xp_rule is not None:
        result["game_date"] = game_date
        result["extra_point_rule"] = xp_rule
    if trackers is not None:
        # Preseason only: the rotation as applied, by possession and kick.
        result["rotation"] = {tid: trackers[tid].receipt() for tid in rosters}
    if profile.record_base:
        # Kernel 2014.6 onward (append-only): the base, its manifest digest
        # and its cell rules, so every later audit can confirm it reads the
        # same base (runtime.calibration_base.base_for_result).
        result["calibration_base"] = calibration_base.record(cbase)
    if sequencing:
        # Batch B8 (append-only): every score in game order, rebuilt from the
        # possessions and kicks (runtime.play_detail.scoring_events); the
        # audit rebuilds it again and compares, never trusting the stored list.
        result["scoring_events"] = scoring_events(result)
    blocks = {team.team_id: {kind: json.loads(json.dumps(getattr(team, field)))
                             for field, kind in (("try_policy", "two_point"), ("kickoff_policy", "kickoff"))
                             if getattr(team, field, None) is not None} for team in (home, away)}
    if any(blocks.values()):
        # Batch B9 (append-only): each club's decision blocks as frozen on its
        # sheet, id and source text included; the outcome packet and every
        # draw read only their canonical form (scoring_decisions.canonical_policy).
        result["decision_policies"] = {tid: b for tid, b in blocks.items() if b}
    return result


# Ledger fields naming a participant, and which club (row key) he plays for.
REMOVAL_FIELDS = (("passer", "offense"), ("runner", "offense"), ("target", "offense"),
                  ("blocker", "offense"), ("kicker", "offense"), ("punter", "offense"),
                  ("long_snapper", "offense"), ("cover_player", "offense"),
                  ("tackler", "defense"), ("assist_tackler", "defense"), ("returner", "defense"))


def validate_result(result, base=None):
    """Invariant errors of a closed result; its ledger coherence is checked
    with the calibration base of the result's own kernel_version
    (play_detail.check_ledger), or `base` for a synthetic test base."""
    errors = []
    first_team = next(iter(result["team_stats"].values()), {})
    current = "extra_points_made" in first_team

    for team, score in result["final_score"].items():
        s = result["team_stats"][team]
        players = s["players"]

        if current:
            # Kernel 2014.6 batch B9: + 2 per two-point conversion.
            expected = (
                6 * s["touchdowns"] + s["extra_points_made"] + 2 * s.get("two_point_conversions", 0)
                + 3 * s["field_goals"] + 2 * s["safeties"]
            )
        else:
            # Legacy 2013.4/2013.5 results: every touchdown carried seven.
            expected = s["touchdowns"] * 7 + s["field_goals"] * 3
        if score != expected or s["points"] != score:
            errors.append("score ledger mismatch")
        if sum(p["passing_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("passing yardage mismatch")
        if sum(p["rushing_yards"] for p in players.values()) != s["rushing_yards"]:
            errors.append("rushing yardage mismatch")
        if sum(p["receiving_yards"] for p in players.values()) != s["passing_yards"]:
            errors.append("receiving yardage mismatch")
        if sum(p["sacks_allowed"] for p in players.values()) != s["sacks_allowed"]:
            errors.append("sack attribution mismatch")
        if sum(p["receptions"] for p in players.values()) != sum(p["completions"] for p in players.values()):
            errors.append("reception/completion mismatch")
        participation_recorded = bool(players) and all("offensive_snaps" in p for p in players.values())
        drive_passers = [p.get("passer") for p in result["possessions"] if p["team"] == team]
        if participation_recorded and drive_passers and all(drive_passers):
            # Kernel 2014.4 (E2): a backup can pass. Every thrower is a drive
            # passer, and the passer changes only after the previous one was
            # removed at an earlier drive's end.
            throwers = {pid for pid, p in players.items() if p["pass_attempts"] > 0}
            if not throwers <= set(drive_passers):
                errors.append("pass attempt credited to a player who was not a drive passer")
            removed_at = {i["player"]: i["drive"] for i in result.get("injuries", ())
                          if i.get("removed") and i.get("team") == team}
            # Preseason: a rotation block may bring on its own quarterback.
            rotated = {e["possession"]: (e["lineup"].get("QB") or [None])[0]
                       for e in ((result.get("rotation") or {}).get(team) or {}).get("applied", {}).get("offense", ())}
            previous = None
            for poss in (p for p in result["possessions"] if p["team"] == team):
                if previous is not None and poss["passer"] != previous:
                    if rotated.get(poss["number"]) == poss["passer"]:
                        previous = poss["passer"]
                        continue
                    if not removed_at.get(previous, poss["number"]) < poss["number"]:
                        errors.append("passer change without a removal")
                        break
                previous = poss["passer"]
            for pid, p in players.items():
                if (p["pass_attempts"] or p["rushing_attempts"] or p["targets"] or p["sacks_allowed"]) \
                        and not p["offensive_snaps"]:
                    errors.append("offensive credit without an offensive snap")
                    break
            for pid, p in players.items():
                if (p["tackles"] or p["sacks"] or p["defensive_interceptions"] or p["passes_defended"]) \
                        and not p["defensive_snaps"]:
                    errors.append("defensive credit without a defensive snap")
                    break
            for pid, p in players.items():
                if (p["punts"] or p["field_goals_attempted"] or p["extra_points_attempted"] or p["long_snaps"]
                        or p["kick_returns"] or p["punt_returns"] or p["special_teams_tackles"]) \
                        and not p["special_teams_snaps"]:
                    errors.append("special-teams credit without a special-teams snap")
                    break
        elif sum(p["pass_attempts"] > 0 for p in players.values()) > 1:
            errors.append("more than one passer without a game-passer change")
        if any(p["tackles"] != p["solo_tackles"] + p["assisted_tackles"] for p in players.values()):
            errors.append("tackle credit mismatch")
        opponent = next(t for t in result["team_stats"] if t != team)
        if sum(p["sacks"] for p in result["team_stats"][opponent]["players"].values()) != s["sacks_allowed"]:
            errors.append("defensive sack credit mismatch")
        if current and all("line_starts" in p for p in players.values()):
            # Kernel 2014.3 credit checks (legacy inputs without linemen or a
            # long snapper keep the old fallbacks).
            linemen = sum(usage.group(p["position"]) == "OL" for p in players.values())
            snapper = linemen or any(p["position"] == "LS" for p in players.values())
            if sum(p["line_starts"] for p in players.values()) != min(5, linemen):
                errors.append("line start count mismatch")
            # Kernel 2014.4: line starts are the game-opening front only; a
            # substitute lineman who entered later is on the field when he has
            # offensive snaps.
            if linemen and any(p["sacks_allowed"] and not (p["offensive_snaps"] if participation_recorded
                                                           else p["line_starts"])
                               for p in players.values()):
                errors.append("sack charged to a lineman off the field")
            kicks = [row for row in result.get("play_ledger", [])
                     if row.get("offense") == team and row.get("play_type") in ("kickoff", "free_kick", "punt")]
            if sum(p["special_teams_tackles"] for p in players.values()) != sum(
                    1 for row in kicks if row.get("cover_player")):
                errors.append("coverage tackle count mismatch")
            if any(row.get("outcome") == "returned" and not row.get("cover_player") for row in kicks):
                errors.append("returned kick without a coverage tackler")
            if any(row.get("cover_player") and row.get("outcome") != "returned" for row in kicks):
                errors.append("coverage tackle on a kick that was not returned")
            for pid, line in players.items():
                if line["special_teams_tackles"] != sum(1 for row in kicks if row.get("cover_player") == pid):
                    errors.append("coverage tackle credit differs from the ledger")
                    break
            snaps = s["punts"] + s["field_goal_attempts"] + s["extra_point_attempts"]
            if snapper and sum(p["long_snaps"] for p in players.values()) != snaps:
                errors.append("long snap count mismatch")
        if (
            sum(p["interceptions_thrown"] + p["fumbles_lost"] for p in players.values())
            != s["turnovers"]
        ):
            errors.append("turnover attribution mismatch")
        # Kernel 2014.6 batch B8: a touchdown scored on a kick return or by
        # the defense (non_offensive_score) is the club's, not a passer's or
        # rusher's (its player credit arrives with R15, batch B9).
        non_offensive = (sum(1 for k in result.get("kickoffs", ()) if k.get("touchdown") and k.get("scoring_team") == team)
                         + sum(1 for p in result["possessions"]
                               if (p.get("non_offensive_score") or {}).get("team") == team
                               and p["non_offensive_score"].get("kind") == "touchdown"))
        if (
            sum(p["passing_touchdowns"] + p["rushing_touchdowns"] for p in players.values()) + non_offensive
            != s["touchdowns"]
        ):
            errors.append("touchdown attribution mismatch")
        if "two_point_attempts" in s:
            # Kernel 2014.6 batch B9: every non-offensive and return
            # touchdown names its player (the blocked-kick credit by the
            # labelled even draw); two-point credits reconcile with the club's
            # conversions; every touchdown outside overtime has exactly one
            # try, an extra point or a two-point try.
            credited = sum(p.get(field, 0) for p in players.values() for field in set(scoring.PLAYER_TD_FIELD.values()))
            if credited != non_offensive:
                errors.append("return touchdown attribution mismatch")
            passing = sum(p.get("passing_two_point_conversions", 0) for p in players.values())
            if (passing != sum(p.get("receiving_two_point_conversions", 0) for p in players.values())
                    or passing + sum(p.get("rushing_two_point_conversions", 0) for p in players.values())
                    != s["two_point_conversions"]):
                errors.append("two-point conversion attribution mismatch")
            if s["two_point_conversions"] > s["two_point_attempts"]:
                errors.append("two-point conversions exceed attempts")
            tries_due = sum(1 for e in scoring_events(result)
                            if e["kind"] == "touchdown" and e["team"] == team and e["half"] != "OT")
            if s["extra_point_attempts"] + s["two_point_attempts"] != tries_due:
                errors.append("tries differ from the touchdowns outside overtime")
            if (s.get("defensive_touchdowns", 0) + s.get("special_teams_touchdowns", 0)) != non_offensive:
                errors.append("non-offensive touchdown counters differ from the scores")
        if current:
            if s["field_goals"] > s["field_goal_attempts"]:
                errors.append("field goals made exceed attempts")
            if not s["extra_points_made"] <= s["extra_point_attempts"] <= s["touchdowns"] - s.get(
                    "two_point_attempts", 0):
                errors.append("extra-point counts inconsistent")
            if sum(p["field_goals_made"] for p in players.values()) != s["field_goals"]:
                errors.append("field-goal made attribution mismatch")
            if sum(p["field_goals_attempted"] for p in players.values()) != s["field_goal_attempts"]:
                errors.append("field-goal attempt attribution mismatch")
            if sum(p["extra_points_made"] for p in players.values()) != s["extra_points_made"]:
                errors.append("extra-point made attribution mismatch")
            if sum(p["extra_points_attempted"] for p in players.values()) != s["extra_point_attempts"]:
                errors.append("extra-point attempt attribution mismatch")

    if return_touchdown_distance_errors(result):
        # Kernel 2014.6 batch B9 (R15; review round 2): every return
        # touchdown covers 1 to 109 yards.
        errors.append("return touchdown distance outside 1-109 yards")

    possessions = result["possessions"]
    elapsed = sum(p["seconds"] for p in possessions)
    removed_at = {(i["team"], i["player"]): i["drive"] for i in result.get("injuries", ())
                  if i.get("removed") and "drive" in i}
    if removed_at:
        # Kernel 2014.4 (E2): a removed player takes no later snap or credit.
        late = False
        for row in result.get("play_ledger", []):
            for field, side in REMOVAL_FIELDS:
                pid = row.get(field)
                onset = removed_at.get((row.get(side), pid)) if pid else None
                if onset is not None and row.get("drive", 0) > onset:
                    late = True
        if late:
            errors.append("removed player participates after his removal")
    if sum(s["time_of_possession"] for s in result["team_stats"].values()) != elapsed:
        errors.append("clock mismatch")
    if any(
        p["end_clock"] < 0 or p["start_clock"] < p["end_clock"]
        for p in possessions
    ):
        errors.append("invalid clock")

    scrimmage_expected = sum(p.get("scrimmage_plays", 0) for p in possessions)
    scrimmage_actual = sum(
        play.get("play_type") in {"pass", "run"} for play in result.get("play_ledger", [])
    )
    if scrimmage_actual != scrimmage_expected:
        errors.append("snap ledger mismatch")

    if any(
        play.get("sequence") != index
        for index, play in enumerate(result.get("play_ledger", []), 1)
    ):
        errors.append("play sequence mismatch")

    if not current:
        return errors

    regulation = [p for p in possessions if p.get("half") in (1, 2)]
    overtime = [p for p in possessions if p.get("half") == "OT"]
    for half in (1, 2):
        if sum(p["seconds"] for p in regulation if p["half"] == half) != RULES.quarter_seconds * 2:
            errors.append(f"half {half} possession seconds do not total 1800")
    period = (
        RULES.postseason_ot_seconds if result.get("game_type") == "postseason" else RULES.regular_ot_seconds
    )
    if result.get("game_type") != "postseason" and sum(p["seconds"] for p in overtime) > period:
        errors.append("overtime elapsed exceeds the period")
    if any(p["start_clock"] > 1800 > p["end_clock"] for p in regulation):
        errors.append("possession spans halftime")
    opening = regulation[0]["team"] if regulation else None
    second = next((p for p in regulation if p["half"] == 2), None)
    pro_bowl = result.get("game_type") == PRO_BOWL
    if pro_bowl:
        openers = [next((p for p in regulation if p.get("quarter") == q), None) for q in (1, 2, 3, 4)]
        if any(p is None or p["start_spot"] != PRO_BOWL_SPOT for p in openers) or not (
                openers[0]["team"] == openers[2]["team"] != openers[1]["team"] == openers[3]["team"]):
            errors.append("pro bowl quarter possession mismatch")
        if any(p["start_clock"] > b > p["end_clock"] for p in regulation for b in (2700, 900)):
            errors.append("possession spans a quarter")
    kicks = result.get("kickoffs", [])
    sequencing = bool(kicks) and all("chain" in k for k in kicks)
    if pro_bowl:
        pass
    elif sequencing:
        # Kernel 2014.6 batch B8: the second-half kicker is the opening
        # receiver, read from the kicks (a return touchdown on an opener
        # changes who possesses first, not who kicked).
        openers = {h: next((k for k in kicks if k["half"] == h and k["after_drive"] is None and k["chain"] == 1), None)
                   for h in (1, 2)}
        if None in openers.values() or openers[2]["kicking"] != openers[1]["receiving"]:
            errors.append("second half opened by the opening receiver")
    elif second is None or second["team"] == opening:
        errors.append("second half opened by the opening receiver")
    if sequencing:
        # Batch B8: the kick count derives from the scoring events: one
        # opener per half played, one chain after every score followed by a
        # kick (kickoff_after), and one further link after every return
        # touchdown that did not end the game.
        kick_touchdowns = [e for e in scoring_events(result) if e["source"] == "kick"]
        ot_played = bool(overtime) or any(k["half"] == "OT" for k in kicks)
        links = sum(1 for k in kicks if k["chain"] > 1)
        expected_kicks = (0 if pro_bowl else 2 + (1 if ot_played else 0)
                          + sum(1 for p in possessions if p.get("kickoff_after")) + links)
        ended_on_kick = bool(kicks) and kicks[-1].get("touchdown") and (
            not possessions or kicks[-1]["drive"] > possessions[-1]["number"])
        if links != len(kick_touchdowns) - (1 if ended_on_kick else 0):
            errors.append("kick chain count differs from the return touchdowns")
    else:
        expected_kicks = 0 if pro_bowl else 2 + (1 if overtime else 0) + sum(1 for p in possessions if p.get("kickoff_after"))
    if len(kicks) != expected_kicks:
        errors.append("kickoff count mismatch")
    for team, s in result["team_stats"].items():
        if s["kickoffs"] != sum(1 for k in kicks if k["kicking"] == team):
            errors.append("kickoff counter mismatch")
        if s["kick_returns"] != sum(1 for k in kicks if k["receiving"] == team and k["returned"]):
            errors.append("kick return counter mismatch")
        if s["drives"] != sum(1 for p in possessions if p["team"] == team):
            errors.append("drive counter mismatch")
    if possessions and all(p.get("start_spot") is not None for p in possessions):
        # Kernel 2013.7: the team chain counters are the drives' chains (from
        # kernel 2014.4 walked from the snap ledger, plus the real drive's
        # penalty first downs; check_ledger reconciles them with the rows).
        for team, s in result["team_stats"].items():
            mine = [p["chains"] for p in possessions if p["team"] == team]
            if (s["first_downs"] != sum(c[0] + c[1] for c in mine)
                    or s["third_down_attempts"] != sum(c[2] for c in mine)
                    or s["third_down_conversions"] != sum(c[3] for c in mine)):
                errors.append("chain counters differ from the drive chains")
    if has_chain_ledger(result):
        # Kernel 2014.4: the scrimmage first downs and third-down counts are
        # the snap ledger's own walk; only penalty first downs (chains[1])
        # have no rows.
        for team, s in result["team_stats"].items():
            rows = [r for r in result["play_ledger"] if r.get("offense") == team and r.get("play_type") in ("pass", "run")]
            penalty = sum(p["chains"][1] for p in possessions if p["team"] == team)
            third = [r for r in rows if r.get("down") == 3]
            if (s["first_downs"] != sum(bool(r.get("first_down")) for r in rows) + penalty
                    or s["third_down_attempts"] != len(third)
                    or s["third_down_conversions"] != sum(bool(r.get("first_down")) for r in third)):
                errors.append("chain counters differ from the snap ledger")
    # A window's final possession ends it: each half, or each Pro Bowl quarter.
    windows = ((("quarter", q), (4 - q) * RULES.quarter_seconds) for q in (1, 2, 3, 4)) if pro_bowl else (
        (("half", h), 1800 if h == 1 else 0) for h in (1, 2))
    for (kind, number), boundary in windows:
        rows = [p for p in regulation if p.get(kind) == number]
        finals = [p for p in rows if p.get("half_final")]
        if any(p["end_clock"] != boundary for p in finals):
            errors.append("half-final possession does not end its window")
        if len(finals) > 1 or (finals and finals[0] is not rows[-1]):
            errors.append(f"{kind} {number} continues after its half-final possession")
    if any(p.get("half_final") and p["end_clock"] != 0 for p in overtime):
        errors.append("half-final possession does not end its window")
    errors.extend(check_ledger(result, base))
    return errors
