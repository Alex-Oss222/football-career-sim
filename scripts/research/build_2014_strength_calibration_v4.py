#!/usr/bin/env python3
"""Strength calibration v4: the matchup terms refit on player-state E-values (kernel 2014.6, plan batch B4c).

  python scripts/research/build_2014_strength_calibration_v4.py [--sources DIR] [--check]

Writes library/data/2014_strength_calibration_v4.json and the generated section 11 of
library/2014_strength_calibration.md (between the strength-v4 markers). Data only: nothing
in runtime/ reads it until batch B7. Stdlib only; sources only through the B2 gate.

Rules (library/2014_6_pre_build_specification.md, section 4, Strength v4; U1(b), U3):
- Targets: the 2012 regular season with 2010-2011 evidence and the 2013 regular season with
  2011-2012 evidence; club outcomes from the play-by-play (touchdown share per drive, sacks
  per dropback, interceptions per drive, yards per carry), per side.
- Inputs are one-step-forecast E-values from the player-state model
  (library/data/2010_2014_player_state_model.json) at each target's evidence cutoff: the
  player's own lines in the two evidence seasons, his honours in them (public before the
  target's kickoff), the flat draft-slot prior for a rookie (his own class left out). A
  player's value is E over his family's true-state SD; a family with no state (offensive
  linemen), no spread, or a held swing (U5) contributes 0, the Average of the runtime.
  Offensive linemen keep rule B plus honours (the phase-2 rule): an honour's value
  (Elite 2, Plus 1, times its evidence weight), else -1 when unproven (no evidence season
  with 8 or more starts), else 0.
- Lineups: each club's Week 1 depth chart, depth_team 1, in the chart's listed order, with
  contemporaneous labels: the chart slot's family, then that season's weekly roster
  position, never the chart's back-filled position column. DB units are the slot-family
  base four; the box safety is the first of them in an SS slot, else S or FS, else the fourth.
- Fit: pooled drive-weighted least squares with season intercepts over the 64 club-seasons,
  leave-one-club-out prediction (both of a club's seasons out), the shrinkage prior N(0,
  0.025^2) per composite unit (N(0, 0.25^2) yards for yards per carry). Keep rule: positive
  leave-one-club-out skill and the right sign, reproduced by pass 2 (nflscrapR outcomes
  with an independent drive classifier, and pass-2 E-values). Symmetric (U3): a live term
  that fails goes to slope 0, a newly passing term becomes live; the individual passer
  interception term stays not adopted; yards-per-carry terms are reported only.
- Centres are the target-set means of the composites. HOME_EDGE comes from the drive-level
  joint regression (season intercepts, the adopted touchdown-share composites, home) with a
  500-draw game-cluster bootstrap. PUNTER_SLOPE is refit on the committed pt_net_yards
  definition with the 2010-2011, 2011-2012 and 2012-2013 pairs, pass 2 on the same
  definition from nflscrapR; if the passes disagree beyond 2 pass-1 standard errors the
  smaller is adopted, labelled single-pass. Kicker and returner slopes stay 0.
- Only aggregate fits are committed: no per-club composite, outcome or contributor row.
  Self-influence is reported as a summary over every club and every player.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2010_2014_player_state_model as ps  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402
import verify_2010_2014_player_state_model as verify  # noqa: E402

_spec = importlib.util.spec_from_file_location("study_v3", HERE / "build_2014_strength_calibration_v3.py")
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)

ROOT = HERE.parents[1]
OUT = ROOT / "library/data/2014_strength_calibration_v4.json"
REPORT = ROOT / "library/2014_strength_calibration.md"
BEGIN, END = "<!-- strength-v4:begin -->", "<!-- strength-v4:end -->"
PRODUCTION = ROOT / "library/data/2010_2012_production_evidence.json"
RULES = pre_build_specification.frozen_rules()["strength_v4"]
TARGETS = tuple((t["outcomes"], tuple(t["evidence"])) for t in RULES["targets"])
KICKOFF = {2012: "2012-09-05", 2013: "2013-09-05"}
PRIOR_RATE = RULES["prior_sd"]
PRIOR_YPC = 0.25
SEED = 20140401
SCHEMA = "2014-strength-calibration-v4"
UNITS = v3.UNITS
OUTCOMES = sorted(v3.OUTCOMES)
RAW_SIGN = v3.RAW_SIGN
SLOT_FAMILY = {
    "QB": "QB", "RB": "RB", "HB": "RB", "H-B": "RB", "FB": "FB", "F": "FB", "WR": "WR", "TE": "TE",
    "LT": "OL", "LG": "OL", "C": "OL", "OC": "OL", "RG": "OL", "RT": "OL", "LOT": "OL", "ROT": "OL",
    "LE": "DL", "RE": "DL", "DE": "DL", "LDE": "DL", "RDE": "DL", "DT": "DL", "NT": "DL", "LDT": "DL", "RDT": "DL",
    "UT": "DL", "END": "DL", "LEO": "DL",
    "OLB": "LB", "ILB": "LB", "MLB": "LB", "WLB": "LB", "SLB": "LB", "LOLB": "LB", "ROLB": "LB", "LILB": "LB",
    "RILB": "LB", "MILB": "LB", "MOLB": "LB", "WILL": "LB", "SAM": "LB", "MIKE": "LB", "JLB": "LB", "BLB": "LB",
    "LB": "LB", "LLB": "LB", "RLB": "LB",
    "LCB": "DB", "RCB": "DB", "CB": "DB", "SS": "DB", "FS": "DB", "S": "DB",
}
ROSTER_FAMILY = dict(lb.GROUP, FB="FB")


def team(code):
    """One club code across the sources (nflverse's later codes and nflscrapR's JAC)."""
    code = v3.v1.team(code)
    return {"JAC": "JAX"}.get(code, code)


def clean(label):
    return (label or "").strip().strip('"').strip().upper()


# ====================================================================== lineups
def week1_starters(season, dest, roster_pos):
    """{club: {"offense": [row], "defense": [row]}}, rows {player_id, slot, family, label_source, position}."""
    name = "depth_charts_%s.csv" % lb.TAG[season]
    out = defaultdict(lambda: {"offense": [], "defense": []})
    for r in sources.rows(name, dest):
        if r["week"] != "1" or r["game_type"] != "REG" or r["depth_team"].strip() != "1":
            continue
        side = {"Offense": "offense", "Defense": "defense"}.get(r["formation"])
        if not side or not r.get("gsis_id"):
            continue
        slot = clean(r["depth_position"])
        fam = SLOT_FAMILY.get(slot)
        source = "chart slot"
        if fam is None:
            fam = ROSTER_FAMILY.get(roster_pos.get(r["gsis_id"], ""))
            source = "weekly roster position"
        out[team(r["club_code"])][side].append(
            {"player_id": r["gsis_id"], "slot": slot, "family": fam, "label_source": source,
             "backfilled_position": clean(r["position"])})
    return out


def week1_roster_positions(season, dest):
    """gsis -> that season's Week 1 weekly-roster position (most common across the file as a fallback)."""
    first, mode = {}, defaultdict(lambda: defaultdict(int))
    for r in sources.rows("roster_weekly_%s.csv" % lb.TAG[season], dest):
        g = r.get("gsis_id")
        if not g or not r.get("position"):
            continue
        if r.get("week") == "1" and r.get("game_type") == "REG":
            first[g] = clean(r["position"])
        mode[g][clean(r["position"])] += 1
    return {g: first.get(g) or sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for g, c in mode.items()}


