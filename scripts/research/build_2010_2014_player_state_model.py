#!/usr/bin/env python3
"""The 2010-2014 player-state model, pass 1 (kernel 2014.6, plan batch B4b; data only).

  python scripts/research/build_2010_2014_player_state_model.py [--sources DIR] [--check]

Writes, from the gated sources (scripts/research/sources_2010_2014.py) and the branch
identity table (career/2014/League/personnel/branch_identity.json):
- library/data/2010_2014_player_state_model.json     the fitted model (aggregates only)
- library/data/2014_player_state_public.json         per gsis: record family, basis, the
                                                     public expectations m_b, m_u and P
- library/data/2014_player_state_manifest.json       digests and the derivation tag
and the generated tables of library/2010_2014_player_state_study.md. Nothing in runtime/
reads these until batch B7. Stdlib only.

Policy (runtime/2014_engine_decisions.md, "The player-state policy (A to D)"): hidden-state
statistical priors for the engine only, never scouting evidence or a staff-facing grade.
A real player's own 2013-2014 statistics never set his own value: the public table uses
each player's 2010-2012 lines only, and 2013 and 2014 Weeks 1-4 enter the pooled fits as an
anonymous league population. Staff assessments, grades and E2 advice never read any of it.

U5 is unanswered (specification section 4, Player states), so this build uses the plan's
fallback: zero aging for every family (candidate Z) and flat rookie estimates (draft-slot
slope 0). The rules resting on amendments 2 and 3 that the fallback does not name are
held, never replaced: the 30-event minimum cell, the tier population on the qualifier
floors (no tiers are produced) and the DL and LB carry from pass 1 (a DL or LB family
whose swing the two passes disagree on, so that amendment 3 would decide it, is held). Fitted values the fallback sets aside (the
draft-slot slopes) are reported, not applied.

Model, per family (QB, RB, WR, TE, DL, LB, DB, K, P, KR, PR; offensive linemen have no
public performance rate and no state):
- a player-season line is the family's rate (specification metrics) centred on that
  season's opportunity-weighted league mean over floor qualifiers, with noise variance
  sigma2 / n, sigma2 from the within-season split-half moment (odd and even games);
- the true state is x = b + u: b persistent, u a stationary AR(1) swing with variance su2
  and carry rho; lag-k covariance C_k = sb2 + rho^k su2 over lags 0-4, fitted by weighted
  least squares on a 0.01 grid of rho; the 2013-to-2014 Weeks 1-4 pair is held out;
- the swing is kept only if su2's bootstrap 95% interval (200 resamples of players)
  excludes 0 in both passes; its size is pass 1's when pass 2's point lies inside pass 1's
  interval (Confirmed two-pass), otherwise the smaller point (Reconciled down, flagged);
- the public expectations come from a two-state Kalman filter over the player's own
  2010-2012 lines, started from the draft-slot prior (drafted or undrafted family means,
  each player's own class left out) or, for a veteran entering before 2010, from the
  population N(0, diag(sb2, su2)); an admissible honour (AP All-Pro or original Pro Bowl,
  public before the cutoff) enters as a pseudo-observation split by the Kalman gain, with
  EVIDENCE_WEIGHT 1.0 (Confirmed two-pass) or 0.5 (Single-pass); the record family is the
  family holding most of his 2010-2012 opportunities (latest season breaks ties).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library/data"
MODEL_OUT = DATA / "2010_2014_player_state_model.json"
PUBLIC_OUT = DATA / "2014_player_state_public.json"
MANIFEST_OUT = DATA / "2014_player_state_manifest.json"
STUDY = ROOT / "library/2010_2014_player_state_study.md"
IDENTITY = ROOT / "career/2014/League/personnel/branch_identity.json"
HONOURS = DATA / "2010_2012_honours_evidence.json"
RULES = pre_build_specification.frozen_rules()
PS = RULES["player_state"]
CUT = RULES["data_window"]["cut_2014"]
SCHEMA_MODEL = "2010-2014-player-state-model-v1"
SCHEMA_PUBLIC = "2014-player-state-public-v1"
SCHEMA_MANIFEST = "2014-player-state-manifest-v1"
DERIVATION = "player-state-v1"
SEASONS = (2010, 2011, 2012, 2013, 2014)
RECORD_SEASONS = (2010, 2011, 2012)
FAMILIES = ("QB", "RB", "WR", "TE", "DL", "LB", "DB", "K", "P", "KR", "PR")
POSITION_FAMILIES = ("QB", "RB", "WR", "TE", "DL", "LB", "DB", "K", "P")
RETURN_FAMILIES = ("KR", "PR")
FLOORS = PS["fit_floors"]
LAGS = tuple(PS["swing_lags"])
RHO_GRID = tuple(round(i * PS["rho_grid_step"], 2) for i in range(int(round(1 / PS["rho_grid_step"]))))
BOOT = PS["bootstrap_resamples"]
EVIDENCE_WEIGHT = PS["evidence_weight"]
HELD_OUT_PAIR = (2013, 2014)
FG_BANDS = ("0_19", "20_29", "30_39", "40_49", "50_59", "60_")
HONOUR_KINDS = ("AP1", "AP2", "PB")
AGE_ON = date(2014, 9, 1)
METRICS = {
    "QB": "EPA per dropback (passing_epa over attempts plus sacks), weekly statistics",
    "RB": "EPA per opportunity (rushing plus receiving EPA over carries plus targets), weekly statistics",
    "WR": "EPA per opportunity (rushing plus receiving EPA over carries plus targets), weekly statistics",
    "TE": "EPA per opportunity (rushing plus receiving EPA over carries plus targets), weekly statistics",
    "DL": "disruption per game: sacks + 0.5 QB hits + tackles for loss + interceptions + 0.5 passes defended "
          "(tackles for loss from the play-by-play every season); games with a recorded statistic",
    "LB": "disruption per game, as DL",
    "DB": "disruption per game, as DL",
    "K": "field goals made over expected per attempt (expected: that season's league make rate by distance band)",
    "P": "net yards per punt (pt_net_yards over pt_att, weekly statistics)",
    "KR": "kickoff return yards per return",
    "PR": "punt return yards per return",
}
HONOUR_FAMILY = {"KR": "KR", "PR": "PR"}


def family_of_position(position):
    group = lb.GROUP.get((position or "").strip().upper())
    return group if group in POSITION_FAMILIES else group


def num(value):
    try:
        return float(value) if value not in ("", "NA", None) else 0.0
    except ValueError:
        return 0.0


def seed_of(label):
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


# ====================================================================== extraction (pass 1)
def assert_cut(season, week, game_date=None):
    """The 2014 date check (players review R16): week <= 4 and game date <= 2014-09-29, asserted
    again in the builder on top of the source gate. A game id's date part is not a date; only an
    ISO date is compared."""
    if season == 2014:
        if week is not None and int(week) > CUT["max_week"]:
            raise ValueError("a 2014 row after Week %d reached the player-state build" % CUT["max_week"])
        if game_date and len(game_date) == 10 and game_date[4] == "-" and game_date > CUT["max_game_date"]:
            raise ValueError("a 2014 row dated %s reached the player-state build" % game_date)


def _tfl_by_week(season, dest):
    """{(gsis, week): tackles for loss} from the nflverse play-by-play (two-point tries excluded)."""
    out = Counter()
    for r in sources.rows(lb.pbp_name(season, "nflverse"), dest):
        if r.get("season_type") != "REG" or r.get("two_point_attempt") == "1":
            continue
        assert_cut(season, r.get("week"), r.get("game_date"))
        for col in ("tackle_for_loss_1_player_id", "tackle_for_loss_2_player_id"):
            pid = r.get(col)
            if pid and pid != "NA":
                out[(pid, int(r["week"]))] += 1
    return out


def extract_pass1(dest, log=print):
    """raw[(family, gsis, season)] = {"weeks": {week: [n, s]}, "clubs": Counter}; K rows carry band counts."""
    raw = {}
    kbands = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # season -> band -> [made, att]
    kweeks = defaultdict(lambda: defaultdict(dict))             # (gsis, season) -> week -> band -> [made, att]
    for season in SEASONS:
        log("player states pass 1: %s" % lb.TAG[season])
        pos = lb.positions(season, dest)
        tfl = _tfl_by_week(season, dest)
        used_tfl = set()
        name = "stats_player_week_2014w4.csv" if season == 2014 else "stats_player_week_%d.csv" % season
        for r in sources.rows(name, dest):
            if r.get("season_type") != "REG":
                continue
            pid, week, club = r["player_id"], int(r["week"]), r.get("team") or ""
            assert_cut(season, week, r.get("game_id"))
            fam = family_of_position(pos.get(pid))

            def add(family, n, s):
                if n <= 0:
                    return
                acc = raw.setdefault((family, pid, season), {"weeks": {}, "clubs": Counter()})
                w = acc["weeks"].setdefault(week, [0.0, 0.0])
                w[0] += n
                w[1] += s
                acc["clubs"][club] += n

            if fam == "QB":
                add("QB", num(r["attempts"]) + num(r["sacks_suffered"]), num(r["passing_epa"]))
            elif fam in ("RB", "WR", "TE"):
                add(fam, num(r["carries"]) + num(r["targets"]), num(r["rushing_epa"]) + num(r["receiving_epa"]))
            elif fam in ("DL", "LB", "DB"):
                stats = (num(r["def_tackles_solo"]) + num(r["def_tackles_with_assist"]) + num(r["def_tackle_assists"])
                         + num(r["def_sacks"]) + num(r["def_qb_hits"]) + num(r["def_interceptions"])
                         + num(r["def_pass_defended"]) + num(r["def_fumbles_forced"]))
                t = tfl.get((pid, week), 0)
                if stats > 0 or t:
                    used_tfl.add((pid, week))
                    add(fam, 1.0, num(r["def_sacks"]) + 0.5 * num(r["def_qb_hits"]) + t
                        + num(r["def_interceptions"]) + 0.5 * num(r["def_pass_defended"]))
            elif fam == "K":
                bands = {}
                for b in FG_BANDS:
                    made = num(r["fg_made_" + b])
                    att = made + num(r["fg_missed_" + b])
                    if att:
                        bands[b] = [made, att]
                        kbands[season][b][0] += made
                        kbands[season][b][1] += att
                if bands:
                    kweeks[(pid, season)][week] = bands
                    acc = raw.setdefault(("K", pid, season), {"weeks": {}, "clubs": Counter()})
                    acc["clubs"][club] += sum(a for _, a in bands.values())
            elif fam == "P":
                add("P", num(r["pt_att"]), num(r["pt_net_yards"]))
            add("KR", num(r["kickoff_returns"]), num(r["kickoff_return_yards"]))
            add("PR", num(r["punt_returns"]), num(r["punt_return_yards"]))
        for (pid, week), t in sorted(tfl.items()):
            if (pid, week) in used_tfl:
                continue
            fam = family_of_position(pos.get(pid))
            if fam in ("DL", "LB", "DB"):
                acc = raw.setdefault((fam, pid, season), {"weeks": {}, "clubs": Counter()})
                w = acc["weeks"].setdefault(week, [0.0, 0.0])
                w[0] += 1.0
                w[1] += t
    for (pid, season), weeks in kweeks.items():
        rate = {b: (m / a if a else 0.0) for b, (m, a) in kbands[season].items()}
        acc = raw[("K", pid, season)]
        for week, bands in weeks.items():
            att = sum(a for _, a in bands.values())
            made = sum(m for m, _ in bands.values())
            exp = sum(a * rate[b] for b, (_, a) in bands.items())
            acc["weeks"][week] = [att, made - exp]
    return raw


# ====================================================================== lines
def season_lines(raw, floors=FLOORS, split="parity"):
    """lines[family][(gsis, season)] = {n, rate, y, R, halves, club}; plus centres and noise by family-season."""
    by_fs = defaultdict(dict)
    for (fam, pid, season), acc in raw.items():
        weeks = sorted(acc["weeks"].items())
        n = sum(v[0] for _, v in weeks)
        if n <= 0:
            continue
        s = sum(v[1] for _, v in weeks)
        if split == "parity":
            a = [v for i, (_, v) in enumerate(weeks) if i % 2 == 0]
            b = [v for i, (_, v) in enumerate(weeks) if i % 2 == 1]
        else:  # chronological halves (pass 2)
            h = (len(weeks) + 1) // 2
            a = [v for _, v in weeks[:h]]
            b = [v for _, v in weeks[h:]]
        club = sorted(acc["clubs"].items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if acc["clubs"] else ""
        by_fs[(fam, season)][pid] = {"n": n, "s": s, "a": (sum(x[0] for x in a), sum(x[1] for x in a)),
                                     "b": (sum(x[0] for x in b), sum(x[1] for x in b)), "club": club}
    lines = {f: {} for f in FAMILIES}
    centres, noise = {}, {}
    for (fam, season), players in sorted(by_fs.items()):
        q = {p: v for p, v in players.items() if v["n"] >= floors[fam]}
        tot_n = sum(v["n"] for v in q.values())
        centre = sum(v["s"] for v in q.values()) / tot_n if tot_n else 0.0
        terms = []
        for v in q.values():
            (na, sa), (nb, sb) = v["a"], v["b"]
            if na > 0 and nb > 0:
                terms.append((sa / na - sb / nb) ** 2 / (1 / na + 1 / nb))
        sigma2 = sum(terms) / len(terms) if terms else 0.0
        centres[(fam, season)] = {"centre": centre, "qualifiers": len(q), "opportunities": tot_n}
        noise[(fam, season)] = {"sigma2": sigma2, "split_half_players": len(terms)}
        for pid, v in players.items():
            lines[fam][(pid, season)] = {"n": v["n"], "rate": v["s"] / v["n"], "y": v["s"] / v["n"] - centre,
                                         "R": sigma2 / v["n"], "qualifies": v["n"] >= floors[fam], "club": v["club"]}
    return lines, centres, noise


# ====================================================================== moments and the swing fit
def player_moments(fam_lines, held_out=HELD_OUT_PAIR):
    """{gsis: [[sum_k, count_k] for k in LAGS]} over qualifying lines (the held-out pair excluded)."""
    by_player = defaultdict(dict)
    for (pid, season), ln in fam_lines.items():
        if ln["qualifies"]:
            by_player[pid][season] = ln
    out = {}
    for pid, seasons in by_player.items():
        acc = [[0.0, 0] for _ in LAGS]
        for t, ln in seasons.items():
            acc[0][0] += ln["y"] ** 2 - ln["R"]
            acc[0][1] += 1
            for k in LAGS[1:]:
                other = seasons.get(t + k)
                if other is None or (t, t + k) == held_out:
                    continue
                acc[k][0] += ln["y"] * other["y"]
                acc[k][1] += 1
        out[pid] = acc
    return out


def total_moments(moments, players=None):
    tot = [[0.0, 0] for _ in LAGS]
    for pid in (players if players is not None else moments):
        for k, (s, c) in enumerate(moments[pid]):
            tot[k][0] += s
            tot[k][1] += c
    return tot


def fit_covariance(tot):
    """(sb2, su2, rho, sse) minimising sum_k w_k (C_k - sb2 - rho^k su2)^2 with sb2, su2 >= 0."""
    C = [(s / c if c else None, c) for s, c in tot]
    pts = [(k, ck, w) for k, (ck, w) in zip(LAGS, C) if ck is not None and w > 0]
    if not pts:
        return 0.0, 0.0, 0.0, 0.0
    best = None
    sw = sum(w for _, _, w in pts)
    swc = sum(w * c for _, c, w in pts)
    for rho in RHO_GRID:
        f = [rho ** k for k, _, _ in pts]
        swf = sum(w * fk for (_, _, w), fk in zip(pts, f))
        swff = sum(w * fk * fk for (_, _, w), fk in zip(pts, f))
        swfc = sum(w * fk * c for (_, c, w), fk in zip(pts, f))
        cands = []
        det = sw * swff - swf * swf
        if det > 1e-15:
            sb2 = (swc * swff - swf * swfc) / det
            su2 = (sw * swfc - swf * swc) / det
            if sb2 >= 0 and su2 >= 0:
                cands.append((sb2, su2))
        cands.append((0.0, max(0.0, swfc / swff) if swff else 0.0))
        cands.append((max(0.0, swc / sw), 0.0))
        cands.append((0.0, 0.0))
        for sb2, su2 in cands:
            sse = sum(w * (c - sb2 - fk * su2) ** 2 for (_, c, w), fk in zip(pts, f))
            key = (round(sse, 15), rho)
            if best is None or key < best[0]:
                best = (key, sb2, su2, rho, sse)
    _, sb2, su2, rho, sse = best
    if su2 == 0.0:
        rho = 0.0  # the carry is not identified without a swing
    return sb2, su2, rho, sse


def bootstrap_su2(moments, label, resamples=BOOT):
    rng = random.Random(seed_of(label))
    players = sorted(moments)
    draws = []
    for _ in range(resamples):
        pick = [players[rng.randrange(len(players))] for _ in players]
        sb2, su2, rho, _ = fit_covariance(total_moments(moments, pick))
        draws.append((su2, sb2, rho))
    su = sorted(d[0] for d in draws)
    lo, hi = su[int(0.025 * resamples)], su[int(math.ceil(0.975 * resamples)) - 1]
    return {"su2_interval": [lo, hi], "sb2_sd": statistics.pstdev(d[1] for d in draws),
            "rho_sd": statistics.pstdev(d[2] for d in draws), "resamples": resamples}


def swing_fit(fam_lines, label):
    moments = player_moments(fam_lines)
    tot = total_moments(moments)
    sb2, su2, rho, sse = fit_covariance(tot)
    boot = bootstrap_su2(moments, label)
    empirical = [{"lag": k, "moment": (s / c if c else None), "terms": c,
                  "fitted": sb2 + (rho ** k) * su2} for k, (s, c) in zip(LAGS, tot)]
    return {"sb2": sb2, "su2": su2, "rho": rho, "sse": sse, "bootstrap": boot, "lag_moments": empirical,
            "players": len(moments)}, moments


def plain_reconcile(p1, p2):
    """The frozen keep and size rules (specification section 4, Swing)."""
    lo1 = p1["bootstrap"]["su2_interval"][0]
    lo2 = p2["bootstrap"]["su2_interval"][0]
    if not (lo1 > 0 and lo2 > 0):
        where = "both passes" if lo1 <= 0 and lo2 <= 0 else ("pass 1" if lo1 <= 0 else "pass 2")
        return {"swing_kept": False, "status": "not kept (su2 interval reaches 0 in %s)" % where,
                "sb2": p1["sb2_no_swing"], "su2": 0.0, "rho": 0.0, "from": "pass 1, swing fixed at 0"}
    lo, hi = p1["bootstrap"]["su2_interval"]
    if lo <= p2["su2"] <= hi:
        chosen, source, status = p1, "pass 1", "Confirmed two-pass"
    else:
        chosen, source = (p1, "pass 1") if p1["su2"] <= p2["su2"] else (p2, "pass 2")
        status = "Reconciled down, flagged"
    return {"swing_kept": True, "status": status, "from": source,
            "sb2": chosen["sb2"], "su2": chosen["su2"], "rho": chosen["rho"]}


def amendment3_reconcile(p1):
    """What amendment 3 would adopt for DL and LB: pass 1's set (conditional on U5; never applied here)."""
    if p1["bootstrap"]["su2_interval"][0] > 0:
        return {"swing_kept": True, "sb2": p1["sb2"], "su2": p1["su2"], "rho": p1["rho"]}
    return {"swing_kept": False, "sb2": p1["sb2_no_swing"], "su2": 0.0, "rho": 0.0}


