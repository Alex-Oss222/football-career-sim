#!/usr/bin/env python3
"""Calibrate the combined honours + production unit-strength composite (E1 second pass).

  python scripts/research/build_2014_strength_calibration_v2.py SOURCE_DIR PBP_2012

SOURCE_DIR holds the pinned nflverse files the first study used (weekly
depth charts, weekly rosters); PBP_2012 is the 2012 regular-season
play-by-play file (drive results and scores only). Honours come from
library/data/2010_2012_honours_evidence.json and production from
library/data/2010_2012_production_evidence.json.

Outputs library/data/2014_strength_calibration_v2.json. The prose report is
section 9 of library/2014_strength_calibration.md.

Everything in PREREGISTERED was fixed before the first fit ran. The study
method is the first study's, unchanged: 2012 Week 1 depth-chart starters for
role, drive-weighted least squares of each club's per-drive touchdown share
on its unit composite, shrinkage prior N(0, 0.025^2), leave-one-club-out
prediction, drive-level joint check with a game-cluster bootstrap. The
target is the real 2012 regular season (pre-divergence). No branch record,
no post-divergence real result and no club-specific treatment enters.
"""
from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("study_v1", HERE / "build_2014_strength_calibration.py")
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
sys.path.insert(0, str(ROOT))
from runtime import strength as rt_strength  # noqa: E402  (offense/defense starter slots, id joins)
from runtime.player_evidence import PlayerInput  # noqa: E402

HONOURS = ROOT / "library/data/2010_2012_honours_evidence.json"
PRODUCTION = ROOT / "library/data/2010_2012_production_evidence.json"
BIRTHS = ROOT / "library/data/player_birth_dates.json"
LEAGUE = ROOT / 'career/2014/League/personnel/league_players.json'
V1_JSON = ROOT / "library/data/2014_strength_calibration.json"
OUT = ROOT / "library/data/2014_strength_calibration_v2.json"

