"""Kernel 2014.4 candidate, defect register item 1 (E1, second pass): unit
strength from dated public honours, dated pre-divergence production and the
actual available lineup.

Policy: runtime/2014_engine_decisions.md E1. Calibration:
library/2014_strength_calibration.md (section 9) and
library/data/2014_strength_calibration_v2.json (the first pass remains in
library/data/2014_strength_calibration.json). Evidence:
library/data/2010_2012_honours_evidence.json (honours) and
library/data/2010_2012_production_evidence.json (production).

Honours tier rule (unchanged from the first pass, preregistered):

* window: the two most recent completed pre-divergence seasons before the
  season being played (2014 branch: 2011-2012; 2012 study target:
  2010-2011). The real 2013 season is post-divergence and never read.
* Elite: an AP All-Pro 1st team in the window; Plus: AP 2nd team or an
  original Pro Bowl selection. Alternates and replacements have no effect.
* honours value = max over admissible honours of (tier value - 2) x evidence
  weight (Elite 4, Plus 3; weight 1 two-pass, 0.5 single-pass); never below 0.
* an honour is admissible only when its public date is known, before the
  divergence (2013-01-15) and before the date the input is built for.
* specialist honours are special-teams evidence only.

Production tier rule (second pass, preregistered in the production file):

* each qualifying season's metric (QB EPA per dropback; RB/WR/TE EPA per
  opportunity; DL/LB/DB disruption per game; K and P carried for special
  teams) is shrunk to the league mean and cut at fixed percentiles among that
  season's qualifiers in the group: top 10% Elite, next 20% Plus, middle 40%
  Average, next 20% Below-Average, bottom 10% Replacement-Level. Offensive
  linemen carry starts and games only (job evidence) and no tier.
* a player's production tier is the best tier over the same two-season
  window; the season before the window (2010 for the 2014 branch) counts
  only when neither window season qualifies, discounted one tier.
* production value = Elite 2, Plus 1, Average 0, Below-Average -1,
  Replacement-Level -2, times the evidence weight (1 for a season the
  play-by-play recomputation confirmed or corrected, 0.5 unverified).
* a season's statistics are admissible only when its public date (the last
  regular-season game) is before the divergence and before the input date.

Player value (preregistered before the second fit; calibration section 9):

    value = max(honours value, production value) with an admissible honour,
            production value (negative tiers included) without one

with the side rule: a QB honour or QB production tier counts only in the
passer slot (weight 3); a non-QB honour or tier never counts there; an
offensive tier counts only on offense and a defensive tier only on defense.
The age shrink on stale honours was fitted and not adopted (it lowered the
offense leave-one-club-out skill), so no age enters a value.

Sub-composites (phase 2, per drive, from the drive's ACTUAL lineup: the live
roster after injuries and removals, through participation.emergency_view).
Declared before the phase-2 fit (library/2014_strength_calibration.md
section 10; library/data/2014_strength_calibration_v3.json), a slot
convention applied identically to every club:

* offense: protection = the five linemen of usage.protection_front and RB1;
  passing = the passer (weight 3), WR1-3 and TE1; run = the five linemen,
  TE1, FB1 when the club dressed a fullback, and RB1;
* defense: rush = DL1-4 and LB1; coverage = DB1-4 and LB2-3; run defense =
  DL1-4, LB1-3 and the box safety (the first of DB1-4 labelled SS, else the
  first labelled S or FS, else DB4);
* unit composite = sum of position weight x player value.

Offensive-line job evidence (phase 2, rule B adopted by the preregistered
leave-one-club-out test): a lineman with no admissible honour and no window
season with 8 or more starts (the production file's OL job rows, under the
same public-date gate) counts -1 in the protection and run composites; a
proven lineman without an honour counts 0. A lineman absent from the
evidence altogether is unproven under this rule.

Terms (phase 2). Each kept term is one sub-matchup difference with its own
shrunk slope on the outcome it moves; the kept set, slopes and 2012 centres
are the study's (TERMS below, checked against the file by the tests):

* touchdown share: passing slope x (passing - centre) - run-defense slope x
  (run_defense - centre) + HOME_EDGE, clamped to +/-EDGE_CLAMP, fed to
  drive_model.apply_edge through field_position.category_mix (unchanged);
* sack rate: - protection slope x (protection - centre) shifts the
  per-dropback sack probability from the 2012 base; the drawn category's
  real drive is then resampled by each tuple's binomial likelihood ratio
  (field_position); clamped to +/-SACK_SHIFT_CLAMP;
* interception share: no term survived the fit; the channel is wired
  (category_mix takes an interception shift) with slope 0.

Terms that were fitted and dropped for lack of leave-one-club-out skill
(rush on sack rate, passing and coverage on interception share, run and
coverage on touchdown share, yards per carry) are carried with slope 0 so a
receipt shows every sub-composite. The centres are the 2012 study means
(coordinator decision, September 30, 2026: the identity-ordered 2014
inventory lineups are not depth charts, so their mean shift is not evidence
of a league shift; revisited with the real 2014 Week 1 depth charts).

Special teams (phase 2). The punter's net-punt persistence survived its
season-pair test (continuous predictor, slope PUNTER_SLOPE yards of gross per
yard of the punter's shrunk net above his season's league mean); the kicker,
kick-returner and punt-returner tiers did not, so their channels are wired
with slope 0 (carried, inactive). Coverage-unit strength is out of scope.

A club whose TeamInput carries no strength record (old synthetic inputs,
closed 2013 inputs) keeps the legacy anchor path, one side at a time:
(anchor - 2) x 0.025, with no sack, interception or special-teams shift.

Attribution (defect register item 19): each player's record also carries
his `attribution_tier` (the tier his own value maps to on his own side);
runtime/usage.py tilts carry, target and sack credit by it. That tilt reads
this record only after the possession is resolved and can change no score.

Nothing here reads a club name or which side is the protagonist; Jacksonville
is scored from the same evidence files by the same rule.

Kernel 2014.6 (batch B7): model player-state-v1 (PLAYER_STATE_MODEL), the
entry PROFILE_2014_6 resolves with. The honours and production rules above
stay the record's public evidence; what changes is the value a lineup slot
reads and the fitted terms:

* each player's value is his drawn player state in his family's true-state SD
  units (runtime/player_state.py: the public expectation plus the private
  once-per-season draw the service made at bind, fetched after the event is
  journaled and written into the record as `latent_value`); a no-state row
  (offensive linemen, long snappers), a held family (LB under U5) and a
  family with no spread read 0;
* the family's side rule replaces the tier's: an offensive family counts only
  on offense, a defensive family only on defense, the QB family only in the
  passer slot and no other family there; a position change moves the matchup
  slot only (the value is keyed by gsis id, never by position);
* honours act as floors: with an admissible honour on that side (the QB rule
  included) the slot reads max(drawn value, honours value), never less;
* offensive linemen keep rule B plus honours (the honours value if any, else
  0 proven, OL_UNPROVEN_VALUE unproven);
* TERMS_V4 (library/data/2014_strength_calibration_v4.json, read at import
  under its sha256 pin, never typed): passing on touchdown share and passing
  on interception share are live; protection-to-sack and run defense turned
  off by the keep rule (U3), every other term carried at slope 0 with its
  composite centre so a receipt shows every sub-composite;
* HOME_EDGE_V4 is the drive-level joint regression's home term and
  PUNTER_SLOPE_V4 the refit on the committed net definition; the punter's
  input stays his public pre-divergence net (`deviation`); the kicker and
  returner terms stay 0;
* the attribution tilt (runtime/usage.py) keeps reading the record's
  honours-production `attribution_tier`: the drawn-tier population rests on
  amendment 3 and is held with U5, so the item 19 rule stands unchanged and
  no state value reaches credit;
* under this model the kernel publishes no per-possession strength block
  (the drawn values would be readable from the contributors), and a record
  whose drawable players lack their latent value fails closed
  (runtime.player_state.latent_errors).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from . import usage
from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "library/data/2010_2012_honours_evidence.json"
PRODUCTION = ROOT / "library/data/2010_2012_production_evidence.json"
CALIBRATION = ROOT / "library/data/2014_strength_calibration_v2.json"
PHASE2_CALIBRATION = ROOT / "library/data/2014_strength_calibration_v3.json"
FIRST_PASS_CALIBRATION = ROOT / "library/data/2014_strength_calibration.json"


def league_players_path(season):
    """The season's league player inventory (identity joins), resolved
    through the season layout (`career/2014/league/personnel/...`)."""
    return SeasonPaths(int(season), ROOT).record("league/personnel/league_players.json")


def club_codes_path(season):
    """The season's rotation file, which carries the club code map."""
    return SeasonPaths(int(season), ROOT).record("schedule/rotation_%d.json" % int(season))