def reconcile_swing(fam, p1, p2):
    """The adopted (sb2, su2, rho) and status under the frozen rules and the U5 fallback.

    For DL and LB the design's resolution (amendment 3: pass 1's set) rests on U5. Where the
    plain rule and that amendment adopt different sets, the family's swing depends on U5 and
    is held; where they agree, the plain rule's result stands."""
    out = plain_reconcile(p1, p2)
    out["held"] = False
    if fam in ("DL", "LB"):
        alt = amendment3_reconcile(p1)
        same = alt["swing_kept"] == out["swing_kept"] and all(
            abs(alt[k] - out[k]) <= 1e-15 for k in ("sb2", "su2", "rho"))
        out["amendment_3_would_adopt"] = alt
        if not same:
            out["held"] = True
            out["held_reason"] = ("U5 unanswered: the passes disagree on the %s swing and the design's resolution "
                                  "(amendment 3, pass 1's set) is conditional on U5, so the family's state is held"
                                  % fam)
    out["tau"] = math.sqrt(out["su2"] * (1 - out["rho"] ** 2))
    return out


def no_swing_sb2(moments):
    """sb2 with su2 fixed at 0: the weighted mean of every lag moment, floored at 0."""
    tot = total_moments(moments)
    w = sum(c for _, c in tot)
    return max(0.0, sum(s for s, _ in tot) / w) if w else 0.0


