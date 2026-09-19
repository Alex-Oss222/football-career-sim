import unittest
from runtime.packets import Packet, PacketConflict, resolve


class FakeJournal:
    """Synthetic test fake only. It provides no real privacy or durability."""
    def __init__(self):
        self.packets = {}
        self.results = {}
        self.fail_freeze = False
        self.fail_close = False

    def freeze_once(self, event_id, payload):
        if self.fail_freeze:
            raise OSError('synthetic persistence failure')
        return self.packets.setdefault(event_id, payload)

    def close_result(self, event_id, packet_digest, outcome):
        assert event_id in self.packets
        if self.fail_close:
            raise OSError('synthetic closure failure')
        original = self.results.setdefault(event_id, (packet_digest, outcome))
        if original != (packet_digest, outcome):
            raise PacketConflict('conflicting close')
        return original[1]


class PacketTests(unittest.TestCase):
    seed = b'synthetic-unit-test-seed-only-0001'

    def packet(self, **overrides):
        args = dict(event_id='synthetic-event-1', procedure_version='test-v1',
                    snapshot='synthetic-snapshot', inputs={'run_block': 'synthetic'},
                    modifiers={}, weights={'outcome-a': 3, 'outcome-b': 2, 'impossible': 0})
        args.update(overrides)
        return Packet.freeze(**args)

    def test_deterministic_replay_and_idempotent_closure(self):
        journal = FakeJournal()
        first = resolve(self.packet(), self.seed, journal)
        self.assertEqual(first, resolve(self.packet(), self.seed, journal))
        self.assertEqual(first, resolve(self.packet(), self.seed, FakeJournal()))
        self.assertNotEqual(first, 'impossible')
        self.assertEqual(len(journal.results), 1)

    def test_refuses_altered_snapshot_inputs_weights_or_version(self):
        journal = FakeJournal()
        resolve(self.packet(), self.seed, journal)
        for change in [dict(snapshot='other'), dict(inputs={'changed': True}),
                       dict(weights={'outcome-a': 1}), dict(procedure_version='v2')]:
            with self.subTest(change=change), self.assertRaises(PacketConflict):
                resolve(self.packet(**change), self.seed, journal)

    def test_recovery_after_failed_close_keeps_packet_and_seed(self):
        journal = FakeJournal()
        journal.fail_close = True
        with self.assertRaises(OSError):
            resolve(self.packet(), self.seed, journal)
        self.assertEqual(len(journal.packets), 1)
        self.assertFalse(journal.results)
        with self.assertRaises(PacketConflict):
            resolve(self.packet(), b'a-different-synthetic-career-seed', journal)
        journal.fail_close = False
        self.assertEqual(resolve(self.packet(), self.seed, journal),
                         resolve(self.packet(), self.seed, FakeJournal()))

    def test_failed_freeze_never_publishes_a_result(self):
        journal = FakeJournal()
        journal.fail_freeze = True
        with self.assertRaises(OSError):
            resolve(self.packet(), self.seed, journal)
        self.assertFalse(journal.results)

    def test_mutating_callers_input_does_not_change_frozen_packet(self):
        inputs = {'facts': ['original']}
        packet = self.packet(inputs=inputs)
        digest = packet.digest
        inputs['facts'].append('changed')
        self.assertEqual(packet.digest, digest)
        self.assertNotEqual(packet, self.packet(inputs=inputs))

    def test_equivalent_weight_scaling_and_order_preserve_packet(self):
        self.assertEqual(self.packet(), self.packet(weights={'impossible': 0, 'outcome-b': 4, 'outcome-a': 6}))

    def test_invalid_distribution_fails_before_journal(self):
        for weights in [{}, {'a': 0}, {'a': -1}, {'a': float('nan')}, {'a': True}, {'a': 1, 'b': 2**256}]:
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                self.packet(weights=weights)

    def test_no_packet_contents_in_repr(self):
        self.assertNotIn('run_block', repr(self.packet()))

    def test_team_labels_cannot_change_draw_with_same_distribution(self):
        # Upstream kernel symmetry remains unimplemented. This tests only the
        # sampler: no team/protagonist label can affect its event seed or weights.
        first = self.packet(inputs={'side_a': 'user', 'side_b': 'opponent'})
        swapped = self.packet(inputs={'side_a': 'opponent', 'side_b': 'user'})
        self.assertEqual(resolve(first, self.seed, FakeJournal()), resolve(swapped, self.seed, FakeJournal()))


if __name__ == '__main__':
    unittest.main()
