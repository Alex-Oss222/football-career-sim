#!/usr/bin/env python3
"""Calibrate the matchup sub-composites and the special-teams adjustments (E1 phase 2).

  python scripts/research/build_2014_strength_calibration_v3.py SOURCE_DIR

SOURCE_DIR holds the pinned nflverse files the earlier studies used: the
weekly depth charts and the regular-season play-by-play for 2010, 2011 and
2012 (sha256 recorded in the output). Honours come from
library/data/2010_2012_honours_evidence.json, production and returner tiers
from library/data/2010_2012_production_evidence.json.

Outputs library/data/2014_strength_calibration_v3.json. The prose report is
section 10 of library/2014_strength_calibration.md.

Everything in PREREGISTERED was written before this script's first fit ran.
The study method is the first study's, unchanged: 2012 Week 1 depth-chart
starters for role, drive-weighted least squares of each club's per-drive
outcome on its unit composite over the 32 clubs, shrinkage prior N(0,
0.025^2) per composite unit for a rate outcome, leave-one-club-out
prediction, drive-level joint check with a 500-draw game-cluster bootstrap
(seed 20140401). The target is the real 2012 regular season (pre-divergence);
the special-teams fits use the 2010-2011 and 2011-2012 season pairs of the
same pre-divergence files. No branch record, no post-divergence real result
and no club-specific treatment enters.

Disclosure, written before the fit: an earlier attempt at this phase was
lost to a container restart and only its printed summary survived in the
session scratchpad; the author read that summary before writing this block.
The rules below were therefore declared with knowledge of roughly what a
first fit would show. They are recorded as declared here, and the keep rule
is mechanical, so the record is still checkable, but this study is not
blind in the way the first two were.
"""
from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("study_v1", HERE / "build_2014_strength_calibration.py")
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
spec2 = importlib.util.spec_from_file_location("study_v2", HERE / "build_2014_strength_calibration_v2.py")
v2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v2)

HONOURS = ROOT / "library/data/2010_2012_honours_evidence.json"
PRODUCTION = ROOT / "library/data/2010_2012_production_evidence.json"
DRIVE_MODEL = ROOT / "library/data/2012_nfl_drive_model.json"
FIELD_POSITION = ROOT / "library/data/2012_nfl_field_position_model.json"
OUT = ROOT / "library/data/2014_strength_calibration_v3.json"
SEED = 20140401