# ====================================================================== career facts
def career_info(dest):
    """gsis -> {class, drafted, pick, first_season, birth_date} from players.csv, draft_picks.csv and the dated rosters."""
    info = defaultdict(dict)
    for r in sources.rows("players.csv", dest):
        d = info[r["gsis_id"]]
        d["birth_date"] = r.get("birth_date") or None
        if r.get("draft_year"):
            d.update(drafted=True, cls=int(r["draft_year"]), pick=int(r["draft_pick"]))
    for r in sources.rows("draft_picks.csv", dest):
        g = r.get("gsis_id") or ""
        if g.startswith("00-") and not info[g].get("drafted"):
            info[g].update(drafted=True, cls=int(r["season"]), pick=int(r["pick"]))
    for season in SEASONS:
        for r in sources.rows(lb.roster_name(season), dest):
            g = r.get("gsis_id") or ""
            if not g:
                continue
            d = info[g]
            d["first_season"] = min(d.get("first_season", season), season)
            if not d.get("birth_date") and r.get("birth_date"):
                d["birth_date"] = r["birth_date"]
    for g, d in info.items():
        if not d.get("drafted"):
            d["drafted"] = False
            first = d.get("first_season")
            d["cls"] = first
            d["censored"] = first == 2010 or first is None
    return info