PREREGISTERED = {
    "written_before_first_fit": "2026-09-30",
    "player_value": {
        "rule": "value = max(honours_value, production_value)",
        "honours_value": "as the first study: max over admissible honours of (tier value - 2) x evidence weight; "
                         "0 when the player holds no admissible honour; never below 0",
        "production_value": "the player's window production tier mapped Elite 2, Plus 1, Average 0, Below-Average -1, "
                            "Replacement-Level -2, times its evidence weight (1.0 Confirmed two-pass or Corrected, 0.5 Unverified); "
                            "0 when the player has no qualifying window season",
        "window": "the two most recent completed pre-divergence seasons before the season being predicted "
                  "(2012 target: 2010-2011; 2014 branch: 2011-2012); 2014 only: 2010 is a fallback discounted one tier "
                  "when neither window season qualifies (library/data/2010_2012_production_evidence.json)",
        "side_rule": "a production tier counts only on its own side: a QB tier only in the passer slot (weight 3), "
                     "RB/WR/TE tiers in the other offensive slots, DL/LB/DB tiers in the defensive slots; offensive linemen "
                     "carry no production tier (job evidence only) and so contribute only their honours value; "
                     "a non-QB tier never counts in the passer slot",
        "correction_2026_09_30": "the first fit of this script read the rule as max(honours value, production value) with "
                                 "honours value 0 for an unhonoured player, which floored every unhonoured starter at 0 and "
                                 "let no Below-Average (-1) or Replacement-Level (-2) tier enter a composite, contradicting the "
                                 "declared tier values; a unit test on the runtime exposed it before any game or acceptance run. "
                                 "The rule as declared and now implemented: with an admissible honour, the larger of the honour "
                                 "and the production value; without one, the production value, negative tiers included. The "
                                 "first (floored) fit is kept in the JSON as variants_floored_first_fit for the record",
        "why_max": "a production tier is a measured, pre-divergence, two-pass verified season outcome that covers every "
                   "qualifier, so it can place a player above or below Average on its own; an honour is an expert judgement "
                   "that can only lift a player. Taking the maximum keeps the honour's lift for an honoured player whose "
                   "production is contaminated by his old offense or defense, and lets production speak for the unhonoured "
                   "majority. The alternative, a fitted two-term model, is run as a sensitivity and reported; the kernel adopts "
                   "the max rule whatever the two-term fit says, because that choice was made here, before the fit",
    },
    "position_weights": {"QB": 3, "other offensive starter": 1, "defensive starter": 1},
    "age_shrink": {
        "rule": "halve the honours value of a player whose only admissible honours come from the earlier season of the "
                "window (none in the later season) and whose age on September 1 of the target season is at or above the "
                "group threshold; applied to the honours value before the max, never to production",
        "thresholds": {"QB": 35, "RB": 29, "WR": 31, "TE": 31, "OL": 32, "DL": 31, "LB": 31, "DB": 31},
        "birth_dates": "2012 target: the nflverse 2012 weekly roster birth dates; 2014 branch: "
                       "library/data/player_birth_dates.json by gsis id",
        "adoption": "kept in the kernel only if the leave-one-club-out skill improves on both sides against the same "
                    "composite without it; otherwise reported and left out",
    },
    "fit": v1.PREREGISTERED["fit"],
    "targets": v1.PREREGISTERED["targets"],
    "edge_target": v1.PREREGISTERED["edge_target"],
    "points_conversion": "7.0 points per drive per unit of touchdown share and 11.8 drives per team-game "
                         "(the first study's conversion), so a per-drive edge SD s is s x 7.0 x 11.8 points per team-game",
    "variants": ["honours_only (the first study, recomputed)", "production_only", "combined_max (primary)",
                 "combined_max_age_shrink", "two_term_sensitivity (honours and production composites as two predictors)",
                 "continuous_production_sensitivity (added after the first fit was read, labelled as such: the production "
                 "value is the within-group, within-season z-score of the shrunk metric clipped to +/-2 instead of the tier "
                 "value; reported only, never adopted by this study)"],
    "attribution_tilt": {
        "source": "2012 regular season (nflverse stats_player_reg_2012): each club's top-target player's share of club "
                  "targets, top-carry player's share of club carries, and top sack-getter's share of club sacks, grouped by "
                  "that player's combined tier from the 2010-2011 window",
        "factor": "tier mean share / all-club mean share, clipped to [0.6, 1.6], the Average tier included (so the "
                  "2012 mix of tiers reproduces the all-club mean the rank shapes were built on); a tier with fewer than "
                  "3 clubs takes the nearest populated tier's factor toward Average",
        "use": "runtime/usage.py multiplies the sourced rank weight of a player by his tier factor when a carry, target or "
               "sack credit is attributed; it never touches a possession draw or a score",
    },
}
TIER_VALUE = {"Elite": 2, "Plus": 1, "Average": 0, "Below-Average": -1, "Replacement-Level": -2}
TIER_STEP = ["Elite", "Plus", "Average", "Below-Average", "Replacement-Level"]
PRODUCTION_WEIGHT = {"Confirmed two-pass": 1.0, "Corrected": 1.0, "Unverified": 0.5}
GROUP_SIDE = {"QB": "offense", "RB": "offense", "WR": "offense", "TE": "offense", "OL": "offense",
              "DL": "defense", "LB": "defense", "DB": "defense"}
TIER_ORDER = {"Elite": 0, "Plus": 1, "Average": 2, "Below-Average": 3, "Replacement-Level": 4}
DRIVES_PER_TEAM_GAME = 11.8
POINTS_PER_TD_SHARE = 7.0
TARGET = {"offense": 0.0455, "defense": 0.0223, "net": 0.048}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------- player values
def production_values(production, window, fallback=None):
    """gsis -> {tier, value, weight, group, season, evidence}: the window's best tier."""
    out = {}
    for pid, p in production["players"].items():
        best = None
        for season in window:
            s = p["seasons"].get(str(season))
            if not s or s.get("tier") is None:
                continue
            cand = {"tier": s["tier"], "group": s["group"], "season": season, "verification": s["verification"],
                    "discounted": False}
            if best is None or TIER_ORDER[cand["tier"]] < TIER_ORDER[best["tier"]]:
                best = cand
        if best is None and fallback is not None:
            s = p["seasons"].get(str(fallback))
            if s and s.get("tier") is not None:
                tier = TIER_STEP[min(4, TIER_ORDER[s["tier"]] + 1)]
                best = {"tier": tier, "group": s["group"], "season": fallback, "verification": s["verification"],
                        "discounted": True, "undiscounted_tier": s["tier"]}
        if best is None:
            continue
        weight = PRODUCTION_WEIGHT[best["verification"]]
        best["weight"] = weight
        best["value"] = TIER_VALUE[best["tier"]] * weight
        out[pid] = best
    return out


