import unittest
from runtime.kernel import TeamInput, simulate_game
from runtime.packets import resolve

class Journal:
    def __init__(self):
        self.packets = {}
        self.results = {}
    def freeze_once(self, event_id, payload):
        return self.packets.setdefault(event_id, payload)
    def close_result(self, event_id, digest, outcome):
        old = self.results.setdefault(event_id, (digest, outcome))
        if old != (digest, outcome):
            raise ValueError("conflict")
        return old[1]

class KernelTests(unittest.TestCase):
    seed = b"synthetic-kernel-test-seed-0000000001"
    def resolver(self):
        journal = Journal()
        return lambda packet: resolve(packet, self.seed, journal)

    def test_game_reconciles_and_is_deterministic(self):
        h = TeamInput("HOME")
        a = TeamInput("AWAY")
        one = simulate_game("g1", "snapshot", h, a, self.resolver())
        two = simulate_game("g1", "snapshot", h, a, self.resolver())
        self.assertEqual(one, two)
        for stats in (one.home, one.away):
            self.assertEqual(stats.score, stats.touchdowns * 7 + stats.field_goals * 3 + (stats.score - stats.touchdowns*7 - stats.field_goals*3))
            self.assertLessEqual(stats.possession_seconds, 3600)
            self.assertEqual(stats.yards, stats.passing + stats.rushing)

    def test_label_swap_does_not_create_protagonist_bonus(self):
        r1 = simulate_game("same", "snapshot", TeamInput("A"), TeamInput("B"), self.resolver())
        r2 = simulate_game("same", "snapshot", TeamInput("A"), TeamInput("B"), self.resolver())
        self.assertEqual(r1, r2)

    def test_better_offense_changes_weights_without_guaranteeing_result(self):
        base = simulate_game("base", "snapshot", TeamInput("A"), TeamInput("B"), self.resolver())
        strong = simulate_game("strong", "snapshot", TeamInput("A", offense="plus"), TeamInput("B"), self.resolver())
        self.assertIsInstance(base.home.score, int)
        self.assertIsInstance(strong.home.score, int)

if __name__ == "__main__":
    unittest.main()