# ====================================================================== draft-slot priors
def rookie_lines(fam_lines, info, fam):
    """[(class, drafted, pick, y, R)] for first and second seasons above the floor."""
    out = []
    for (pid, season), ln in fam_lines.items():
        d = info.get(pid)
        if not d or not ln["qualifies"] or d.get("cls") is None:
            continue
        if not d["drafted"] and d.get("censored"):
            continue
        if d["cls"] < 2010 or season not in (d["cls"], d["cls"] + 1):
            continue
        out.append((d["cls"], d["drafted"], d.get("pick"), ln["y"], ln["R"]))
    return sorted(out)


def _prior_stats(rows):
    ys = [r[3] for r in rows]
    if len(ys) < 2:
        return None
    m = statistics.fmean(ys)
    var = statistics.variance(ys)
    noise = statistics.fmean(r[4] for r in rows)
    return {"mean": m, "se": math.sqrt(var / len(ys)), "true_var": max(0.0, var - noise), "lines": len(ys)}


def draft_priors(rows):
    """Flat priors (U5 fallback: slope 0): drafted and undrafted means, overall and with each class left out;
    plus the fitted log-pick slope for disclosure (not applied)."""
    out = {}
    for kind, flag in (("drafted", True), ("undrafted", False)):
        sel = [r for r in rows if r[1] is flag]
        out[kind] = {"all": _prior_stats(sel),
                     "leave_class_out": {str(c): _prior_stats([r for r in sel if r[0] != c])
                                         for c in sorted({r[0] for r in sel})},
                     "lines_by_class": {str(c): sum(1 for r in sel if r[0] == c) for c in sorted({r[0] for r in sel})}}
    drafted = [r for r in rows if r[1] and r[2]]
    if len(drafted) >= 3:
        x = [math.log(r[2]) for r in drafted]
        y = [r[3] for r in drafted]
        mx, my = statistics.fmean(x), statistics.fmean(y)
        sxx = sum((a - mx) ** 2 for a in x)
        b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
        resid = [c - my - b * (a - mx) for a, c in zip(x, y)]
        se = math.sqrt(sum(e * e for e in resid) / (len(x) - 2) / sxx)
        out["log_pick_slope"] = {"slope": b, "se": se, "lines": len(x), "applied": 0.0,
                                 "why": "U5 fallback: flat rookie estimates for every family (c1 = 0)"}
    else:
        out["log_pick_slope"] = {"slope": None, "lines": len(drafted), "applied": 0.0}
    return out


def prior_for(priors, d, params):
    """(m_b, m_u, P, basis) for a player before his first line, by the flat draft-slot rule."""
    sb2, su2 = params["sb2"], params["su2"]
    total = sb2 + su2
    if d and d.get("cls") is not None and d["cls"] >= 2010 and not (not d["drafted"] and d.get("censored")):
        kind = "drafted" if d["drafted"] else "undrafted"
        block = priors.get(kind) or {}
        stats = (block.get("leave_class_out") or {}).get(str(d["cls"])) or block.get("all")
        if stats is not None:
            share_b = sb2 / total if total > 0 else 0.0
            vr = stats["true_var"]
            return (stats["mean"], 0.0, [vr * share_b + stats["se"] ** 2, 0.0, vr * (1 - share_b)],
                    "draft" if d["drafted"] else "undrafted")
    return 0.0, 0.0, [sb2, 0.0, su2], "population"


# ====================================================================== the filter
def propagate(state, params, gap):
    mb, mu, (pbb, pbu, puu) = state
    if gap <= 0:
        return state
    r = params["rho"] ** gap
    return (mb, mu * r, [pbb, pbu * r, puu * r * r + params["su2"] * (1 - r * r)])


def update(state, y, R):
    mb, mu, (pbb, pbu, puu) = state
    S = pbb + 2 * pbu + puu + R
    if S <= 0:
        return state
    kb, ku = (pbb + pbu) / S, (pbu + puu) / S
    v = y - (mb + mu)
    return (mb + kb * v, mu + ku * v, [pbb - kb * kb * S, pbu - kb * ku * S, puu - ku * ku * S])


def filter_player(start, lines, honours, params, honour_cell, target):
    """Forecast of (m_b, m_u, P) for season `target` from `start` = (season, state), the
    player's lines {season: (y, R)} and honours {season: weight}, seasons before target only."""
    season, state = start
    while season < target:
        if season in lines:
            state = update(state, *lines[season])
        if season in honours and honour_cell is not None:
            state = update(state, honour_cell["mean"], honour_cell["true_var"] / honours[season])
        state = propagate(state, params, 1)
        season += 1
    return state


def honour_entries(cutoff, seasons):
    """{gsis: {season: (family, weight)}} for admissible honours public before `cutoff`."""
    data = json.loads(HONOURS.read_text(encoding="utf-8"))
    out = defaultdict(dict)
    for e in data["entries"]:
        if e["honour_kind"] not in HONOUR_KINDS or e["season"] not in seasons:
            continue
        if not e.get("public_date") or e["public_date"] >= cutoff or not e.get("admissible_pre_divergence"):
            continue
        pos = (e.get("position") or "").upper()
        fam = HONOUR_FAMILY.get(pos) or family_of_position(pos)
        if fam not in FAMILIES:
            continue
        w = EVIDENCE_WEIGHT.get(e["verification"], 0.0)
        prev = out[e["player_id"]].get(e["season"])
        if w and (prev is None or w > prev[1]):
            out[e["player_id"]][e["season"]] = (fam, w)
    return out


