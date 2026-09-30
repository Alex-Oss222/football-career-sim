import random
import unittest

from runtime.player_progression import (
    DIRECTIONS,
    DevelopmentCase,
    ObservedTraitUpdate,
    TransitionPrior,
    influenced_traits,
    resolve_private_change,
    validate_development_case,
    validate_observed_update,
)


class PlayerProgressionTests(unittest.TestCase):
    def test_qb_case_accepts_football_mechanism(self):
        case = DevelopmentCase(
            player_id="Kirk Cousins",
            position="QB",
            trait="coverage_rotation_confirmation",
            mechanisms=("film_study", "game_experience", "scheme_continuity"),
            evidence_ids=("2013-exit-review", "2013-film-index"),
            confidence="medium",
            rationale=(
                "A full season of the same coverage language gives a basis to "
                "test faster post-snap confirmation."
            ),
        )
        validate_development_case(case)
        self.assertIn(
            "progression_timing",
            influenced_traits("QB", case.trait),
        )

    def test_age_alone_cannot_create_decline(self):
        case = DevelopmentCase(
            player_id="Veteran",
            position="CB",
            trait="long_speed",
            mechanisms=("age_context",),
            evidence_ids=("age-2014",),
            confidence="low",
            rationale="Age only.",
        )
        with self.assertRaisesRegex(ValueError, "sole development mechanism"):
            validate_development_case(case)

    def test_scheme_familiarity_cannot_make_player_faster(self):
        case = DevelopmentCase(
            player_id="Corner",
            position="CB",
            trait="long_speed",
            mechanisms=("scheme_continuity", "game_experience"),
            evidence_ids=("2013-exit-review",),
            confidence="medium",
            rationale="The player knows the defense better.",
        )
        with self.assertRaisesRegex(ValueError, "physical trait"):
            validate_development_case(case)

    def test_private_draw_requires_complete_calibrated_prior(self):
        case = DevelopmentCase(
            player_id="Receiver",
            position="WR",
            trait="route_pacing",
            mechanisms=("deliberate_practice", "coaching_correction"),
            evidence_ids=("film-1",),
            confidence="medium",
            rationale="Route pacing is the coached target.",
        )
        prior = TransitionPrior(
            probabilities={
                "substantial_regression": 0.0,
                "slight_regression": 0.1,
                "stable": 0.4,
                "slight_improvement": 0.4,
                "substantial_improvement": 0.1,
            },
            calibration_id="test-only",
        )
        change = resolve_private_change(case, prior, random.Random(1))
        self.assertIn(change.direction, DIRECTIONS)
        self.assertEqual(change.calibration_id, "test-only")

    def test_observed_state_is_separate_from_private_resolution(self):
        update = ObservedTraitUpdate(
            player_id="Kirk Cousins",
            position="QB",
            trait="protection_identification",
            observed_direction="slight_improvement",
            confidence="medium",
            visibility="noncontact_observed",
            evidence_ids=("2014-ota-session-1",),
            explanation=(
                "He identified and communicated the changed pressure answer "
                "more consistently in the observed OTA work."
            ),
        )
        validate_observed_update(update)


if __name__ == "__main__":
    unittest.main()