def production_z_values(production, window):
    """Continuous sensitivity: gsis -> {value: best clipped z over the window, group}."""
    stats = {}
    for pid, p in production["players"].items():
        for season, s in p["seasons"].items():
            if s.get("tier") is not None and int(season) in window:
                stats.setdefault((s["group"], season), []).append(s["shrunk"])
    moments = {k: (v1.mean(v), v1.sd(v)) for k, v in stats.items() if len(v) > 2}
    out = {}
    for pid, p in production["players"].items():
        best = None
        for season in window:
            s = p["seasons"].get(str(season))
            if not s or s.get("tier") is None or (s["group"], str(season)) not in moments:
                continue
            m, sdv = moments[(s["group"], str(season))]
            z = max(-2.0, min(2.0, (s["shrunk"] - m) / sdv)) if sdv else 0.0
            if best is None or z > best["value"]:
                best = {"value": z, "group": s["group"], "season": season, "tier": s["tier"], "weight": 1.0}
        if best is not None:
            out[pid] = best
    return out


def honours_values(honours, seasons, cutoff):
    return v1.player_values(honours, seasons, cutoff)


def honour_is_stale(hv, seasons):
    """True when none of the player's admissible honours comes from the window's later season."""
    return not any(h["season"] == max(seasons) for h in hv["honours"])


def honour_groups(honours):
    """evidence_id -> position group of the honour."""
    return {e["evidence_id"]: rt_strength.usage.group(e["position"]) or e["position"] for e in honours["entries"]}


def age_on(birth, season):
    if not birth:
        return None
    b = date.fromisoformat(birth)
    anchor = date(season, 9, 1)
    return anchor.year - b.year - ((anchor.month, anchor.day) < (b.month, b.day))


FLOOR_UNHONOURED = {"on": False}


def combined_value(pid, position, slot_is_qb, hv, pv, side, *, age=None, age_shrink=False):
    """(value, receipt) for one starter under the preregistered rule."""
    grp = v1.unit_of(position)
    honour = 0.0
    h = (hv.get(pid) or {}).get("offdef")
    if h and h["unit"] == side:
        # QB honours count only in the passer slot; non-QB honours never do (first study rule).
        if (hv[pid].get("group") == "QB") == slot_is_qb:
            honour = h["value"]
    prod = 0.0
    p = pv.get(pid)
    if p and GROUP_SIDE.get(p["group"]) == side:
        if (p["group"] == "QB") == slot_is_qb:
            prod = p["value"]
    receipt = {"honours_value": honour, "production_value": prod}
    if age_shrink and honour > 0 and age is not None and hv[pid].get("stale") and age >= PREREGISTERED["age_shrink"]["thresholds"].get(hv[pid].get("group", ""), 99):
        honour *= 0.5
        receipt["age_shrunk"] = True
    # An honour can only lift: with one, the larger of the two; without one,
    # the production value stands, negative tiers included (see the
    # correction note in PREREGISTERED["player_value"]).
    if FLOOR_UNHONOURED["on"]:
        return max(honour, prod), receipt
    return (max(honour, prod) if honour > 0 else prod), receipt


def unit_composite(rows, hv, pv, side, *, ages=None, age_shrink=False, qb_cap=True):
    """(composite, contributors, honours-only composite, production-only composite)."""
    total = h_total = p_total = 0.0
    rows_out, seen, qbs = [], set(), []
    for row in rows:
        pid = row["player_id"]
        if pid in seen:
            continue
        seen.add(pid)
        is_qb = row["position"] == "QB"
        weight = 3 if is_qb else 1
        value, receipt = combined_value(pid, row["position"], is_qb, hv, pv, side,
                                        age=(ages or {}).get(pid), age_shrink=age_shrink)
        item = {"player_id": pid, "name": row["name"], "position": row["position"], "position_weight": weight,
                "value": value, **receipt, "contribution": weight * value}
        if is_qb and qb_cap:
            qbs.append(item)
            continue
        if item["contribution"] or item["production_value"] or item["honours_value"]:
            rows_out.append(item)
    if qbs:
        rows_out.append(max(qbs, key=lambda i: i["contribution"]))
    for item in rows_out:
        total += item["contribution"]
        h_total += item["position_weight"] * (item["honours_value"] if item["honours_value"] > 0 else 0.0)
        p_total += item["position_weight"] * item["production_value"]
    return total, rows_out, h_total, p_total