PREREGISTERED = {
    "written_before_first_fit": "2026-09-30",
    "disclosure": "an earlier attempt at this phase was lost to a container restart; its printed summary was read "
                  "before this block was written (module docstring)",
    "centring": {
        "decision": "keep the preregistered 2012 study centres for every fit in this phase (the mean of the 32 real "
                    "2012 starting units for each sub-composite)",
        "reason": "the 2014 identity-ordered inventory lineups are not real depth charts, so their mean shift against "
                  "the 2012 centres is not evidence of a league shift; centring is revisited when the real 2014 "
                  "Week 1 depth charts are built in September (coordinator decision, September 30, 2026)",
    },
    "player_value": "as the second study (library/data/2014_strength_calibration_v2.json): with an admissible honour "
                    "the larger of the honours value and the production value, without one the production value "
                    "(negative tiers included); the QB rule and the side rule unchanged; no age shrink",
    "sub_units": {
        "note": "a mechanical slot convention applied identically to every club, declared here and mirrored by "
                "runtime/strength.py; the 2012 study reads the club's Week 1 depth chart rows in listed order, the "
                "runtime reads the drive's live lineup by club depth order",
        "offense": {
            "protection": "the five linemen of the protection front (weight 1 each) and RB1, the back who stays in "
                          "(weight 1)",
            "passing": "the passer (weight 3), WR1, WR2, WR3 and TE1 (weight 1 each)",
            "run": "the five linemen, TE1, FB1 when the club dressed a fullback, and RB1 the ball carrier (weight 1 each)",
        },
        "defense": {
            "rush": "DL1-4 and LB1, the first linebacker by depth (the rushing linebacker; weight 1 each)",
            "coverage": "DB1-4 and LB2-3, the coverage linebackers (weight 1 each)",
            "run_defense": "DL1-4, LB1-3 and the box safety: the first of DB1-4 labelled SS, else the first labelled "
                           "S or FS, else DB4 (weight 1 each)",
        },
        "unobserved": "which linebacker rushes and which safety plays the box is not observed pre-2013 in the pinned "
                      "sources; the split is a convention, reported as such",
    },
    "offensive_line_job_evidence": {
        "A_honours_only": "a lineman contributes his honours value only (the second study's rule)",
        "B_unproven_minus_one": "a lineman with no admissible honour and no window season with 8 or more starts "
                                "(library/data/2010_2012_production_evidence.json OL job rows; 2012 target: 2010-2011; "
                                "2014 branch: 2011-2012) counts -1 (Below-Average) in the protection and run "
                                "composites; a proven lineman without an honour counts 0",
        "adoption": "B is adopted only if the protection composite's leave-one-club-out skill on the sack-rate outcome "
                    "is higher under B than under A; otherwise A stands and the reason is recorded",
        "contamination": "a club that starts unproven linemen may be weak for other reasons; the term can carry club "
                         "quality, which is reported, not corrected",
    },
    "targets_2012": {
        "td_share": "per-drive touchdown share for the offense and allowed by the defense (as the first study)",
        "sack_rate": "sacks per dropback (pass attempts + sacks, two-point tries excluded), taken and allowed; "
                     "weight: dropbacks",
        "int_share": "interceptions thrown per drive and taken per drive (a drive with an interception "
                     "play, nflverse `interception`); weight: drives",
        "ypc": "rushing yards per carry on designed and scramble runs (play_type run; kneels excluded), gained and "
               "allowed; weight: carries; reported only: the kernel's drive tuples fix each drive's net and expose no "
               "yards-per-carry channel, so no ypc term can enter the kernel",
    },
    "terms": {
        "protection_vs_rush": "offense protection on sack_rate taken; defense rush on sack_rate allowed",
        "passing_vs_coverage": "offense passing on td_share and int_share thrown; defense coverage on td_share and "
                               "int_share allowed",
        "run_vs_front": "offense run on td_share and ypc; defense run_defense on td_share and ypc allowed",
    },
    "fit": "per term a single-slope drive-weighted least squares with intercept over the 32 clubs; shrinkage prior "
           "N(0, 0.025^2) per composite unit for a rate outcome (td_share, sack_rate, int_share) and N(0, 0.25^2) "
           "yards per composite unit for ypc; leave-one-club-out skill = 1 - (rmse / null rmse)^2; sign as strength "
           "(offense positive raises the good outcome; defense positive lowers the opponent's)",
    "keep_rule": "a term is kept only if its leave-one-club-out skill is positive and its sign is right; the "
                 "sack-rate sign is negative for protection (more protection, fewer sacks) and positive for the "
                 "rush, the int-share sign is negative for passing and positive for coverage",
    "same_outcome_two_terms": "when both of a side's td_share terms are kept, the adopted slopes are the joint "
                              "two-term fit's, each shrunk with its own joint standard error; when one is kept its "
                              "single-term shrunk slope is adopted",
    "drive_joint": "drive-level ordinary least squares of the outcome on every kept composite of both sides plus "
                   "the home indicator, standard errors from a 500-draw game-cluster bootstrap (seed 20140401)",
    "kernel_channels": {
        "td_share": "the sum of the kept td_share terms is the drive edge fed to drive_model.apply_edge through "
                    "field_position.category_mix (touchdown up, punt and turnover categories down), with the 0.023 "
                    "home term and the +/-0.12 clamp unchanged",
        "int_share": "the sum of the kept int_share terms shifts the interception category by that amount and the "
                     "punt category by its negative in category_mix (renormalised), separately from the td edge",
        "sack_rate": "the sum of the kept sack_rate terms shifts the per-dropback sack probability from the 2012 "
                     "league rate p0 to p1 = p0 + shift; the real drive of the drawn category is then drawn with "
                     "each tuple weighted by its binomial likelihood ratio (p1/p0)^sacks x ((1-p1)/(1-p0))^(dropbacks "
                     "- sacks); the drive tuples carry sacks and attempts, so the resample is supported; a zero "
                     "shift keeps the uniform draw exactly",
    },
    "special_teams": {
        "pairs": "2010 to 2011 and 2011 to 2012: a specialist with a tier in season t and a qualifying line in t+1; "
                 "outcome = the t+1 raw metric (kicker: field goals made over expected per attempt; punter: net "
                 "yards per punt; returner: yards per return), weight = the t+1 denominator",
        "predictors": {"tier": "the season-t tier value (Elite 2, Plus 1, Average 0, Below-Average -1, "
                               "Replacement-Level -2)",
                       "continuous": "the season-t shrunk metric minus that season's league mean (the same units "
                                     "as the outcome), a sensitivity declared here"},
        "priors": {"kicker": "N(0, 0.025^2) per tier unit; N(0, 1) persistence for the continuous predictor",
                   "punter": "N(0, 1 yard^2) per tier unit; N(0, 1) persistence",
                   "returner": "N(0, 1 yard^2) per tier unit; N(0, 1) persistence"},
        "keep_rule": "a predictor is kept only if its leave-one-pair-out skill is positive and its slope positive; "
                     "when both predictors are kept the one with the higher skill is adopted (the tier on a tie); a "
                     "specialist term with no kept predictor is wired in the kernel with slope 0 (carried, inactive) "
                     "and reported as dropped for lack of skill",
        "channels": {"kicker": "the adopted slope times the kicker's value is added to the field-goal make "
                               "probability at the drawn distance, clipped to [0.02, 0.99]",
                     "punter": "the adopted slope times the punter's value, rounded, is added to a returned or "
                               "downed punt's gross yards with the start recomputed and kept inside the field; "
                               "touchbacks are unchanged",
                     "returner": "the adopted slope times the returner's value, rounded, is added to a returned "
                                 "kick's or punt's return yards with the start recomputed and kept inside the field",
                     "coverage_units": "out of scope: no coverage-unit strength is modelled"},
    },
    "field_goal_distance": {
        "why": "defect register item 18: the drive model's make rate is flat inside each distance band (55+ yards "
               "made 34 of 48 in the earlier sample)",
        "fit": "one logistic slope per yard of kick distance on every 2010-2012 regular-season field-goal attempt "
               "(blocked counted as missed, as the drive model counts them), by Newton iteration",
        "anchor": "per drive-model band a separate intercept solved by bisection so that the mean fitted probability "
                  "over the band's own 2012 attempts equals the band's 2012 make rate; the band rows of "
                  "runtime/bands.py keep their 2012 centres by construction",
    },
    "return_centres": "mean and SD of return yards over the returned records of the 2012 kickoff and punt pools "
                      "(library/data/2012_nfl_field_position_model.json) for two new band rows",
}
TIER_VALUE = {"Elite": 2, "Plus": 1, "Average": 0, "Below-Average": -1, "Replacement-Level": -2}
PRIOR_RATE = 0.025
PRIOR_YPC = 0.25
PRIOR_ST = {"K": (0.025, 1.0), "P": (1.0, 1.0), "KR": (1.0, 1.0), "PR": (1.0, 1.0)}
OL_LABELS = {"T", "G", "C", "OT", "OG", "OL", "LT", "LG", "RG", "RT"}
DL_LABELS = {"DE", "DT", "NT", "DL"}
LB_LABELS = {"LB", "OLB", "ILB", "MLB"}
DB_LABELS = {"CB", "S", "SS", "FS", "DB", "SAF"}
TARGET = v2.TARGET
UNITS = {"offense": ("protection", "passing", "run"), "defense": ("rush", "coverage", "run_defense")}
OUTCOMES = {
    # (outcome, side, unit, expected sign as strength, prior)
    ("sack_rate", "offense", "protection"), ("sack_rate", "defense", "rush"),
    ("td_share", "offense", "passing"), ("int_share", "offense", "passing"),
    ("td_share", "defense", "coverage"), ("int_share", "defense", "coverage"),
    ("td_share", "offense", "run"), ("ypc", "offense", "run"),
    ("td_share", "defense", "run_defense"), ("ypc", "defense", "run_defense"),
}
# Sign convention on the raw fitted slope (outcome regressed on the composite)
# that makes the term "right": offense strength raises td_share and ypc and
# lowers sack_rate and int_share; defense strength lowers the opponent's
# td_share and ypc, raises its sack_rate and int_share taken.
RAW_SIGN = {("offense", "td_share"): 1, ("offense", "ypc"): 1, ("offense", "sack_rate"): -1, ("offense", "int_share"): -1,
            ("defense", "td_share"): -1, ("defense", "ypc"): -1, ("defense", "sack_rate"): 1, ("defense", "int_share"): 1}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def shrink(b, se, prior):
    tau2 = prior ** 2
    return b * tau2 / (tau2 + se * se), math.sqrt(tau2 * se * se / (tau2 + se * se))


