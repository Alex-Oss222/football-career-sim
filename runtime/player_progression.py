"""Position-specific offseason player-development primitives.

This module deliberately does not create an overall rating, an age curve, or a
magic coaching multiplier. It defines the football dimensions a progression
resolver may change, validates causal development cases, and keeps a private
latent change separate from public/staff observations.

Probability calibration is intentionally external. A caller must supply a
TransitionPrior derived from an approved calibration source before a latent
change can be sampled. This prevents an implementation detail from turning an
unsupported development hunch into simulation canon.
"""
from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Mapping


DIRECTIONS = (
    "substantial_regression",
    "slight_regression",
    "stable",
    "slight_improvement",
    "substantial_improvement",
)
CONFIDENCE_LEVELS = ("low", "medium", "high")
VISIBILITY_LEVELS = (
    "unobserved",
    "reported",
    "noncontact_observed",
    "padded_observed",
    "game_observed",
)

POSITION_GROUP = {
    "QB": "QB",
    "RB": "RB",
    "FB": "RB",
    "WR": "WR",
    "TE": "TE",
    "OT": "OL",
    "G": "OL",
    "OG": "OL",
    "C": "OL",
    "OL": "OL",
    "DE": "DL",
    "DT": "DL",
    "NT": "DL",
    "DL": "DL",
    "OLB": "LB",
    "ILB": "LB",
    "LB": "LB",
    "CB": "CB",
    "DB": "CB",
    "S": "S",
    "FS": "S",
    "SS": "S",
    "K": "K",
    "P": "P",
    "LS": "LS",
}