# --------------------------------------------------------------------- fits
def fit_side(x, y, w):
    a, b, se, r2 = v1.wls(x, y, w)
    return a, b, se, r2, v1.loo(x, y, w)


def side_report(comp, rates, clubs, side, key):
    x = [comp[c] for c in clubs]
    w = [rates[c][f"{key}_drives"] for c in clubs]
    y = [rates[c][f"{key}_td"] for c in clubs]
    a, b, se, r2, loo = fit_side(x, y, w)
    slope = b if side == "offense" else -b
    shrunk, shrunk_sd = v1.shrink(slope, se)
    comp_sd = v1.sd(x)
    implied = abs(shrunk) * comp_sd
    return {"intercept": a, "slope": slope, "se": se, "r2": r2, "loo": loo, "shrunk_slope": shrunk,
            "shrunk_sd": shrunk_sd, "composite_mean": v1.mean(x), "composite_sd": comp_sd,
            "composite_min": min(x), "composite_max": max(x), "implied_club_sd": implied,
            "fraction_of_target": implied / TARGET[side],
            "points_per_team_game_sd": implied * POINTS_PER_TD_SHARE * DRIVES_PER_TEAM_GAME}


def net_report(off_comp, def_comp, rates, clubs, b_off, b_def):
    off = {c: b_off * (off_comp[c] - v1.mean(list(off_comp.values()))) for c in clubs}
    dfn = {c: b_def * (def_comp[c] - v1.mean(list(def_comp.values()))) for c in clubs}
    implied = math.sqrt(v1.sd(list(off.values())) ** 2 + v1.sd(list(dfn.values())) ** 2)
    # direct check: club net TD share (scored minus allowed) on net composite parts
    x = [off[c] - dfn[c] for c in clubs]
    y = [rates[c]["off_td"] - rates[c]["def_td"] for c in clubs]
    w = [rates[c]["off_drives"] + rates[c]["def_drives"] for c in clubs]
    a, b, se, r2, loo = fit_side(x, y, w)
    return {"implied_edge_sd": implied, "fraction_of_target": implied / TARGET["net"],
            "points_per_team_game_sd": implied * POINTS_PER_TD_SHARE * DRIVES_PER_TEAM_GAME,
            "direct_net_fit": {"slope_on_predicted_edge": b, "se": se, "r2": r2, "loo": loo}}


def two_term(h_comp, p_comp, rates, clubs, key, side):
    X = [[1.0, h_comp[c], p_comp[c]] for c in clubs]
    y = [rates[c][f"{key}_td"] for c in clubs]
    w = [rates[c][f"{key}_drives"] for c in clubs]
    k = len(w) / sum(w)
    sw = [wi * k for wi in w]
    Xw = [[v * math.sqrt(wi) for v in row] for row, wi in zip(X, sw)]
    yw = [yi * math.sqrt(wi) for yi, wi in zip(y, sw)]
    beta = v1.ols(Xw, yw)
    pred = [sum(b * v for b, v in zip(beta, row)) for row in X]
    my = v1.mean(y, sw)
    sse = sum(wi * (yi - pi) ** 2 for yi, pi, wi in zip(y, pred, sw))
    sst = sum(wi * (yi - my) ** 2 for yi, wi in zip(y, sw))
    errors, null = [], []
    for i in range(len(clubs)):
        keep = [j for j in range(len(clubs)) if j != i]
        bi = v1.ols([Xw[j] for j in keep], [yw[j] for j in keep])
        errors.append(y[i] - sum(b * v for b, v in zip(bi, X[i])))
        null.append(y[i] - v1.mean([y[j] for j in keep], [sw[j] for j in keep]))
    rmse = math.sqrt(v1.mean([e * e for e in errors]))
    rmse0 = math.sqrt(v1.mean([e * e for e in null]))
    sign = 1 if side == "offense" else -1
    return {"b_honours": sign * beta[1], "b_production": sign * beta[2], "r2": 1 - sse / sst,
            "loo": {"rmse": rmse, "null_rmse": rmse0, "skill": 1 - (rmse / rmse0) ** 2}}