def offense_units(rows):
    pick = lambda fam, n: [r for r in rows if r["family"] == fam][:n]  # noqa: E731
    ol, qb, rb, fb, wr, te = pick("OL", 5), pick("QB", 1), pick("RB", 1), pick("FB", 1), pick("WR", 3), pick("TE", 1)
    return {"protection": [(r, 1) for r in ol + rb], "passing": [(r, 3) for r in qb] + [(r, 1) for r in wr + te],
            "run": [(r, 1) for r in ol + te + fb + rb]}


def box_safety(dbs, key="slot"):
    for labels in (("SS",), ("S", "FS", "SAF")):
        for r in dbs:
            if r[key] in labels:
                return r
    return dbs[3] if len(dbs) >= 4 else None


def defense_units(rows):
    dl = [r for r in rows if r["family"] == "DL"][:4]
    lbs = [r for r in rows if r["family"] == "LB"][:3]
    db = [r for r in rows if r["family"] == "DB"][:4]
    box = box_safety(db)
    return {"rush": [(r, 1) for r in dl + lbs[:1]], "coverage": [(r, 1) for r in db + lbs[1:3]],
            "run_defense": [(r, 1) for r in dl + lbs + ([box] if box else [])]}


# ====================================================================== E-values
class Evidence:
    """E-values for one pass: lines, family parameters, priors and honour cells."""

    def __init__(self, lines, info, params, priors, cells):
        self.lines, self.info, self.params, self.priors, self.cells = lines, info, params, priors, cells
        self.cache = {}

    def value(self, pid, slot_family, target, window):
        key = (pid, slot_family, target)
        if key in self.cache:
            return self.cache[key]
        fam = ps.record_family(pid, self.lines, window)
        if fam is None:
            fam = slot_family if slot_family in ps.POSITION_FAMILIES else ("RB" if slot_family == "FB" else None)
        out = (0.0, "no family")
        if fam in self.params:
            p = self.params[fam]
            total = p["sb2"] + p["su2"]
            if total > 0:
                honours = ps.honour_entries(KICKOFF[target], window)
                state, basis, _, _ = ps.player_state(pid, fam, self.lines, self.info, self.priors[fam], p, honours,
                                                     self.cells.get(fam), window, target)
                out = ((state[0] + state[1]) / math.sqrt(total), basis)
            else:
                out = (0.0, "no spread")
        elif fam is not None:
            out = (0.0, "held" if fam in ("DL", "LB") else "no state")
        self.cache[key] = out
        return out


def ol_honour_values(window, cutoff):
    data = json.loads(ps.HONOURS.read_text(encoding="utf-8"))
    tiers = {"AP1": 2.0, "AP2": 1.0, "PB": 1.0}
    out = {}
    for e in data["entries"]:
        if e["honour_kind"] not in tiers or e["season"] not in window or not e.get("public_date"):
            continue
        if e["public_date"] >= cutoff or lb.GROUP.get((e.get("position") or "").upper()) != "OL":
            continue
        v = tiers[e["honour_kind"]] * ps.EVIDENCE_WEIGHT.get(e["verification"], 0.0)
        out[e["player_id"]] = max(out.get(e["player_id"], 0.0), v)
    return out