# Traits are grouped by the kind of change they represent. The same physical
# trait name is not assumed to mean the same football consequence at every
# position.
TRAITS_BY_GROUP: dict[str, dict[str, tuple[str, ...]]] = {
    "QB": {
        "physical": (
            "arm_strength", "throwing_velocity_capacity", "functional_mobility",
            "short_area_quickness", "play_strength",
        ),
        "technical": (
            "drop_footwork", "base_and_reset", "lower_upper_sequencing",
            "throwing_mechanics", "release_efficiency", "pocket_movement",
            "pressure_escape_mechanics",
            "ball_placement_short", "ball_placement_intermediate",
            "ball_placement_deep", "ball_placement_outside_numbers",
        ),
        "processing": (
            "pre_snap_structure_identification", "coverage_rotation_confirmation",
            "pressure_identification", "protection_identification",
            "blitz_hot_answer", "progression_timing", "anticipation",
            "decision_under_pressure", "situational_risk_management",
        ),
        "system": (
            "terminology_and_playbook", "concept_rules", "protection_calls",
            "checks_and_adjustments", "cadence_and_hard_count", "tempo_command",
            "receiver_timing_and_landmarks",
        ),
        "consistency": (
            "mechanics_under_pressure", "decision_repeatability",
            "late_game_execution", "ball_security",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "offense_command_scope", "audible_scope", "protection_control_scope",
        ),
    },
    "RB": {
        "physical": (
            "burst", "long_speed", "short_area_quickness", "contact_balance",
            "functional_strength",
        ),
        "technical": (
            "run_track_discipline", "cut_efficiency", "ball_security_technique",
            "pass_protection_base", "pass_protection_strike", "route_detail",
            "catch_technique", "short_yardage_body_position",
        ),
        "processing": (
            "run_concept_vision", "blocking_surface_read", "patience_and_tempo",
            "protection_recognition", "pressure_scan", "coverage_recognition",
        ),
        "system": (
            "run_concept_rules", "protection_rules", "route_adjustments",
            "motion_and_alignment_knowledge",
        ),
        "consistency": (
            "read_repeatability", "ball_security", "late_rep_execution",
            "protection_reliability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "down_and_distance_scope", "third_down_scope", "special_teams_scope",
        ),
    },
    "WR": {
        "physical": (
            "acceleration", "long_speed", "short_area_quickness",
            "functional_strength", "play_balance",
        ),
        "technical": (
            "press_release_plan", "release_footwork", "release_hand_combat",
            "stem_manipulation", "route_pacing", "break_efficiency",
            "catch_technique", "contested_catch_technique", "ball_tracking",
            "sideline_technique", "stalk_blocking", "crack_blocking",
        ),
        "processing": (
            "leverage_recognition", "coverage_recognition", "zone_spacing",
            "route_adjustment", "option_route_decision", "scramble_adjustment",
        ),
        "system": (
            "formation_and_motion_knowledge", "route_landmarks",
            "concept_spacing_rules", "quarterback_timing",
        ),
        "consistency": (
            "release_repeatability", "route_depth_repeatability",
            "catch_finish_repeatability", "assignment_reliability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "alignment_scope", "route_tree_scope", "special_teams_scope",
        ),
    },
    "TE": {
        "physical": (
            "acceleration", "short_area_quickness", "functional_strength",
            "contact_balance", "play_balance",
        ),
        "technical": (
            "release_technique", "route_detail", "break_efficiency",
            "catch_technique", "ball_tracking", "inline_run_block_base",
            "inline_hand_placement", "move_blocking", "second_level_blocking",
            "pass_protection_set", "chip_and_release_timing",
        ),
        "processing": (
            "coverage_recognition", "route_adjustment", "box_and_front_recognition",
            "block_target_identification", "protection_recognition",
        ),
        "system": (
            "alignment_knowledge", "route_landmarks", "run_block_rules",
            "protection_rules", "motion_and_shift_knowledge",
        ),
        "consistency": (
            "route_assignment_reliability", "block_fit_repeatability",
            "catch_finish_repeatability", "late_rep_execution",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "inline_scope", "move_scope", "detached_scope", "protection_scope",
        ),
    },
    "OL": {
        "physical": (
            "functional_strength", "anchor_strength", "foot_quickness",
            "short_area_mobility", "play_balance",
        ),
        "technical": (
            "pass_set_angle", "kick_slide_efficiency", "lateral_recovery",
            "hand_placement", "punch_timing", "independent_hands", "anchor_technique",
            "recovery_technique", "pad_level_and_leverage", "drive_blocking",
            "reach_blocking", "combination_blocking", "pulling_technique",
            "second_level_blocking", "snap_mechanics",
        ),
        "processing": (
            "front_identification", "protection_recognition", "twist_stunt_recognition",
            "blitz_exchange_recognition", "run_fit_target_recognition",
        ),
        "system": (
            "protection_rules", "combination_calls", "run_concept_rules",
            "quarterback_center_communication", "line_adjustment_language",
        ),
        "consistency": (
            "set_repeatability", "hand_fit_repeatability", "assignment_reliability",
            "penalty_control", "late_rep_execution",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "position_versatility", "protection_call_scope", "sixth_ol_scope",
        ),
    },
    "DL": {
        "physical": (
            "get_off_burst", "functional_strength", "anchor_strength",
            "lateral_quickness", "change_of_direction",
        ),
        "technical": (
            "stance_and_get_off", "strike_timing", "hand_placement",
            "pad_level_and_leverage", "shed_technique", "double_team_technique",
            "bull_rush", "speed_to_power", "rip", "swim", "club",
            "chop", "long_arm", "counter_move", "rush_lane_control",
        ),
        "processing": (
            "block_recognition", "run_pass_key", "gap_discipline",
            "pass_rush_plan", "protection_tendency_recognition",
            "screen_draw_recognition",
        ),
        "system": (
            "front_and_alignment_rules", "run_fit_rules", "stunt_game_rules",
            "contain_rules", "substitution_and_check_language",
        ),
        "consistency": (
            "get_off_repeatability", "pad_level_repeatability", "gap_integrity",
            "rush_plan_discipline", "late_rep_execution",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "alignment_scope", "early_down_scope", "passing_down_scope",
        ),
    },
    "LB": {
        "physical": (
            "range", "short_area_quickness", "functional_strength",
            "closing_burst", "change_of_direction",
        ),
        "technical": (
            "block_destruction", "hand_use", "pursuit_angle", "tackling",
            "zone_drop_technique", "man_coverage_technique", "blitz_entry",
            "pass_rush_hand_use",
        ),
        "processing": (
            "run_key_recognition", "backfield_flow_read", "gap_fit_recognition",
            "play_action_recognition", "route_recognition", "pattern_match_rules",
            "pressure_timing", "screen_draw_recognition",
        ),
        "system": (
            "front_check_knowledge", "fit_exchange_knowledge", "coverage_checks",
            "pressure_checks", "communication",
        ),
        "consistency": (
            "fit_discipline", "tackle_finish_repeatability",
            "coverage_assignment_reliability", "pursuit_discipline",
            "late_rep_execution",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "base_down_scope", "subpackage_scope", "pressure_scope",
            "special_teams_scope",
        ),
    },
    "CB": {
        "physical": (
            "acceleration", "long_speed", "recovery_speed", "short_area_quickness",
            "hip_transition_capacity", "functional_strength",
        ),
        "technical": (
            "press_stance", "press_footwork", "jam_timing", "mirror_technique",
            "off_man_footwork", "bail_technique", "hip_transition_technique",
            "leverage_maintenance", "recovery_technique", "play_through_hands",
            "ball_tracking", "tackling", "block_defeat",
        ),
        "processing": (
            "route_recognition", "receiver_tendency_recognition", "eye_discipline",
            "pattern_match_rules", "route_combination_recognition",
            "run_pass_recognition",
        ),
        "system": (
            "coverage_checks", "leverage_rules", "zone_landmarks",
            "match_communication", "formation_adjustments",
        ),
        "consistency": (
            "leverage_discipline", "eye_discipline_repeatability",
            "assignment_reliability", "catch_point_finish",
            "tackle_finish_repeatability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "outside_scope", "slot_scope", "travel_scope", "special_teams_scope",
        ),
    },
    "S": {
        "physical": (
            "range", "acceleration", "long_speed", "short_area_quickness",
            "functional_strength",
        ),
        "technical": (
            "pedal_and_open", "angle_technique", "man_coverage_technique",
            "zone_spacing", "ball_tracking", "tackling", "block_defeat",
            "run_support_entry",
        ),
        "processing": (
            "formation_recognition", "route_combination_recognition",
            "coverage_rotation", "pattern_match_rules", "play_action_recognition",
            "deep_field_positioning", "run_pass_recognition",
        ),
        "system": (
            "coverage_checks", "rotation_rules", "match_communication",
            "front_fit_communication", "formation_adjustments",
        ),
        "consistency": (
            "depth_discipline", "angle_repeatability", "assignment_reliability",
            "tackle_finish_repeatability", "late_rep_execution",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_reps", "body_composition",
        ),
        "role": (
            "post_scope", "split_field_scope", "box_scope", "slot_scope",
            "special_teams_scope",
        ),
    },
    "K": {
        "physical": ("leg_strength", "lower_body_explosiveness", "mobility"),
        "technical": (
            "approach_consistency", "plant_foot", "swing_path", "contact_point",
            "launch_control", "kickoff_directional_control", "onside_technique",
        ),
        "processing": (
            "wind_field_adjustment", "rush_timing_awareness",
            "situational_targeting",
        ),
        "system": (
            "snap_hold_operation", "protection_timing", "coverage_targeting",
        ),
        "consistency": (
            "operation_repeatability", "contact_repeatability",
            "pressure_repeatability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_kicks", "body_composition",
        ),
        "role": (
            "field_goal_range_scope", "kickoff_scope", "onside_scope",
        ),
    },
    "P": {
        "physical": ("leg_strength", "lower_body_explosiveness", "mobility"),
        "technical": (
            "catch_and_mold", "drop_location", "steps_and_get_off", "contact_point",
            "hangtime_distance_control", "directional_location",
            "plus_territory_control",
        ),
        "processing": (
            "rush_timing_awareness", "field_position_targeting",
            "returner_targeting",
        ),
        "system": (
            "snap_operation", "protection_timing", "coverage_targeting",
        ),
        "consistency": (
            "drop_repeatability", "operation_repeatability",
            "pressure_repeatability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_punts", "body_composition",
        ),
        "role": (
            "open_field_punt_scope", "plus_territory_scope", "holder_scope",
        ),
    },
    "LS": {
        "physical": (
            "functional_strength", "mobility", "short_area_quickness",
        ),
        "technical": (
            "set_position", "release_mechanics", "snap_velocity", "snap_accuracy",
            "spiral_and_rotation", "punt_snap_trajectory",
            "field_goal_snap_trajectory", "protection_transition",
            "coverage_tackling",
        ),
        "processing": (
            "protection_recognition", "rush_timing_awareness",
            "coverage_lane_recognition",
        ),
        "system": (
            "punt_operation_rhythm", "field_goal_operation_rhythm",
            "protection_calls",
        ),
        "consistency": (
            "target_repeatability", "velocity_repeatability",
            "pressure_repeatability",
        ),
        "conditioning": (
            "work_capacity", "recovery_between_snaps", "body_composition",
        ),
        "role": (
            "punt_snap_scope", "placekick_snap_scope", "coverage_scope",
        ),
    },
}

