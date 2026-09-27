import hashlib
import json
from pathlib import Path
import unittest

from scripts import recover_injury_projection as rec
from runtime.injuries import SEVERITY

ROOT = Path(__file__).resolve().parents[1]


def fake_ref(i):
    return hashlib.sha256(b"test-ref-%d" % i).hexdigest()


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(rec.MANIFEST.read_text(encoding="utf-8"))
        self.packets = [rec.build_packet(self.manifest, e) for e in self.manifest["recoveries"]]

    def test_registered_digests_and_model(self):
        self.assertEqual(self.manifest["model_sha256"], rec.model_digest())
        for packet in self.packets:
            self.assertEqual(self.manifest["packet_sha256"][packet["event_id"]], rec.packet_digest(packet))
            self.assertNotIn("Jacksonville", json.dumps(packet))

    def test_draw_is_deterministic_and_inside_the_model(self):
        for packet in self.packets:
            for i in range(200):
                a = rec.resolve(fake_ref(i), packet)
                self.assertEqual(a, rec.resolve(fake_ref(i), packet))
                band = next(b for b in SEVERITY if b[1] == a["severity"])
                self.assertTrue(band[2] <= a["return_days"] <= band[3])
                self.assertGreaterEqual(a["return_days"], packet["min_return_days"])
                self.assertEqual(a["reassessment_days"], min(max(a["return_days"] // 3, 1), 7))

    def test_band_frequencies_match_the_model(self):
        packet = dict(self.packets[0], min_return_days=0)
        counts = {}
        n = 4000
        for i in range(n):
            s = rec.resolve(fake_ref(i), packet)["severity"]
            counts[s] = counts.get(s, 0) + 1
        previous = 0.0
        for ceiling, name, _, _ in SEVERITY:
            expected = ceiling - previous
            previous = ceiling
            self.assertAlmostEqual(counts.get(name, 0) / n, expected, delta=0.03)


if __name__ == "__main__":
    unittest.main()