MODEL = "honours-production-v3"
# Second study (combined_max variant) shrunk TD-share slopes per composite
# unit and its 2012 composite means (library/data/2014_strength_calibration_v2.json,
# study_2012.variants.combined_max.fits.*; tests/test_strength.py checks
# these against the file).
OFFENSE_SLOPE = 0.005785739981127017
DEFENSE_SLOPE = 0.004587405854420489
OFFENSE_CENTRE = 4.296875
DEFENSE_CENTRE = 8.109375
# Phase 2 (library/data/2014_strength_calibration_v3.json, study_2012.adopted_terms
# and special_teams; tests/test_strength.py checks every number against the
# file). A term with slope 0 was fitted and dropped for lack of
# leave-one-club-out skill: its composite is still published.
TERMS = (
    {"name": "td_share_offense_passing", "outcome": "td_share", "side": "offense", "unit": "passing",
     "slope": 0.006431863122501438, "centre": 2.828125, "active": True},
    {"name": "td_share_defense_run_defense", "outcome": "td_share", "side": "defense", "unit": "run_defense",
     "slope": 0.00534883340577881, "centre": 5.0, "active": True},
    {"name": "sack_rate_offense_protection", "outcome": "sack_rate", "side": "offense", "unit": "protection",
     "slope": 0.005653299631387429, "centre": 0.4375, "active": True},
    {"name": "sack_rate_defense_rush", "outcome": "sack_rate", "side": "defense", "unit": "rush",
     "slope": 0.0, "centre": 3.125, "active": False},
    {"name": "int_share_offense_passing", "outcome": "int_share", "side": "offense", "unit": "passing",
     "slope": 0.0, "centre": 2.828125, "active": False},
    {"name": "int_share_defense_coverage", "outcome": "int_share", "side": "defense", "unit": "coverage",
     "slope": 0.0, "centre": 4.609375, "active": False},
    {"name": "td_share_offense_run", "outcome": "td_share", "side": "offense", "unit": "run",
     "slope": 0.0, "centre": 1.015625, "active": False},
    {"name": "td_share_defense_coverage", "outcome": "td_share", "side": "defense", "unit": "coverage",
     "slope": 0.0, "centre": 4.609375, "active": False},
)
UNITS = {"offense": ("protection", "passing", "run"), "defense": ("rush", "coverage", "run_defense")}
OL_UNPROVEN_VALUE = -1.0
OL_PROVEN_STARTS = 8
SACK_SHIFT_CLAMP = 0.06
INT_EDGE_CLAMP = 0.06
# Special teams (phase 2): the punter term is the continuous persistence
# slope (yards of gross per yard of shrunk net above the league mean); the
# kicker (make rate per tier unit), kick-returner and punt-returner (yards
# per tier unit) terms had no season-pair skill and are inactive.
PUNTER_SLOPE = 0.33992720349671446
KICKER_SLOPE = 0.0
KICK_RETURNER_SLOPE = 0.0
PUNT_RETURNER_SLOPE = 0.0
FG_PROB_FLOOR, FG_PROB_CEILING = 0.02, 0.99
# Home term per drive for the home offense at a home venue, none at a neutral
# site (user decision, September 29, 2026; library/2014_strength_calibration.md
# section 4: drive-level fit 0.0227, SE 0.0102). Replaces kernel 2013.11's 0.008.
HOME_EDGE = 0.023
# Widened from +/-0.06 (user decision, September 29, 2026).
EDGE_CLAMP = 0.12
# Legacy anchor path (TeamInputs without a strength record).
LEGACY_ANCHOR_SCALE = 0.025
LEGACY_ANCHOR_CENTRE = 2.0