def honour_cells(lines, honours):
    """Per family: the true-state mean and dispersion among honoured qualifier seasons (pseudo-observation)."""
    out = {}
    for fam in FAMILIES:
        rows = [(ln["y"], ln["R"]) for (pid, s), ln in lines[fam].items()
                if ln["qualifies"] and honours.get(pid, {}).get(s, (None,))[0] == fam]
        if len(rows) < 2:
            out[fam] = None
            continue
        m = statistics.fmean(y for y, _ in rows)
        var = statistics.variance([y for y, _ in rows])
        tv = var - statistics.fmean(R for _, R in rows)
        out[fam] = {"mean": m, "true_var": tv, "seasons": len(rows)} if tv > 0 else None
    return out


def player_state(pid, fam, lines, info, priors, params, honours, cell, window, target):
    """(state, basis, source rows) for one player in one family: lines in `window` only."""
    own = {s: (lines[fam][(pid, s)]["y"], lines[fam][(pid, s)]["R"]) for s in window if (pid, s) in lines[fam]}
    d = info.get(pid)
    mb, mu, P, prior_basis = prior_for(priors, d, params)
    first_line = min(own) if own else None
    if prior_basis in ("draft", "undrafted"):
        start = d["cls"]
        if first_line is not None and first_line < start:
            start = first_line
    else:
        start = first_line if first_line is not None else window[0]
    start = max(start, window[0]) if prior_basis == "population" else start
    if start > target:
        start = target
    hon = {s: w for s, (f, w) in honours.get(pid, {}).items() if f == fam and s in window}
    state = filter_player((start, (mb, mu, P)), own, hon, params, cell, target)
    basis = "record" if own else prior_basis
    return state, basis, [{"season": s, "n": lines[fam][(pid, s)]["n"]} for s in sorted(own)], hon


def record_family(pid, lines, window=RECORD_SEASONS):
    """The position family holding most of the player's opportunities in `window` (latest season breaks ties)."""
    totals = {}
    for fam in POSITION_FAMILIES:
        n = sum(lines[fam][(pid, s)]["n"] for s in window if (pid, s) in lines[fam])
        last = max([s for s in window if (pid, s) in lines[fam]], default=None)
        if n:
            totals[fam] = (n, last)
    if not totals:
        return None
    return sorted(totals.items(), key=lambda kv: (-kv[1][0], -kv[1][1], kv[0]))[0][0]


# ====================================================================== checks
def forecast_calibration(fam, lines, info, priors, params):
    """Held-out pair: forecast each qualifying 2014 Weeks 1-4 line from the player's lines through 2013."""
    zs = []
    for (pid, s), ln in lines[fam].items():
        if s != 2014 or not ln["qualifies"]:
            continue
        if not any((pid, t) in lines[fam] for t in (2010, 2011, 2012, 2013)):
            continue
        (mb, mu, P), _, _, _ = player_state(pid, fam, lines, info, priors, params, {}, None,
                                             (2010, 2011, 2012, 2013), 2014)
        var = P[0] + 2 * P[1] + P[2] + ln["R"]
        if var > 0:
            zs.append((ln["y"] - mb - mu) / math.sqrt(var))
    if len(zs) < 3:
        return {"players": len(zs), "status": "too few"}
    n = len(zs)
    m = statistics.fmean(zs)
    v = statistics.variance(zs)
    se_m, se_v = math.sqrt(v / n), math.sqrt(2.0 / (n - 1))
    ok = abs(m) <= 2 * se_m and abs(v - 1) <= 2 * se_v
    return {"players": n, "mean_z": m, "se_mean": se_m, "var_z": v, "se_var": se_v,
            "status": "within 2 SE" if ok else "OUTSIDE 2 SE"}


def drift_tables(fam, lines, centres, moments):
    """Per-season level (centre) and per-pair lag-1 covariances with bootstrap SEs and a heterogeneity test."""
    levels = {}
    for s in SEASONS:
        c = centres.get((fam, s))
        if not c:
            continue
        rates = [ln["rate"] for (pid, t), ln in lines[fam].items() if t == s and ln["qualifies"]]
        se = statistics.pstdev(rates) / math.sqrt(len(rates)) if len(rates) > 1 else None
        levels[str(s)] = {"centre": c["centre"], "qualifiers": c["qualifiers"], "se": se}
    pairs = {}
    rng = random.Random(seed_of("drift-" + fam))
    for t in (2010, 2011, 2012):
        prods = []
        for (pid, s), ln in lines[fam].items():
            o = lines[fam].get((pid, t + 1))
            if s == t and ln["qualifies"] and o and o["qualifies"]:
                prods.append(ln["y"] * o["y"])
        if len(prods) < 3:
            continue
        m = statistics.fmean(prods)
        boots = [statistics.fmean(prods[rng.randrange(len(prods))] for _ in prods) for _ in range(BOOT)]
        pairs["%d-%d" % (t, t + 1)] = {"covariance": m, "se": statistics.pstdev(boots), "players": len(prods)}
    q, df, p = None, None, None
    if len(pairs) >= 2:
        ws = [(v["covariance"], 1 / v["se"] ** 2) for v in pairs.values() if v["se"] > 0]
        pooled = sum(c * w for c, w in ws) / sum(w for _, w in ws)
        q = sum(w * (c - pooled) ** 2 for c, w in ws)
        df = len(ws) - 1
        p = lb.chi2_p(q, df)
    lq, ldf, lp = None, None, None
    pre = [(v["centre"], v["se"]) for k, v in levels.items() if v["se"]]
    if len(pre) >= 2:
        ws = [(c, 1 / se ** 2) for c, se in pre]
        pooled = sum(c * w for c, w in ws) / sum(w for _, w in ws)
        lq = sum(w * (c - pooled) ** 2 for c, w in ws)
        ldf = len(ws) - 1
        lp = lb.chi2_p(lq, ldf)
    return {"levels": levels, "level_heterogeneity": {"cochran_q": lq, "df": ldf, "p": lp}, "lag1_pairs": pairs,
            "heterogeneity": {"cochran_q": q, "df": df, "p": p,
                              "note": "reported; the pooled fit is used whatever it reads (specification section 2)"}}