def composites(starters, evidence, target, window, proven, ol_hon):
    """comps[side][unit][club], plus per-member contributions (kept in memory only)."""
    comps = {side: {u: {} for u in units} for side, units in UNITS.items()}
    members = {}
    bases = defaultdict(int)
    for club, chart in starters.items():
        for side, units in (("offense", offense_units(chart["offense"])), ("defense", defense_units(chart["defense"]))):
            for unit, rows in units.items():
                total, contrib = 0.0, []
                seen = set()
                for r, w in rows:
                    if r["player_id"] in seen:
                        continue
                    seen.add(r["player_id"])
                    if r["family"] == "OL":
                        hv = ol_hon.get(r["player_id"], 0.0)
                        v = hv if hv > 0 else (0.0 if proven.get(r["player_id"]) else -1.0)
                        basis = "OL rule B plus honours"
                    else:
                        v, basis = evidence.value(r["player_id"], r["family"], target, window)
                    bases[basis] += 1
                    total += w * v
                    contrib.append((r["player_id"], w * v))
                comps[side][unit][club] = total
                members[(club, side, unit)] = contrib
    return comps, members, dict(sorted(bases.items()))


# ====================================================================== outcomes
def outcomes_pass1(season, dest):
    """Per-drive rows from the nflverse play-by-play (the committed v3 classifier: fixed_drive_result)."""
    grouped = {}
    for r in sources.rows(lb.pbp_name(season, "nflverse"), dest):
        if r.get("season_type") != "REG" or not r.get("posteam") or not r.get("fixed_drive"):
            continue
        key = (r["game_id"], r["fixed_drive"])
        d = grouped.get(key)
        if d is None:
            d = grouped[key] = {"game": r["game_id"], "off": team(r["posteam"]), "def": team(r["defteam"]),
                                "home": int(r["posteam"] == r["home_team"]), "result": r["fixed_drive_result"],
                                "sacks": 0, "dropbacks": 0, "carries": 0, "rush_yards": 0.0, "interception": 0}
        if d["off"] != team(r["posteam"]):
            continue
        if r["interception"] == "1":
            d["interception"] = 1
        if r["play_type"] == "pass" and r["two_point_attempt"] != "1":
            d["dropbacks"] += 1
            d["sacks"] += r["sack"] == "1"
        elif r["play_type"] == "run" and r["two_point_attempt"] != "1":
            d["carries"] += 1
            d["rush_yards"] += float(r["yards_gained"] or 0)
    return [{**d, "season": season, "td": 1.0 if d["result"] == "Touchdown" else 0.0, "int": float(d["interception"])}
            for d in grouped.values()]


def outcomes_pass2(season, dest):
    """Per-drive rows from nflscrapR with an independent classifier: a drive is the (game, drive)
    group of one offense; a touchdown is any scoring play of that offense (td_team = posteam)."""
    grouped = {}
    for r in sources.rows(lb.pbp_name(season, "nflscrapr"), dest):
        off = r.get("posteam")
        if not off or off == "NA" or r.get("drive") in ("", "NA"):
            continue
        key = (r["game_id"], r["drive"])
        d = grouped.get(key)
        if d is None:
            d = grouped[key] = {"game": r["game_id"], "off": team(off), "def": team(r["defteam"]),
                                "home": int(off == r["home_team"]), "td": 0.0, "int": 0.0, "sacks": 0,
                                "dropbacks": 0, "carries": 0, "rush_yards": 0.0, "season": season}
        if d["off"] != team(off):
            continue
        two = r.get("two_point_attempt") == "1"
        if r.get("touchdown") == "1" and r.get("td_team") == off and not two:
            d["td"] = 1.0
        if r.get("interception") == "1":
            d["int"] = 1.0
        if r.get("play_type") == "pass" and not two:
            d["dropbacks"] += 1
            d["sacks"] += r.get("sack") == "1"
        elif r.get("play_type") == "run" and not two:
            d["carries"] += 1
            d["rush_yards"] += float(r["yards_gained"]) if r.get("yards_gained") not in ("", "NA") else 0.0
    return list(grouped.values())


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
        out[club] = {side: {"td_share": (a[side + "_td"] / a[side + "_drives"], a[side + "_drives"]),
                            "int_share": (a[side + "_int"] / a[side + "_drives"], a[side + "_drives"]),
                            "sack_rate": (a[side + "_sacks"] / a[side + "_dropbacks"], a[side + "_dropbacks"]),
                            "ypc": (a[side + "_rush_yards"] / a[side + "_carries"], a[side + "_carries"])}
                     for side in ("off", "def")}
    return out


# ====================================================================== the pooled fit
def _demean(vals, w, groups):
    out = list(vals)
    for g in set(groups):
        idx = [i for i, x in enumerate(groups) if x == g]
        m = sum(vals[i] * w[i] for i in idx) / sum(w[i] for i in idx)
        for i in idx:
            out[i] = vals[i] - m
    return out


def wls_season(x, y, w, seasons):
    """Slope with season intercepts (weights normalised to mean 1); (slope, se, r2, season means)."""
    k = len(w) / sum(w)
    w = [v * k for v in w]
    xd, yd = _demean(x, w, seasons), _demean(y, w, seasons)
    sxx = sum(wi * a * a for wi, a in zip(w, xd))
    if sxx == 0:
        return 0.0, float("inf"), 0.0
    b = sum(wi * a * c for wi, a, c in zip(w, xd, yd)) / sxx
    resid = [c - b * a for a, c in zip(xd, yd)]
    sse = sum(wi * e * e for wi, e in zip(w, resid))
    syy = sum(wi * c * c for wi, c in zip(w, yd))
    se = math.sqrt(sse / (len(x) - 1 - len(set(seasons))) / sxx)
    return b, se, (1 - sse / syy if syy else 0.0)


def predict(x, y, w, seasons, train, test):
    """Predictions for `test` from a season-intercept fit on `train`."""
    xs, ys, ws, ss = ([v[i] for i in train] for v in (x, y, w, seasons))
    b, _, _ = wls_season(xs, ys, ws, ss)
    preds, nulls = {}, {}
    for s in set(seasons[i] for i in test):
        idx = [j for j, sj in zip(train, ss) if sj == s]
        wsum = sum(w[j] for j in idx)
        mx = sum(x[j] * w[j] for j in idx) / wsum
        my = sum(y[j] * w[j] for j in idx) / wsum
        for i in test:
            if seasons[i] == s:
                preds[i] = my + b * (x[i] - mx)
                nulls[i] = my
    return preds, nulls