# ------------------------------------------------------------- 2012 study
def study_2012(source, pbp12, honours, production):
    starters = v1.depth_starters(source / "depth_charts_2012.csv")
    rows = v1.drives(pbp12)
    rates = v1.team_rates(rows)
    clubs = sorted(rates)
    hv = honours_values(honours, [2010, 2011], "2012-09-05")
    groups = honour_groups(honours)
    for pid, h in hv.items():
        h["stale"] = honour_is_stale(h, [2010, 2011])
        h["group"] = groups.get(h["honours"][0]["evidence_id"])
    pv = production_values(production, [2010, 2011])
    births = {}
    for r in v1.read(source / "roster_weekly_2012.csv"):
        if r["week"] == "1" and r["game_type"] == "REG" and r["birth_date"]:
            births[r["gsis_id"]] = r["birth_date"]
    ages = {pid: age_on(b, 2012) for pid, b in births.items()}
    variants = {}
    club_rows = {}
    pz = production_z_values(production, [2010, 2011])
    for name, use_h, use_p, shrink_age in (("honours_only", True, False, False), ("production_only", False, True, False),
                                           ("combined_max", True, True, False), ("combined_max_age_shrink", True, True, True),
                                           ("continuous_production_sensitivity", True, "z", False)):
        comp = {"offense": {}, "defense": {}}
        h_comp = {"offense": {}, "defense": {}}
        p_comp = {"offense": {}, "defense": {}}
        detail = {}
        for club in clubs:
            for side in ("offense", "defense"):
                total, contributors, h_total, p_total = unit_composite(
                    starters[club][side], hv if use_h else {}, (pz if use_p == "z" else pv) if use_p else {}, side,
                    ages=ages, age_shrink=shrink_age)
                comp[side][club] = total
                h_comp[side][club] = h_total
                p_comp[side][club] = p_total
                detail.setdefault(club, {})[side] = {"composite": total, "contributors": contributors}
        fits = {side: side_report(comp[side], rates, clubs, side, key)
                for side, key in (("offense", "off"), ("defense", "def"))}
        net = net_report(comp["offense"], comp["defense"], rates, clubs,
                         fits["offense"]["shrunk_slope"], fits["defense"]["shrunk_slope"])
        joint = {m: v1.drive_joint(rows, comp["offense"], comp["defense"], m) for m in ("td",)}
        variants[name] = {"fits": fits, "net": net, "drive_joint": joint,
                          "clubs_composite": {c: [comp["offense"][c], comp["defense"][c]] for c in clubs}}
        if name == "combined_max":
            club_rows = detail
            variants["two_term_sensitivity"] = {
                side: two_term(h_comp[side], p_comp[side], rates, clubs, key, side)
                for side, key in (("offense", "off"), ("defense", "def"))}
    age = variants["combined_max_age_shrink"]["fits"]
    base = variants["combined_max"]["fits"]
    adopt_age = all(age[s]["loo"]["skill"] > base[s]["loo"]["skill"] for s in ("offense", "defense"))
    variants["age_shrink_decision"] = {
        "adopted": adopt_age,
        "loo_skill_without": {s: base[s]["loo"]["skill"] for s in base},
        "loo_skill_with": {s: age[s]["loo"]["skill"] for s in age},
    }
    shrunk_players = []
    for club in clubs:
        for side in ("offense", "defense"):
            for row in starters[club][side]:
                pid = row["player_id"]
                h = hv.get(pid)
                if h and h.get("offdef") and h["stale"] and ages.get(pid) is not None and \
                        ages[pid] >= PREREGISTERED["age_shrink"]["thresholds"].get(h.get("group") or "", 99):
                    shrunk_players.append({"name": row["name"], "club": club, "age": ages[pid], "group": h.get("group")})
    variants["age_shrink_decision"]["players_shrunk"] = shrunk_players
    primary = "combined_max_age_shrink" if adopt_age else "combined_max"
    variants["primary_variant"] = primary
    return {"season": 2012, "honour_seasons": [2010, 2011], "production_seasons": [2010, 2011],
            "league": {"drives": len(rows), "td_share": v1.mean([d["td"] for d in rows]),
                       "clubs": {c: {k: round(v, 4) for k, v in rates[c].items()} for c in clubs}},
            "variants": variants, "clubs": club_rows, "primary_variant": primary}