# ------------------------------------------------------------- sub-units
def offense_units(rows):
    """{unit: [(row, weight)]} from a club's Week 1 offense depth rows (listed order)."""
    ol = [r for r in rows if r["position"] in OL_LABELS][:5]
    qb = [r for r in rows if r["position"] == "QB"][:1]
    rb = [r for r in rows if r["position"] in ("RB", "HB")][:1]
    fb = [r for r in rows if r["position"] == "FB"][:1]
    wr = [r for r in rows if r["position"] == "WR"][:3]
    te = [r for r in rows if r["position"] == "TE"][:1]
    return {"protection": [(r, 1) for r in ol] + [(r, 1) for r in rb],
            "passing": [(r, 3) for r in qb] + [(r, 1) for r in wr + te],
            "run": [(r, 1) for r in ol + te + fb + rb]}


def box_safety(dbs):
    for label in (("SS",), ("S", "FS", "SAF")):
        for r in dbs:
            if r["position"] in label:
                return r
    return dbs[3] if len(dbs) >= 4 else None


def defense_units(rows):
    dl = [r for r in rows if r["position"] in DL_LABELS][:4]
    lb = [r for r in rows if r["position"] in LB_LABELS][:3]
    db = [r for r in rows if r["position"] in DB_LABELS][:4]
    box = box_safety(db)
    return {"rush": [(r, 1) for r in dl + lb[:1]],
            "coverage": [(r, 1) for r in db + lb[1:3]],
            "run_defense": [(r, 1) for r in dl + lb + ([box] if box else [])]}


def ol_proven(production, window):
    """gsis -> True when the lineman has a window season with 8+ starts."""
    out = {}
    for pid, p in production["players"].items():
        for season in window:
            s = p["seasons"].get(str(season))
            if s and s.get("group") == "OL" and s.get("starts", 0) >= 8:
                out[pid] = True
    return out