def loo_club(x, y, w, seasons, clubs):
    groups = defaultdict(list)
    for i, c in enumerate(clubs):
        groups[c].append(i)
    err, null = [], []
    for c, idx in sorted(groups.items()):
        train = [i for i in range(len(x)) if clubs[i] != c]
        p, n0 = predict(x, y, w, seasons, train, idx)
        for i in idx:
            err.append(y[i] - p[i])
            null.append(y[i] - n0[i])
    rmse = math.sqrt(statistics.fmean(e * e for e in err))
    rmse0 = math.sqrt(statistics.fmean(e * e for e in null))
    return {"rmse": rmse, "null_rmse": rmse0, "skill": 1 - (rmse / rmse0) ** 2}


def shrink(b, se, prior):
    if not math.isfinite(se):
        return 0.0, prior
    tau2 = prior ** 2
    return b * tau2 / (tau2 + se * se), math.sqrt(tau2 * se * se / (tau2 + se * se))


def design(comps, outs, side, unit, outcome):
    key = "off" if side == "offense" else "def"
    x, y, w, seasons, clubs = [], [], [], [], []
    for season in sorted(comps):
        for club in sorted(comps[season][side][unit]):
            val, n = outs[season][club][key][outcome]
            x.append(comps[season][side][unit][club])
            y.append(val)
            w.append(n)
            seasons.append(season)
            clubs.append(club)
    return x, y, w, seasons, clubs


def fit_term(comps, outs, side, unit, outcome):
    x, y, w, seasons, clubs = design(comps, outs, side, unit, outcome)
    b, se, r2 = wls_season(x, y, w, seasons)
    sign = RAW_SIGN[(side, outcome)]
    prior = PRIOR_YPC if outcome == "ypc" else PRIOR_RATE
    shrunk, shrunk_sd = shrink(sign * b, se, prior)
    sd = statistics.pstdev(x)
    loo = loo_club(x, y, w, seasons, clubs)
    return {"raw_slope": b, "slope": sign * b, "se": se, "r2": r2, "loo": loo, "shrunk_slope": shrunk,
            "shrunk_sd": shrunk_sd, "prior_sd": prior, "composite_mean": statistics.fmean(x), "composite_sd": sd,
            "composite_range": [min(x), max(x)], "implied_club_sd": abs(shrunk) * sd, "club_seasons": len(x),
            "right_sign_and_skill": loo["skill"] > 0 and sign * b > 0}


def joint_td(comps, outs, side, u1, u2):
    """Two-term fit with season intercepts (both kept); shrunk slopes."""
    x1, y, w, seasons, _ = design(comps, outs, side, u1, "td_share")
    x2, _, _, _, _ = design(comps, outs, side, u2, "td_share")
    k = len(w) / sum(w)
    wn = [v * k for v in w]
    a, b, c = _demean(x1, wn, seasons), _demean(x2, wn, seasons), _demean(y, wn, seasons)
    s11 = sum(wi * p * p for wi, p in zip(wn, a))
    s22 = sum(wi * p * p for wi, p in zip(wn, b))
    s12 = sum(wi * p * q for wi, p, q in zip(wn, a, b))
    s1y = sum(wi * p * q for wi, p, q in zip(wn, a, c))
    s2y = sum(wi * p * q for wi, p, q in zip(wn, b, c))
    det = s11 * s22 - s12 * s12
    b1, b2 = (s1y * s22 - s2y * s12) / det, (s2y * s11 - s1y * s12) / det
    resid = [q - b1 * p - b2 * r for p, r, q in zip(a, b, c)]
    s2 = sum(wi * e * e for wi, e in zip(wn, resid)) / (len(y) - 2 - len(set(seasons)))
    se1, se2 = math.sqrt(s2 * s22 / det), math.sqrt(s2 * s11 / det)
    sign = RAW_SIGN[(side, "td_share")]
    return {"units": [u1, u2], "slopes": [sign * b1, sign * b2], "se": [se1, se2],
            "shrunk_slopes": [shrink(sign * b1, se1, PRIOR_RATE)[0], shrink(sign * b2, se2, PRIOR_RATE)[0]]}


def all_fits(comps, outs):
    return {"%s_%s_%s" % (o, s, u): fit_term(comps, outs, s, u, o) for o, s, u in OUTCOMES}


def adopt(fits1, fits2, comps, outs):
    """Adopted terms under the keep rule reproduced by pass 2 (U3: symmetric)."""
    kept = {k: fits1[k]["right_sign_and_skill"] and fits2[k]["right_sign_and_skill"] for k in fits1}
    adopted = {}
    for side, (u1, u2) in (("offense", ("passing", "run")), ("defense", ("coverage", "run_defense"))):
        names = [u for u in (u1, u2) if kept["td_share_%s_%s" % (side, u)]]
        joint = joint_td(comps, outs, side, u1, u2) if len(names) == 2 else None
        for u in names:
            f = fits1["td_share_%s_%s" % (side, u)]
            slope = joint["shrunk_slopes"][(u1, u2).index(u)] if joint else f["shrunk_slope"]
            adopted["td_share_%s_%s" % (side, u)] = {
                "outcome": "td_share", "side": side, "unit": u, "slope": slope, "centre": f["composite_mean"],
                "composite_sd": f["composite_sd"], "loo_skill": f["loo"]["skill"],
                "pass2_loo_skill": fits2["td_share_%s_%s" % (side, u)]["loo"]["skill"],
                "from": "joint two-term fit (both kept)" if joint else "single-term fit"}
    for outcome in ("sack_rate", "int_share"):
        for side, unit in (("offense", "protection" if outcome == "sack_rate" else "passing"),
                           ("defense", "rush" if outcome == "sack_rate" else "coverage")):
            k = "%s_%s_%s" % (outcome, side, unit)
            if kept[k]:
                f = fits1[k]
                adopted[k] = {"outcome": outcome, "side": side, "unit": unit, "slope": f["shrunk_slope"],
                              "centre": f["composite_mean"], "composite_sd": f["composite_sd"],
                              "loo_skill": f["loo"]["skill"], "pass2_loo_skill": fits2[k]["loo"]["skill"],
                              "from": "single-term fit"}
    return adopted, kept


