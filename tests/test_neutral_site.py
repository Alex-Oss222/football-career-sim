"""Kernel 2013.11: no home term for either team at a neutral venue."""
import unittest
from types import SimpleNamespace

from runtime.kernel import _edge


def _team(offense=2.0, defense=2.0):
    return SimpleNamespace(offense_anchor=offense, defense_anchor=defense)


class NeutralSiteTests(unittest.TestCase):
    def test_home_venue_keeps_the_home_term(self):
        home, away = _team(), _team()
        self.assertAlmostEqual(_edge(home, away, home, "home") - _edge(away, home, home, "home"), 0.008)

    def test_neutral_venue_gives_neither_team_the_home_term(self):
        home, away = _team(), _team()
        self.assertEqual(_edge(home, away, home, "neutral"), _edge(away, home, home, "neutral"))
        self.assertEqual(_edge(home, away, home, "neutral"), 0)

    def test_anchor_difference_is_unchanged_at_a_neutral_site(self):
        strong, weak = _team(offense=3.0), _team(defense=1.0)
        self.assertAlmostEqual(_edge(strong, weak, weak, "neutral"), 0.05)

    def test_default_venue_is_home(self):
        home, away = _team(), _team()
        self.assertEqual(_edge(home, away, home), _edge(home, away, home, "home"))


if __name__ == "__main__":
    unittest.main()