def unit_composite(members, hv, pv, side, proven, ol_rule):
    """(composite, contributors) for one sub-unit under the phase-2 rules."""
    total, rows, seen = 0.0, [], set()
    for row, weight in members:
        pid = row["player_id"]
        if pid in seen:
            continue
        seen.add(pid)
        is_qb = row["position"] == "QB"
        value, receipt = v2.combined_value(pid, row["position"], is_qb and weight == 3, hv, pv, side)
        if ol_rule == "B" and row["position"] in OL_LABELS and receipt["honours_value"] <= 0 and not proven.get(pid):
            value = -1.0
            receipt["ol_unproven"] = True
        if value or receipt["honours_value"] or receipt["production_value"]:
            rows.append({"player_id": pid, "name": row["name"], "position": row["position"], "position_weight": weight,
                         "value": value, "contribution": weight * value, **receipt})
            total += weight * value
    return total, rows


# ------------------------------------------------------------- 2012 drives
def drive_rows(path):
    """Per-drive rows of the 2012 regular season with the phase-2 outcomes."""
    grouped = {}
    for r in v1.read(path):
        if r["season_type"] != "REG" or not r["posteam"] or not r["fixed_drive"]:
            continue
        key = (r["game_id"], r["fixed_drive"])
        d = grouped.get(key)
        if d is None:
            d = grouped[key] = {"game": r["game_id"], "off": v1.team(r["posteam"]), "def": v1.team(r["defteam"]),
                                "home": int(r["posteam"] == r["home_team"]), "result": r["fixed_drive_result"],
                                "sacks": 0, "dropbacks": 0, "carries": 0, "rush_yards": 0.0, "interception": 0}
        if d["off"] != v1.team(r["posteam"]):
            continue
        if r["interception"] == "1":
            d["interception"] = 1
        if r["play_type"] == "pass" and r["two_point_attempt"] != "1":
            d["dropbacks"] += 1
            d["sacks"] += r["sack"] == "1"
        elif r["play_type"] == "run" and r["two_point_attempt"] != "1":
            d["carries"] += 1
            d["rush_yards"] += float(r["yards_gained"] or 0)
    out = []
    for d in grouped.values():
        out.append({**d, "td": 1.0 if d["result"] == "Touchdown" else 0.0,
                    "int": float(d["interception"])})
    return out


def club_outcomes(rows):
    agg = defaultdict(lambda: defaultdict(float))
    for d in rows:
        for side, club in (("off", d["off"]), ("def", d["def"])):
            a = agg[club]
            a[side + "_drives"] += 1
            a[side + "_td"] += d["td"]
            a[side + "_int"] += d["int"]
            a[side + "_sacks"] += d["sacks"]
            a[side + "_dropbacks"] += d["dropbacks"]
            a[side + "_carries"] += d["carries"]
            a[side + "_rush_yards"] += d["rush_yards"]
    out = {}
    for club, a in agg.items():
        out[club] = {}
        for side in ("off", "def"):
            out[club][side] = {
                "td_share": (a[side + "_td"] / a[side + "_drives"], a[side + "_drives"]),
                "int_share": (a[side + "_int"] / a[side + "_drives"], a[side + "_drives"]),
                "sack_rate": (a[side + "_sacks"] / a[side + "_dropbacks"], a[side + "_dropbacks"]),
                "ypc": (a[side + "_rush_yards"] / a[side + "_carries"], a[side + "_carries"]),
            }
    return out


def fit_term(x, y, w, side, outcome):
    a, b, se, r2 = v1.wls(x, y, w)
    prior = PRIOR_YPC if outcome == "ypc" else PRIOR_RATE
    strength_slope = RAW_SIGN[(side, outcome)] * b
    shrunk, shrunk_sd = shrink(strength_slope, se, prior)
    comp_sd = v1.sd(x)
    return {"intercept": a, "raw_slope": b, "slope": strength_slope, "se": se, "r2": r2, "loo": v1.loo(x, y, w),
            "shrunk_slope": shrunk, "shrunk_sd": shrunk_sd, "prior_sd": prior, "composite_mean": v1.mean(x),
            "composite_sd": comp_sd, "composite_min": min(x), "composite_max": max(x),
            "implied_club_sd": abs(shrunk) * comp_sd}