def drive_joint(rows, comps, adopted, outcome="td_share"):
    """Drive-level OLS of the outcome on season intercepts, the adopted composites and home,
    with a 500-draw game-cluster bootstrap (seed 20140401)."""
    terms = [(t["unit"], t["side"]) for t in adopted.values() if t["outcome"] == outcome]
    seasons = sorted({d["season"] for d in rows})
    sample = rows

    def x_of(d):
        row = [1.0 if d["season"] == s else 0.0 for s in seasons]
        for unit, side in terms:
            club = d["off"] if side == "offense" else d["def"]
            row.append(comps[d["season"]][side][unit][club])
        row.append(float(d["home"]))
        return row

    def fit(ds):
        return v3.v1.ols([x_of(d) for d in ds], [d["td"] for d in ds])

    point = fit(sample)
    by_game = defaultdict(list)
    for d in sample:
        by_game[d["game"]].append(d)
    games = sorted(by_game)
    rng = random.Random(SEED)
    draws = []
    for _ in range(500):
        ds = []
        for g in (games[rng.randrange(len(games))] for _ in games):
            ds.extend(by_game[g])
        draws.append(fit(ds))
    ses = [statistics.stdev(dr[i] for dr in draws) for i in range(len(point))]
    out = {"home": point[-1], "se_home": ses[-1], "drives": len(sample),
           "terms": {"%s_%s" % (side, unit): {"coefficient": point[len(seasons) + i], "se": ses[len(seasons) + i],
                                               "as_strength": RAW_SIGN[(side, outcome)] * point[len(seasons) + i]}
                     for i, (unit, side) in enumerate(terms)}}
    return out


# ====================================================================== punter
def punter_pairs_pass1(dest):
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    pairs = v3.st_pairs(production, "P")
    nxt = defaultdict(lambda: [0.0, 0.0])
    for r in sources.rows("stats_player_week_2013.csv", dest):
        if r.get("season_type") == "REG" and ps.num(r["pt_att"]) > 0:
            nxt[r["player_id"]][0] += ps.num(r["pt_net_yards"])
            nxt[r["player_id"]][1] += ps.num(r["pt_att"])
    means = {s: production["seasons"][s]["league_means"]["P"]["mean"] for s in production["seasons"]}
    for pid, p in production["players"].items():
        row = p["seasons"].get("2012")
        if row and row.get("group") == "P" and row.get("tier") is not None and pid in nxt:
            pairs.append({"player_id": pid, "seasons": [2012, 2013], "deviation": row["shrunk"] - means["2012"],
                          "next_raw": nxt[pid][0] / nxt[pid][1], "next_n": nxt[pid][1]})
    return pairs


def punter_pairs_pass2(dest):
    """Same definition (net per punt; shrunk with k 10 toward the qualifier mean, minimum 30 punts) from nflscrapR."""
    seasons = {}
    for season in (2010, 2011, 2012, 2013):
        tot = defaultdict(lambda: [0.0, 0])
        for r in sources.rows(lb.pbp_name(season, "nflscrapr"), dest):
            pid = r.get("punter_player_id") or ""
            if r.get("punt_attempt") != "1" or pid in ("", "NA") or r.get("punt_blocked") == "1" \
                    or r.get("two_point_attempt") == "1" or r.get("play_type") == "no_play":
                continue
            tb = r.get("touchback") == "1"
            gross = (float(r["kick_distance"]) if r.get("kick_distance") not in ("", "NA")
                     else (float(r["yardline_100"]) if tb else None))
            if gross is None:
                continue
            ret = float(r["return_yards"]) if r.get("return_yards") not in ("", "NA") else 0.0
            tot[pid][0] += gross - ret - 20 * tb
            tot[pid][1] += 1
        q = {p: v for p, v in tot.items() if v[1] >= 30}
        mean = sum(v[0] for v in q.values()) / sum(v[1] for v in q.values())
        seasons[season] = {"tot": tot, "mean": mean, "qualifiers": q}
    pairs = []
    for t in (2010, 2011, 2012):
        a, b = seasons[t], seasons[t + 1]
        for pid, (s, n) in a["qualifiers"].items():
            if pid in b["tot"] and b["tot"][pid][1] > 0:
                shrunk = (s + 10 * a["mean"]) / (n + 10)
                pairs.append({"player_id": pid, "seasons": [t, t + 1], "deviation": shrunk - a["mean"],
                              "next_raw": b["tot"][pid][0] / b["tot"][pid][1], "next_n": b["tot"][pid][1]})
    return pairs