def self_influence(fam, lines, info, priors, params, moments, honours, cell):
    """|change in a player's own 2014 expectation| / true SD when his own 2013-2014 rows leave the moment sums."""
    sd = math.sqrt(params["sb2"] + params["su2"]) if params["sb2"] + params["su2"] > 0 else None
    if sd is None:
        return {"players": 0, "note": "no true-state spread"}
    full = total_moments(moments)
    out = []
    by_player = defaultdict(dict)
    for (pid, s), ln in lines[fam].items():
        by_player[pid][s] = ln
    for pid, seasons in by_player.items():
        if not any(s in (2013, 2014) and ln["qualifies"] for s, ln in seasons.items()):
            continue
        if not any(s in RECORD_SEASONS for s in seasons):
            continue
        # the player's 2013-2014 contribution to the lag sums
        sub = {(p, s): ln for (p, s), ln in lines[fam].items() if p == pid and s in (2013, 2014)}
        keep = {(p, s): ln for (p, s), ln in lines[fam].items() if p == pid and s not in (2013, 2014)}
        own_all = player_moments({**sub, **keep}).get(pid, [[0.0, 0] for _ in LAGS])
        own_keep = player_moments(keep).get(pid, [[0.0, 0] for _ in LAGS])
        tot = [[full[k][0] - own_all[k][0] + own_keep[k][0], full[k][1] - own_all[k][1] + own_keep[k][1]]
               for k in range(len(LAGS))]
        sb2, su2, rho, _ = fit_covariance(tot)
        alt = dict(params, sb2=sb2, su2=su2 if params["su2"] > 0 else 0.0, rho=rho if params["su2"] > 0 else 0.0)
        if params["su2"] == 0:
            alt["sb2"] = max(0.0, sum(s for s, _ in tot) / sum(c for _, c in tot))
        a, _, _, _ = player_state(pid, fam, lines, info, priors, params, honours, cell, RECORD_SEASONS, 2014)
        b, _, _, _ = player_state(pid, fam, lines, info, priors, alt, honours, cell, RECORD_SEASONS, 2014)
        out.append(abs((a[0] + a[1]) - (b[0] + b[1])) / sd)
    if not out:
        return {"players": 0}
    out.sort()
    q = lambda f: out[min(len(out) - 1, int(f * len(out)))]  # noqa: E731
    return {"players": len(out), "median": q(0.5), "p90": q(0.9), "p99": q(0.99), "max": out[-1],
            "unit": "true-state SD of the family"}


# ====================================================================== feedback (D)
def starter_shares(dest, seasons=SEASONS):
    """{(gsis, season): share of the club's charted regular-season weeks at depth_team 1}."""
    out = {}
    for season in seasons:
        name = "depth_charts_2014w4.csv" if season == 2014 else "depth_charts_%d.csv" % season
        club_weeks = defaultdict(set)
        starts = defaultdict(set)
        for r in sources.rows(name, dest):
            if r.get("game_type") != "REG":
                continue
            club, week = r["club_code"], int(r["week"])
            club_weeks[club].add(week)
            if r["depth_team"].strip() == "1" and r.get("gsis_id"):
                starts[(r["gsis_id"], club)].add(week)
        best = {}
        for (pid, club), weeks in starts.items():
            share = len(weeks) / len(club_weeks[club])
            best[pid] = max(best.get(pid, 0.0), share)
        for pid, share in best.items():
            out[(pid, season)] = share
    return out


def feedback_rows(fam, lines, info, priors, params, roles):
    """[(family, club, role change, seasons missed, standardised residual)] for one family: each
    qualifying season t in 2011-2013 with an earlier line, forecast from the player's lines before t."""
    rows = []
    if params["sb2"] + params["su2"] <= 0:
        return rows
    sd = math.sqrt(params["sb2"] + params["su2"])
    by_player = defaultdict(dict)
    for (pid, s), ln in lines[fam].items():
        by_player[pid][s] = ln
    for pid in sorted(by_player):
        seasons = by_player[pid]
        for t in sorted(seasons):
            ln = seasons[t]
            if t in (2010, 2014) or not ln["qualifies"]:
                continue
            prev = max([s for s in seasons if s < t], default=None)
            if prev is None:
                continue
            (mb, mu, _), _, _, _ = player_state(pid, fam, lines, info, priors, params, {}, None,
                                                 tuple(range(2010, t)), t)
            role = roles.get((pid, t), 0.0) - roles.get((pid, prev), 0.0)
            rows.append((fam, ln["club"], role, t - prev - 1, (ln["y"] - mb - mu) / sd))
    return rows