def joint_two_term(x1, x2, y, w, side, outcome):
    """Weighted two-term fit with intercept; drop-one-club LOO and per-term standard errors."""
    n = len(y)
    k = n / sum(w)
    sw = [wi * k for wi in w]
    X = [[1.0, a, b] for a, b in zip(x1, x2)]

    def fit(idx):
        Xw = [[v * math.sqrt(sw[i]) for v in X[i]] for i in idx]
        yw = [y[i] * math.sqrt(sw[i]) for i in idx]
        return v1.ols(Xw, yw)

    beta = fit(range(n))
    pred = [sum(b * v for b, v in zip(beta, row)) for row in X]
    my = v1.mean(y, sw)
    resid = [yi - pi for yi, pi in zip(y, pred)]
    sse = sum(wi * r * r for r, wi in zip(resid, sw))
    sst = sum(wi * (yi - my) ** 2 for yi, wi in zip(y, sw))
    s2 = sse / (n - 3)
    # (X'WX)^-1 diagonal for the standard errors.
    XtWX = [[sum(sw[i] * X[i][a] * X[i][b] for i in range(n)) for b in range(3)] for a in range(3)]
    inv_diag = []
    for j in range(3):
        e = [1.0 if i == j else 0.0 for i in range(3)]
        col = v1.solve([row[:] for row in XtWX], e)
        inv_diag.append(col[j])
    ses = [math.sqrt(max(0.0, s2 * d)) for d in inv_diag]
    errors, null = [], []
    for i in range(n):
        keep = [j for j in range(n) if j != i]
        bi = fit(keep)
        errors.append(y[i] - sum(b * v for b, v in zip(bi, X[i])))
        null.append(y[i] - v1.mean([y[j] for j in keep], [sw[j] for j in keep]))
    rmse = math.sqrt(v1.mean([e * e for e in errors]))
    rmse0 = math.sqrt(v1.mean([e * e for e in null]))
    sign = RAW_SIGN[(side, outcome)]
    prior = PRIOR_YPC if outcome == "ypc" else PRIOR_RATE
    return {"slopes": [sign * beta[1], sign * beta[2]], "se": ses[1:], "r2": 1 - sse / sst,
            "shrunk_slopes": [shrink(sign * beta[1], ses[1], prior)[0], shrink(sign * beta[2], ses[2], prior)[0]],
            "loo": {"rmse": rmse, "null_rmse": rmse0, "skill": 1 - (rmse / rmse0) ** 2}}


def drive_joint(rows, comps, home_key, outcome):
    """Drive-level OLS of `outcome` on the given composites (name -> {club: value})
    and the home indicator, with a game-cluster bootstrap. `comps` is a list of
    (name, side, mapping)."""
    games = sorted({d["game"] for d in rows})
    by_game = defaultdict(list)
    for d in rows:
        by_game[d["game"]].append(d)
    if outcome == "sack_rate":
        sample_rows = [d for d in rows if d["dropbacks"]]
        yfn, wfn = (lambda d: d["sacks"] / d["dropbacks"]), (lambda d: d["dropbacks"])
    elif outcome == "ypc":
        sample_rows = [d for d in rows if d["carries"]]
        yfn, wfn = (lambda d: d["rush_yards"] / d["carries"]), (lambda d: d["carries"])
    else:
        sample_rows = rows
        yfn, wfn = (lambda d: d["td"] if outcome == "td_share" else d["int"]), (lambda d: 1.0)
    by_game = defaultdict(list)
    for d in sample_rows:
        by_game[d["game"]].append(d)

    def design(d):
        return [1.0] + [m[d["off"] if side == "offense" else d["def"]] for _, side, m in comps] + [float(d["home"])]

    def fit(sample):
        X = [[v * math.sqrt(wfn(d)) for v in design(d)] for d in sample]
        return v1.ols(X, [yfn(d) * math.sqrt(wfn(d)) for d in sample])

    point = fit(sample_rows)
    rng = random.Random(SEED)
    draws = []
    for _ in range(500):
        sample = []
        for g in (rng.choice(games) for _ in games):
            sample.extend(by_game.get(g, []))
        draws.append(fit(sample))
    ses = [v1.sd([dr[i] for dr in draws]) for i in range(len(point))]
    out = {"intercept": point[0], "home": point[-1], "se_home": ses[-1], "drives": len(sample_rows)}
    for i, (name, side, _) in enumerate(comps):
        out[side + "_" + name] = {"coefficient": point[i + 1], "se": ses[i + 1],
                                  "as_strength": RAW_SIGN[(side, outcome)] * point[i + 1]}
    return out


