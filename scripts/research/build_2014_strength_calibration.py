#!/usr/bin/env python3
"""Calibrate the size of the honours-based unit-strength effect (E1 first pass).

  python scripts/research/build_2014_strength_calibration.py SOURCE_DIR PBP_2012 [PBP_2011]

SOURCE_DIR holds the pinned nflverse files in SOURCES (weekly depth charts and
weekly rosters). PBP_2012 / PBP_2011 are the nflverse regular-season
play-by-play files (only drive results and scores are read). Honours come
from the committed library/data/2010_2012_honours_evidence.json.

Outputs library/data/2014_strength_calibration.json. The prose report is
library/2014_strength_calibration.md.

Everything in PREREGISTERED below was fixed and written down before the
first fit was run. The fit targets are real 2012 (pre-divergence) aggregate
per-drive results; no branch 2013 result, no Jacksonville record and no
post-divergence real result is read. Jacksonville players are treated
exactly like every other club's players.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "library/data/2010_2012_honours_evidence.json"
# The inventory moved to career/2014/league/personnel/ in the readable season layout;
# the JSON keeps the path string it was built from.
LEAGUE = ROOT / "career/2014/league/personnel/league_players.json"
OUT = ROOT / "library/data/2014_strength_calibration.json"
SOURCES = {
    "depth_charts_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2012.csv",
    "depth_charts_2011.csv": "https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2011.csv",
    "roster_weekly_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2012.csv",
}
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{}.csv.gz"

PREREGISTERED = {
    "tier_rule": {
        "window": "the two most recent completed pre-divergence seasons before the season being predicted "
                  "(2012 target: 2010-2011 honours; 2014 branch: 2011-2012 honours)",
        "Elite": "any AP All-Pro 1st team in the window",
        "Plus": "AP All-Pro 2nd team or an original Pro Bowl selection in the window",
        "Average": "everyone else (low-confidence fallback: insufficient knowledge, not verified average)",
        "alternates_replacements": "no effect: a replacement is chosen after withdrawals from a truncated pool, "
                                   "its announcement date is not pinned, and 2012-season replacements may post-date the divergence",
        "specialists": "K/P/KR/PR/LS/ST honours feed special teams only, never the offense/defense composites",
    },
    "tier_values": {"Elite": 4, "Plus": 3, "Average": 2},
    "evidence_weight": {"Confirmed two-pass": 1.0, "Single-pass": 0.5},
    "player_value": "max over admissible honours of (tier_value - 2) * evidence_weight",
    "position_weights": {"QB": 3, "other offensive starter": 1, "defensive starter": 1},
    "unit_composite": "sum over the unit's starters of position_weight * player_value",
    "role_source_primary": "the club's Week 1 regular-season depth chart, depth_team 1, formation Offense/Defense (role only, not ability)",
    "role_source_sensitivity": "all players on the club's Week 1 weekly roster (status ACT) grouped by position; at most one QB (highest value)",
    "targets": "per-drive touchdown share (fixed_drive_result == 'Touchdown') and points per drive, offense and defense, 2012 regular season, all drives with a possession team",
    "fit": "one slope per side by drive-weighted least squares on the 32 clubs (with intercept); "
           "shrinkage prior N(0, 0.025^2) per composite unit (the installed kernel's per-tier edge); "
           "leave-one-club-out prediction; joint drive-level check with home indicator and game-cluster bootstrap (500 draws, seed 20140401)",
    "edge_target": "implied true SD of per-drive offense-minus-defense TD-share difference about 0.048 (offense:defense variance about 4:1), "
                   "derived from 2012 nflverse drives; reported, never used to inflate the fitted scale",
    "clamp": "installed kernel: edge = clip((off_anchor - def_anchor) * 0.025 + 0.008 home, -0.06, 0.06)",
}
TEAM_FIX = {"LA": "STL", "LAC": "SD", "LV": "OAK", "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "SL": "STL"}
OFFENSE_POS = {"QB", "RB", "HB", "FB", "WR", "TE", "T", "G", "C", "OT", "OG", "OL", "LT", "LG", "RG", "RT"}
DEFENSE_POS = {"DE", "DT", "NT", "DL", "OLB", "ILB", "MLB", "LB", "CB", "S", "SS", "FS", "DB"}
SPECIAL_POS = {"K", "P", "KR", "PR", "LS", "ST"}
PRIOR_SD = 0.025
SEED = 20140401


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def team(code):
    return TEAM_FIX.get(code, code)


def unit_of(position):
    position = position.strip().upper()
    if position in SPECIAL_POS:
        return "special"
    if position in OFFENSE_POS:
        return "offense"
    if position in DEFENSE_POS:
        return "defense"
    return None


# ---------------------------------------------------------------- evidence
def player_values(evidence, seasons, cutoff):
    """player_id -> {value, tier, honours[], unit_of_honour}; specialist honours kept apart."""
    tiers = {"AP1": ("Elite", 4), "AP2": ("Plus", 3), "PB": ("Plus", 3)}
    out = {}
    for row in evidence["entries"]:
        if row["season"] not in seasons or row["honour_kind"] not in tiers:
            continue
        if not row["public_date"] or row["public_date"] >= cutoff:
            continue
        tier, value = tiers[row["honour_kind"]]
        weight = PREREGISTERED["evidence_weight"][row["verification"]]
        scored = (value - 2) * weight
        unit = unit_of(row["position"]) or "unknown"
        slot = out.setdefault(row["player_id"], {"player": row["player"], "offdef": None, "special": None, "honours": []})
        slot["honours"].append({"evidence_id": row["evidence_id"], "season": row["season"], "honour": row["honour"],
                                "verification": row["verification"], "public_date": row["public_date"], "club": row["club"]})
        key = "special" if unit == "special" else "offdef"
        best = slot[key]
        if best is None or scored > best["value"] or (scored == best["value"] and value > best["tier_value"]):
            slot[key] = {"value": scored, "tier": tier, "tier_value": value, "weight": weight, "unit": unit}
    return out


# ------------------------------------------------------------ role sources
def depth_starters(path):
    starters = defaultdict(lambda: {"offense": [], "defense": [], "special": []})
    for row in read(path):
        if row["week"] != "1" or row["game_type"] != "REG" or row["depth_team"].strip() != "1":
            continue
        formation = {"Offense": "offense", "Defense": "defense", "Special Teams": "special"}.get(row["formation"])
        if formation:
            starters[team(row["club_code"])][formation].append({"player_id": row["gsis_id"], "name": row["full_name"],
                                                                "position": row["position"].strip().upper(),
                                                                "slot": row["depth_position"].strip()})
    return starters


def roster_units(path):
    units = defaultdict(lambda: {"offense": [], "defense": [], "special": []})
    for row in read(path):
        if row["week"] != "1" or row["game_type"] != "REG" or row["status"] != "ACT":
            continue
        unit = unit_of(row["position"])
        if unit:
            units[team(row["team"])][unit].append({"player_id": row["gsis_id"], "name": row["full_name"],
                                                   "position": row["position"].strip().upper(), "slot": row["depth_chart_position"]})
    return units


def composite(unit_rows, values, side, qb_cap=False):
    total, contributors, seen = 0.0, [], set()
    qbs = []
    for row in unit_rows:
        pid = row["player_id"]
        if pid in seen:
            continue
        seen.add(pid)
        best = (values.get(pid) or {}).get("offdef")
        if not best or best["unit"] != side:
            continue
        weight = 3 if row["position"] == "QB" else 1
        item = {"player_id": pid, "name": row["name"], "position": row["position"], "tier": best["tier"],
                "evidence_weight": best["weight"], "position_weight": weight, "contribution": weight * best["value"]}
        if row["position"] == "QB" and qb_cap:
            qbs.append(item)
            continue
        contributors.append(item)
    if qbs:
        contributors.append(max(qbs, key=lambda item: item["contribution"]))
    total = sum(item["contribution"] for item in contributors)
    return total, contributors


# ------------------------------------------------------------------ drives
def drives(path):
    grouped = {}
    for row in read(path):
        if row["season_type"] != "REG" or not row["posteam"] or not row["fixed_drive"]:
            continue
        key = (row["game_id"], row["fixed_drive"])
        d = grouped.get(key)
        start, post = float(row["posteam_score"] or 0), float(row["posteam_score_post"] or 0)
        if d is None:
            grouped[key] = {"game": row["game_id"], "off": team(row["posteam"]), "def": team(row["defteam"]),
                            "home": int(row["posteam"] == row["home_team"]), "result": row["fixed_drive_result"],
                            "start": start, "end": post}
        elif d["off"] == team(row["posteam"]):
            d["start"], d["end"] = min(d["start"], start), max(d["end"], post)
    out = []
    for d in grouped.values():
        out.append({"game": d["game"], "off": d["off"], "def": d["def"], "home": d["home"],
                    "td": 1.0 if d["result"] == "Touchdown" else 0.0, "pts": max(0.0, d["end"] - d["start"])})
    return out


def game_margins(path):
    finals = {}
    for row in read(path):
        if row["season_type"] != "REG":
            continue
        finals[row["game_id"]] = (float(row["total_home_score"] or 0), float(row["total_away_score"] or 0))
    margins = [h - a for h, a in finals.values()]
    return margins


def team_rates(rows):
    agg = defaultdict(lambda: {"off_n": 0, "off_td": 0.0, "off_pts": 0.0, "def_n": 0, "def_td": 0.0, "def_pts": 0.0})
    for d in rows:
        a, b = agg[d["off"]], agg[d["def"]]
        a["off_n"] += 1; a["off_td"] += d["td"]; a["off_pts"] += d["pts"]
        b["def_n"] += 1; b["def_td"] += d["td"]; b["def_pts"] += d["pts"]
    return {t: {"off_drives": v["off_n"], "off_td": v["off_td"] / v["off_n"], "off_ppd": v["off_pts"] / v["off_n"],
                "def_drives": v["def_n"], "def_td": v["def_td"] / v["def_n"], "def_ppd": v["def_pts"] / v["def_n"]}
            for t, v in agg.items()}


# -------------------------------------------------------------- statistics
def mean(xs, ws=None):
    ws = ws or [1.0] * len(xs)
    return sum(x * w for x, w in zip(xs, ws)) / sum(ws)


def sd(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def wls(x, y, w):
    """Weighted least squares y = a + b x. Returns a, b, se_b (weights normalised to mean 1)."""
    k = len(w) / sum(w)
    w = [wi * k for wi in w]
    mx, my = mean(x, w), mean(y, w)
    sxx = sum(wi * (xi - mx) ** 2 for xi, wi in zip(x, w))
    if sxx == 0:
        return my, 0.0, float("inf"), 0.0
    b = sum(wi * (xi - mx) * (yi - my) for xi, yi, wi in zip(x, y, w)) / sxx
    a = my - b * mx
    resid = [yi - a - b * xi for xi, yi in zip(x, y)]
    s2 = sum(wi * r * r for r, wi in zip(resid, w)) / (len(x) - 2)
    syy = sum(wi * (yi - my) ** 2 for yi, wi in zip(y, w))
    r2 = 1 - sum(wi * r * r for r, wi in zip(resid, w)) / syy
    return a, b, math.sqrt(s2 / sxx), r2


def shrink(b, se):
    tau2 = PRIOR_SD ** 2
    return b * tau2 / (tau2 + se * se), math.sqrt(tau2 * se * se / (tau2 + se * se))


def loo(x, y, w):
    errors, null = [], []
    for i in range(len(x)):
        xs = x[:i] + x[i + 1:]; ys = y[:i] + y[i + 1:]; ws = w[:i] + w[i + 1:]
        a, b, _, _ = wls(xs, ys, ws)
        errors.append(y[i] - (a + b * x[i]))
        null.append(y[i] - mean(ys, ws))
    rmse = math.sqrt(mean([e * e for e in errors]))
    rmse0 = math.sqrt(mean([e * e for e in null]))
    return {"rmse": rmse, "null_rmse": rmse0, "skill": 1 - (rmse / rmse0) ** 2}


def corr(x, y):
    mx, my = mean(x), mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else 0.0


def solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[c][c]:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def ols(X, y):
    k = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    b = [sum(r[i] * yi for r, yi in zip(X, y)) for i in range(k)]
    return solve(A, b)


def drive_joint(rows, comp_off, comp_def, target):
    games = sorted({d["game"] for d in rows})
    by_game = defaultdict(list)
    for d in rows:
        by_game[d["game"]].append(d)

    def fit(sample):
        X = [[1.0, comp_off[d["off"]], comp_def[d["def"]], float(d["home"])] for d in sample]
        return ols(X, [d[target] for d in sample])

    point = fit(rows)
    rng = random.Random(SEED)
    draws = []
    for _ in range(500):
        sample = []
        for g in (rng.choice(games) for _ in games):
            sample.extend(by_game[g])
        draws.append(fit(sample))
    ses = [sd([dr[i] for dr in draws]) for i in range(4)]
    return {"intercept": point[0], "b_off": point[1], "se_off": ses[1], "b_def_raw": point[2], "se_def": ses[2],
            "b_def": -point[2], "home": point[3], "se_home": ses[3]}


def binomial_true_sd(rates, drives_n):
    obs = sd(rates)
    p = mean(rates)
    noise = math.sqrt(mean([p * (1 - p) / n for n in drives_n]))
    return obs, noise, math.sqrt(max(0.0, obs * obs - noise * noise))


# -------------------------------------------------------------------- main
def study(evidence, source, pbp_path, season, honour_seasons, cutoff):
    values = player_values(evidence, honour_seasons, cutoff)
    starters = depth_starters(source / f"depth_charts_{season}.csv")
    rows = drives(pbp_path)
    rates = team_rates(rows)
    clubs = sorted(rates)
    result = {"season": season, "honour_seasons": honour_seasons, "clubs": {}}
    variants = {"primary_week1_depth_starters": starters}
    if season == 2012:
        variants["sensitivity_week1_active_roster"] = roster_units(source / "roster_weekly_2012.csv")
    for variant, units in variants.items():
        comp = {}
        for club in clubs:
            off, off_rows = composite(units[club]["offense"], values, "offense", qb_cap=True)
            dfn, def_rows = composite(units[club]["defense"], values, "defense")
            comp[club] = {"offense": off, "defense": dfn, "offense_players": off_rows, "defense_players": def_rows}
        fits = {}
        for side, key in (("offense", "off"), ("defense", "def")):
            x = [comp[c][side] for c in clubs]
            w = [rates[c][f"{key}_drives"] for c in clubs]
            for measure in ("td", "ppd"):
                y = [rates[c][f"{key}_{measure}"] for c in clubs]
                a, b, se, r2 = wls(x, y, w)
                # defense: a better defense lowers the rate allowed; report the strength slope as -b
                slope = b if side == "offense" else -b
                entry = {"intercept": a, "slope": slope, "se": se, "r2": r2, "loo": loo(x, y, w),
                         "composite_mean": mean(x), "composite_sd": sd(x), "composite_max": max(x)}
                if measure == "td":
                    entry["shrunk_slope"], entry["shrunk_sd"] = shrink(slope, se)
                fits[f"{side}_{measure}"] = entry
        joint = {m: drive_joint(rows, {c: comp[c]["offense"] for c in clubs}, {c: comp[c]["defense"] for c in clubs}, m)
                 for m in ("td", "pts")}
        result[variant] = {"fits": fits, "drive_joint": joint}
        if variant.startswith("primary"):
            result["clubs"] = {c: {"offense_composite": comp[c]["offense"], "defense_composite": comp[c]["defense"],
                                   "offense_players": comp[c]["offense_players"], "defense_players": comp[c]["defense_players"],
                                   **{k: round(v, 4) for k, v in rates[c].items()}} for c in clubs}
            honoured = {pid for pid, v in values.items() if v["offdef"]}
            placed = {p["player_id"] for c in clubs for u in ("offense", "defense") for p in units[c][u]}
            result["honoured_not_week1_starter"] = sorted(values[p]["player"] for p in honoured - placed)
    result["league"] = {
        "drives": len(rows), "td_share": mean([d["td"] for d in rows]), "ppd": mean([d["pts"] for d in rows]),
        "offense_td_sd": dict(zip(("observed", "binomial_noise", "implied_true"),
                                  binomial_true_sd([rates[c]["off_td"] for c in clubs], [rates[c]["off_drives"] for c in clubs]))),
        "defense_td_sd": dict(zip(("observed", "binomial_noise", "implied_true"),
                                  binomial_true_sd([rates[c]["def_td"] for c in clubs], [rates[c]["def_drives"] for c in clubs]))),
    }
    margins = game_margins(pbp_path)
    home_rows = [d for d in rows if d["home"]]
    away_rows = [d for d in rows if not d["home"]]
    result["home_observation"] = {"games": len(margins), "home_margin_mean": mean(margins), "home_margin_sd": sd(margins),
                                  "home_win_rate": mean([1.0 if m > 0 else 0.0 for m in margins]),
                                  "home_td_share": mean([d["td"] for d in home_rows]), "away_td_share": mean([d["td"] for d in away_rows]),
                                  "home_ppd": mean([d["pts"] for d in home_rows]), "away_ppd": mean([d["pts"] for d in away_rows])}
    return result, rows, values


def edges(study_result, rows, b_off, b_def, centred=True):
    """Matchup edges implied by the fitted slopes. Centred: composites minus the
    league mean composite, which keeps the league-average drive mix on the 2012
    calibration. Uncentred: Average-only clubs sit at zero and honours only add."""
    clubs = study_result["clubs"]
    m_off = mean([clubs[c]["offense_composite"] for c in clubs]) if centred else 0.0
    m_def = mean([clubs[c]["defense_composite"] for c in clubs]) if centred else 0.0
    off = {c: b_off * (clubs[c]["offense_composite"] - m_off) for c in clubs}
    dfn = {c: b_def * (clubs[c]["defense_composite"] - m_def) for c in clubs}
    games = {}
    for d in rows:
        games.setdefault((d["game"], d["off"]), (d["off"], d["def"], d["home"]))
    matchup = [off[o] - dfn[x] for o, x, _ in games.values()]
    with_home = [m + (0.008 if h else 0.0) for m, (_, _, h) in zip(matchup, games.values())]
    true_off, true_def = sd(list(off.values())), sd(list(dfn.values()))
    return {"b_off": b_off, "b_def": b_def, "centred": centred, "centre": {"offense": m_off, "defense": m_def},
            "team_offense_sd": true_off, "team_defense_sd": true_def,
            "implied_edge_sd": math.sqrt(true_off ** 2 + true_def ** 2),
            "matchup_edge_sd_2012_schedule": sd(matchup),
            "mean_edge": mean(matchup),
            "max_abs_edge_with_home": max(abs(e) for e in with_home),
            "share_beyond_clamp": sum(1 for e in with_home if abs(e) > 0.06) / len(with_home),
            "clubs_beyond_clamp_alone": sorted(c for c in clubs if abs(off[c]) > 0.06 or abs(dfn[c]) > 0.06),
            "anchor_units_per_composite_unit": {"offense": b_off / 0.025, "defense": b_def / 0.025},
            "anchor_range": {"offense": [2 + min(off.values()) / 0.025, 2 + max(off.values()) / 0.025],
                             "defense": [2 + min(dfn.values()) / 0.025, 2 + max(dfn.values()) / 0.025]}}


def influence(study_result, side, key):
    clubs = sorted(study_result["clubs"])
    cl = study_result["clubs"]
    out = {}
    for drop in clubs:
        keep = [c for c in clubs if c != drop]
        _, b, _, _ = wls([cl[c][f"{side}_composite"] for c in keep], [cl[c][f"{key}_td"] for c in keep],
                         [cl[c][f"{key}_drives"] for c in keep])
        out[drop] = b if side == "offense" else -b
    lo, hi = min(out, key=out.get), max(out, key=out.get)
    return {"min_slope": out[lo], "min_when_dropping": lo, "max_slope": out[hi], "max_when_dropping": hi}


def preview_2014(evidence, slopes):
    values = player_values(evidence, [2011, 2012], "2014-02-02")
    league = json.loads(LEAGUE.read_text(encoding="utf-8"))
    rosters = defaultdict(list)
    for p in league["players"]:
        rosters[p.get("inventory_club") or "UNPLACED"].append(p)
    clubs = {}
    for club, players in sorted(rosters.items()):
        units = {"offense": [], "defense": [], "special": []}
        for p in players:
            unit = unit_of(p["position"]) or "unknown"
            units.setdefault(unit, []).append({"player_id": p["player_id"], "name": p["name"], "position": p["position"].upper(), "slot": None})
        off, off_rows = composite(units["offense"], values, "offense", qb_cap=True)
        dfn, def_rows = composite(units["defense"], values, "defense")
        special = [{"player_id": p["player_id"], "name": p["name"], "tier": values[p["player_id"]]["special"]["tier"],
                    "evidence_weight": values[p["player_id"]]["special"]["weight"]}
                   for p in players if p["player_id"] in values and values[p["player_id"]]["special"]]
        cross = [{"player_id": p["player_id"], "name": p["name"], "roster_position": p["position"],
                  "honour_unit": values[p["player_id"]]["offdef"]["unit"]}
                 for p in players if p["player_id"] in values and values[p["player_id"]]["offdef"]
                 and values[p["player_id"]]["offdef"]["unit"] != unit_of(p["position"])]
        used = {r["player_id"] for r in off_rows + def_rows}
        benched_qb = [{"player_id": p["player_id"], "name": p["name"]} for p in players
                      if p["position"].upper() == "QB" and p["player_id"] in values and values[p["player_id"]]["offdef"]
                      and p["player_id"] not in used]
        evidence_players = {p["player_id"] for p in players if p["player_id"] in values}
        clubs[club] = {"roster_players": len(players), "offense_composite": off, "defense_composite": dfn,
                       "offense_players": off_rows, "defense_players": def_rows, "special_teams_players": special,
                       "unit_mismatch_not_counted": cross, "honoured_qb_not_counted": benched_qb,
                       "players_with_evidence": len(evidence_players),
                       "players_average_fallback": len(players) - len(evidence_players)}
    real = [c for c in clubs if c != "UNPLACED"]
    centre = {"offense": mean([clubs[c]["offense_composite"] for c in real]), "defense": mean([clubs[c]["defense_composite"] for c in real])}
    for c in clubs:
        clubs[c]["offense_edge_part"] = slopes["offense"] * (clubs[c]["offense_composite"] - centre["offense"])
        clubs[c]["defense_edge_part"] = slopes["defense"] * (clubs[c]["defense_composite"] - centre["defense"])
    honoured = [pid for pid, v in values.items()]
    ids = {p["player_id"] for p in league["players"]}
    missing = sorted(values[p]["player"] for p in honoured if p not in ids)
    return {"as_of": league.get("as_of"), "honour_seasons": [2011, 2012], "centre": centre, "slopes_used": slopes,
            "edge_sd": {"offense": sd([clubs[c]["offense_edge_part"] for c in real]), "defense": sd([clubs[c]["defense_edge_part"] for c in real])},
            "clubs": clubs,
            "honoured_players": len(honoured), "honoured_not_in_league_database": missing}


def main():
    source, pbp12 = Path(sys.argv[1]), Path(sys.argv[2])
    pbp11 = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    main_study, rows12, _ = study(evidence, source, pbp12, 2012, [2010, 2011], "2012-09-05")
    primary = main_study["primary_week1_depth_starters"]["fits"]
    b_off, b_def = primary["offense_td"]["shrunk_slope"], primary["defense_td"]["shrunk_slope"]
    main_study["edge_report"] = {
        "shrunk_centred": edges(main_study, rows12, b_off, b_def),
        "shrunk_uncentred": edges(main_study, rows12, b_off, b_def, centred=False),
        "ols_centred": edges(main_study, rows12, primary["offense_td"]["slope"], primary["defense_td"]["slope"]),
        "target_edge_sd": 0.048,
        "target_components": {"offense": main_study["league"]["offense_td_sd"]["implied_true"],
                              "defense": main_study["league"]["defense_td_sd"]["implied_true"]},
    }
    main_study["influence"] = {"offense": influence(main_study, "offense", "off"), "defense": influence(main_study, "defense", "def")}
    temporal = None
    if pbp11:
        t, rows11, _ = study(evidence, source, pbp11, 2011, [2010], "2011-09-08")
        clubs = sorted(t["clubs"])
        for side, key in (("offense", "off"), ("defense", "def")):
            x = [t["clubs"][c][f"{side}_composite"] for c in clubs]
            y = [t["clubs"][c][f"{key}_td"] for c in clubs]
            slope = primary[f"{side}_td"]["shrunk_slope"] * (1 if side == "offense" else -1)
            pred = [slope * xi for xi in x]
            yc = [yi - mean(y) for yi in y]
            pc = [p - mean(pred) for p in pred]
            rmse = math.sqrt(mean([(a - b) ** 2 for a, b in zip(yc, pc)]))
            t[f"transfer_{side}"] = {"corr_composite_vs_td": corr(x, y), "rmse_with_2012_slope": rmse,
                                    "null_rmse": math.sqrt(mean([v * v for v in yc]))}
        temporal = {k: v for k, v in t.items() if k != "clubs"}
        temporal["club_composites"] = {c: [t["clubs"][c]["offense_composite"], t["clubs"][c]["defense_composite"]] for c in clubs}
    output = {
        "schema_version": 1,
        "built_by": "scripts/research/build_2014_strength_calibration.py",
        "policy": "runtime/2014_engine_decisions.md E1; user choice 'Honours + role'; runtime/defect_register.md item 1",
        "preregistered": PREREGISTERED,
        "sources": {**{name: {"url": url, "sha256": sha(source / name)} for name, url in SOURCES.items()},
                    "play_by_play_2012.csv.gz": {"url": PBP_URL.format(2012), "sha256": sha(pbp12)},
                    **({"play_by_play_2011.csv.gz": {"url": PBP_URL.format(2011), "sha256": sha(pbp11)}} if pbp11 else {}),
                    "honours_evidence": {"file": "library/data/2010_2012_honours_evidence.json", "sha256": sha(EVIDENCE)},
                    "league_players": {"file": "career/2014/offseason/league_rails/league_players.json", "sha256": sha(LEAGUE)}},
        "study_2012": main_study,
        "temporal_check_2011": temporal,
        "preview_2014": preview_2014(evidence, {"offense": b_off, "defense": b_def}),
    }
    OUT.write_text(json.dumps(output, indent=1, default=float) + "\n", encoding="utf-8")
    f = primary
    print(json.dumps({k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "loo"} | {"loo": {a: round(b, 4) for a, b in v["loo"].items()}}
                      for k, v in f.items()}, indent=1))
    print(json.dumps(main_study["edge_report"], indent=1, default=float))
    print(json.dumps(main_study["league"], indent=1))
    print(json.dumps(main_study["home_observation"], indent=1))


if __name__ == "__main__":
    main()