# --------------------------------------------------------- coverage 2014
def _slot_depth(slot):
    nums = [int(m) for m in re.findall(r"(\d+)", slot or "")]
    return min(nums) if nums else 99


def coverage_2014(honours, production):
    league = load(LEAGUE)
    births = load(BIRTHS)
    by_gsis = {v["gsis_id"]: v["birth_date"] for v in births["players"].values() if v.get("gsis_id")}
    hv = honours_values(honours, [2011, 2012], "2014-02-02")
    groups = honour_groups(honours)
    for pid, h in hv.items():
        h["stale"] = honour_is_stale(h, [2011, 2012])
        h["group"] = groups.get(h["honours"][0]["evidence_id"])
    pv = production_values(production, [2011, 2012], fallback=2010)
    rosters = defaultdict(list)
    for p in league["players"]:
        if p.get("inventory_club"):
            rosters[p["inventory_club"]].append(p)
    clubs = {}
    league_groups = defaultdict(lambda: {"starters": 0, "honours": 0, "production": 0, "either": 0})
    for club, players in sorted(rosters.items()):
        view = tuple(PlayerInput(p["player_id"], p["position"], depth=_slot_depth(p.get("branch_week1_slot")))
                     for p in sorted(players, key=lambda p: (_slot_depth(p.get("branch_week1_slot")), p["name"])))
        passer = rt_strength.usage.game_passer(view)
        starters = rt_strength.offense_starters(view, passer) + rt_strength.defense_starters(view)
        groups = defaultdict(lambda: {"starters": 0, "honours": 0, "production": 0, "either": 0})
        rows = []
        for slot, player in starters:
            grp = rt_strength.usage.group(player.position) or player.position
            side = "offense" if slot in ("QB", "OL", "RB", "WR", "TE", "FB") else "defense"
            h = hv.get(player.player_id, {}).get("offdef")
            has_h = bool(h and h["unit"] == side and ((hv[player.player_id].get("group") == "QB") == (slot == "QB")))
            p = pv.get(player.player_id)
            has_p = bool(p and GROUP_SIDE.get(p["group"]) == side and ((p["group"] == "QB") == (slot == "QB")))
            for g in (groups[grp], league_groups[grp]):
                g["starters"] += 1
                g["honours"] += has_h
                g["production"] += has_p
                g["either"] += has_h or has_p
            rows.append({"player_id": player.player_id, "slot": slot, "honours": has_h,
                         "production_tier": p["tier"] if has_p else None})
        n = len(starters)
        clubs[club] = {"starters": n, "with_honours": sum(r["honours"] for r in rows),
                       "with_production": sum(1 for r in rows if r["production_tier"]),
                       "with_either": sum(1 for r in rows if r["honours"] or r["production_tier"]),
                       "by_group": dict(groups)}
    total = sum(c["starters"] for c in clubs.values())
    return {"as_of": league.get("as_of"), "role_source": "inventory identity ordered by branch_week1_slot number "
            "(a job/identity ordering, not a 2014 depth chart); starters per the kernel's slot rule",
            "clubs": clubs,
            "league": {"starters": total,
                       "honours_share": sum(c["with_honours"] for c in clubs.values()) / total,
                       "production_share": sum(c["with_production"] for c in clubs.values()) / total,
                       "either_share": sum(c["with_either"] for c in clubs.values()) / total,
                       "by_group": {g: {**v, "either_share": v["either"] / v["starters"], "honours_share": v["honours"] / v["starters"]}
                                    for g, v in sorted(league_groups.items())}}}


