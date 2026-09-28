import unittest

from runtime.play_detail import _seat_spikes
from synthetic_games import sample


def clock_running(row):
    return row.get("play_type") == "run" or row.get("sack") or (
        row.get("play_type") == "pass" and row.get("completion") and not row.get("spike"))


def misplaced_spikes(ledger):
    """Spikes that would stop an already stopped clock: a drive's first snap,
    or a snap right after an incompletion or another spike."""
    bad = []
    for index, row in enumerate(ledger):
        if not row.get("spike"):
            continue
        prev = ledger[index - 1] if index else None
        same_drive = prev is not None and prev.get("drive") == row.get("drive") and prev.get(
            "play_type") in ("run", "pass")
        if not same_drive or not clock_running(prev):
            bad.append((row.get("drive"), row.get("snap_in_drive")))
    return bad


class SpikeSeatingTests(unittest.TestCase):
    def test_first_snap_spike_moves_behind_a_running_clock(self):
        rows = [("spike", False, 0), ("att", False, 0), ("run", True, 4), ("att", True, 6), ("catch", True, 10)]
        self.assertEqual([r[0] for r in _seat_spikes(rows, 4)], ["att", "run", "spike", "att", "catch"])

    def test_spike_after_incompletion_moves_and_totals_are_unchanged(self):
        rows = [("run", True, 3), ("att", False, 0), ("spike", False, 0), ("att", True, 7), ("run", True, 2)]
        seated = _seat_spikes(rows, 5)
        self.assertEqual([r[0] for r in seated], ["run", "spike", "att", "att", "run"])
        self.assertEqual(sorted(seated), sorted(rows))

    def test_terminal_tail_never_moves(self):
        rows = [("spike", False, 0), ("run", True, 5), ("kneel", True, -1), ("run", True, 1)]
        self.assertEqual(_seat_spikes(rows, 2)[2:], rows[2:])

    def test_synthetic_sample_has_no_misplaced_spike_when_a_running_snap_exists(self):
        spikes = misplaced = 0
        for result in sample():
            ledger = result.get("play_ledger") or []
            spikes += sum(1 for row in ledger if row.get("spike"))
            for drive, snap in misplaced_spikes(ledger):
                rows = [r for r in ledger if r.get("drive") == drive and r.get("play_type") in ("run", "pass")]
                if any(clock_running(r) for r in rows if not r.get("spike")):
                    misplaced += 1
        self.assertGreater(spikes, 0)
        self.assertEqual(misplaced, 0)


if __name__ == "__main__":
    unittest.main()