CAUSE_DOMAINS: dict[str, frozenset[str]] = {
    "deliberate_practice": frozenset(
        {"technical", "processing", "system", "consistency"}
    ),
    "live_reps": frozenset(
        {"technical", "processing", "system", "consistency", "role"}
    ),
    "film_study": frozenset({"processing", "system"}),
    "scheme_continuity": frozenset(
        {"processing", "system", "consistency", "role"}
    ),
    "coaching_correction": frozenset(
        {"technical", "processing", "system", "consistency"}
    ),
    "strength_training": frozenset({"physical", "conditioning"}),
    "conditioning_training": frozenset({"conditioning", "consistency"}),
    "body_composition_change": frozenset({"physical", "conditioning"}),
    "injury_recovery": frozenset(
        {"physical", "conditioning", "consistency"}
    ),
    "injury_limitation": frozenset(
        {"physical", "technical", "conditioning", "consistency", "role"}
    ),
    "accumulated_mileage": frozenset(
        {"physical", "conditioning", "consistency"}
    ),
    "role_change": frozenset({"role", "system", "consistency"}),
    "technique_transfer": frozenset({"technical", "consistency"}),
    "game_experience": frozenset(
        {"technical", "processing", "system", "consistency", "role"}
    ),
    "player_adaptation": frozenset(
        {"technical", "processing", "system", "consistency", "role"}
    ),
    "medical_restriction": frozenset(
        {"physical", "technical", "conditioning", "consistency", "role"}
    ),
    # Age is context, never a sufficient football mechanism on its own.
    "age_context": frozenset({"physical", "conditioning", "consistency"}),
}