# ------------------------------------------------------- attribution tilt
def attribution_tilt(source, honours, production):
    stats = v1.read(source / "stats_player_reg_2012.csv")
    hv = honours_values(honours, [2010, 2011], "2012-09-05")
    groups = honour_groups(honours)
    for pid, h in hv.items():
        h["group"] = groups.get(h["honours"][0]["evidence_id"])
    pv = production_values(production, [2010, 2011])

    def tier_of(pid, side, is_qb=False):
        h = (hv.get(pid) or {}).get("offdef")
        hv_val = h["value"] if h and h["unit"] == side and (hv[pid].get("group") == "QB") == is_qb else 0.0
        p = pv.get(pid)
        pv_val = p["value"] if p and GROUP_SIDE.get(p["group"]) == side and (p["group"] == "QB") == is_qb else 0.0
        value = max(hv_val, pv_val)
        if value >= 2:
            return "Elite"
        if value >= 1:
            return "Plus"
        if value <= -2:
            return "Replacement-Level"
        if value <= -1:
            return "Below-Average"
        return "Average"

    by_team = defaultdict(list)
    for r in stats:
        if r["season_type"] == "REG":
            by_team[r["recent_team"]].append(r)
    out = {}
    for name, field, groups, side in (("top_receiver_target_share", "targets", ("WR", "TE", "RB"), "offense"),
                                      ("top_rusher_carry_share", "carries", ("RB", "FB"), "offense"),
                                      ("top_sacker_sack_share", "def_sacks", ("DE", "DT", "NT", "OLB", "ILB", "MLB", "LB"), "defense")):
        shares = []
        for team, rows in by_team.items():
            total = sum(float(r[field] or 0) for r in rows)
            cands = [r for r in rows if r["position"].strip().upper() in groups]
            if not total or not cands:
                continue
            top = max(cands, key=lambda r: float(r[field] or 0))
            shares.append({"team": team, "player": top["player_display_name"], "share": float(top[field] or 0) / total,
                           "tier": tier_of(top["player_id"], side)})
        mean_all = v1.mean([s["share"] for s in shares])
        sd_all = v1.sd([s["share"] for s in shares])
        by_tier = defaultdict(list)
        for s in shares:
            by_tier[s["tier"]].append(s["share"])
        factors = {}
        for tier in TIER_STEP:
            if len(by_tier.get(tier, [])) >= 3:
                factors[tier] = max(0.6, min(1.6, v1.mean(by_tier[tier]) / mean_all))
        # fill thin tiers from the nearest tier toward Average
        for i, tier in enumerate(TIER_STEP):
            if tier in factors:
                continue
            step = 1 if i < 2 else -1
            j = i + step
            while 0 <= j < len(TIER_STEP) and TIER_STEP[j] not in factors:
                j += step
            factors[tier] = factors.get(TIER_STEP[j], 1.0) if 0 <= j < len(TIER_STEP) else 1.0
        out[name] = {"clubs": len(shares), "mean": mean_all, "sd": sd_all,
                     "by_tier": {t: {"clubs": len(v), "mean_share": v1.mean(v)} for t, v in by_tier.items()},
                     "factors": factors, "rows": sorted(shares, key=lambda s: -s["share"])}
    return out


def team_game_top_shares(source, pbp12):
    """Per team-game top-receiver target share and top-rusher (non-QB) carry
    share over the 2012 regular season: the centres and SDs for the
    runtime/bands.py rows (a team-game top share runs above a club-season
    one, so the rows need their own centre)."""
    positions = {r["player_id"]: r["position"].strip().upper() for r in v1.read(source / "stats_player_reg_2012.csv")}
    targets, carries = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))
    for r in v1.read(pbp12):
        if r["season_type"] != "REG" or r["two_point_attempt"] == "1":
            continue
        key = (r["game_id"], r["posteam"])
        if r["play_type"] == "pass" and r["receiver_player_id"]:
            targets[key][r["receiver_player_id"]] += 1
        elif r["play_type"] in ("run", "qb_kneel") and r["rusher_player_id"] and positions.get(r["rusher_player_id"]) != "QB":
            carries[key][r["rusher_player_id"]] += 1
    out = {}
    for name, table in (("top_receiver_target_share", targets), ("top_rusher_carry_share", carries)):
        shares = [max(c.values()) / sum(c.values()) for c in table.values() if sum(c.values())]
        out[name] = {"team_games": len(shares), "mean": v1.mean(shares), "sd": v1.sd(shares),
                     "definition": "per team-game, the top player's share of the club's targets (or non-QB carries), "
                                   "2012 regular season, two-point tries excluded"}
    return out