def _ols1(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return my, 0.0, float("inf")
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    a0 = my - b * mx
    resid = [c - a0 - b * a for a, c in zip(x, y)]
    se = math.sqrt(sum(e * e for e in resid) / (len(x) - 2) / sxx)
    return a0, b, se


def loo_club_skill(x, y, clubs):
    sse, sse0 = 0.0, 0.0
    groups = defaultdict(list)
    for i, c in enumerate(clubs):
        groups[c].append(i)
    for c, idx in groups.items():
        out = set(idx)
        xs = [x[i] for i in range(len(x)) if i not in out]
        ys = [y[i] for i in range(len(y)) if i not in out]
        a, b, _ = _ols1(xs, ys)
        m0 = statistics.fmean(ys)
        for i in idx:
            sse += (y[i] - a - b * x[i]) ** 2
            sse0 += (y[i] - m0) ** 2
    return 1 - sse / sse0 if sse0 else 0.0


def capped(x, q):
    mags = sorted(abs(v) for v in x)
    cap = mags[min(len(mags) - 1, max(0, int(math.ceil(q * len(mags))) - 1))]
    return [max(-cap, min(cap, v)) for v in x], cap


def feedback_fit(rows, q=None):
    """Per term: slope, SE, leave-one-club-out skill; the cap q chosen by skill when not given."""
    out = {}
    clubs = [r[1] for r in rows]
    y = [r[4] for r in rows]
    for term, col in (("role", 2), ("availability", 3)):
        raw = [r[col] for r in rows]
        choices = [q[term]] if q else PS["feedback_cap_quantiles"]
        best = None
        for qq in choices:
            x, cap = capped(raw, qq)
            if len(set(x)) < 2:
                continue  # a cap that leaves no variation is not a predictor
            skill = loo_club_skill(x, y, clubs)
            _, b, se = _ols1(x, y)
            cand = (skill, qq, b, se, cap)
            if best is None or (skill, qq) > (best[0], best[1]):
                best = cand
        if best is None:
            out[term] = {"slope": 0.0, "se": None, "loo_club_skill": None, "cap_quantile": None, "cap": None,
                         "rows": len(rows), "note": "no variation in the predictor"}
            continue
        skill, qq, b, se, cap = best
        out[term] = {"slope": b, "se": se, "loo_club_skill": skill, "cap_quantile": qq, "cap": cap, "rows": len(rows)}
    return out


def reconcile_feedback(f1, f2):
    out = {}
    for term, sign in (("role", 1), ("availability", -1)):
        a, b = f1[term], f2[term]
        if a["loo_club_skill"] is None or b["loo_club_skill"] is None:
            out[term] = {"kept": False, "weight": 0.0}
            continue
        kept = (a["loo_club_skill"] > 0 and b["loo_club_skill"] > 0 and a["slope"] * sign > 0 and b["slope"] * sign > 0)
        if not kept:
            out[term] = {"kept": False, "weight": 0.0}
            continue
        if abs(b["slope"] - a["slope"]) <= PS["feedback_slope_tolerance_se"] * a["se"]:
            out[term] = {"kept": True, "weight": a["slope"], "status": "Confirmed two-pass"}
        else:
            w = a["slope"] if abs(a["slope"]) <= abs(b["slope"]) else b["slope"]
            out[term] = {"kept": True, "weight": w, "status": "smaller magnitude, flagged"}
    return out


# ====================================================================== the build
MIN_CELL = RULES["thresholds"]["PLAYER_STATE_MIN_CELL"]


def fit_family(fam, lines, label):
    p, moments = swing_fit(lines[fam], label)
    p["sb2_no_swing"] = no_swing_sb2(moments)
    return p, moments


def thin_cells(priors, cell, p1):
    """Fitted cells under the amendment-3 minimum (30): flagged, never merged (the rule is held under U5)."""
    out = []
    for kind in ("drafted", "undrafted"):
        stats = priors[kind]["all"]
        lines_n = stats["lines"] if stats else sum(priors[kind]["lines_by_class"].values())
        if lines_n < MIN_CELL:
            out.append("%s rookie prior: %d lines" % (kind, lines_n))
    if cell is not None and cell["seasons"] < MIN_CELL:
        out.append("honour cell: %d seasons" % cell["seasons"])
    if p1["players"] < MIN_CELL:
        out.append("swing fit: %d players" % p1["players"])
    return out


def build(dest, log=print):
    import verify_2010_2014_player_state_model as verify

    info = career_info(dest)
    raw1 = extract_pass1(dest, log)
    lines, centres, noise = season_lines(raw1)
    second = verify.pass2(dest, info, log)
    honours_2014 = honour_entries("2013-01-15", RECORD_SEASONS)
    cells = honour_cells(lines, honours_2014)
    fams, adopted, moments_by = {}, {}, {}
    for fam in FAMILIES:
        log("player states: fit %s" % fam)
        p1, moments = fit_family(fam, lines, "player-state-pass1-" + fam)
        moments_by[fam] = moments
        rec = reconcile_swing(fam, p1, second["families"][fam])
        adopted[fam] = rec
        priors = draft_priors(rookie_lines(lines[fam], info, fam))
        fams[fam] = {"metric": METRICS[fam], "floor": FLOORS[fam],
                     "centres": {lb.TAG[s]: centres[(fam, s)] for s in SEASONS if (fam, s) in centres},
                     "noise": {lb.TAG[s]: noise[(fam, s)] for s in SEASONS if (fam, s) in noise},
                     "pass1": p1, "adopted": rec, "draft_priors": priors, "honour_cell": cells[fam],
                     "aging": {"adopted": "Z", "basis": "U5 fallback (zero aging for every family)",
                               "candidates_fitted": "held (amendments 2 and 3 rest on U5)",
                               "punter_curve": "held (the punter curve is an aging candidate; Z under the fallback)"},
                     "below_min_cell": thin_cells(priors, cells[fam], p1)}
    params = {f: {"sb2": a["sb2"], "su2": a["su2"], "rho": a["rho"]} for f, a in adopted.items() if not a["held"]}
    roles = starter_shares(dest)
    fb1_rows = []
    for fam in FAMILIES:
        log("player states: checks %s" % fam)
        priors = fams[fam]["draft_priors"]
        if fam in params:
            fams[fam]["forecast_calibration_2013_to_2014w4"] = forecast_calibration(fam, lines, info, priors,
                                                                                   params[fam])
            fams[fam]["self_influence"] = self_influence(fam, lines, info, priors, params[fam], moments_by[fam],
                                                         honours_2014, cells[fam])
            fb1_rows += feedback_rows(fam, lines, info, priors, params[fam], roles)
        else:
            fams[fam]["forecast_calibration_2013_to_2014w4"] = {"status": "held"}
            fams[fam]["self_influence"] = {"status": "held"}
        fams[fam]["drift"] = drift_tables(fam, lines, centres, moments_by[fam])
        fams[fam]["two_pass_agreement"] = agreement(fams[fam], second["record"]["families"][fam])
    fb1 = feedback_fit(fb1_rows)
    caps = {"role": fb1["role"]["cap_quantile"] or 1.0, "availability": fb1["availability"]["cap_quantile"] or 1.0}
    fb2 = verify.feedback_pass2(second, caps, dest, [f for f in FAMILIES if f in params])
    feedback = {"pass1": fb1, "pass2": fb2, "reconciled": reconcile_feedback(fb1, fb2),
                "applied": {"snaps": PS["snap_feedback_weight"], "role_2015": PS["role_feedback_2015"],
                            "in_2014": PS["feedback_in_2014"],
                            "availability": "from the 2015 transition (default 1B.13); F is 0 in 2014"},
                "outcome": ("one-step forecast residual of a qualifying 2011-2013 season, in true-state SD units, "
                            "pooled over families; role = change in starter share since the previous line, "
                            "availability = seasons missed between lines; the 2013-to-2014 Weeks 1-4 pair held out")}
    model = {
        "schema": SCHEMA_MODEL,
        "derivation": DERIVATION,
        "builder": "scripts/research/build_2010_2014_player_state_model.py",
        "verifier": "scripts/research/verify_2010_2014_player_state_model.py",
        "specification_sha256": pre_build_specification.digest(),
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through 2014-09-29), cut "
                                 "at fetch; positions from each season's own roster; 2013 and 2014 enter pooled "
                                 "fits only as an anonymous league population; no club, game or player field"),
        "data_cutoff": CUT["max_game_date"],
        "u5": {"status": "unanswered", "fallback": PS["u5_fallback"], "held": PS["u5_conditional"],
               "effect": ("aging Z for every family; draft-slot slope 0; no tiers; a DL or LB family whose swing the "
                          "two passes disagree on (so that amendment 3 would decide it) is held; cells under 30 are "
                          "flagged, not merged")},
        "boundary": ("hidden-state statistical priors for the engine only; never scouting evidence or a staff-facing "
                     "grade; no staff assessment, grade or E2 advice reads them or their tiers"),
        "sources": source_pins(),
        "honours_evidence_sha256": hashlib.sha256(HONOURS.read_bytes()).hexdigest(),
        "evidence_weight": EVIDENCE_WEIGHT,
        "lags": list(LAGS), "rho_grid": [RHO_GRID[0], RHO_GRID[-1], PS["rho_grid_step"]],
        "held_out_pair": list(HELD_OUT_PAIR),
        "families": fams,
        "tiers": {"status": "held", "why": "the tier population on the qualifier floors rests on amendment 3 (U5)"},
        "feedback": feedback,
        "second_pass": second["record"],
    }
    positions = latest_positions(dest)
    public, coverage = public_table(lines, info, fams, params, honours_2014, cells, positions)
    return model, public, coverage


def agreement(block, second):
    """Pass 1 against pass 2, each tolerance 2 SE from pass 1's own n (players review R12)."""
    rows = []
    for season, lvl in block["drift"]["levels"].items():
        other = second["centres"].get(season)
        if other is None or lvl["se"] is None:
            continue
        diff = other["centre"] - lvl["centre"]
        rows.append({"quantity": "centre %s" % season, "pass1": lvl["centre"], "pass2": other["centre"],
                     "tolerance": 2 * lvl["se"], "within": abs(diff) <= 2 * lvl["se"]})
    for kind in ("drafted", "undrafted"):
        a, b = block["draft_priors"][kind]["all"], second["draft_priors"][kind]["all"]
        if a and b:
            rows.append({"quantity": "%s rookie prior mean" % kind, "pass1": a["mean"], "pass2": b["mean"],
                         "tolerance": 2 * a["se"], "within": abs(b["mean"] - a["mean"]) <= 2 * a["se"]})
    return {"rows": rows, "outside": sum(1 for r in rows if not r["within"]),
            "rule": "reported; a quantity outside its tolerance is flagged, and the pass-1 value is the one used"}