# Causal links, not automatic rating changes. A source trait can alter the
# effective expression of a target trait without changing the target's
# underlying physical ceiling. Material target-state changes still need evidence.
INTERDEPENDENCIES: dict[tuple[str, str], tuple[str, ...]] = {
    ("QB", "coverage_rotation_confirmation"): (
        "progression_timing", "decision_under_pressure",
    ),
    ("QB", "drop_footwork"): (
        "ball_placement_short", "ball_placement_intermediate",
        "ball_placement_deep",
    ),
    ("QB", "protection_identification"): (
        "decision_under_pressure", "pocket_movement",
    ),
    ("WR", "leverage_recognition"): (
        "press_release_plan", "stem_manipulation", "route_pacing",
    ),
    ("WR", "functional_strength"): (
        "release_hand_combat", "stalk_blocking",
    ),
    ("RB", "run_concept_vision"): (
        "patience_and_tempo", "cut_efficiency",
    ),
    ("OL", "twist_stunt_recognition"): (
        "lateral_recovery", "assignment_reliability",
    ),
    ("DL", "block_recognition"): (
        "gap_discipline", "shed_technique",
    ),
    ("DL", "hand_placement"): (
        "shed_technique", "bull_rush", "long_arm",
    ),
    ("LB", "run_key_recognition"): (
        "pursuit_angle", "fit_discipline",
    ),
    ("CB", "route_recognition"): (
        "leverage_maintenance", "recovery_technique",
    ),
    ("CB", "eye_discipline"): (
        "pattern_match_rules", "leverage_discipline",
    ),
    ("S", "route_combination_recognition"): (
        "deep_field_positioning", "angle_technique",
    ),
    ("S", "play_action_recognition"): ("depth_discipline",),
    ("K", "snap_hold_operation"): ("operation_repeatability",),
    ("P", "drop_location"): (
        "contact_point", "directional_location", "hangtime_distance_control",
    ),
    ("LS", "release_mechanics"): ("snap_velocity", "snap_accuracy"),
}


@dataclass(frozen=True)
class DevelopmentCase:
    """A causal case for one trait entering an offseason transition draw."""

    player_id: str
    position: str
    trait: str
    mechanisms: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    confidence: str
    rationale: str
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransitionPrior:
    """Externally calibrated probabilities for the five allowed outcomes."""

    probabilities: Mapping[str, float]
    calibration_id: str


@dataclass(frozen=True)
class PrivateTraitChange:
    """Hidden latent resolution. Do not write this directly to coach-facing files."""

    case: DevelopmentCase
    direction: str
    calibration_id: str


@dataclass(frozen=True)
class ObservedTraitUpdate:
    """What staff/user can currently support about a trait after observation."""

    player_id: str
    position: str
    trait: str
    observed_direction: str
    confidence: str
    visibility: str
    evidence_ids: tuple[str, ...]
    explanation: str