def main():
    source, pbp12 = Path(sys.argv[1]), Path(sys.argv[2])
    honours, production = load(HONOURS), load(PRODUCTION)
    study = study_2012(source, pbp12, honours, production)
    FLOOR_UNHONOURED["on"] = True
    floored = study_2012(source, pbp12, honours, production)
    FLOOR_UNHONOURED["on"] = False
    study["variants_floored_first_fit"] = {k: {"fits": v["fits"], "net": v["net"]} for k, v in floored["variants"].items()
                                          if isinstance(v, dict) and "fits" in v}
    v1_fits = load(V1_JSON)["study_2012"]["primary_week1_depth_starters"]["fits"]
    before = {}
    for side in ("offense", "defense"):
        f = v1_fits[f"{side}_td"]
        implied = f["shrunk_slope"] * f["composite_sd"]
        before[side] = {"r2": f["r2"], "loo_skill": f["loo"]["skill"], "shrunk_slope": f["shrunk_slope"],
                        "implied_club_sd": implied, "fraction_of_target": implied / TARGET[side],
                        "points_per_team_game_sd": implied * POINTS_PER_TD_SHARE * DRIVES_PER_TEAM_GAME}
    before_net = math.sqrt(before["offense"]["implied_club_sd"] ** 2 + before["defense"]["implied_club_sd"] ** 2)
    before["net"] = {"implied_edge_sd": before_net, "fraction_of_target": before_net / TARGET["net"],
                     "points_per_team_game_sd": before_net * POINTS_PER_TD_SHARE * DRIVES_PER_TEAM_GAME}
    output = {
        "schema_version": 1,
        "built_by": "scripts/research/build_2014_strength_calibration_v2.py",
        "policy": "runtime/2014_engine_decisions.md E1 second pass (honours + production); runtime/defect_register.md items 1 and 19",
        "preregistered": PREREGISTERED,
        "sources": {"honours_evidence": {"file": str(HONOURS.relative_to(ROOT)), "sha256": v1.sha(HONOURS)},
                    "production_evidence": {"file": str(PRODUCTION.relative_to(ROOT)), "sha256": v1.sha(PRODUCTION)},
                    "depth_charts_2012.csv": {"sha256": v1.sha(source / "depth_charts_2012.csv")},
                    "roster_weekly_2012.csv": {"sha256": v1.sha(source / "roster_weekly_2012.csv")},
                    "stats_player_reg_2012.csv": {"sha256": v1.sha(source / "stats_player_reg_2012.csv")},
                    "play_by_play_2012.csv.gz": {"sha256": v1.sha(pbp12)},
                    "league_players": {"file": str(LEAGUE.relative_to(ROOT)), "sha256": v1.sha(LEAGUE)},
                    "player_birth_dates": {"file": str(BIRTHS.relative_to(ROOT)), "sha256": v1.sha(BIRTHS)}},
        "before_first_study": before,
        "study_2012": study,
        "coverage_2014": coverage_2014(honours, production),
        "attribution_tilt_2012": attribution_tilt(source, honours, production),
        "team_game_top_shares_2012": team_game_top_shares(source, pbp12),
    }
    OUT.write_text(json.dumps(output, indent=1, default=float) + "\n", encoding="utf-8")
    for name, var in study["variants"].items():
        if "fits" not in var:
            continue
        print(name)
        for side in ("offense", "defense"):
            f = var["fits"][side]
            print("  %-8s slope %.5f se %.5f shrunk %.5f R2 %.3f LOO %.3f compSD %.2f implied %.4f (%.0f%% of target) pts %.2f" % (
                side, f["slope"], f["se"], f["shrunk_slope"], f["r2"], f["loo"]["skill"], f["composite_sd"],
                f["implied_club_sd"], 100 * f["fraction_of_target"], f["points_per_team_game_sd"]))
        n = var["net"]
        print("  net implied %.4f (%.0f%% of target) pts %.2f" % (n["implied_edge_sd"], 100 * n["fraction_of_target"], n["points_per_team_game_sd"]))
    print("two-term", json.dumps(study["variants"]["two_term_sensitivity"], indent=0))
    print("age shrink", json.dumps({k: v for k, v in study["variants"]["age_shrink_decision"].items() if k != "players_shrunk"}))
    print("primary", study["primary_variant"])
    print("coverage", json.dumps(output["coverage_2014"]["league"], indent=0))
    print("tilt", json.dumps({k: {"mean": v["mean"], "factors": v["factors"], "by_tier": v["by_tier"]}
                              for k, v in output["attribution_tilt_2012"].items()}, indent=0))


if __name__ == "__main__":
    main()