@dataclass(frozen=True)
class StrengthParameters:
    """Every resolution constant of one strength model version (kernel 2014.6
    plumbing, batch B1). The kernel reads its profile's entry of PARAMETERS
    (runtime.profiles.Profile.strength); the module constants above are the
    honours-production-v3 entry, checked against their files by the tests."""
    model: str
    offense_slope: float
    defense_slope: float
    offense_centre: float
    defense_centre: float
    terms: tuple
    sack_shift_clamp: float
    int_edge_clamp: float
    punter_slope: float
    kicker_slope: float
    kick_returner_slope: float
    punt_returner_slope: float
    fg_prob_floor: float
    fg_prob_ceiling: float
    home_edge: float
    edge_clamp: float
    legacy_anchor_scale: float
    legacy_anchor_centre: float


# Per-version table. Kernels 2014.4 and 2014.5 resolve with
# honours-production-v3; a later model is a new entry, never an edit.
PARAMETERS = {
    MODEL: StrengthParameters(
        model=MODEL, offense_slope=OFFENSE_SLOPE, defense_slope=DEFENSE_SLOPE,
        offense_centre=OFFENSE_CENTRE, defense_centre=DEFENSE_CENTRE, terms=TERMS,
        sack_shift_clamp=SACK_SHIFT_CLAMP, int_edge_clamp=INT_EDGE_CLAMP, punter_slope=PUNTER_SLOPE,
        kicker_slope=KICKER_SLOPE, kick_returner_slope=KICK_RETURNER_SLOPE,
        punt_returner_slope=PUNT_RETURNER_SLOPE, fg_prob_floor=FG_PROB_FLOOR, fg_prob_ceiling=FG_PROB_CEILING,
        home_edge=HOME_EDGE, edge_clamp=EDGE_CLAMP, legacy_anchor_scale=LEGACY_ANCHOR_SCALE,
        legacy_anchor_centre=LEGACY_ANCHOR_CENTRE),
}


def parameters(model=MODEL):
    """The parameter-table entry of a strength model version; unknown raises."""
    try:
        return PARAMETERS[model]
    except KeyError:
        raise ValueError("no strength parameters are registered for model %r" % (model,)) from None


# ---- Kernel 2014.6 (batch B7): the player-state model's parameter entry -----------
PLAYER_STATE_MODEL = "player-state-v1"
V4_CALIBRATION = ROOT / "library/data/2014_strength_calibration_v4.json"
V4_SHA256 = "9be9ebad137e0f118f2f7bbf9a564e5ceaf54e691e249823bce5762e788d6ea5"
# The fitted terms in a fixed order (the three kernel channels; the ypc
# terms have no channel and are reported only).
V4_TERM_ORDER = ("td_share_offense_passing", "td_share_defense_run_defense", "sack_rate_offense_protection",
                 "sack_rate_defense_rush", "int_share_offense_passing", "int_share_defense_coverage",
                 "td_share_offense_run", "td_share_defense_coverage")


@lru_cache(maxsize=1)
def v4_calibration_file():
    raw = V4_CALIBRATION.read_bytes()
    if hashlib.sha256(raw).hexdigest() != V4_SHA256:
        raise ValueError("library/data/2014_strength_calibration_v4.json differs from its pinned sha256")
    data = json.loads(raw.decode("utf-8"))
    if data.get("schema") != "2014-strength-calibration-v4":
        raise ValueError("unknown strength v4 schema")
    return data


def _v4_terms(data):
    terms = []
    for name in V4_TERM_ORDER:
        outcome = "td_share" if name.startswith("td_share") else "sack_rate" if name.startswith("sack_rate") \
            else "int_share"
        rest = name[len(outcome) + 1:]
        side, unit = rest.split("_", 1)
        fit = data["fits"][name]
        kept = bool(data["kept"].get(name))
        slope = float(data["adopted_terms"][name]["slope"]) if kept else 0.0
        terms.append({"name": name, "outcome": outcome, "side": side, "unit": unit, "slope": slope,
                      "centre": float(fit["composite_mean"]), "active": kept})
    return tuple(terms)


def _register_player_state_parameters():
    data = v4_calibration_file()
    PARAMETERS[PLAYER_STATE_MODEL] = StrengthParameters(
        model=PLAYER_STATE_MODEL, offense_slope=OFFENSE_SLOPE, defense_slope=DEFENSE_SLOPE,
        offense_centre=OFFENSE_CENTRE, defense_centre=DEFENSE_CENTRE, terms=_v4_terms(data),
        sack_shift_clamp=SACK_SHIFT_CLAMP, int_edge_clamp=INT_EDGE_CLAMP,
        punter_slope=float(data["punter"]["adopted"]["slope"]) if data["punter"]["adopted"].get("kept") else 0.0,
        kicker_slope=float(data["kicker_slope"]), kick_returner_slope=float(data["returner_slope"]),
        punt_returner_slope=float(data["returner_slope"]), fg_prob_floor=FG_PROB_FLOOR,
        fg_prob_ceiling=FG_PROB_CEILING, home_edge=float(data["home_edge"]["value"]), edge_clamp=EDGE_CLAMP,
        legacy_anchor_scale=LEGACY_ANCHOR_SCALE, legacy_anchor_centre=LEGACY_ANCHOR_CENTRE)