def study_2012(source, honours, production, ol_rule):
    starters = v1.depth_starters(source / "depth_charts_2012.csv")
    rows = drive_rows(source / "play_by_play_2012.csv.gz")
    outcomes = club_outcomes(rows)
    clubs = sorted(outcomes)
    hv = v2.honours_values(honours, [2010, 2011], "2012-09-05")
    groups = v2.honour_groups(honours)
    for pid, h in hv.items():
        h["group"] = groups.get(h["honours"][0]["evidence_id"])
    pv = v2.production_values(production, [2010, 2011])
    proven = ol_proven(production, [2010, 2011])
    comps = {side: {unit: {} for unit in units} for side, units in UNITS.items()}
    detail = {}
    for club in clubs:
        off = offense_units(starters[club]["offense"])
        dfn = defense_units(starters[club]["defense"])
        for side, units in (("offense", off), ("defense", dfn)):
            for unit, members in units.items():
                total, contributors = unit_composite(members, hv, pv, side, proven, ol_rule)
                comps[side][unit][club] = total
                detail.setdefault(club, {})[side + "_" + unit] = {"composite": total, "contributors": contributors}
    fits = {}
    for outcome, side, unit in sorted(OUTCOMES):
        key = "off" if side == "offense" else "def"
        x = [comps[side][unit][c] for c in clubs]
        y = [outcomes[c][key][outcome][0] for c in clubs]
        w = [outcomes[c][key][outcome][1] for c in clubs]
        f = fit_term(x, y, w, side, outcome)
        f["keep"] = f["loo"]["skill"] > 0 and f["slope"] > 0
        fits["%s_%s_%s" % (outcome, side, unit)] = f
    # joint two-term td_share fits per side
    joint = {}
    for side, (u1, u2) in (("offense", ("passing", "run")), ("defense", ("coverage", "run_defense"))):
        key = "off" if side == "offense" else "def"
        joint[side] = joint_two_term([comps[side][u1][c] for c in clubs], [comps[side][u2][c] for c in clubs],
                                     [outcomes[c][key]["td_share"][0] for c in clubs],
                                     [outcomes[c][key]["td_share"][1] for c in clubs], side, "td_share")
        joint[side]["units"] = [u1, u2]
    adopted = {}
    for side, (u1, u2) in (("offense", ("passing", "run")), ("defense", ("coverage", "run_defense"))):
        kept = [u for u in (u1, u2) if fits["td_share_%s_%s" % (side, u)]["keep"]]
        for u in kept:
            f = fits["td_share_%s_%s" % (side, u)]
            slope = joint[side]["shrunk_slopes"][(u1, u2).index(u)] if len(kept) == 2 else f["shrunk_slope"]
            adopted["td_share_%s_%s" % (side, u)] = {
                "outcome": "td_share", "side": side, "unit": u, "slope": slope, "centre": f["composite_mean"],
                "composite_sd": f["composite_sd"], "loo_skill": f["loo"]["skill"], "r2": f["r2"],
                "from": "joint two-term fit (both kept)" if len(kept) == 2 else "single-term fit"}
    for outcome in ("sack_rate", "int_share"):
        for side, unit in (("offense", "protection" if outcome == "sack_rate" else "passing"),
                           ("defense", "rush" if outcome == "sack_rate" else "coverage")):
            f = fits["%s_%s_%s" % (outcome, side, unit)]
            if f["keep"]:
                adopted["%s_%s_%s" % (outcome, side, unit)] = {
                    "outcome": outcome, "side": side, "unit": unit, "slope": f["shrunk_slope"],
                    "centre": f["composite_mean"], "composite_sd": f["composite_sd"], "loo_skill": f["loo"]["skill"],
                    "r2": f["r2"], "from": "single-term fit"}
    # ypc terms are reported only (no kernel channel), never adopted
    joint_drive = {}
    for outcome in ("td_share", "sack_rate", "int_share"):
        terms = [(t["unit"], t["side"], comps[t["side"]][t["unit"]]) for t in adopted.values() if t["outcome"] == outcome]
        if terms:
            joint_drive[outcome] = drive_joint(rows, terms, "home", outcome)
    implied = {k: abs(t["slope"]) * t["composite_sd"] for k, t in adopted.items()}
    td_parts = [v for k, v in implied.items() if k.startswith("td_share")]
    net = math.sqrt(sum(v * v for v in td_parts))
    league = {"drives": len(rows), "td_share": v1.mean([d["td"] for d in rows]),
              "int_share": v1.mean([d["int"] for d in rows]),
              "sack_rate": sum(d["sacks"] for d in rows) / sum(d["dropbacks"] for d in rows),
              "ypc": sum(d["rush_yards"] for d in rows) / sum(d["carries"] for d in rows)}
    club_sd = {}
    for outcome in ("td_share", "sack_rate", "int_share", "ypc"):
        for key in ("off", "def"):
            club_sd["%s_%s" % (outcome, key)] = v1.sd([outcomes[c][key][outcome][0] for c in clubs])
    return {"ol_rule": ol_rule, "league": league, "club_outcome_sd": club_sd, "fits": fits, "joint_two_term": joint,
            "adopted_terms": adopted, "drive_joint_kept_terms": joint_drive, "implied_club_sd": implied,
            "net_td_share_edge_sd": net, "fraction_of_target": net / TARGET["net"],
            "points_per_team_game_sd": net * v2.POINTS_PER_TD_SHARE * v2.DRIVES_PER_TEAM_GAME,
            "composites": {side: {unit: {c: comps[side][unit][c] for c in clubs} for unit in units}
                           for side, units in UNITS.items()},
            "clubs": detail}


# --------------------------------------------------------- special teams
def st_pairs(production, group):
    """[(prior tier value, prior deviation, next raw, next n, name, seasons)] over 2010->2011, 2011->2012."""
    pairs = []
    if group in ("KR", "PR"):
        block = production["returners"]
        rows = {pid: {s: v.get(group) for s, v in p["seasons"].items() if v.get(group)} for pid, p in block.items()}
        means = {s: production["seasons"][s]["returners"]["league_means"].get(group, {}).get("mean")
                 for s in production["seasons"]}
    else:
        rows = {pid: {s: v for s, v in p["seasons"].items() if v.get("group") == group}
                for pid, p in production["players"].items()}
        means = {s: production["seasons"][s]["league_means"].get(group, {}).get("mean") for s in production["seasons"]}
    for pid, seasons in rows.items():
        for t in (2010, 2011):
            prior, nxt = seasons.get(str(t)), seasons.get(str(t + 1))
            if not prior or not nxt or prior.get("tier") is None or nxt.get("raw") is None:
                continue
            pairs.append({"player_id": pid, "seasons": [t, t + 1], "tier": prior["tier"],
                          "tier_value": TIER_VALUE[prior["tier"]], "deviation": prior["shrunk"] - means[str(t)],
                          "next_raw": nxt["raw"], "next_n": nxt["n"]})
    return pairs


