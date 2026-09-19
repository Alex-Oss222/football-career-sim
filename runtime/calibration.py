"""Load and validate the reproducible 2012 -> 2013 era calibration."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_aggregate_baseline.json"


def load():
    return json.loads(DATA.read_text())


def validate(data=None):
    data = data or load()
    errors = []
    model = data.get("model", {})
    outcomes = model.get("drive_outcomes", {})
    if abs(sum(outcomes.values()) - 1.0) > 1e-9:
        errors.append("drive outcome probabilities do not sum to one")
    for group, values in (("drive outcomes", outcomes),
                          ("injury severity", data.get("injury_model", {}).get("severity", {}))):
        if any(not 0 <= value <= 1 for value in values.values()):
            errors.append(f"{group} contains an invalid probability")
    for key in ("drives_per_team_game", "plays_per_team_game", "yards_per_team_game"):
        if model.get(key, 0) <= 0:
            errors.append(f"missing positive {key}")
    return errors
