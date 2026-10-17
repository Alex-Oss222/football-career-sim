"""Load and validate the reproducible 2012 -> 2013 era calibration.

Kernel 2014.6 plumbing (batch B1): the aggregate baseline and the drive model
it is cross-checked against are read through a calibration base
(runtime.calibration_base), verified against their sha256 pins. With no base
named, the 2012 base is used; DATA and DRIVE_MODEL are its paths. load() and
load_drive_model() return a fresh parsed copy on every call, as before.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_aggregate_baseline.json"
DRIVE_MODEL = ROOT / "library/data/2012_nfl_drive_model.json"


def _base(base):
    from .calibration_base import BASE_2012
    return base if base is not None else BASE_2012


def load(base=None):
    """A fresh copy of the base's aggregate baseline (sha256 verified)."""
    return _base(base).fresh("aggregate")


def load_drive_model(base=None):
    """A fresh copy of the base's drive model (sha256 verified)."""
    return _base(base).fresh("drive_model")


def _int(value):
    return isinstance(value, int) and not isinstance(value, bool)


AGGREGATE_V3 = "2010-2014w4-nfl-aggregate-baseline-v3"


def _pooled(data, block, name):
    pair = data.get(block, {}).get(name, {}).get("pooled")
    if not (isinstance(pair, list) and len(pair) == 2 and all(_int(v) for v in pair) and pair[1] > 0):
        raise ValueError("aggregate %s %s has no pooled integer pair" % (block, name))
    return pair


def kernel_rates(data, legacy=None):
    """The yardage numbers the kernel reads from an aggregate baseline:
    gross yards per pass attempt, yards per carry and the completion rate
    (R16 owns how they are used; the base only supplies them, plan section
    2.11). The 2012 schema keeps its exact expressions (numerator over
    denominator; the stored completion value), so kernels up to 2014.5 are
    byte-identical; schema 3 reads its pooled integer pairs.

    The per-play penalty counter belongs to R11 (batch B11): on schema 3 it
    stays the 2012 base's factor, read from `legacy` (the 2012 aggregate)."""
    if data.get("schema") == AGGREGATE_V3:
        if legacy is None:
            raise ValueError("a schema-3 aggregate needs the 2012 aggregate for the penalty counter")
        made, att = _pooled(data, "derived", "gross_yards_per_pass_attempt")
        yards, carries = _pooled(data, "derived", "yards_per_carry")
        comp, passes = _pooled(data, "derived", "completion_rate")
        return {"yards_per_attempt": made / att, "yards_per_carry": yards / carries,
                "completion_rate": comp / passes, "penalty_per_play": legacy["model"]["penalty_per_play"]}
    gross = data["derived"]["gross_yards_per_pass_attempt"]
    carry = data["derived"]["yards_per_carry"]
    return {"yards_per_attempt": gross["numerator"] / gross["denominator"],
            "yards_per_carry": carry["numerator"] / carry["denominator"],
            "completion_rate": data["derived"]["completion_rate"]["value"],
            "penalty_per_play": data["model"]["penalty_per_play"]}


def validate_drive_model_v2(drive, data):
    """Cross-check a schema-2 drive model against a schema-3 aggregate
    baseline (the 2010-2014 base): the field-goal, extra-point and
    interception counts are the same events. The drive model's
    field-goal-attempt category counts drives, which is one fewer than the
    attempts (2013_05_SD_OAK, two attempts on one drive, counted in rates
    only; field-position EXPLAINED)."""
    from .drive_model import validate_v2

    errors = list(validate_v2(drive))
    totals = data.get("period_totals", {})
    rates = drive.get("rates", {})
    fg = rates.get("field_goal") or [None, None]
    if fg != [totals.get("field_goals_made"), totals.get("field_goal_attempts")]:
        errors.append("drive model field goals do not equal period_totals")
    if not 0 <= totals.get("field_goal_attempts", 0) - drive.get("category_counts", {}).get("field_goal_attempt", -99) <= 1:
        errors.append("drive model field-goal drives differ from period_totals attempts by more than the explained one")
    xp = rates.get("extra_point") or [None, None]
    if xp != [totals.get("extra_points_made"), totals.get("extra_point_attempts")]:
        errors.append("drive model extra points do not equal period_totals")
    if drive.get("category_counts", {}).get("interception") != totals.get("interceptions"):
        errors.append("drive model interceptions do not equal period_totals")
    accuracy = data.get("model", {}).get("field_goal_accuracy")
    if fg[1] and (accuracy is None or abs(accuracy - fg[0] / fg[1]) > 1e-9):
        errors.append("field_goal_accuracy differs from the drive model pair")
    return errors


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


def validate(data=None, drive=None, base=None):
    """Errors in an aggregate baseline; with no drive model given it is
    cross-checked against the base's own (the 2012 base by default)."""
    data = data or load(base)
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
    if data.get("schema") == AGGREGATE_V3:
        for block, name in (("derived", "gross_yards_per_pass_attempt"), ("derived", "yards_per_carry"),
                            ("derived", "completion_rate"), ("volume", "points_per_team_game"),
                            ("volume", "plays_per_team_game"), ("volume", "net_yards_per_team_game"),
                            ("volume", "first_downs_per_team_game"),
                            ("volume", "third_down_attempts_per_team_game"), ("volume", "third_down_rate")):
            try:
                _pooled(data, block, name)
            except ValueError as exc:
                errors.append(str(exc))
        if not _int(totals.get("team_games")) or totals["team_games"] <= 0:
            errors.append("period_totals team_games invalid")
    if drive is not None:
        errors += (validate_drive_model_v2 if data.get("schema") == AGGREGATE_V3 else validate_drive_model)(drive, data)
    else:
        subset = {"period_totals": totals, "field_goal_accuracy": model.get("field_goal_accuracy")}
        if data.get("schema") == AGGREGATE_V3:
            subset["schema"] = AGGREGATE_V3
        errors += list(_default_drive_errors(json.dumps(subset, sort_keys=True), _base(base)))
    return errors


def _default_drive_errors(key, base):
    """The base's committed drive model checked once per distinct set of
    totals (memoised on the base)."""
    def check():
        subset = json.loads(key)
        data = {"period_totals": subset["period_totals"],
                "model": {"field_goal_accuracy": subset["field_goal_accuracy"]}}
        if subset.get("schema") == AGGREGATE_V3:
            return tuple(validate_drive_model_v2(base.raw("drive_model"), data))
        return tuple(validate_drive_model(base.raw("drive_model"), data))
    return base.memo(("aggregate_drive_errors", key), check)