def position_group(position: str) -> str:
    try:
        return POSITION_GROUP[position.upper()]
    except (AttributeError, KeyError) as exc:
        raise ValueError(f"unsupported position: {position!r}") from exc


def trait_catalog(position: str) -> dict[str, tuple[str, ...]]:
    return TRAITS_BY_GROUP[position_group(position)]


def trait_domain(position: str, trait: str) -> str:
    for domain, traits in trait_catalog(position).items():
        if trait in traits:
            return domain
    raise ValueError(f"{trait!r} is not a registered trait for {position}")


def influenced_traits(position: str, trait: str) -> tuple[str, ...]:
    return INTERDEPENDENCIES.get((position_group(position), trait), ())


def validate_development_case(case: DevelopmentCase) -> None:
    if not case.player_id.strip():
        raise ValueError("player_id is required")
    domain = trait_domain(case.position, case.trait)
    if case.confidence not in CONFIDENCE_LEVELS:
        raise ValueError("unknown confidence level")
    if not case.rationale.strip():
        raise ValueError("football rationale is required")
    if not case.mechanisms:
        raise ValueError("at least one development mechanism is required")
    unknown = sorted(set(case.mechanisms) - set(CAUSE_DOMAINS))
    if unknown:
        raise ValueError("unknown mechanism(s): " + ", ".join(unknown))
    if set(case.mechanisms) == {"age_context"}:
        raise ValueError("age cannot be the sole development mechanism")
    if not case.evidence_ids:
        raise ValueError(
            "development case requires dated/source evidence identifiers"
        )
    if domain == "physical" and set(case.mechanisms) <= {
        "film_study",
        "scheme_continuity",
        "game_experience",
        "role_change",
        "age_context",
    }:
        raise ValueError(
            "knowledge, experience or role alone cannot change a physical trait"
        )
    if not any(domain in CAUSE_DOMAINS[cause] for cause in case.mechanisms):
        raise ValueError(
            f"mechanisms {case.mechanisms!r} do not support a {domain} change"
        )


def validate_prior(prior: TransitionPrior) -> None:
    if not prior.calibration_id.strip():
        raise ValueError("calibration_id is required")
    keys = set(prior.probabilities)
    if keys != set(DIRECTIONS):
        missing = set(DIRECTIONS) - keys
        extra = keys - set(DIRECTIONS)
        raise ValueError(
            f"prior keys mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
        )
    values = tuple(float(prior.probabilities[key]) for key in DIRECTIONS)
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("transition probabilities must be in [0, 1]")
    if abs(sum(values) - 1.0) > 1e-9:
        raise ValueError("transition probabilities must sum to 1")


def resolve_private_change(
    case: DevelopmentCase, prior: TransitionPrior, rng: Random
) -> PrivateTraitChange:
    """Sample one hidden change from an approved/calibrated prior.

    The function intentionally has no default prior. Age, draft position,
    potential, or role may not silently manufacture a probability table.
    """

    validate_development_case(case)
    validate_prior(prior)
    draw = rng.random()
    running = 0.0
    for direction in DIRECTIONS:
        running += float(prior.probabilities[direction])
        if draw <= running:
            return PrivateTraitChange(case, direction, prior.calibration_id)
    return PrivateTraitChange(case, DIRECTIONS[-1], prior.calibration_id)


def validate_observed_update(update: ObservedTraitUpdate) -> None:
    trait_domain(update.position, update.trait)
    if update.observed_direction not in DIRECTIONS:
        raise ValueError("unknown observed direction")
    if update.confidence not in CONFIDENCE_LEVELS:
        raise ValueError("unknown confidence level")
    if update.visibility not in VISIBILITY_LEVELS:
        raise ValueError("unknown visibility level")
    if update.visibility != "unobserved" and not update.evidence_ids:
        raise ValueError("an observed/reported update requires evidence")
    if not update.explanation.strip():
        raise ValueError("football explanation is required")


__all__ = [
    "CAUSE_DOMAINS",
    "CONFIDENCE_LEVELS",
    "DIRECTIONS",
    "DevelopmentCase",
    "INTERDEPENDENCIES",
    "ObservedTraitUpdate",
    "POSITION_GROUP",
    "PrivateTraitChange",
    "TRAITS_BY_GROUP",
    "TransitionPrior",
    "VISIBILITY_LEVELS",
    "influenced_traits",
    "position_group",
    "resolve_private_change",
    "trait_catalog",
    "trait_domain",
    "validate_development_case",
    "validate_observed_update",
    "validate_prior",
]