_register_player_state_parameters()
TERMS_V4 = PARAMETERS[PLAYER_STATE_MODEL].terms
HOME_EDGE_V4 = PARAMETERS[PLAYER_STATE_MODEL].home_edge
PUNTER_SLOPE_V4 = PARAMETERS[PLAYER_STATE_MODEL].punter_slope


DIVERGENCE = "2013-01-15"
LAST_PRE_DIVERGENCE_SEASON = 2012
TIERS = {"AP1": ("Elite", 4), "AP2": ("Plus", 3), "PB": ("Plus", 3)}
AVERAGE_VALUE = 2
EVIDENCE_WEIGHT = {"Confirmed two-pass": 1.0, "Single-pass": 0.5}
PRODUCTION_TIER_VALUE = {"Elite": 2, "Plus": 1, "Average": 0, "Below-Average": -1, "Replacement-Level": -2}
PRODUCTION_WEIGHT = {"Confirmed two-pass": 1.0, "Corrected": 1.0, "Unverified": 0.5}
TIER_STEP = ("Elite", "Plus", "Average", "Below-Average", "Replacement-Level")
QB_WEIGHT = 3
SPECIAL_POSITIONS = frozenset({"K", "P", "KR", "PR", "LS", "ST"})
OFFENSE_POSITIONS = frozenset({"QB", "RB", "HB", "FB", "WR", "TE", "T", "G", "C", "OT", "OG", "OL",
                               "LT", "LG", "RG", "RT"})
DEFENSE_POSITIONS = frozenset({"DE", "DT", "NT", "DL", "OLB", "ILB", "MLB", "LB", "CB", "S", "SS",
                               "FS", "DB"})
GROUP_SIDE = {"QB": "offense", "RB": "offense", "WR": "offense", "TE": "offense", "OL": "offense",
              "DL": "defense", "LB": "defense", "DB": "defense", "K": "special", "P": "special",
              "KR": "special", "PR": "special"}
DEFENSE_STARTERS = (("DL", 4), ("LB", 3), ("DB", 4))
GSIS = re.compile(r"^\d{2}-\d{7}$")


def unit_of(position):
    position = str(position or "").strip().upper()
    if position in SPECIAL_POSITIONS:
        return "special"
    if position in OFFENSE_POSITIONS:
        return "offense"
    if position in DEFENSE_POSITIONS:
        return "defense"
    return None


def honour_seasons(season):
    """The preregistered window: the two most recent completed
    pre-divergence seasons before `season`."""
    latest = min(int(season) - 1, LAST_PRE_DIVERGENCE_SEASON)
    return (latest - 1, latest)


