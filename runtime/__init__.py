"""The single, era-calibrated football runtime used by every game path."""

KERNEL_VERSION = "2013.2"
SCHEMA_VERSION = "1"

# Production callers import these names.  Low-level kernel access remains for
# synthetic calibration tests only.
def run_game(*args, **kwargs):
    from .game_runner import run_game as implementation
    return implementation(*args, **kwargs)

resolve_protagonist_game = run_game
resolve_background_game = run_game
