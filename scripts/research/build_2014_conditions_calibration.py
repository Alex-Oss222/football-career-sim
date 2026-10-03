#!/usr/bin/env python3
"""Build the kernel 2014.6 conditions calibration, venues and climatology (plan batch B3d; data only).

  python scripts/research/build_2014_conditions_calibration.py [--sources DIR] [--check] [--jobs N]

Writes
  library/data/2014_conditions_calibration.json   pooled condition slopes, the keep rule, centres
  library/data/2014_venues.json                   static venue facts for the 2014 season
  library/data/2010_2013_venue_climatology.json   venue x month climatology (wind, cold)
and the generated tables of library/2014_context_and_conditions_calibration.md.

Sources come only through scripts/research/sources_2010_2014.py (the batch B2 gate): nflverse
play-by-play 2010-2013 and 2014 Weeks 1-4 (events, game conditions, venue facts), nflscrapR
reg_pbp for the same seasons (second pass, events only: nflscrapR carries no weather; it is
joined to the nflverse game conditions by its game id). Rules: library/2014_6_pre_build_
specification.md, section 4, Context and conditions (covariates, forms, the keep rule,
centring, the climatology basis).

Covariates per game: indoor (roof dome or closed); wind (outdoor mph, 0 indoor); cold
(max(0, 50 - temp F) / 10 outdoor, 0 indoor); alt (Denver's home venue); turf (surface not
grass); precip (the weather string names rain, snow, shower, drizzle, sleet, flurries or storm;
report only); tz_edge, alt_edge and body_edge as signed offense edges, 0 at neutral sites. An
outdoor game without temperature or wind leaves every weather model (counted).

Outcomes and forms (season fixed effects in every model; fixed effects are absorbed by
alternating updates and never stored):
- field-goal make: logit on kicker fixed effects with the kernel's distance model (the league
  base drive model's band intercept plus slope x distance) as an offset;
- punt gross: least squares on punts from yardline_100 >= 55 with yardline and punter fixed
  effects;
- kickoff touchback: logit on 2011-2014 Week 4 kickoffs from the 35, not onside, kicker fixed
  effects (applied by the kernel as a likelihood ratio on the kickoff record draw);
- drive touchdown share: logit with start-bin, home, offense club-season and defense
  club-season fixed effects;
- interception rate and passing-touchdown share: fitted, live only if kept; sack rate and
  yards: report only.

The keep rule: a preregistered sign, the full-sample sign, positive leave-one-stadium-out
skill, and the second pass reproducing both. Kept terms are refit jointly; a term whose joint
sign flips is dropped (lower single skill first). Altitude terms stay at slope 0 (decision
1B.2). Only pooled slopes are stored, with no club, kicker or punter fixed effect. Centres
are each outcome's mean covariate over its base events. A per-game list of condition tuples
(no identifiers) is stored for the centring sample.

--check rebuilds and compares: adopted sets and signs exactly, estimates within 1e-6
relative, the venue and climatology files byte-for-byte.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import multiprocessing
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library" / "data"
OUT = DATA / "2014_conditions_calibration.json"
VENUES = DATA / "2014_venues.json"
CLIMATE = DATA / "2010_2013_venue_climatology.json"
RECORD = ROOT / "library" / "2014_context_and_conditions_calibration.md"
DRIVE_MODEL = DATA / "2010_2014w4_nfl_drive_model.json"
FIELD_POSITION = DATA / "2010_2014w4_nfl_field_position_model.json"
SEASONS = (2010, 2011, 2012, 2013, 2014)
CLIMATE_SEASONS = (2010, 2011, 2012, 2013)
CONTEXT = lb.RULES["context"]
MIN_GAMES = lb.RULES["thresholds"]["CLIMATOLOGY_MIN_GAMES"]
PRECIP = re.compile(r"rain|snow|shower|drizzle|sleet|flurr|storm", re.I)
SCHEMA = "2014-conditions-calibration-v1"
MONTH_BINS = (("Sep-Oct", (9, 10)), ("Nov", (11,)), ("Dec-Jan", (12, 1)))
REL_TOL = 1e-6

# Club home time zones (static geography of each club's home city in 2010-2014; IANA names).
# The only typed facts here: categorical, not fitted, and read by tz_edge and body_edge only.
CLUB_TZ = {
    **{c: "America/New_York" for c in ("ATL", "BUF", "CAR", "CIN", "CLE", "DET", "IND", "JAX", "MIA", "NE", "NYG",
                                       "NYJ", "PHI", "PIT", "TB", "WAS", "BAL")},
    **{c: "America/Chicago" for c in ("CHI", "DAL", "GB", "HOU", "KC", "MIN", "NO", "TEN")},
    "STL": "America/Chicago", "DEN": "America/Denver", "ARI": "America/Phoenix",
    **{c: "America/Los_Angeles" for c in ("OAK", "SD", "SF", "SEA")},
}
ALIAS = {"JAC": "JAX", "LA": "STL", "LAC": "SD", "LV": "OAK", "SL": "STL"}


def club(code):
    return ALIAS.get(code, code)


# Preregistered signs (specification section 4; the design's preregistration).
TERMS = {
    "fg": {"wind_x": "-", "cold_x": "-", "indoor": "+", "alt": "+", "turf": "+", "precip": None},
    "punt": {"wind_x": "-", "cold_x": "-", "indoor": "+", "alt": "+"},
    "kickoff": {"wind_x": "-", "cold_x": "-", "indoor": "+", "alt": "+"},
    "drive": {"wind_x": "-", "cold_x": "-", "indoor": "+", "alt_edge": "+", "tz_edge": "+", "body_edge": "+",
              "turf": None, "precip": None},
    "int": {"wind_x": "+", "cold_x": "+", "indoor": "-"},
    "td": {"wind_x": "-", "cold_x": "-", "indoor": "+"},
    "sack": {"wind_x": None, "cold_x": None, "indoor": None},
    "pass_yds": {"wind_x": "-", "cold_x": "-", "indoor": "+", "turf": None},
    "rush_yds": {"wind_x": None, "cold_x": None, "indoor": None, "turf": None},
}
BINARY = {"fg", "kickoff", "drive", "int", "td", "sack"}
CHANNEL = {"fg": "live", "punt": "live", "kickoff": "live", "drive": "live", "int": "live if kept",
           "td": "live if kept", "sack": "report only", "pass_yds": "report only (no channel in the drive replay)",
           "rush_yds": "report only (no channel in the drive replay)"}
ALTITUDE = ("alt", "alt_edge")
# Outcomes whose terms go through leave-one-stadium-out (a preregistered sign and a channel).
LOSO = ("fg", "punt", "kickoff", "drive", "int", "td")


# ============================================================================ extraction

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def flag(r, k):
    return r.get(k) in ("1", "1.0")


def offset_hours(tz, day):
    return ZoneInfo(tz).utcoffset(datetime.fromisoformat(day + "T13:00:00")).total_seconds() / 3600


def game_conditions(season, dest):
    """nflverse game-level conditions (first row of each game), keyed by game id; also the
    mapping from the nflscrapR (old) game id."""
    games, old = {}, {}
    for r in sources.rows(lb.pbp_name(season, "nflverse"), dest):
        if r.get("season_type") != "REG" or r["game_id"] in games:
            continue
        roof = r.get("roof") or ""
        indoor = int(roof in ("dome", "closed"))
        temp, wind = num(r.get("temp")), num(r.get("wind"))
        neutral = int(r.get("location") == "Neutral")
        home, away = club(r["home_team"]), club(r["away_team"])
        day = r["game_date"]
        tz = 0.0 if neutral else abs(offset_hours(CLUB_TZ[home], day) - offset_hours(CLUB_TZ[away], day))
        start = (r.get("start_time") or "").split(", ")[-1]
        body = int(not neutral and CLUB_TZ[away] == "America/Los_Angeles" and start.startswith("13:"))
        g = {"season": season, "month": int(day[5:7]), "home": home, "away": away, "venue": r.get("stadium_id") or "",
             "venue_name": r.get("game_stadium") or r.get("stadium") or "", "roof": roof,
             "surface": r.get("surface") or "", "indoor": indoor, "neutral": neutral,
             "wx_missing": int(not indoor and (temp is None or wind is None)),
             "wind_x": 0.0 if indoor else (wind if wind is not None else 0.0),
             "cold_x": 0.0 if indoor else max(0.0, 50 - (temp if temp is not None else 50)) / 10.0,
             "alt": int(r["home_team"] == "DEN" and not neutral), "turf": int((r.get("surface") or "") != "grass"),
             "precip": int(bool(PRECIP.search(r.get("weather") or ""))), "tz_diff": tz, "body": body,
             "temp": temp, "wind": wind}
        g["group"] = g["venue"] + ("_N" if neutral else "")
        games[r["game_id"]] = g
        old[r.get("old_game_id") or ""] = r["game_id"]
    return games, old


KEEP_COLS = ("game_id", "season_type", "posteam", "defteam", "home_team", "yardline_100", "play_type", "desc",
             "field_goal_attempt", "field_goal_result", "kick_distance", "kicker_player_id", "punt_attempt",
             "punt_blocked", "punter_player_id", "kickoff_attempt", "touchback", "pass_attempt", "sack", "qb_spike",
             "qb_dropback", "qb_kneel", "rush_attempt", "interception", "touchdown", "td_team", "pass_touchdown",
             "rush_touchdown", "yards_gained", "down", "fixed_drive", "fixed_drive_result", "drive", "two_point_attempt")


def events(season, source, dest, games, old):
    """The outcome event tables of one season and source: each event is [game key, y, extras]."""
    out = {k: [] for k in TERMS}
    drives = collections.OrderedDict()
    for r in sources.rows(lb.pbp_name(season, source), dest):
        if source == "nflverse" and r.get("season_type") != "REG":
            continue
        gid = r["game_id"] if source == "nflverse" else old.get(r["game_id"])
        if gid is None or gid not in games:
            continue
        pt = r.get("play_type") or ""
        pos, dfn = club(r.get("posteam") or ""), club(r.get("defteam") or "")
        if flag(r, "two_point_attempt"):
            continue
        if flag(r, "field_goal_attempt") and r.get("field_goal_result") in ("made", "missed", "blocked") \
                and num(r.get("kick_distance")) is not None:
            out["fg"].append([gid, int(r["field_goal_result"] == "made"), num(r["kick_distance"]),
                              r.get("kicker_player_id") or "?"])
        if flag(r, "punt_attempt") and not flag(r, "punt_blocked") and (num(r.get("yardline_100")) or 0) >= \
                CONTEXT["punt_gross_min_yardline_100"] and num(r.get("kick_distance")) is not None:
            out["punt"].append([gid, num(r["kick_distance"]), num(r["yardline_100"]), r.get("punter_player_id") or "?"])
        if flag(r, "kickoff_attempt") and season >= 2011 and num(r.get("yardline_100")) == 35 \
                and "onside" not in (r.get("desc") or "").lower():
            out["kickoff"].append([gid, int(flag(r, "touchback")), r.get("kicker_player_id") or "?"])
        if pos and dfn and flag(r, "pass_attempt") and not flag(r, "sack") and not flag(r, "qb_spike"):
            out["int"].append([gid, int(flag(r, "interception")), "%s%d" % (pos, season), "%s%d" % (dfn, season)])
        if pos and dfn and flag(r, "qb_dropback") and not flag(r, "qb_spike"):
            out["sack"].append([gid, int(flag(r, "sack")), "%s%d" % (pos, season), "%s%d" % (dfn, season)])
            out["pass_yds"].append([gid, num(r.get("yards_gained")) or 0.0, "%s%d" % (pos, season),
                                    "%s%d" % (dfn, season)])
        if pos and dfn and flag(r, "rush_attempt") and not flag(r, "qb_kneel") and pt == "run":
            out["rush_yds"].append([gid, num(r.get("yards_gained")) or 0.0, "%s%d" % (pos, season),
                                    "%s%d" % (dfn, season)])
        if flag(r, "touchdown") and club(r.get("td_team") or "") == pos and pos \
                and (flag(r, "pass_touchdown") or flag(r, "rush_touchdown")):
            y100 = num(r.get("yardline_100")) or 0
            ybin = 0 if y100 <= 2 else 1 if y100 <= 5 else 2 if y100 <= 10 else 3 if y100 <= 20 else 4
            out["td"].append([gid, int(flag(r, "pass_touchdown")), ybin, "%s%d" % (pos, season)])
        # Drives: nflverse fixed_drive (its own result), nflscrapR drive (a touchdown by the offense).
        key = r.get("fixed_drive") if source == "nflverse" else r.get("drive")
        if pos and key not in (None, "", "NA"):
            d = drives.setdefault((gid, key), {"pos": pos, "dfn": dfn, "start": None, "td": 0, "result": None,
                                               "home": club(r.get("home_team") or "")})
            if d["start"] is None and pt in ("run", "pass", "punt", "field_goal", "qb_kneel", "qb_spike", "no_play") \
                    and r.get("down") not in ("", "NA", None) and club(r.get("posteam") or "") == d["pos"]:
                d["start"] = num(r.get("yardline_100"))
            if source == "nflverse":
                d["result"] = r.get("fixed_drive_result")
            elif flag(r, "touchdown") and club(r.get("td_team") or "") == d["pos"]:
                d["td"] = 1
    edges = (0, 19, 29, 39, 49, 59, 69, 79, 80, 89, 99)
    for (gid, _), d in drives.items():
        if d["start"] is None:
            continue
        y = int(d["result"] == "Touchdown") if source == "nflverse" else d["td"]
        sb = next(i for i in range(len(edges) - 1) if d["start"] <= edges[i + 1])
        g = games[gid]
        sign = 0 if g["neutral"] else (1 if d["pos"] == g["home"] else -1)
        out["drive"].append([gid, y, sb, int(d["pos"] == g["home"] and not g["neutral"]), sign,
                             "%s%d" % (d["pos"], season), "%s%d" % (d["dfn"], season)])
    return out


# ============================================================================ design matrices

def covariate(name, g, extra=None):
    if name == "alt_edge":
        return extra["sign"] * g["alt"]
    if name == "tz_edge":
        return extra["sign"] * g["tz_diff"]
    if name == "body_edge":
        return extra["sign"] * g["body"]
    return float(g[name])


def table(outcome, evs, games, distance_model=None):
    """(y, base covariates, fixed-effect dimensions, offsets, rows' games, term values)."""
    rows = []
    for e in evs:
        g = games[e[0]]
        if g["wx_missing"]:
            continue
        rows.append((e, g))
    y, X, fe, off, gl, extra = [], [], collections.defaultdict(list), [], [], []
    for e, g in rows:
        y.append(float(e[1]))
        off.append(0.0)
        gl.append(g)
        fe["season"].append(g["season"])
        ex = {"sign": 0}
        base = []
        if outcome == "fg":
            fe["kicker"].append(e[3])
            off[-1] = distance_model(e[2])
        elif outcome == "punt":
            fe["punter"].append(e[3])
            base.append(e[2])
        elif outcome == "kickoff":
            fe["kicker"].append(e[2])
        elif outcome == "drive":
            fe["start_bin"].append(e[2])
            base.append(float(e[3]))
            ex["sign"] = e[4]
            fe["off_cs"].append(e[5])
            fe["def_cs"].append(e[6])
        elif outcome in ("int", "sack", "pass_yds", "rush_yds"):
            fe["off_cs"].append(e[2])
            fe["def_cs"].append(e[3])
        elif outcome == "td":
            fe["ybin"].append(e[2])
            fe["off_cs"].append(e[3])
        X.append(base)
        extra.append(ex)
    terms = {t: [covariate(t, g, ex) for g, ex in zip(gl, extra)] for t in TERMS[outcome]}
    return {"y": y, "X": X, "fe": {k: encode(v) for k, v in fe.items()}, "off": off, "games": gl, "terms": terms,
            "groups": [g["group"] for g in gl]}


def encode(values):
    levels = {}
    return [levels.setdefault(v, len(levels)) for v in values], len(levels)


# ============================================================================ fits

def solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-300:
            raise ArithmeticError("singular")
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [v - f * w for v, w in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A)
    return [solve(A, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]


def fit(data, cols, rows=None, binary=True, start=None, max_iter=400, tol=1e-10, want_se=True):
    """Fixed-effects logit (binary) or least squares; fixed effects absorbed by alternating
    updates. cols: covariate columns (lists). rows: the training subset (indices) or None.
    Returns (beta, fe values, se of beta)."""
    idx = list(range(len(data["y"]))) if rows is None else rows
    y = [data["y"][i] for i in idx]
    off = [data["off"][i] for i in idx]
    Z = [[c[i] for c in cols] for i in idx]
    k = len(cols)
    dims = [(name, [codes[i] for i in idx], n) for name, (codes, n) in sorted(data["fe"].items())]
    beta = list(start[0]) if start else [0.0] * k
    a = {name: (list(start[1][name]) if start else [0.0] * n) for name, _, n in dims}
    if not binary and not start:
        mean_y = sum(y) / len(y)
        a[dims[0][0]] = [mean_y] * dims[0][2]
    m = len(y)
    eta = [off[i] + sum(beta[j] * Z[i][j] for j in range(k)) + sum(a[name][codes[i]] for name, codes, _ in dims)
           for i in range(m)]
    for it in range(max_iter):
        delta = 0.0
        for name, codes, n in dims:
            g, h = [0.0] * n, [0.0] * n
            if binary:
                for i in range(m):
                    p = 1 / (1 + math.exp(-eta[i]))
                    g[codes[i]] += y[i] - p
                    h[codes[i]] += p * (1 - p)
            else:
                for i in range(m):
                    g[codes[i]] += y[i] - eta[i]
                    h[codes[i]] += 1.0
            step = [0.0] * n
            for l in range(n):
                if h[l] > 1e-12:
                    s = g[l] / h[l]
                    s = max(-5.0, min(5.0, s))
                    if abs(a[name][l] + s) > 20:
                        s = math.copysign(20, a[name][l] + s) - a[name][l]
                    step[l] = s
            a[name] = [v + s for v, s in zip(a[name], step)]
            for i in range(m):
                eta[i] += step[codes[i]]
            delta = max(delta, max(abs(s) for s in step))
        if k:
            G = [0.0] * k
            H = [[0.0] * k for _ in range(k)]
            for i in range(m):
                if binary:
                    p = 1 / (1 + math.exp(-eta[i]))
                    r, w = y[i] - p, p * (1 - p)
                else:
                    r, w = y[i] - eta[i], 1.0
                zi = Z[i]
                for j in range(k):
                    G[j] += r * zi[j]
                    wz = w * zi[j]
                    Hj = H[j]
                    for l in range(j, k):
                        Hj[l] += wz * zi[l]
            for j in range(k):
                for l in range(j):
                    H[j][l] = H[l][j]
            step = solve(H, G)
            beta = [b + s for b, s in zip(beta, step)]
            for i in range(m):
                eta[i] += sum(step[j] * Z[i][j] for j in range(k))
            delta = max(delta, max(abs(s) for s in step))
        if delta < tol:
            break
    se = slope_se(Z, eta, y, dims, binary) if k and want_se else []
    return beta, a, se


def slope_se(Z, eta, y, dims, binary):
    """SE of the slopes with the fixed effects partialled out (weighted alternating projections)."""
    m, k = len(Z), len(Z[0])
    if binary:
        w = [(1 / (1 + math.exp(-e))) * (1 - 1 / (1 + math.exp(-e))) for e in eta]
    else:
        w = [1.0] * m
    Xt = [[Z[i][j] for i in range(m)] for j in range(k)]
    for j in range(k):
        col = Xt[j]
        for _ in range(100):
            change = 0.0
            for name, codes, n in dims:
                sw, sx = [0.0] * n, [0.0] * n
                for i in range(m):
                    sw[codes[i]] += w[i]
                    sx[codes[i]] += w[i] * col[i]
                mean = [sx[l] / sw[l] if sw[l] > 0 else 0.0 for l in range(n)]
                for i in range(m):
                    col[i] -= mean[codes[i]]
                change = max(change, max(abs(v) for v in mean))
            if change < 1e-10:
                break
    info = [[sum(w[i] * Xt[a][i] * Xt[b][i] for i in range(m)) for b in range(k)] for a in range(k)]
    inv = inverse(info)
    if binary:
        return [math.sqrt(max(inv[j][j], 0.0)) for j in range(k)]
    resid = sum((y[i] - eta[i]) ** 2 for i in range(m))
    dof = m - k - sum(n for _, _, n in dims)
    sigma2 = resid / max(dof, 1)
    return [math.sqrt(max(inv[j][j] * sigma2, 0.0)) for j in range(k)]


def predict(data, cols, beta, a, i):
    eta = data["off"][i] + sum(b * c[i] for b, c in zip(beta, cols))
    for name, (codes, _) in data["fe"].items():
        values = a[name]
        code = codes[i]
        eta += values[code] if code < len(values) else 0.0
    return eta


def loss(y, eta, binary):
    if binary:
        p = 1 / (1 + math.exp(-eta))
        p = min(max(p, 1e-12), 1 - 1e-12)
        return -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return (y - eta) ** 2


_FOLD = {}


def fold_group(group):
    data, base_cols, term_names, binary, start = _FOLD["args"]
    return fold((data, base_cols, term_names, group, binary, start))


def fold(args):
    """One held-out stadium: base and base+term losses on its rows (training on the rest)."""
    data, base_cols, term_names, group, binary, start = args
    train = [i for i, g in enumerate(data["groups"]) if g != group]
    test = [i for i, g in enumerate(data["groups"]) if g == group]
    seen = {name: {codes[i] for i in train} for name, (codes, _) in data["fe"].items()}

    def masked(a):
        out = {}
        for name, values in a.items():
            out[name] = [v if l in seen[name] else 0.0 for l, v in enumerate(values)]
        return out
    beta0, a0, _ = fit(data, base_cols, train, binary, start=start[None], max_iter=200, tol=1e-8, want_se=False)
    a0 = masked(a0)
    base_loss = sum(loss(data["y"][i], predict(data, base_cols, beta0, a0, i), binary) for i in test)
    out = {}
    for t in term_names:
        cols = base_cols + [data["terms"][t]]
        if len({data["terms"][t][i] for i in train}) < 2:
            # The term is constant without this stadium (a one-venue term held out): the
            # term model cannot be fitted, so it predicts as the base model does.
            out[t] = base_loss
            continue
        beta1, a1, _ = fit(data, cols, train, binary, start=start[t], max_iter=200, tol=1e-8, want_se=False)
        a1 = masked(a1)
        out[t] = sum(loss(data["y"][i], predict(data, cols, beta1, a1, i), binary) for i in test)
    return group, base_loss, out


def base_columns(data):
    k = len(data["X"][0]) if data["X"] else 0
    return [[row[j] for row in data["X"]] for j in range(k)]


def analyse_outcome(outcome, data, jobs):
    """Full-sample single-term fits, leave-one-stadium-out skill, per-season slopes and
    Cochran Q, and the joint refit of kept terms (pass-level; the cross-pass keep is applied
    by the caller)."""
    binary = outcome in BINARY
    base_cols = base_columns(data)
    full_base = fit(data, base_cols, None, binary, want_se=False)
    terms = {}
    starts = {None: (full_base[0], full_base[1])}
    for t in TERMS[outcome]:
        beta, a, se = fit(data, base_cols + [data["terms"][t]], None, binary,
                          start=(full_base[0] + [0.0], full_base[1]))
        terms[t] = {"slope": beta[-1], "se": se[-1]}
        starts[t] = (beta, a)
    loso_terms = [t for t in TERMS[outcome] if TERMS[outcome][t] is not None and outcome in LOSO]
    if loso_terms:
        groups = sorted(set(data["groups"]))
        if jobs > 1:
            _FOLD["args"] = (data, base_cols, loso_terms, binary, starts)
            with multiprocessing.get_context("fork").Pool(jobs) as pool:
                results = pool.map(fold_group, groups, chunksize=1)
            _FOLD.clear()
        else:
            results = [fold((data, base_cols, loso_terms, g, binary, starts)) for g in groups]
        base_total = sum(r[1] for r in results)
        for t in loso_terms:
            terms[t]["loso_skill"] = 1 - sum(r[2][t] for r in results) / base_total
        n_groups = len(groups)
    else:
        n_groups = len(set(data["groups"]))
    # Per-season slopes and Cochran's Q.
    for t in TERMS[outcome]:
        per = {}
        for s in SEASONS:
            rows = [i for i, g in enumerate(data["games"]) if g["season"] == s]
            col = data["terms"][t]
            if len(rows) < 30 or len({col[i] for i in rows}) < 2:
                continue
            try:
                beta, _, se = fit(data, base_cols + [col], rows, binary, max_iter=300, tol=1e-8)
            except ArithmeticError:
                continue
            if se[-1] > 0:
                per[lb.TAG[s]] = [beta[-1], se[-1]]
        terms[t]["per_season"] = per
        if len(per) >= 2:
            ws = [(b, 1 / se ** 2) for b, se in per.values()]
            mean = sum(b * w for b, w in ws) / sum(w for _, w in ws)
            q = sum(w * (b - mean) ** 2 for b, w in ws)
            df = len(ws) - 1
            terms[t]["cochran_q"] = {"q": q, "df": df, "p": lb.chi2_p(q, df), "unstable": lb.chi2_p(q, df) < 0.01}
    means = {t: sum(data["terms"][t]) / len(data["terms"][t]) for t in TERMS[outcome]}
    return {"rows": len(data["y"]), "groups": n_groups, "mean_y": sum(data["y"]) / len(data["y"]),
            "base_slopes": full_base[0], "terms": terms, "centres": means}


def keep_terms(outcome, a, b):
    """The keep rule across both passes (joint refit happens after)."""
    kept = []
    for t, sign in TERMS[outcome].items():
        if sign is None or outcome not in LOSO:
            continue
        ok = True
        for res in (a, b):
            term = res["terms"][t]
            right = term["slope"] < 0 if sign == "-" else term["slope"] > 0
            ok = ok and right and term.get("loso_skill", -1) > 0
        if ok:
            kept.append(t)
    return kept


def joint(outcome, data, kept, single_skill):
    """Refit kept terms jointly; drop a term whose joint sign flips (lower single skill first)."""
    binary = outcome in BINARY
    base_cols = base_columns(data)
    kept = list(kept)
    dropped = []
    while kept:
        beta, _, se = fit(data, base_cols + [data["terms"][t] for t in kept], None, binary)
        slopes = dict(zip(kept, zip(beta[len(base_cols):], se[len(base_cols):])))
        flipped = [t for t in kept if (slopes[t][0] < 0) != (TERMS[outcome][t] == "-")]
        if not flipped:
            return {t: list(v) for t, v in slopes.items()}, dropped
        worst = min(flipped, key=lambda t: single_skill[t])
        kept.remove(worst)
        dropped.append(worst)
    return {}, dropped


# ============================================================================ venues and climatology

def venues_and_climate(games_by_season):
    games = [g for s in SEASONS for g in games_by_season[s].values()]
    venue = collections.defaultdict(lambda: {"names": collections.Counter(), "roof": collections.Counter(),
                                             "surface": collections.Counter(), "home": collections.Counter(),
                                             "seasons": set(), "neutral": 0, "games": 0})
    for g in games:
        v = venue[g["venue"]]
        v["names"][g["venue_name"]] += 1
        v["roof"][g["roof"]] += 1
        v["surface"][g["surface"]] += 1
        v["seasons"].add(g["season"])
        v["games"] += 1
        if g["neutral"]:
            v["neutral"] += 1
        else:
            v["home"][g["home"]] += 1
    out = {}
    for vid, v in sorted(venue.items()):
        roofs = set(v["roof"])
        retractable = bool(roofs & {"open", "closed"})
        home = v["home"].most_common(1)[0][0] if v["home"] else None
        out[vid] = {
            "name_in_source": v["names"].most_common(1)[0][0],
            "roof": v["roof"].most_common(1)[0][0], "retractable": retractable,
            "closed_share_2010_2013": None, "surface": v["surface"].most_common(1)[0][0],
            "turf": int(v["surface"].most_common(1)[0][0] != "grass"),
            "altitude": int(home == "DEN"), "home_club": home,
            "timezone": CLUB_TZ.get(home) if home else None,
            "neutral_site": bool(v["neutral"] and not v["home"]),
            "seasons": [lb.TAG[s] for s in sorted(v["seasons"])], "games": v["games"],
        }
        closed = [g for g in games if g["venue"] == vid and g["season"] in CLIMATE_SEASONS]
        if retractable and closed:
            out[vid]["closed_share_2010_2013"] = sum(g["roof"] == "closed" for g in closed) / len(closed)
    # The 2014 home venue of each club: its latest home venue in the base (2014 Weeks 1-4 first).
    home_2014 = {}
    for s in (2013, 2014):
        for g in games_by_season[s].values():
            if not g["neutral"]:
                home_2014[g["home"]] = g["venue"]
    venues = {
        "schema": "2014-venues-v1",
        "builder": "scripts/research/build_2014_conditions_calibration.py",
        "specification_sha256": pre_build_specification.digest(),
        "basis": "Static venue facts from the nflverse play-by-play game rows 2010-2013 and 2014 Weeks 1-4 (roof, "
                 "surface, venue id, the name as the source spells it today), the Denver altitude flag, and each "
                 "club's home time zone (static geography). A venue whose roof is recorded open or closed is "
                 "retractable; its 2010-2013 closed share weights the climatology (specification section 4). No "
                 "2014 weather is read at runtime (decision 1B.3).",
        "venues": out,
        "club_home_venue_2014": dict(sorted(home_2014.items())),
        "club_timezone": dict(sorted(CLUB_TZ.items())),
    }
    # Climatology: outdoor (and open-roof) non-neutral 2010-2013 games with temp and wind.
    def mbin(month):
        return next(label for label, months in MONTH_BINS if month in months)
    cells = collections.defaultdict(list)
    league = collections.defaultdict(list)
    allseason = collections.defaultdict(list)
    for g in games:
        if g["season"] not in CLIMATE_SEASONS or g["indoor"] or g["neutral"] or g["wx_missing"]:
            continue
        cells[(g["venue"], mbin(g["month"]))].append(g)
        league[mbin(g["month"])].append(g)
        allseason[g["venue"]].append(g)

    def means(gs):
        return {"games": len(gs), "wind_x": sum(g["wind_x"] for g in gs) / len(gs),
                "cold_x": sum(g["cold_x"] for g in gs) / len(gs)}
    league_means = {b: means(gs) for b, gs in league.items()}
    all_league = means([g for gs in league.values() for g in gs])
    climate_venues = {}
    for vid in sorted(out):
        row = {}
        for label, _ in MONTH_BINS:
            gs = cells.get((vid, label), [])
            if len(gs) >= MIN_GAMES:
                row[label] = dict(means(gs), basis="venue cell")
            elif allseason.get(vid):
                base = means(allseason[vid])
                row[label] = {"games": len(gs), "basis": "convention: venue all-season mean plus the league month offset",
                              "wind_x": base["wind_x"] + league_means[label]["wind_x"] - all_league["wind_x"],
                              "cold_x": max(0.0, base["cold_x"] + league_means[label]["cold_x"] - all_league["cold_x"])}
            else:
                row[label] = {"games": 0, "basis": "convention: no 2010-2013 outdoor game at the venue; the league cell",
                              "wind_x": league_means[label]["wind_x"], "cold_x": league_means[label]["cold_x"]}
        climate_venues[vid] = row
    climate = {
        "schema": "2010-2013-venue-climatology-v1",
        "builder": "scripts/research/build_2014_conditions_calibration.py",
        "specification_sha256": pre_build_specification.digest(),
        "source": "nflverse 2010-2013 regular-season game conditions (roof, temp, wind), outdoor or open-roof "
                  "non-neutral games with both temp and wind",
        "month_bins": [label for label, _ in MONTH_BINS],
        "min_games_rule": "a venue-month cell with fewer than %d games uses the venue's all-season mean plus the league "
                          "month offset (a labelled convention); a venue with no such game uses the league cell" % MIN_GAMES,
        "retractable_rule": "a retractable roof applies (1 - closed share) x these open-roof means (2014_venues.json)",
        "league": league_means,
        "venues": climate_venues,
    }
    return venues, climate


# ============================================================================ build

def distance_logit():
    model = json.loads(DRIVE_MODEL.read_text())["field_goal_distance"]
    bands = sorted(((b["low"], b["high"], b["intercept"]) for b in model["bands"].values()))
    slope = model["slope_per_yard"]

    def logit(d):
        intercept = bands[-1][2]
        for low, high, a in bands:
            if d <= high:
                intercept = a
                break
        return intercept + slope * d
    return logit


def build(dest, jobs=1, log=print):
    games_by_season, old_by_season = {}, {}
    for s in SEASONS:
        games_by_season[s], old_by_season[s] = game_conditions(s, dest)
    games = {k: v for s in SEASONS for k, v in games_by_season[s].items()}
    logit = distance_logit()
    results = {}
    tables = {}
    for source in lb.SOURCES:
        evs = {k: [] for k in TERMS}
        for s in SEASONS:
            log("conditions events %s %s" % (source, lb.TAG[s]))
            part = events(s, source, dest, games_by_season[s], old_by_season[s])
            for k in TERMS:
                evs[k] += part[k]
        tables[source] = {k: table(k, evs[k], games, logit) for k in TERMS}
        results[source] = {}
        for outcome in TERMS:
            log("conditions fit %s %s" % (source, outcome))
            results[source][outcome] = analyse_outcome(outcome, tables[source][outcome], jobs)
    outcomes = {}
    for outcome in TERMS:
        a, b = results["nflverse"][outcome], results["nflscrapr"][outcome]
        kept = keep_terms(outcome, a, b)
        single = {t: a["terms"][t].get("loso_skill", -1) for t in kept}
        joint_a, dropped = joint(outcome, tables["nflverse"][outcome], kept, single)
        joint_b, _ = joint(outcome, tables["nflscrapr"][outcome], [t for t in kept if t not in dropped], single)
        adopted = sorted(joint_a)
        live = {t: (0.0 if t in ALTITUDE else joint_a[t][0]) for t in adopted}
        outcomes[outcome] = {
            "channel": CHANNEL[outcome], "rows_pass1": a["rows"], "rows_pass2": b["rows"],
            "stadium_groups": a["groups"], "mean_y_pass1": a["mean_y"], "mean_y_pass2": b["mean_y"],
            "terms": {t: {"sign": TERMS[outcome][t], "pass1": a["terms"][t], "pass2": b["terms"][t]}
                      for t in TERMS[outcome]},
            "kept_by_rule": kept, "dropped_joint_flip": dropped, "adopted": adopted,
            "joint_pass1": joint_a, "joint_pass2": joint_b,
            "live_slopes": live if CHANNEL[outcome].startswith("live") else {},
            "altitude_at_slope_0": [t for t in adopted if t in ALTITUDE],
            "centres": a["centres"],
        }
    venues, climate = venues_and_climate(games_by_season)
    raw = raw_bins(tables["nflverse"], None)
    base_games = [[g["season"], g["indoor"], round(g["wind_x"], 3), round(g["cold_x"], 4), g["alt"], g["turf"],
                   g["precip"], g["neutral"], g["tz_diff"], g["body"], g["wx_missing"]]
                  for gid, g in sorted(games.items())]
    base_games.sort()
    artifact = {
        "schema": SCHEMA,
        "builder": "scripts/research/build_2014_conditions_calibration.py",
        "specification_sha256": pre_build_specification.digest(),
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; pooled slopes only (no club, kicker or punter fixed effect "
                                 "stored); no club, game, player or date field."),
        "league_base": {"field_position": {"file": str(FIELD_POSITION.relative_to(ROOT)),
                                           "sha256": sources.sha256_file(FIELD_POSITION)},
                        "drive_model": {"file": str(DRIVE_MODEL.relative_to(ROOT)),
                                        "sha256": sources.sha256_file(DRIVE_MODEL)}},
        "sources": {name: {"sha256": sources.load_manifest()["assets"][name]["sha256"]}
                    for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"))},
        "covariates": {
            "indoor": "roof dome or closed (an open retractable counts as outdoor)",
            "wind_x": "outdoor wind mph; 0 indoor",
            "cold_x": "max(0, %d - temp F) / %d outdoor; 0 indoor" % (CONTEXT["cold_reference_f"], CONTEXT["cold_scale_f"]),
            "alt": "a game at Denver's home venue", "turf": "surface not grass",
            "precip": "the weather string mentions rain, snow, shower, drizzle, sleet, flurries or storm (report only)",
            "tz_edge": "|home-club UTC offset - visiting-club UTC offset| hours, +1 home offense / -1 visiting offense; "
                       "0 at neutral sites",
            "alt_edge": "+1 Denver offense at home, -1 visiting offense at Denver",
            "body_edge": "visiting club in Pacific time and a 13:00 ET start, +1 home offense / -1 visiting offense",
            "missing": "an outdoor game without temp or wind leaves every weather model",
        },
        "games": {"total": len(games), "outdoor_missing_weather": sum(g["wx_missing"] for g in games.values()),
                  "indoor": sum(g["indoor"] for g in games.values()), "neutral": sum(g["neutral"] for g in games.values()),
                  "denver_home": sum(g["alt"] for g in games.values())},
        "keep_rule": CONTEXT["keep_rule"] + "; kept terms refit jointly, a term whose joint sign flips dropped (lower "
                                            "single skill first); altitude terms at slope 0 (decision 1B.2)",
        "centring": "a shift is slope x (x - the centre), the centre being the outcome's mean covariate over its base "
                    "events (pass 1), so the league mean stays on the base",
        "default_basis": CONTEXT["default_basis"], "observed_weather": CONTEXT["observed_weather"],
        "outcomes": outcomes,
        "centring_sample": {"fields": ["season", "indoor", "wind_x", "cold_x", "alt", "turf", "precip", "neutral",
                                       "tz_diff", "body", "wx_missing"],
                            "games": base_games},
        "raw_kickoff_touchback_by_cold_excluding_denver": raw,
        "plan_and_defensive_calls": "The offense plan test is reported only and cannot be adopted in 2014.6; defensive "
                                    "records label each snap with Stone's sheet (decision 1B.5): nothing here.",
    }
    return artifact, venues, climate


# ============================================================================ check, record

def compare(a, b, path=""):
    """Errors between two artifacts: adopted sets and signs exact, numbers within REL_TOL."""
    errors = []
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            errors.append("%s keys differ" % path)
        for k in set(a) & set(b):
            errors += compare(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            errors.append("%s lengths differ" % path)
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                errors += compare(x, y, "%s[%d]" % (path, i))
    elif isinstance(a, float) or isinstance(b, float):
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            errors.append("%s type differs" % path)
        elif abs(a - b) > REL_TOL * max(1.0, abs(a), abs(b)):
            errors.append("%s %r != %r" % (path, a, b))
    elif a != b:
        errors.append("%s %r != %r" % (path, a, b))
    return errors


BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def tables_md(art, games_by_season=None):
    lines = ["Generated by `scripts/research/build_2014_conditions_calibration.py` from the artifact; do not edit.", ""]
    lines.append("| Outcome | Channel | Rows (pass 1 / 2) | Kept by rule | Adopted | Live slopes |")
    lines.append("|---|---|---|---|---|---|")
    for name, o in art["outcomes"].items():
        lines.append("| %s | %s | %d / %d | %s | %s | %s |" % (
            name, o["channel"], o["rows_pass1"], o["rows_pass2"], ", ".join(o["kept_by_rule"]) or "none",
            ", ".join(o["adopted"]) or "none",
            ", ".join("%s %+.5f" % kv for kv in sorted(o["live_slopes"].items())) or "none"))
    lines += ["", "| Outcome | Term | Sign | Pass 1 slope (SE) | Pass 1 LOSO skill | Pass 2 slope | Pass 2 LOSO skill | "
                  "Cochran Q p (pass 1) |", "|---|---|---|---|---|---|---|---|"]
    for name, o in art["outcomes"].items():
        for t, v in o["terms"].items():
            p1, p2 = v["pass1"], v["pass2"]
            q = p1.get("cochran_q")
            lines.append("| %s | %s | %s | %+.5f (%.5f) | %s | %+.5f | %s | %s |" % (
                name, t, v["sign"] or "report", p1["slope"], p1["se"],
                "%+.5f" % p1["loso_skill"] if "loso_skill" in p1 else "-", p2["slope"],
                "%+.5f" % p2["loso_skill"] if "loso_skill" in p2 else "-",
                ("%.4f%s" % (q["p"], " (unstable)" if q["unstable"] else "")) if q else "-"))
    raw = art.get("raw_kickoff_touchback_by_cold_excluding_denver")
    if raw:
        lines += ["", "Kickoff touchback share by cold bin, Denver home games excluded (raw, pass 1): " + "; ".join(
            "%s %d/%d = %.3f" % (label, k, n, k / n if n else float("nan")) for label, k, n in raw) + "."]
    g = art["games"]
    lines += ["", "Games: %d (indoor %d, neutral %d, Denver home %d); outdoor games without temp or wind, dropped from "
                  "every weather model: %d." % (g["total"], g["indoor"], g["neutral"], g["denver_home"],
                                                g["outdoor_missing_weather"])]
    return "\n".join(lines) + "\n"


def raw_bins(tables_p1, art):
    data = tables_p1["kickoff"]
    bins = (("cold 0 (50F+)", 0, 0), ("40-49F", 1e-9, 1.0), ("30-39F", 1.0 + 1e-9, 2.0), ("20-29F", 2.0 + 1e-9, 3.0),
            ("below 20F", 3.0 + 1e-9, 1e9))
    out = []
    for label, lo, hi in bins:
        rows = [i for i, g in enumerate(data["games"]) if not g["alt"] and lo <= g["cold_x"] <= hi]
        out.append([label, int(sum(data["y"][i] for i in rows)), len(rows)])
    return out


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    art, venues, climate = build(args.sources, args.jobs, log=lambda m: print(m, file=sys.stderr, flush=True))
    record = None
    if RECORD.exists():
        text = RECORD.read_text()
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        record = head + BEGIN + "\n" + tables_md(art) + END + tail
    if args.check:
        failed = False
        current = json.loads(OUT.read_text()) if OUT.exists() else {}
        errors = compare(current, art)
        for e in errors[:20]:
            print("DIFFERS " + e)
        failed |= bool(errors)
        for path, obj in ((VENUES, venues), (CLIMATE, climate)):
            ok = path.exists() and path.read_text() == render(obj)
            print("%s %s" % ("reproduced" if ok else "DIFFERS", path.relative_to(ROOT)))
            failed |= not ok
        if record is not None:
            ok = RECORD.read_text() == record
            print("%s %s (generated tables)" % ("reproduced" if ok else "DIFFERS", RECORD.relative_to(ROOT)))
            failed |= not ok
        print("%s %s (within %g relative)" % ("DIFFERS" if errors else "reproduced", OUT.relative_to(ROOT), REL_TOL))
        return 1 if failed else 0
    OUT.write_text(render(art))
    VENUES.write_text(render(venues))
    CLIMATE.write_text(render(climate))
    if record is not None:
        RECORD.write_text(record)
    print("wrote %s, %s, %s" % (OUT.relative_to(ROOT), VENUES.relative_to(ROOT), CLIMATE.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
