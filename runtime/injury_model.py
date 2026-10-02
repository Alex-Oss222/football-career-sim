"""Kernel 2014.4 in-game injury onset, severity and removal (Tier 1 items 4-5).

Parameters come from library/data/2012_nfl_injury_calibration.json
("recommended" block, as corrected by its verification pass); nothing here is
an unsourced constant. runtime/injuries.py is the closed 2013 model and stays
byte-identical (scripts/recover_injury_projection.py hashes it).

Model, per player and per participation interval (a drive plus any kick that
preceded it), drawn at the END of the interval (E2 step 1, explicit
end-of-drive onset; nothing is backdated):

* Exposure is the player's recorded snaps in the interval
  (runtime/participation.py). Zero snaps: no draw, no injury.
* Hazard per recorded player-snap is the calibration's mean game-onset hazard
  (0.00156 = 2.8 onsets / 1,794 player-plays per team-game) times the
  position group's relative risk divided by the slot-weighted mean relative
  risk of the participation model's 22 scrimmage slots (so the mix averages to
  the mean hazard), times exposure_plays / (exposure_plays - no_play_snapped):
  the 2012 exposure denominator counts snaps nullified by a penalty, which the
  kernel does not record as rows.
* The group is ``usage.group(position)`` (OT/OG/C -> OL, DE/DT/NT -> DL,
  ILB/OLB/MLB -> LB, CB/S/SS/FS -> DB, FB -> RB, K/P/LS -> specialists).
* Class from the game-onset mix; severity conditional on class: the
  confirmed by-class footprint shares reweighted band by band by the
  recommended all-onset mix over the confirmed report mix (the calibration's
  censoring and vanish correction toward longer bands). Days uniform in the
  sourced band (uniform is labelled Unverified in the source).
* Removal for the rest of the game: head/neck always (the canon independent
  medical hold); otherwise by severity with the sourced probabilities.
* A player has at most one onset per game.

Onset draws use their own keyed stream per (event, drive, club, player), so
the possession stream and every other player's draw are independent of how
many players participated.
"""
from __future__ import annotations

from pathlib import Path

from . import usage
from .participation import SCRIMMAGE_SLOT_MIX

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_injury_calibration.json"
ONSET_TAG = "injury-onset-v1"
CLASSES = ("lower_extremity", "upper_extremity", "trunk_other", "head_neck")
SEVERITIES = ("minor", "short", "multi_week", "long_term")
GROUPS = ("QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "K/P/LS")
GROUP_KEY = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "OL": "OL",
             "DL": "DL", "LB": "LB", "DB": "DB", "K": "K/P/LS", "P": "K/P/LS", "LS": "K/P/LS"}
HOLD = "independent medical hold"


def risk_group(position):
    """The calibration group for a raw position label (aliases normalized)."""
    return GROUP_KEY.get(usage.group(position) or "")


def load():
    """The 2012 base's injury calibration (sha256 verified); treat as read-only.

    Kernel 2014.6 plumbing (batch B1): each calibration base owns its injury
    calibration (role "injury") and its derived parameters
    (CalibrationBase.injury_parameters); the kernel passes its base's
    parameters to draw and disposition. DATA is the 2012 base's file."""
    from .calibration_base import BASE_2012
    return BASE_2012.raw("injury")


def _pair(value):
    return (isinstance(value, list) and len(value) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)
            and value[0] <= value[1])