def source_pins():
    names = set()
    for s in SEASONS:
        names |= {lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"), lb.roster_name(s),
                  "roster_weekly_%s.csv" % lb.TAG[s], "stats_player_week_%s.csv" % lb.TAG[s],
                  "depth_charts_%s.csv" % lb.TAG[s]}
    names |= {"players.csv", "draft_picks.csv"}
    manifest = sources.load_manifest()["assets"]
    return {n: {"sha256": manifest[n]["sha256"]} for n in sorted(names)}


def latest_positions(dest):
    """gsis -> (season, position) from the latest dated roster (2014: the Week 1-4 weekly roster)."""
    out = {}
    for season in SEASONS:
        for pid, pos in lb.positions(season, dest).items():
            out[pid] = (season, pos)
    return out


def public_table(lines, info, fams, params, honours, cells, positions):
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    rows = {}
    counts = Counter()
    for gsis, ident in sorted(identity["players"].items()):
        fam = record_family(gsis, lines)
        family_basis = "most 2010-2012 opportunities"
        if fam is None:
            if gsis in positions:
                season, pos = positions[gsis]
                fam = family_of_position(pos) or "unknown"
                family_basis = "latest dated roster position (%s)" % lb.TAG[season]
            elif ident.get("branch_positions"):
                fam = family_of_position(ident["branch_positions"][0]) or "unknown"
                family_basis = "branch roster position (no dated roster)"
            else:
                fam, family_basis = "unknown", "no position"
        row = {"record_family": fam, "family_basis": family_basis, "class": ident["class"],
               "real_slot": ident["real_slot"], "age_used": age_on(info.get(gsis)), "aging": "Z"}
        if fam not in POSITION_FAMILIES:
            row.update(basis="no_state", why=("offensive linemen and long snappers have no public performance rate"
                                              if fam in ("OL", "LS") else "no family"))
        elif fam not in params:
            row.update(basis="held", why="the family's swing is held (U5)")
        else:
            p = params[fam]
            priors = fams[fam]["draft_priors"]
            d = dict(info.get(gsis) or {})
            if not d.get("cls") and ident.get("class"):
                d.update(cls=ident["class"], drafted=ident["real_slot"] != "undrafted", censored=False)
            local = dict(info)
            local[gsis] = d
            state, basis, src, hon = player_state(gsis, fam, lines, local, priors, p, honours, cells[fam],
                                                  RECORD_SEASONS, 2014)
            plain, _, _, _ = player_state(gsis, fam, lines, local, priors, p, {}, None, RECORD_SEASONS, 2014)
            row.update(basis=basis, m_b=rnd(state[0]), m_u=rnd(state[1]), P=[rnd(v) for v in state[2]],
                       honours_lift=rnd((state[0] + state[1]) - (plain[0] + plain[1])) if hon else 0.0,
                       honour_seasons=sorted(hon), source_rows=src)
        returns = {}
        for rf in RETURN_FAMILIES:
            if rf in params and params[rf]["sb2"] + params[rf]["su2"] > 0 and any(
                    (gsis, s) in lines[rf] for s in RECORD_SEASONS):
                st, _, src, _ = player_state(gsis, rf, lines, info, fams[rf]["draft_priors"], params[rf], honours,
                                             cells[rf], RECORD_SEASONS, 2014)
                returns[rf] = {"m_b": rnd(st[0]), "m_u": rnd(st[1]), "P": [rnd(v) for v in st[2]], "source_rows": src}
        if returns:
            row["returns"] = returns
        rows[gsis] = row
        counts[row["basis"]] += 1
    return rows, dict(sorted(counts.items()))


def age_on(d):
    bd = (d or {}).get("birth_date")
    if not bd:
        return None
    y, m, dd = (int(x) for x in bd[:10].split("-"))
    return round((AGE_ON - date(y, m, dd)).days / 365.25, 1)


def rnd(x):
    return float("%.10g" % x)


# ====================================================================== outputs
def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def artifacts(dest, log=print):
    """{path: text} for the three JSON artifacts (the study's tables come from the model)."""
    model, public, coverage = build(dest, log)
    model_text = render(model)
    public_doc = {"schema": SCHEMA_PUBLIC, "derivation": DERIVATION, "league_year": 2014,
                  "specification_sha256": pre_build_specification.digest(),
                  "model_sha256": hashlib.sha256(model_text.encode()).hexdigest(),
                  "identity_sha256": hashlib.sha256(IDENTITY.read_bytes()).hexdigest(),
                  "units": "each family's centred rate (model families[f].metric); m_b persistent, m_u swing, "
                           "P = [Pbb, Pbu, Puu]; expectations for 2014 from 2010-2012 lines only",
                  "boundary": model["boundary"],
                  "append_only": ("rows for later entrants are appended; an edit to an existing row is refused "
                                  "once the season is bound (batch B7)"),
                  "coverage": coverage, "players": public}
    public_text = render(public_doc)
    manifest = {"schema": SCHEMA_MANIFEST, "derivation": DERIVATION, "league_year": 2014,
                "model_sha256": hashlib.sha256(model_text.encode()).hexdigest(),
                "public_table_sha256": hashlib.sha256(public_text.encode()).hexdigest(),
                "families": list(FAMILIES), "data_cutoff": CUT["max_game_date"],
                "specification_sha256": pre_build_specification.digest(), "bound": False}
    return {MODEL_OUT: model_text, PUBLIC_OUT: public_text, MANIFEST_OUT: render(manifest)}, model, public_doc


def append_only_errors(old_public, new_public):
    """A bound table may only gain rows (B7 binds; until then the manifest says bound: false)."""
    errors = []
    for gsis, row in old_public["players"].items():
        if new_public["players"].get(gsis) != row:
            errors.append("%s: an existing row would change after bind" % gsis)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    texts, model, public = artifacts(args.sources, log=lambda m: print(m, file=sys.stderr))
    import player_state_study
    texts[STUDY] = player_state_study.render(model, public, STUDY.read_text() if STUDY.exists() else None)
    if MANIFEST_OUT.exists() and json.loads(MANIFEST_OUT.read_text()).get("bound"):
        errors = append_only_errors(json.loads(PUBLIC_OUT.read_text()), public)
        if errors:
            for e in errors:
                print("REFUSED: " + e, file=sys.stderr)
            return 1
    if args.check:
        bad = [p for p, t in texts.items() if not p.exists() or p.read_text() != t]
        for p in texts:
            print("%s %s" % ("DIFFERS" if p in bad else "reproduced", p.relative_to(ROOT)))
        return 1 if bad else 0
    for p, t in texts.items():
        p.write_text(t)
        print("wrote %s (%d bytes)" % (p.relative_to(ROOT), len(t)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
