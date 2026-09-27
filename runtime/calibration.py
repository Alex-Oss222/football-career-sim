"""Load and validate the reproducible 2012 -> 2013 era calibration."""
from functools import lru_cache
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_aggregate_baseline.json"
DRIVE_MODEL = ROOT / "library/data/2012_nfl_drive_model.json"


def load():
    return json.loads(DATA.read_text())


def load_drive_model():
    return json.loads(DRIVE_MODEL.read_text())


def _int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate_drive_model(drive, data):
    """Cross-check the 2012 drive model (kernel 2013.6 artifact; its category counts,
    kick rates and clock scale are reused by kernel 2013.7) against the aggregate totals."""
    from .drive_model import validate as validate_structure

    errors = list(validate_structure(drive))
    totals = data.get("period_totals", {})
    rates = drive.get("rates", {})
    for name in ("field_goal", "extra_point", "two_point", "td_type_pass", "turnover_type_interception"):
        pair = rates.get(name)
        if not (isinstance(pair, list) and len(pair) == 2 and all(_int(v) for v in pair)):
            errors.append(f"drive model rate {name} is not an integer pair")
    counts = drive.get("category_counts", {})
    fg = rates.get("field_goal") or [None, None]
    if counts.get("field_goal_attempt") != totals.get("field_goal_attempts") or fg[1] != totals.get("field_goal_attempts"):
        errors.append("drive model field-goal attempts do not equal period_totals")
    if fg[0] != totals.get("field_goals_made"):
        errors.append("drive model field goals made do not equal period_totals")
    if counts.get("interception") != totals.get("interceptions"):
        errors.append("drive model interceptions do not equal period_totals")
    by_distance = rates.get("fg_by_distance", {})
    if sum(v[0] for v in by_distance.values()) != fg[0] or sum(v[1] for v in by_distance.values()) != fg[1]:
        errors.append("field-goal distance bins do not sum to the season totals")
    xp = rates.get("extra_point") or [None, None]
    if xp != [totals.get("extra_points_made"), totals.get("extra_point_attempts")]:
        errors.append("drive model extra points do not equal period_totals")
    reconciliation = drive.get("reconciliation", {})
    if reconciliation.get("result") != "pass":
        errors.append("drive model reconciliation did not pass")
    if drive.get("second_pass", {}).get("result") != "pass":
        errors.append("drive model second pass did not pass")
    accuracy = data.get("model", {}).get("field_goal_accuracy")
    if fg[1] and (accuracy is None or abs(accuracy - fg[0] / fg[1]) > 1e-4):
        errors.append("field_goal_accuracy differs from the drive model pair")
    return errors


def validate(data=None, drive=None):
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
    totals = data.get("period_totals", {})
    for made, attempts in (("extra_points_made", "extra_point_attempts"),
                           ("two_point_made", "two_point_attempts"),
                           ("field_goals_made", "field_goal_attempts")):
        if not (_int(totals.get(made)) and _int(totals.get(attempts)) and 0 <= totals[made] <= totals[attempts]):
            errors.append(f"period_totals {made}/{attempts} invalid")
    if not _int(totals.get("safeties")) or totals["safeties"] < 0:
        errors.append("period_totals safeties invalid")
    if drive is not None:
        errors += validate_drive_model(drive, data)
    else:
        errors += list(_default_drive_errors(json.dumps(
            {"period_totals": totals, "field_goal_accuracy": model.get("field_goal_accuracy")},
            sort_keys=True)))
    return errors


@lru_cache(maxsize=8)
def _default_drive_errors(key):
    """The committed drive model checked once per distinct set of totals."""
    subset = json.loads(key)
    data = {"period_totals": subset["period_totals"],
            "model": {"field_goal_accuracy": subset["field_goal_accuracy"]}}
    return tuple(validate_drive_model(load_drive_model(), data))
