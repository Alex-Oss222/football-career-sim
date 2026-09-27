"""One shared, cached synthetic 2013.6 sample for the kernel test modules.

Resolving games is the slow part of the suite (the Railway image runs the
whole suite on every deploy), so the coherence and band tests share one
250-game sample computed once per process. Synthetic seeds only; the private
service is never contacted.
"""
from functools import lru_cache

from runtime.kernel import TeamInput, resolve_game
from support_rosters import game_day_roster

SEED = b"synthetic-calibration-seed-not-career-state"
SAMPLE_SIZE = 250


def team(prefix):
    roster = game_day_roster(prefix)
    return TeamInput(prefix, tuple(p.player_id for p in roster), roster=roster)


@lru_cache(maxsize=1)
def sample():
    a, b = team("A"), team("B")
    return tuple(
        resolve_game(a, b, seed=SEED + b"-%05d" % i, event_id=f"sample-2013-6-{i}")
        for i in range(SAMPLE_SIZE)
    )