def loo_pairs(x, y, w):
    return v1.loo(x, y, w)


def st_fit(pairs, group):
    out = {"pairs": len(pairs)}
    if len(pairs) < 8:
        out["adopted"] = None
        out["reason"] = "fewer than 8 season pairs"
        return out
    y = [p["next_raw"] for p in pairs]
    w = [p["next_n"] for p in pairs]
    prior_tier, prior_cont = PRIOR_ST[group]
    for name, key, prior in (("tier", "tier_value", prior_tier), ("continuous", "deviation", prior_cont)):
        x = [p[key] for p in pairs]
        a, b, se, r2 = v1.wls(x, y, w)
        shrunk, shrunk_sd = shrink(b, se, prior)
        loo = loo_pairs(x, y, w)
        out[name] = {"intercept": a, "slope": b, "se": se, "shrunk_slope": shrunk, "shrunk_sd": shrunk_sd,
                     "prior_sd": prior, "r2": r2, "loo": loo, "keep": loo["skill"] > 0 and b > 0}
    by_tier = defaultdict(list)
    for p in pairs:
        by_tier[p["tier"]].append((p["next_raw"], p["next_n"]))
    out["next_metric_by_prior_tier"] = {t: {"pairs": len(v), "weighted_mean": sum(a * n for a, n in v) / sum(n for _, n in v)}
                                        for t, v in by_tier.items()}
    kept = [n for n in ("tier", "continuous") if out[n]["keep"]]
    if not kept:
        out["adopted"] = None
        out["reason"] = "no predictor with positive leave-one-pair-out skill and a positive slope"
    else:
        best = max(kept, key=lambda n: (out[n]["loo"]["skill"], n == "tier"))
        out["adopted"] = {"predictor": best, "slope": out[best]["shrunk_slope"]}
    return out


# ---------------------------------------------------- field-goal distance
def fg_attempts(source):
    rows = []
    for season in (2010, 2011, 2012):
        for r in v1.read(source / ("play_by_play_%d.csv.gz" % season)):
            if r["season_type"] == "REG" and r["play_type"] == "field_goal" and r["kick_distance"]:
                rows.append((season, float(r["kick_distance"]), r["field_goal_result"] == "made"))
    return rows


def logistic_fit(rows):
    a, b = 4.0, -0.08
    for _ in range(50):
        g = [0.0, 0.0]
        H = [[0.0, 0.0], [0.0, 0.0]]
        for _, d, made in rows:
            p = 1 / (1 + math.exp(-(a + b * d)))
            g[0] += made - p
            g[1] += (made - p) * d
            wgt = p * (1 - p)
            H[0][0] += wgt
            H[0][1] += wgt * d
            H[1][1] += wgt * d * d
        H[1][0] = H[0][1]
        step = v1.solve([row[:] for row in H], g)
        a, b = a + step[0], b + step[1]
        if abs(step[0]) < 1e-10 and abs(step[1]) < 1e-12:
            break
    return a, b


def fg_distance_model(source):
    rows = fg_attempts(source)
    a, b = logistic_fit(rows)
    drive = load(DRIVE_MODEL)["rates"]
    bands = {}
    for label, low, high in drive["fg_bin_edges"]:
        made, att = drive["fg_by_distance"][label]
        rate = made / att
        dists = [d for s, d, _ in rows if s == 2012 and low <= d <= high]
        lo, hi = -20.0, 20.0
        for _ in range(100):
            mid = (lo + hi) / 2
            mean_p = sum(1 / (1 + math.exp(-(mid + b * d))) for d in dists) / len(dists)
            if mean_p < rate:
                lo = mid
            else:
                hi = mid
        bands[label] = {"low": low, "high": high, "intercept": (lo + hi) / 2, "rate_2012": rate,
                        "attempts_2012": len(dists), "made_2012": made, "attempts_2012_drive_model": att}
    return {"attempts_2010_2012": len(rows), "made_2010_2012": sum(1 for _, _, m in rows if m),
            "pooled_intercept": a, "slope_per_yard": b, "bands": bands,
            "long_range_2010_2012": {"50_54": [sum(1 for _, d, m in rows if 50 <= d <= 54 and m),
                                              sum(1 for _, d, _ in rows if 50 <= d <= 54)],
                                     "55_plus": [sum(1 for _, d, m in rows if d >= 55 and m),
                                                 sum(1 for _, d, _ in rows if d >= 55)]}}


