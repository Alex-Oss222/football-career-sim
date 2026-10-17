"""Stage the 2014 player_state gate on a copy of the checkout.

Kernel 2014.6 release: the 2014 release is accepted except the player_state
gate, which reads BLOCKED until the 2014 bind from merged main (release step
6 commits library/data/2014_player_state_binding.json and sets the gate
VERIFIED). A test of either side stages that side on a copy, so it proves the
same thing before and after the bind. The real runtime/season_readiness.json
is never edited.
"""
import json
from pathlib import Path
import shutil
import tempfile

from runtime import seasons
from runtime.seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
IGNORED = ('.git', '.sim_cache', '__pycache__', '.pytest_cache')
BINDING = 'library/data/2014_player_state_binding.json'


def _player_state_gate(root):
    path = root / 'runtime/season_readiness.json'
    data = json.loads(path.read_text())
    gate = next(g for g in data['seasons']['2014']['gates'] if g['id'] == 'player_state')
    return path, data, gate


def stage_bound_release(root):
    """After the bind: the gate reads VERIFIED with a stand-in binding file."""
    path, data, gate = _player_state_gate(root)
    (root / BINDING).write_text(json.dumps({'staged': 'test stand-in for the bind'}))
    gate.update(status='VERIFIED', evidence=[BINDING])
    path.write_text(json.dumps(data, indent=2))
    return root


def stage_unbound_release(root):
    """Before the bind: the gate reads BLOCKED and no binding file exists."""
    path, data, gate = _player_state_gate(root)
    (root / BINDING).unlink(missing_ok=True)
    gate.update(status='BLOCKED', evidence=[e for e in gate.get('evidence', []) if e != BINDING])
    path.write_text(json.dumps(data, indent=2))
    return root


def copied_root(testcase, *, without_depth_chart=False):
    """A throwaway copy of the checkout (no cache, no Git) so a test can take
    a release input away without touching the real tree. The 2014 release has
    been complete since the season depth chart was written after the 53-man
    reduction, so an open gate now has to be staged on a copy."""
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    testcase.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / 'repo'
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    if without_depth_chart:
        SeasonPaths(2014, root).depth_chart.unlink()
    return root


def unbound_release_errors(testcase):
    """runtime.seasons.game_release_errors judged on a copy staged before the
    2014 bind, whatever the real checkout's gate reads; for patching over
    game_release_errors where a caller reads the real checkout."""
    root = stage_unbound_release(copied_root(testcase))
    real = seasons.game_release_errors
    return lambda season, root_=None, preseason=None, receipt_kernel=None: real(season, root, preseason, receipt_kernel)