@lru_cache(maxsize=1)
def evidence_file():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def production_file():
    return json.loads(PRODUCTION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def calibration_file():
    return json.loads(CALIBRATION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def phase2_calibration_file():
    return json.loads(PHASE2_CALIBRATION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def first_pass_calibration_file():
    return json.loads(FIRST_PASS_CALIBRATION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _by_player():
    index = {}
    for row in evidence_file()["entries"]:
        index.setdefault(row.get("player_id"), []).append(row)
    return index


def _iso(value):
    return value.isoformat() if isinstance(value, date) else str(value)


def player_evidence(player_id, season, as_of, entries=None):
    """(honours record or None, rejected receipts) for one nflverse gsis id.

    record = {"offdef": {...} | None, "special": {...} | None}; each part
    holds tier, value, evidence_weight, honour position/group/unit and the
    evidence ids used. Rejected receipts name every in-window honour that
    was not admissible and why (future-dated, undated, post-divergence,
    alternate/replacement)."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    cutoff = min(as_of, DIVERGENCE)
    if entries is None:
        rows = _by_player().get(player_id, ())
    else:
        rows = entries
    record = {"offdef": None, "special": None}
    rejected = []
    for row in rows:
        if row.get("player_id") != player_id or row.get("season") not in window:
            continue
        reason = None
        if row.get("honour_kind") not in TIERS:
            reason = "alternate_or_replacement_no_effect"
        elif not row.get("public_date"):
            reason = "public_date_unpinned"
        elif row["public_date"] >= as_of:
            reason = "future_dated"
        elif row["public_date"] >= cutoff or not row.get("admissible_pre_divergence", False):
            reason = "post_divergence"
        if reason:
            rejected.append({"evidence_id": row["evidence_id"], "reason": reason,
                             "public_date": row.get("public_date")})
            continue
        tier, tier_value = TIERS[row["honour_kind"]]
        weight = EVIDENCE_WEIGHT[row["verification"]]
        value = (tier_value - AVERAGE_VALUE) * weight
        unit = unit_of(row["position"]) or "unknown"
        key = "special" if unit == "special" else "offdef"
        best = record[key]
        part = {"tier": tier, "tier_value": tier_value, "evidence_weight": weight, "value": value,
                "unit": unit, "honour_position": row["position"],
                "honour_group": usage.group(row["position"]) or row["position"],
                "evidence_ids": [row["evidence_id"]]}
        if best is None or value > best["value"] or (value == best["value"] and tier_value > best["tier_value"]):
            if best is not None:
                part["evidence_ids"] = sorted(set(best["evidence_ids"]) | {row["evidence_id"]})
            record[key] = part
        else:
            best["evidence_ids"] = sorted(set(best["evidence_ids"]) | {row["evidence_id"]})
    if record["offdef"] is None and record["special"] is None:
        return None, rejected
    return record, rejected


def production_evidence(player_id, season, as_of, rows=None, season_meta=None):
    """(production part or None, rejected receipts) for one gsis id.

    part = {tier, value, evidence_weight, group, unit, season, discounted,
    evidence_ids}: the best tier over the window, else the season before it
    discounted one tier. A season is rejected (and listed) when its public
    date is not before both the divergence and the input date."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    fallback = window[0] - 1
    cutoff = min(as_of, DIVERGENCE)
    if rows is None:
        rows = (production_file()["players"].get(player_id) or {}).get("seasons", {})
    if season_meta is None:
        season_meta = production_file()["seasons"]
    rejected, admissible = [], {}
    for year, row in rows.items():
        year = int(year)
        if year not in window and year != fallback:
            continue
        meta = season_meta.get(str(year), {})
        public = meta.get("public_date")
        evidence_id = "production-%d-%s" % (year, player_id)
        if not public:
            rejected.append({"evidence_id": evidence_id, "reason": "public_date_unpinned", "public_date": None})
        elif public >= as_of:
            rejected.append({"evidence_id": evidence_id, "reason": "future_dated", "public_date": public})
        elif public >= cutoff or not meta.get("admissible_pre_divergence", False):
            rejected.append({"evidence_id": evidence_id, "reason": "post_divergence", "public_date": public})
        elif row.get("tier") is None:
            continue  # offensive-line job evidence or a non-qualifier: no tier
        else:
            admissible[year] = (row, evidence_id)
    best = None
    for year in window:
        if year in admissible:
            row, evidence_id = admissible[year]
            if best is None or TIER_STEP.index(row["tier"]) < TIER_STEP.index(best["tier"]):
                best = {"tier": row["tier"], "season": year, "discounted": False, "evidence_ids": [evidence_id],
                        "group": row["group"], "verification": row["verification"]}
    if best is None and fallback in admissible:
        row, evidence_id = admissible[fallback]
        best = {"tier": TIER_STEP[min(4, TIER_STEP.index(row["tier"]) + 1)], "season": fallback, "discounted": True,
                "undiscounted_tier": row["tier"], "evidence_ids": [evidence_id], "group": row["group"],
                "verification": row["verification"]}
    if best is None:
        return None, rejected
    weight = PRODUCTION_WEIGHT.get(best.pop("verification"), 0.5)
    best["evidence_weight"] = weight
    best["value"] = PRODUCTION_TIER_VALUE[best["tier"]] * weight
    best["unit"] = GROUP_SIDE.get(best["group"], "unknown")
    if best["group"] in ("K", "P") and not best["discounted"]:
        # Phase 2: the specialist's shrunk metric above his season's league
        # mean (the continuous predictor of the season-pair study).
        row = admissible[best["season"]][0]
        league = season_meta.get(str(best["season"]), {}).get("league_means", {}).get(best["group"], {})
        if row.get("shrunk") is not None and league.get("mean") is not None:
            best["deviation"] = row["shrunk"] - league["mean"]
    return best, rejected


def job_evidence(player_id, season, as_of, rows=None, season_meta=None):
    """(offensive-line job part or None, rejected receipts): the window's
    depth-chart starts per season under the same public-date gate, and
    whether any window season reaches OL_PROVEN_STARTS."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    cutoff = min(as_of, DIVERGENCE)
    if rows is None:
        rows = (production_file()["players"].get(player_id) or {}).get("seasons", {})
    if season_meta is None:
        season_meta = production_file()["seasons"]
    rejected, starts, ids = [], {}, []
    for year, row in rows.items():
        year = int(year)
        if year not in window or row.get("group") != "OL":
            continue
        meta = season_meta.get(str(year), {})
        public = meta.get("public_date")
        evidence_id = "job-%d-%s" % (year, player_id)
        if not public:
            rejected.append({"evidence_id": evidence_id, "reason": "public_date_unpinned", "public_date": None})
        elif public >= as_of:
            rejected.append({"evidence_id": evidence_id, "reason": "future_dated", "public_date": public})
        elif public >= cutoff or not meta.get("admissible_pre_divergence", False):
            rejected.append({"evidence_id": evidence_id, "reason": "post_divergence", "public_date": public})
        else:
            starts[str(year)] = int(row.get("starts", 0))
            ids.append(evidence_id)
    if not starts:
        return None, rejected
    return {"group": "OL", "unit": "offense", "starts": starts, "evidence_ids": ids,
            "proven": any(n >= OL_PROVEN_STARTS for n in starts.values())}, rejected


def returner_evidence(player_id, season, as_of, kind, rows=None, season_meta=None):
    """(returner part or None, rejected receipts) for kind "KR" or "PR": the
    window's best tier from the production file's returner block, with its
    deviation from the season's league mean; the same date gate."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    cutoff = min(as_of, DIVERGENCE)
    if rows is None:
        rows = (production_file().get("returners", {}).get(player_id) or {}).get("seasons", {})
    if season_meta is None:
        season_meta = production_file()["seasons"]
    rejected, best = [], None
    for year, groups in rows.items():
        year = int(year)
        row = groups.get(kind)
        if year not in window or not row or row.get("tier") is None:
            continue
        meta = season_meta.get(str(year), {})
        public = meta.get("public_date")
        evidence_id = "return-%s-%d-%s" % (kind, year, player_id)
        if not public:
            rejected.append({"evidence_id": evidence_id, "reason": "public_date_unpinned", "public_date": None})
            continue
        if public >= as_of:
            rejected.append({"evidence_id": evidence_id, "reason": "future_dated", "public_date": public})
            continue
        if public >= cutoff or not meta.get("admissible_pre_divergence", False):
            rejected.append({"evidence_id": evidence_id, "reason": "post_divergence", "public_date": public})
            continue
        if best is None or TIER_STEP.index(row["tier"]) < TIER_STEP.index(best["tier"]):
            league = meta.get("returners", {}).get("league_means", {}).get(kind, {})
            weight = PRODUCTION_WEIGHT.get(row.get("verification"), 0.5)
            best = {"tier": row["tier"], "season": year, "group": kind, "unit": "special",
                    "evidence_weight": weight, "value": PRODUCTION_TIER_VALUE[row["tier"]] * weight,
                    "deviation": (row["shrunk"] - league["mean"]) if league.get("mean") is not None else None,
                    "evidence_ids": [evidence_id]}
    return best, rejected


def tier_for_value(value):
    """The five-tier label a combined player value maps to."""
    if value >= 2:
        return "Elite"
    if value >= 1:
        return "Plus"
    if value <= -2:
        return "Replacement-Level"
    if value <= -1:
        return "Below-Average"
    return "Average"


def player_record(player_id, season, as_of):
    """(record or None, rejected receipts): the honours parts, the production
    part and the player's attribution tier (his own value on his own side)."""
    honours, rejected = player_evidence(player_id, season, as_of)
    production, rejected_p = production_evidence(player_id, season, as_of)
    job, rejected_j = job_evidence(player_id, season, as_of)
    returns = {}
    rejected = rejected + rejected_p + rejected_j
    for kind in ("KR", "PR"):
        part, rejected_r = returner_evidence(player_id, season, as_of, kind)
        rejected += rejected_r
        if part:
            returns[kind] = part
    if honours is None and production is None and job is None and not returns:
        return None, rejected
    record = dict(honours or {"offdef": None, "special": None})
    record["production"] = production
    if job:
        record["job"] = job
    if returns:
        record["returns"] = returns
    h = record.get("offdef")
    prod_value = production["value"] if production and production["unit"] != "special" else 0.0
    value = max(h["value"], prod_value) if h else prod_value
    record["attribution_tier"] = tier_for_value(value)
    return record, rejected


# ---- identity -------------------------------------------------------------------

@lru_cache(maxsize=4)
def _league(season):
    path = league_players_path(season)
    if not path.is_file():
        return {"players": []}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def club_codes(season):
    """{club name: code} from the season's rotation file."""
    data = json.loads(club_codes_path(season).read_text(encoding="utf-8"))
    return {name: code for code, name in data["club_codes"].items()}


def resolve_id(row, club_code, season):
    """(gsis id or None, join note) for one TeamInput roster row."""
    gsis = row.get("gsis_id")
    if gsis:
        return gsis, "gsis_id"
    pid = str(row.get("player_id", ""))
    if GSIS.match(pid):
        return pid, "player_id"
    matches = [p for p in _league(season)["players"] if p.get("name") == pid]
    here = [p for p in matches if p.get("inventory_club") == club_code]
    if len(here) == 1:
        return here[0]["player_id"], "name_and_club"
    if len(matches) == 1:
        return matches[0]["player_id"], "unique_name"
    return None, "unresolved" if not matches else "ambiguous_name"


# ---- TeamInput strength record --------------------------------------------------

def live_model():
    """The strength model of the installed kernel's profile."""
    from . import KERNEL_VERSION
    from .profiles import profile_for
    return profile_for(KERNEL_VERSION).strength


def team_strength(team_name, roster, season, as_of, model=None):
    """(strength record for TeamInput.strength, coverage receipt).

    `model` is the strength model (the installed kernel's when None). Under
    honours-production-v3 the record carries only players with admissible
    evidence (honours or production); every other roster player is an
    Average low-confidence fallback, listed with the reason in the coverage
    receipt. Under player-state-v1 every roster row must carry its gsis id
    (an unresolved identity fails closed), the record adds each player's
    public state {family, basis, expected, drawn} and the league year's
    bound manifest digest, commitment and sorted latent keys; a player with
    no public row is listed as a fallback (no state, honours only).
    Identical for every club."""
    model = model or live_model()
    if model not in PARAMETERS:
        raise ValueError("unknown strength model %r" % (model,))
    code = club_codes(season).get(team_name, team_name)
    players, fallbacks, receipts = {}, [], []
    state_model = model == PLAYER_STATE_MODEL
    if state_model:
        from . import player_state
        bound = player_state.require_binding(season)
    for row in roster:
        pid = row["player_id"] if isinstance(row, dict) else row.player_id
        data = row if isinstance(row, dict) else {"player_id": pid, "gsis_id": getattr(row, "gsis_id", None)}
        gsis, join = resolve_id(data, code, season)
        if gsis is None:
            if state_model:
                raise ValueError("%s: no gsis id for %s (%s); the player-state model needs every identity"
                                 % (team_name, pid, join))
            fallbacks.append({"player_id": pid, "reason": "identity_" + join})
            continue
        record, rejected = player_record(gsis, season, as_of)
        if rejected:
            receipts.append({"player_id": pid, "gsis_id": gsis, "rejected": rejected})
        if state_model:
            state = player_state.public_state(gsis, season)
            if state is None:
                fallbacks.append({"player_id": pid, "gsis_id": gsis, "reason": "no_public_state"})
            if record is None and state is None:
                continue
            players[pid] = {"gsis_id": gsis, "join": join, **(record or {"offdef": None, "special": None,
                                                                          "production": None})}
            if state is not None:
                players[pid]["state"] = state
            continue
        if record is None:
            fallbacks.append({"player_id": pid, "reason": "no_admissible_evidence"})
            continue
        players[pid] = {"gsis_id": gsis, "join": join, **record}
    strength = {"model": model, "season": int(season), "as_of": _iso(as_of),
                "honour_seasons": list(honour_seasons(season)), "players": players}
    if state_model:
        strength.update({
            "league_year": int(season), "manifest_sha256": bound["manifest_sha256"],
            "commitment": bound["commitment"],
            "latent_keys": player_state.record_keys(
                sorted(p["gsis_id"] for p in players.values() if (p.get("state") or {}).get("drawn")), season)})
    coverage = {"team": team_name, "code": code, "roster_players": len(roster),
                "with_evidence": sorted(players),
                "with_honours": sorted(p for p, r in players.items() if r.get("offdef") or r.get("special")),
                "with_production": sorted(p for p, r in players.items() if r.get("production")),
                "with_job_evidence": sorted(p for p, r in players.items() if r.get("job")),
                "with_return_evidence": sorted(p for p, r in players.items() if r.get("returns")),
                "fallbacks": fallbacks, "rejected": receipts}
    if state_model:
        coverage["with_state"] = sorted(p for p, r in players.items() if (r.get("state") or {}).get("drawn"))
        coverage["state_bases"] = {}
        for r in players.values():
            basis = (r.get("state") or {}).get("basis") or "no_public_row"
            coverage["state_bases"][basis] = coverage["state_bases"].get(basis, 0) + 1
    return strength, coverage


def coverage_report(season, as_of, rosters=None):
    """Coverage for all 32 clubs: players with evidence, Average fallbacks
    (with reason) and rejected receipts. `rosters` maps club name to its
    roster rows; by default the 2014 league inventory (inventory_club),
    which is identity, not a depth chart."""
    if rosters is None:
        names = {code: name for name, code in club_codes(season).items()}
        rosters = {name: [] for name in names.values()}
        for p in _league(season)["players"]:
            if p.get("inventory_club") in names:
                rosters[names[p["inventory_club"]]].append({"player_id": p["player_id"]})
    clubs = {}
    for team, roster in sorted(rosters.items()):
        strength, coverage = team_strength(team, roster, season, as_of, model=MODEL)
        clubs[team] = {**coverage, "strength": strength}
    return {"model": MODEL, "season": int(season), "as_of": _iso(as_of),
            "honour_seasons": list(honour_seasons(season)), "clubs": clubs,
            "summary": {"clubs": len(clubs),
                        "players": sum(c["roster_players"] for c in clubs.values()),
                        "with_evidence": sum(len(c["with_evidence"]) for c in clubs.values()),
                        "with_honours": sum(len(c["with_honours"]) for c in clubs.values()),
                        "with_production": sum(len(c["with_production"]) for c in clubs.values()),
                        "with_job_evidence": sum(len(c["with_job_evidence"]) for c in clubs.values()),
                        "with_return_evidence": sum(len(c["with_return_evidence"]) for c in clubs.values()),
                        "fallbacks": sum(len(c["fallbacks"]) for c in clubs.values())}}


# ---- per-drive sub-composites and the edges -------------------------------------

def offense_starters(view, passer):
    """[(slot, player)] for the drive's offensive eleven (the union of the
    three offensive sub-units; kept for the coverage tooling)."""
    seen, unique = set(), []
    for members in offense_units(view, passer).values():
        for slot, p in members:
            if p.player_id not in seen:
                seen.add(p.player_id)
                unique.append((slot, p))
    return unique


def defense_starters(view):
    return [(grp, p) for grp, count in DEFENSE_STARTERS for p in usage.depth_order(view, grp)[:count]]


def offense_units(view, passer):
    """{unit: [(slot, player)]} for the drive's offensive sub-units (module docstring)."""
    front = [("OL", p) for p in usage.protection_front(view).values()]
    rb = [("RB", p) for p in usage.depth_order(view, "RB")[:1]]
    wr = [("WR", p) for p in usage.depth_order(view, "WR")[:3]]
    te = [("TE", p) for p in usage.depth_order(view, "TE")[:1]]
    fb = [("FB", p) for p in usage.depth_order(view, "FB")[:1]]
    qb = [("QB", passer)] if passer is not None else []
    return {"protection": front + rb, "passing": qb + wr + te, "run": front + te + fb + rb}


def box_safety(dbs):
    """The box safety among DB1-4: the first labelled SS, else the first
    labelled S or FS, else DB4 (a convention, applied to every club)."""
    for labels in (("SS",), ("S", "FS", "SAF")):
        for p in dbs:
            if str(p.position).upper() in labels:
                return p
    return dbs[3] if len(dbs) >= 4 else None


def defense_units(view):
    dl = [("DL", p) for p in usage.depth_order(view, "DL")[:4]]
    lb = [("LB", p) for p in usage.depth_order(view, "LB")[:3]]
    db = [("DB", p) for p in usage.depth_order(view, "DB")[:4]]
    box = box_safety([p for _, p in db])
    return {"rush": dl + lb[:1], "coverage": db + lb[1:3],
            "run_defense": dl + lb + ([("DB", box)] if box is not None else [])}


def _honours_value(record, slot, side):
    part = (record or {}).get("offdef")
    if part and part["unit"] == side and (slot == "QB") == (part["honour_group"] == "QB"):
        return part["value"]
    return 0.0


def state_slot_value(record, slot, side):
    """(value, honours value, drawn value) of one player in one lineup slot
    under the player-state model: his drawn value in SD units when his
    family's side is this side (the QB family only in the passer slot and
    no other family there), with an admissible honour on that side as a
    floor. A record without a state reads the honours value alone."""
    from . import player_state
    honours = _honours_value(record, slot, side)
    state = (record or {}).get("state") or {}
    drawn = 0.0
    family = state.get("family")
    if state.get("drawn") and player_state.FAMILY_SIDE.get(family) == side and (slot == "QB") == (family == "QB"):
        if "latent_value" not in record:
            raise player_state.PlayerStateError("latent value missing for a drawn player")
        drawn = float(record["latent_value"])
    return (max(honours, drawn) if honours > 0 else drawn), honours, drawn


def slot_value(record, slot, side):
    """(value, honours value, production value) of one player in one lineup
    slot under the preregistered max rule and the side/passer rule."""
    honours = _honours_value(record, slot, side)
    production = 0.0
    prod = (record or {}).get("production")
    if prod and prod["unit"] == side and (slot == "QB") == (prod["group"] == "QB"):
        production = prod["value"]
    # An honour can only lift: with one, the larger of the two; without one,
    # the production value stands, negative tiers included.
    return (max(honours, production) if honours > 0 else production), honours, production


def composite(strength, starters, side, unit=None):
    """(unit composite, contributor receipts) for one side's starters.

    With `unit` "protection" or "run", the offensive-line job rule applies:
    an OL slot with no honour and no proven window job counts
    OL_UNPROVEN_VALUE."""
    players = (strength or {}).get("players", {})
    state_model = (strength or {}).get("model") == PLAYER_STATE_MODEL
    total, rows = 0.0, []
    seen = set()
    for slot, player in starters:
        if player is None or player.player_id in seen:
            continue
        seen.add(player.player_id)
        record = players.get(player.player_id)
        if state_model:
            value, honours, production = state_slot_value(record, slot, side)
        else:
            value, honours, production = slot_value(record, slot, side)
        unproven = False
        if slot == "OL" and unit in ("protection", "run") and honours <= 0:
            if not ((record or {}).get("job") or {}).get("proven"):
                value, unproven = OL_UNPROVEN_VALUE, True
        if not value and not honours and not production:
            continue
        weight = QB_WEIGHT if slot == "QB" else 1
        contribution = weight * value
        total += contribution
        row = {"player_id": player.player_id, "slot": slot, "value": value, "position_weight": weight,
               "contribution": contribution}
        if honours:
            row["tier"] = record["offdef"]["tier"]
            row["evidence_weight"] = record["offdef"]["evidence_weight"]
        if production and not state_model:
            row["production_tier"] = record["production"]["tier"]
        if production and state_model:
            row["drawn_value"] = production
        if unproven:
            row["ol_unproven"] = True
        rows.append(row)
    return total, rows


def unit_composites(strength, view, side, passer=None):
    """{unit: {"composite", "contributors"}} for one side's three sub-units."""
    units = offense_units(view, passer) if side == "offense" else defense_units(view)
    out = {}
    for unit, members in units.items():
        comp, rows = composite(strength, members, side, unit)
        out[unit] = {"composite": comp, "contributors": rows}
    return out


def term_parts(units_by_side, params=None):
    """{term name: part} for every phase-2 term from the two sides' unit
    composites (a side without a record contributes no term)."""
    params = params or parameters()
    parts = {}
    for term in params.terms:
        units = units_by_side.get(term["side"])
        if units is None:
            continue
        parts[term["name"]] = term["slope"] * (units[term["unit"]]["composite"] - term["centre"])
    return parts


def drive_edge(offense_team, defense_team, off_view, def_view, passer, home_offense, params=None):
    """(touchdown-share edge, receipt) for one drive. `home_offense` is True
    only for the designated home club's offense at a home venue. The receipt
    also carries `int_edge` (interception-share shift) and `sack_shift`
    (per-dropback sack-probability shift) for the drive draw. `params` is the
    profile's StrengthParameters (honours-production-v3 when None)."""
    params = params or parameters()
    receipt = {"units": {}, "terms": {}}
    units_by_side = {}
    if getattr(offense_team, "strength", None):
        units_by_side["offense"] = unit_composites(offense_team.strength, off_view, "offense", passer)
        receipt["units"]["offense"] = units_by_side["offense"]
        off_part = None
    else:
        off_part = (offense_team.offense_anchor - params.legacy_anchor_centre) * params.legacy_anchor_scale
    if getattr(defense_team, "strength", None):
        units_by_side["defense"] = unit_composites(defense_team.strength, def_view, "defense")
        receipt["units"]["defense"] = units_by_side["defense"]
        def_part = None
    else:
        def_part = (defense_team.defense_anchor - params.legacy_anchor_centre) * params.legacy_anchor_scale
    parts = term_parts(units_by_side, params)
    receipt["terms"] = parts

    def total(outcome, side):
        return sum(v for t, v in ((t, parts.get(t["name"])) for t in params.terms)
                   if v is not None and t["outcome"] == outcome and t["side"] == side)

    if off_part is None:
        off_part = total("td_share", "offense")
    if def_part is None:
        def_part = total("td_share", "defense")
    home = params.home_edge if home_offense else 0.0
    edge = max(-params.edge_clamp, min(params.edge_clamp, off_part - def_part + home))
    int_edge = max(-params.int_edge_clamp, min(params.int_edge_clamp,
                                               total("int_share", "defense") - total("int_share", "offense")))
    sack_shift = max(-params.sack_shift_clamp, min(params.sack_shift_clamp,
                                                   total("sack_rate", "defense") - total("sack_rate", "offense")))
    receipt.update({"offense_part": off_part, "defense_part": def_part, "home": home, "edge": edge,
                    "int_edge": int_edge, "sack_shift": sack_shift})
    return edge, receipt


# ---- special teams --------------------------------------------------------------

def _special_value(strength, player, kind):
    """(tier value, continuous deviation) of a specialist from the club's record."""
    if player is None:
        return 0.0, None
    record = ((strength or {}).get("players") or {}).get(player.player_id) or {}
    if kind in ("KR", "PR"):
        part = (record.get("returns") or {}).get(kind)
    else:
        part = record.get("production")
        if part and part.get("group") != kind:
            part = None
    if not part:
        return 0.0, None
    return part.get("value", 0.0), part.get("deviation")


def kicker_adjustment(strength, kicker, params=None):
    """(make-probability shift, receipt): KICKER_SLOPE x the kicker's tier value."""
    params = params or parameters()
    value, _ = _special_value(strength, kicker, "K")
    shift = params.kicker_slope * value
    return shift, {"player_id": getattr(kicker, "player_id", None), "value": value, "shift": shift}


def punter_adjustment(strength, punter, params=None):
    """(gross-yards shift, receipt): PUNTER_SLOPE x the punter's shrunk net
    above his season's league mean (the continuous predictor), rounded."""
    params = params or parameters()
    _, deviation = _special_value(strength, punter, "P")
    shift = int(round(params.punter_slope * deviation)) if deviation is not None else 0
    return shift, {"player_id": getattr(punter, "player_id", None), "deviation": deviation, "shift": shift}


def returner_adjustment(strength, returner, kind, params=None):
    """(return-yards shift, receipt): the returner slope x his tier value, rounded."""
    params = params or parameters()
    value, _ = _special_value(strength, returner, kind)
    slope = params.kick_returner_slope if kind == "KR" else params.punt_returner_slope
    shift = int(round(slope * value))
    return shift, {"player_id": getattr(returner, "player_id", None), "value": value, "shift": shift}