def validate(data=None):
    """Structural and arithmetic checks on the calibration file."""
    data = data or load()
    errors = []
    rec = data.get("recommended", {})
    d = data.get("data", {})
    for key in ("D1", "D2", "D3"):
        if not data.get("sources", {}).get(key, {}).get("sha256"):
            errors.append(f"source {key} has no sha256")
    mixes = (("class_mix_game_onsets", CLASSES), ("severity_mix_all_onsets", SEVERITIES))
    for name, keys in mixes:
        values = rec.get(name, {}).get("values", {})
        if set(values) != set(keys) or any(not 0 <= v <= 1 for v in values.values()):
            errors.append(f"{name} invalid")
        elif abs(sum(values.values()) - 1) > 1e-6:
            errors.append(f"{name} does not sum to one")
    report = d.get("severity_report_onsets_footprint", {})
    shares = report.get("shares", {})
    if set(shares) != set(SEVERITIES) or abs(sum(shares.values()) - 1) > 0.002 or min(shares.values(), default=0) <= 0:
        errors.append("report severity shares invalid")
    for klass in CLASSES:
        row = report.get("by_class", {}).get(klass, {})
        if set(row) != set(SEVERITIES) or abs(sum(row.values()) - 1) > 0.002:
            errors.append(f"severity by class {klass} invalid")
    ranges = rec.get("severity_bands", {}).get("day_ranges", {})
    previous = -1
    for name in SEVERITIES:
        band = ranges.get(name)
        if not (_pair(band) and all(isinstance(v, int) for v in band) and band[0] == previous + 1):
            errors.append(f"day range {name} invalid or not contiguous")
            break
        previous = band[1]
    removal = rec.get("in_game_removal", {}).get("removal_probability_by_severity", {})
    if any(not 0 <= removal.get(s, -1) <= 1 for s in SEVERITIES) or removal.get("head_neck_any") != 1.0:
        errors.append("removal probabilities invalid")
    hazard = rec.get("mean_game_onset_hazard_per_player_snap", {}).get("value")
    if not isinstance(hazard, (int, float)) or not 0 < hazard < 0.01:
        errors.append("mean hazard invalid")
    onsets = rec.get("game_onsets_per_team_game", {})
    if not _pair(onsets.get("range")) or not onsets["range"][0] <= onsets.get("value", -1) <= onsets["range"][1]:
        errors.append("game onsets per team-game invalid")
    rr = rec.get("position_relative_risk_per_snap", {}).get("values", {})
    if set(rr) != set(GROUPS) or any(v <= 0 for v in rr.values()):
        errors.append("position relative risks invalid")
    denominators = d.get("denominators", {})
    exposure, nullified = denominators.get("exposure_plays"), denominators.get("play_types", {}).get("no_play_snapped")
    if not (isinstance(exposure, int) and isinstance(nullified, int) and 0 <= nullified < exposure):
        errors.append("exposure denominators invalid")
    bands = rec.get("acceptance_bands_for_kernel_2014_4", {})
    for key in ("game_onsets_per_team_game", "rest_of_game_removals_per_team_game",
                "head_neck_share_game_onsets", "lower_extremity_share_game_onsets",
                "time_loss_share_(short+)", "long_term_share"):
        if not _pair(bands.get(key)):
            errors.append(f"acceptance band {key} invalid")
    return errors


def parameters():
    """The 2012 base's derived, validated parameter set."""
    from .calibration_base import BASE_2012
    return BASE_2012.injury_parameters()


def parameters_from(data):
    """The derived, validated parameter set of one injury calibration."""
    errors = validate(data)
    if errors:
        raise ValueError("injury calibration invalid: " + "; ".join(errors))
    rec, d = data["recommended"], data["data"]
    rr = rec["position_relative_risk_per_snap"]["values"]
    slots = sum(SCRIMMAGE_SLOT_MIX.values())
    mean_rr = sum(share * rr[g] for g, share in SCRIMMAGE_SLOT_MIX.items()) / slots
    denominators = d["denominators"]
    exposure = denominators["exposure_plays"]
    nullified = denominators["play_types"]["no_play_snapped"]
    base = rec["mean_game_onset_hazard_per_player_snap"]["value"] * exposure / (exposure - nullified)
    hazard = {g: base * rr[g] / mean_rr for g in GROUPS}
    mix = rec["severity_mix_all_onsets"]["values"]
    report = d["severity_report_onsets_footprint"]["shares"]
    severity = {}
    for klass in CLASSES:
        row = d["severity_report_onsets_footprint"]["by_class"][klass]
        weights = {s: row[s] * mix[s] / report[s] for s in SEVERITIES}
        total = sum(weights.values())
        severity[klass] = tuple((s, weights[s] / total) for s in SEVERITIES)
    removal = rec["in_game_removal"]["removal_probability_by_severity"]
    return {
        "hazard": hazard,
        "classes": tuple((k, rec["class_mix_game_onsets"]["values"][k]) for k in CLASSES),
        "severity": severity,
        "days": {s: tuple(rec["severity_bands"]["day_ranges"][s]) for s in SEVERITIES},
        "removal": {s: removal[s] for s in SEVERITIES},
        "head_neck_removal": removal["head_neck_any"],
    }


def _weighted(rng, pairs):
    draw = rng.random()
    total = 0.0
    for name, weight in pairs:
        total += weight
        if draw < total:
            return name
    return pairs[-1][0]


def onset_probability(position, snaps, params=None):
    group = risk_group(position)
    if snaps <= 0 or group is None:
        return 0.0
    return 1 - (1 - (params or parameters())["hazard"][group]) ** snaps


def disposition(rng, injury_class=None, severity=None, params=None):
    """Class, severity, days, restriction and removal for one onset
    (`params`: the base's parameters; the 2012 base's when None)."""
    p = params or parameters()
    klass = injury_class or _weighted(rng, p["classes"])
    band = severity or _weighted(rng, p["severity"][klass])
    low, high = p["days"][band]
    days = rng.randint(low, high)
    if klass == "head_neck":
        removed = rng.random() < p["head_neck_removal"]
        restriction = HOLD
    else:
        removed = rng.random() < p["removal"][band]
        restriction = "limited" if not days else "out"
    return {"injury_class": klass, "severity": band, "restriction": restriction,
            "return_days": days, "reassessment_days": min(max(days // 3, 1), 7),
            "removed": removed}


def draw(rng, position, snaps, params=None):
    """One interval's onset for one player, or None. Zero exposure: None."""
    probability = onset_probability(position, snaps, params)
    if probability <= 0 or rng.random() >= probability:
        return None
    return disposition(rng, params=params)