def punter_fit(pairs):
    x = [p["deviation"] for p in pairs]
    y = [p["next_raw"] for p in pairs]
    w = [p["next_n"] for p in pairs]
    a, b, se, r2 = v3.v1.wls(x, y, w)
    shrunk, _ = v3.shrink(b, se, 1.0)
    return {"pairs": len(pairs), "pairs_by_season": {"%d-%d" % tuple(k): n for k, n in sorted(
        defaultdict(int, {tuple(p["seasons"]): sum(1 for q in pairs if q["seasons"] == p["seasons"])
                          for p in pairs}).items())},
            "slope": b, "se": se, "shrunk_slope": shrunk, "r2": r2, "loo": v3.loo_pairs(x, y, w)}


# ====================================================================== influence
def influence(comps, outs, members, adopted):
    """Summaries of each adopted term's slope change when one club (both seasons) or one player's
    contribution is removed; nothing per club or player is stored."""
    out = {}
    for name, t in adopted.items():
        side, unit, outcome = t["side"], t["unit"], t["outcome"]
        x, y, w, seasons, clubs = design(comps, outs, side, unit, outcome)
        base, _, _ = wls_season(x, y, w, seasons)
        club_d = []
        for c in sorted(set(clubs)):
            keep = [i for i in range(len(x)) if clubs[i] != c]
            b, _, _ = wls_season(*([v[i] for i in keep] for v in (x, y, w, seasons)))
            club_d.append(abs(b - base))
        player_d = []
        contrib = defaultdict(list)
        for season in sorted(comps):
            for (club, s_side, s_unit), rows in members[season].items():
                if s_side == side and s_unit == unit:
                    for pid, v in rows:
                        if v:
                            contrib[pid].append((season, club, v))
        index = {(s, c): i for i, (s, c) in enumerate(zip(seasons, clubs))}
        for pid, items in contrib.items():
            xx = list(x)
            for season, club, v in items:
                xx[index[(season, club)]] -= v
            b, _, _ = wls_season(xx, y, w, seasons)
            player_d.append(abs(b - base))

        def summary(vals):
            vals = sorted(vals)
            if not vals:
                return {"count": 0}
            return {"count": len(vals), "median": vals[len(vals) // 2], "p90": vals[int(0.9 * (len(vals) - 1))],
                    "max": vals[-1], "relative_max": vals[-1] / abs(base) if base else None}
        out[name] = {"clubs": summary(club_d), "players": summary(player_d), "unit": "absolute change in the raw slope"}
    return out


# ====================================================================== the build
def evidence_pass(lines, info, model_families, params_source):
    params, priors = {}, {}
    for fam in ps.FAMILIES:
        block = model_families[fam]
        priors[fam] = block["draft_priors"]
        if params_source == "adopted":
            a = block["adopted"]
            if not a.get("held"):
                params[fam] = {"sb2": a["sb2"], "su2": a["su2"], "rho": a["rho"]}
    return params, priors


def build(dest, log=print):
    model = json.loads(ps.MODEL_OUT.read_text(encoding="utf-8"))
    if model.get("specification_sha256") != pre_build_specification.digest():
        raise SystemExit("the player-state model was built under another specification")
    info = ps.career_info(dest)
    log("strength v4: pass 1 lines")
    lines1, _, _ = ps.season_lines(ps.extract_pass1(dest, lambda m: None))
    log("strength v4: pass 2 lines")
    lines2, _, _ = ps.season_lines(verify.extract_pass2(dest, lambda m: None), split="chrono")
    params1, priors1 = evidence_pass(lines1, info, model["families"], "adopted")
    # Pass 2 E-values use pass 2's own fits and keep rule (its own interval), its own priors and honour cells.
    params2, priors2 = {}, {}
    for fam, rec in model["second_pass"]["families"].items():
        f = rec["fit"]
        priors2[fam] = rec["draft_priors"]
        if model["families"][fam]["adopted"].get("held"):
            continue
        if f["bootstrap"]["su2_interval"][0] > 0:
            params2[fam] = {"sb2": f["sb2"], "su2": f["su2"], "rho": f["rho"]}
        else:
            tot = ps.total_moments(verify.player_mean_moments(lines2[fam]))
            wsum = sum(c for _, c in tot)
            params2[fam] = {"sb2": max(0.0, sum(s for s, _ in tot) / wsum) if wsum else 0.0, "su2": 0.0, "rho": 0.0}
    hon = ps.honour_entries("2013-01-15", ps.RECORD_SEASONS)
    ev1 = Evidence(lines1, info, params1, priors1, ps.honour_cells(lines1, hon))
    ev2 = Evidence(lines2, info, params2, priors2, ps.honour_cells(lines2, hon))
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    comps1, comps2, members, outs1, outs2, rows1, bases, labels = {}, {}, {}, {}, {}, [], {}, {}
    contamination = None
    for target, window in TARGETS:
        log("strength v4: target %d" % target)
        roster_pos = week1_roster_positions(target, dest)
        starters = week1_starters(target, dest, roster_pos)
        labels[str(target)] = dict(sorted(defaultdict(int, {
            src: sum(1 for c in starters.values() for side in c.values() for r in side if r["label_source"] == src)
            for src in ("chart slot", "weekly roster position")}).items()))
        if target == 2012:
            contamination = box_contamination(starters)
        proven = v3.ol_proven(production, list(window))
        ol_hon = ol_honour_values(window, KICKOFF[target])
        comps1[target], members[target], bases[str(target)] = composites(starters, ev1, target, window, proven, ol_hon)
        comps2[target], _, _ = composites(starters, ev2, target, window, proven, ol_hon)
        r1 = outcomes_pass1(target, dest)
        rows1 += r1
        outs1[target] = club_outcomes(r1)
        outs2[target] = club_outcomes(outcomes_pass2(target, dest))
    fits1 = all_fits(comps1, outs1)
    fits2 = all_fits(comps2, outs2)
    adopted, kept = adopt(fits1, fits2, comps1, outs1)
    joint = drive_joint(rows1, comps1, adopted)
    log("strength v4: punter")
    pp1, pp2 = punter_fit(punter_pairs_pass1(dest)), punter_fit(punter_pairs_pass2(dest))
    if abs(pp2["shrunk_slope"] - pp1["shrunk_slope"]) <= 2 * pp1["se"]:
        punter = {"slope": pp1["shrunk_slope"], "status": "Confirmed two-pass"}
    else:
        small = min((pp1["shrunk_slope"], "pass 1"), (pp2["shrunk_slope"], "pass 2"), key=lambda v: abs(v[0]))
        punter = {"slope": small[0], "status": "single-pass (the passes disagree; the smaller, %s)" % small[1]}
    punter["kept"] = pp1["loo"]["skill"] > 0 and pp1["slope"] > 0
    if not punter["kept"]:
        punter.update(slope=0.0, status="not kept (leave-one-pair-out skill or sign)")
    implied = {k: abs(t["slope"]) * t["composite_sd"] for k, t in adopted.items()}
    td = [v for k, v in implied.items() if k.startswith("td_share")]
    net = math.sqrt(sum(v * v for v in td))
    v3_terms = json.loads((ROOT / "library/data/2014_strength_calibration_v3.json").read_text())
    previous = sorted(v3_terms["study_2012"]["adopted_terms"])
    artifact = {
        "schema": SCHEMA,
        "builder": "scripts/research/build_2014_strength_calibration_v4.py",
        "specification_sha256": pre_build_specification.digest(),
        "player_state_model_sha256": hashlib.sha256(ps.MODEL_OUT.read_bytes()).hexdigest(),
        "information_boundary": ("targets: the 2012 and 2013 regular seasons, club outcomes from the play-by-play, "
                                 "anonymous in the committed record (aggregate fits only); inputs: player-state "
                                 "E-values from each target's two evidence seasons; 2013 is a post-divergence "
                                 "league population and enters pooled fits only"),
        "targets": [{"outcomes": t, "evidence": list(w), "kickoff": KICKOFF[t]} for t, w in TARGETS],
        "player_value": ("E-value over the family's true-state SD (player-state model); 0 for no state, no spread "
                         "or a held family (U5: LB); offensive linemen rule B plus honours"),
        "label_sources": labels,
        "value_bases": bases,
        "fits": fits1,
        "pass2": {"source": "nflscrapR reg_pbp drives (td_team = posteam), pass-2 E-values",
                  "fits": {k: {"slope": f["slope"], "se": f["se"], "loo_skill": f["loo"]["skill"],
                               "right_sign_and_skill": f["right_sign_and_skill"]} for k, f in fits2.items()}},
        "kept": kept,
        "adopted_terms": adopted,
        "previously_live_v3": previous,
        "terms_changed_by_refit": {"turned_off": [k for k in previous if k not in adopted],
                                   "turned_on": [k for k in adopted if k not in previous]},
        "individual_passer_interception_term": "not adopted (October 2, 2026 decision)",
        "ypc_terms": "reported only (no kernel channel)",
        "home_edge": {"value": joint["home"], "se": joint["se_home"], "drives": joint["drives"],
                      "from": "drive-level joint regression, season intercepts and the adopted touchdown-share "
                              "composites, 500-draw game-cluster bootstrap"},
        "drive_joint": joint,
        "punter": {"pass1": pp1, "pass2": pp2, "adopted": punter,
                   "definition": "net yards per punt (pt_net_yards over pt_att; pass 2 gross minus return minus 20 "
                                 "per touchback from nflscrapR); predictor: the season-t shrunk net (k 10, minimum "
                                 "30 punts) minus the league mean; the punter's input stays his public "
                                 "pre-divergence net"},
        "kicker_slope": RULES["kicker_slope"], "returner_slope": RULES["returner_slope"],
        "implied_club_sd": implied, "net_td_share_edge_sd": net,
        "fraction_of_target": net / v3.TARGET["net"],
        "self_influence": influence(comps1, outs1, members, adopted),
        "contamination_2012_box_safety": contamination,
    }
    return artifact


def box_contamination(starters):
    """2012 clubs whose box safety differs between the chart's back-filled position labels (the
    2012 study's rule) and the contemporaneous slot labels (this study's)."""
    differ = 0
    for club, chart in starters.items():
        dbs_slot = [r for r in chart["defense"] if r["family"] == "DB"][:4]
        dbs_back = [r for r in chart["defense"] if r["backfilled_position"] in v3.DB_LABELS][:4]
        a = box_safety(dbs_slot)
        b = box_safety(dbs_back, key="backfilled_position")
        if (a or {}).get("player_id") != (b or {}).get("player_id"):
            differ += 1
    return {"clubs": len(starters), "box_safety_differs": differ}


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def report_section(a):
    """Section 11 of library/2014_strength_calibration.md, generated from the artifact."""
    f = lambda x, d=4: ("%%.%df" % d) % x  # noqa: E731
    lines = [BEGIN, "", "## 11. Strength v4 (kernel 2014.6, batch B4c): the terms refit on player-state E-values", "",
             "Generated by `scripts/research/build_2014_strength_calibration_v4.py` from "
             "[`data/2014_strength_calibration_v4.json`](data/2014_strength_calibration_v4.json); `--check` "
             "reproduces both. Data only: the runtime reads it from batch B7. Rules: the "
             "[pre-build specification](2014_6_pre_build_specification.md) (section 4, Strength v4), Stone's U1(b) "
             "and the symmetric keep rule (U3), recorded in the "
             "[engine decisions](../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated).", "",
             "**What changed from section 10.** Targets are the 2012 season (2010-2011 evidence) and the 2013 season "
             "(2011-2012 evidence), pooled with season intercepts over %d club-seasons. A starter's value is his "
             "one-step-forecast E-value from the [player-state model](2010_2014_player_state_study.md) over his "
             "family's true-state SD; offensive linemen keep rule B plus honours. Labels are contemporaneous: the "
             "Week 1 chart slot's family, then that season's weekly roster position. Under U5's fallback the "
             "linebacker family's state is held, so linebackers contribute 0 (the runtime's Average) in every "
             "composite. A term is kept when its leave-one-club-out skill is positive with the right sign and pass 2 "
             "(nflscrapR drives with an independent classifier, pass-2 E-values) reproduces both." %
             a["fits"]["td_share_offense_passing"]["club_seasons"], "",
             "| Term | Slope (strength) | SE | Shrunk | Centre | Composite SD | LOO skill | Pass 2 skill | Kept |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for k in sorted(a["fits"]):
        t, p2 = a["fits"][k], a["pass2"]["fits"][k]
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, f(t["slope"], 5), f(t["se"], 5), f(t["shrunk_slope"], 5), f(t["composite_mean"], 3),
            f(t["composite_sd"], 3), f(t["loo"]["skill"], 3), f(p2["loo_skill"], 3),
            "yes" if a["kept"][k] and not k.startswith("ypc") else ("reported only" if k.startswith("ypc") else "no")))
    ch = a["terms_changed_by_refit"]
    lines += ["", "**Adopted terms:** %s. Turned off by the refit: %s. Turned on: %s." % (
        ", ".join("%s (slope %s, centre %s, %s)" % (k, f(t["slope"], 5), f(t["centre"], 3), t["from"])
                  for k, t in sorted(a["adopted_terms"].items())) or "none",
        ", ".join(ch["turned_off"]) or "none", ", ".join(ch["turned_on"]) or "none"), "",
        "**Home edge** (drive level, %d drives): %s per drive (SE %s)." % (
            a["home_edge"]["drives"], f(a["home_edge"]["value"]), f(a["home_edge"]["se"])), "",
        "**Implied touchdown-share edge SD** from the adopted terms: %s (%s of the 0.048 target)." % (
            f(a["net_td_share_edge_sd"]), "%.0f%%" % (100 * a["fraction_of_target"])), ""]
    pp = a["punter"]
    lines += ["**Punter.** Pass 1 (committed pt_net_yards, %d pairs): slope %s (SE %s, shrunk %s, leave-one-pair-out "
              "skill %s). Pass 2 (nflscrapR, same definition, %d pairs): shrunk %s. Adopted: %s, %s. Kicker and "
              "returner slopes stay 0." % (
                  pp["pass1"]["pairs"], f(pp["pass1"]["slope"]), f(pp["pass1"]["se"]), f(pp["pass1"]["shrunk_slope"]),
                  f(pp["pass1"]["loo"]["skill"], 3), pp["pass2"]["pairs"], f(pp["pass2"]["shrunk_slope"]),
                  f(pp["adopted"]["slope"]), pp["adopted"]["status"]), ""]
    si = a["self_influence"]
    lines += ["**Self-influence** (absolute change of each adopted raw slope when one club's two seasons, or one "
              "player's contributions, are removed; summaries only, nothing per club or player is stored):", "",
              "| Term | Clubs | Median | Max | Players | Median | Max |", "|---|---:|---:|---:|---:|---:|---:|"]
    for k, v in sorted(si.items()):
        lines.append("| %s | %d | %s | %s | %d | %s | %s |" % (
            k, v["clubs"]["count"], f(v["clubs"]["median"], 5), f(v["clubs"]["max"], 5), v["players"]["count"],
            f(v["players"]["median"], 5), f(v["players"]["max"], 5)))
    c = a["contamination_2012_box_safety"]
    lines += ["", "**Disclosure: the 2012 study's box safety.** Section 10's sub-units read the chart's back-filled "
              "position column; on the 2012 Week 1 charts the box safety chosen that way differs from the one the "
              "contemporaneous slot labels give for %d of %d clubs. This study uses the slot labels; section 10's "
              "fits are kept as recorded." % (c["box_safety_differs"], c["clubs"]), "",
              "**Value bases** (starter slots per target): %s." % "; ".join(
                  "%s: %s" % (t, ", ".join("%s %d" % kv for kv in sorted(b.items()))) for t, b in
                  sorted(a["value_bases"].items())), "",
              "**Limits.** Only aggregate fits are committed. 2013 enters as an anonymous post-divergence population; "
              "no club's 2013 outcome or composite is recorded. The player-state inputs carry the U5 fallback (no "
              "aging, flat rookie estimates, linebackers held). The sub-unit slot split remains a convention.", "",
              END]
    return "\n".join(lines) + "\n"


def splice(text, section):
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        tail = rest.split(END, 1)[1].lstrip("\n")
        return head + section + (("\n" + tail) if tail else "")
    return text.rstrip("\n") + "\n\n" + section


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    artifact = build(args.sources, log=lambda m: print(m, file=sys.stderr))
    texts = {OUT: render(artifact), REPORT: splice(REPORT.read_text(encoding="utf-8"), report_section(artifact))}
    if args.check:
        bad = [p for p, t in texts.items() if p.read_text() != t]
        for p in texts:
            print("%s %s" % ("DIFFERS" if p in bad else "reproduced", p.relative_to(ROOT)))
        return 1 if bad else 0
    for p, t in texts.items():
        p.write_text(t)
        print("wrote %s" % p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