def return_centres():
    fp = load(FIELD_POSITION)
    kick = [r[3] for r in fp["kickoff_pool"] if r[5] == "returned"]
    punt = [r[3] for r in fp["punt_pool"] if r[1] == "returned"]
    return {"kickoff_return_yards": {"n": len(kick), "mean": v1.mean(kick), "sd": v1.sd(kick)},
            "punt_return_yards": {"n": len(punt), "mean": v1.mean(punt), "sd": v1.sd(punt)}}


def main():
    source = Path(sys.argv[1])
    honours, production = load(HONOURS), load(PRODUCTION)
    study_a = study_2012(source, honours, production, "A")
    study_b = study_2012(source, honours, production, "B")
    skill_a = study_a["fits"]["sack_rate_offense_protection"]["loo"]["skill"]
    skill_b = study_b["fits"]["sack_rate_offense_protection"]["loo"]["skill"]
    ol_rule = "B" if skill_b > skill_a else "A"
    primary = study_b if ol_rule == "B" else study_a
    special = {}
    for group in ("K", "P", "KR", "PR"):
        special[group] = st_fit(st_pairs(production, group), group)
    fg = fg_distance_model(source)
    fp = load(FIELD_POSITION)
    made, n = fp["band_centres"]["sacks_per_dropback"]
    output = {
        "schema_version": 1,
        "built_by": "scripts/research/build_2014_strength_calibration_v3.py",
        "policy": "runtime/2014_engine_decisions.md E1 phase 2 (matchup sub-composites, special teams); "
                  "runtime/defect_register.md items 1, 18",
        "preregistered": PREREGISTERED,
        "sources": {"honours_evidence": {"file": str(HONOURS.relative_to(ROOT)), "sha256": v1.sha(HONOURS)},
                    "production_evidence": {"file": str(PRODUCTION.relative_to(ROOT)), "sha256": v1.sha(PRODUCTION)},
                    "drive_model": {"file": str(DRIVE_MODEL.relative_to(ROOT)), "sha256": v1.sha(DRIVE_MODEL)},
                    "field_position_model": {"file": str(FIELD_POSITION.relative_to(ROOT)), "sha256": v1.sha(FIELD_POSITION)},
                    **{name: {"sha256": v1.sha(source / name)} for name in
                       ("depth_charts_2012.csv", "play_by_play_2010.csv.gz", "play_by_play_2011.csv.gz",
                        "play_by_play_2012.csv.gz")}},
        "ol_job_evidence_decision": {"adopted": ol_rule, "protection_sack_rate_loo_skill": {"A": skill_a, "B": skill_b}},
        "study_2012": primary,
        "study_2012_other_ol_rule": {"ol_rule": "A" if ol_rule == "B" else "B",
                                     "fits": (study_a if ol_rule == "B" else study_b)["fits"],
                                     "adopted_terms": (study_a if ol_rule == "B" else study_b)["adopted_terms"]},
        "sack_rate_base": {"p0": made / n, "made": made, "n": n,
                           "source": "2012 field-position artifact band centre sacks_per_dropback"},
        "special_teams": special,
        "field_goal_distance": fg,
        "return_centres_2012": return_centres(),
    }
    OUT.write_text(json.dumps(output, indent=1, default=float) + "\n", encoding="utf-8")
    print("OL rule", json.dumps(output["ol_job_evidence_decision"]))
    for name, f in sorted(primary["fits"].items()):
        print("%-34s slope %+.5f se %.5f shrunk %+.5f R2 %.3f LOO %+.3f mean %.2f sd %.2f implied %.4f keep %s" % (
            name, f["slope"], f["se"], f["shrunk_slope"], f["r2"], f["loo"]["skill"], f["composite_mean"],
            f["composite_sd"], abs(f["shrunk_slope"]) * f["composite_sd"], f["keep"]))
    for side, j in primary["joint_two_term"].items():
        print("joint td_share", side, j["units"], "slopes", j["slopes"], "shrunk", j["shrunk_slopes"], "R2 %.3f LOO %.3f" % (j["r2"], j["loo"]["skill"]))
    print("adopted", json.dumps(primary["adopted_terms"], indent=0))
    print("drive joint", json.dumps(primary["drive_joint_kept_terms"], indent=0))
    print("net td edge sd %.4f (%.0f%% of target) pts %.2f" % (primary["net_td_share_edge_sd"], 100 * primary["fraction_of_target"], primary["points_per_team_game_sd"]))
    for grp, s in special.items():
        print("special", grp, json.dumps({k: v for k, v in s.items() if k in ("pairs", "adopted", "reason", "next_metric_by_prior_tier")}))
        for name in ("tier", "continuous"):
            if name in s:
                f = s[name]
                print("   %-11s slope %+.4f se %.4f shrunk %+.4f R2 %.3f LOO %+.3f keep %s" % (
                    name, f["slope"], f["se"], f["shrunk_slope"], f["r2"], f["loo"]["skill"], f["keep"]))
    print("fg distance", json.dumps({k: v for k, v in fg.items() if k != "bands"}), json.dumps(fg["bands"]))
    print("return centres", json.dumps(output["return_centres_2012"]))


if __name__ == "__main__":
    main()
