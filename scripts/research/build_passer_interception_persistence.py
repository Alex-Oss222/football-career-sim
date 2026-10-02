#!/usr/bin/env python3
"""Individual passer interception-rate persistence, 2010 to 2014 (research only).

  python scripts/research/build_passer_interception_persistence.py SOURCE_DIR

SOURCE_DIR holds the nflverse files named in SOURCES (stats_player_reg_{season}.csv
for the research pass, play_by_play_{season}.csv.gz for the separate verification
pass). Output: library/data/passer_interception_persistence.json. Prose report:
library/passer_interception_persistence_study.md.

The question (Alex Stone, October 2, 2026): the kernel's interception-share
channel carries no passer term (runtime/strength.py: "no term survived the
fit"). Does an individual passer's interception rate persist from one season to
the next, under the same season-pair test that kept the punter term
(library/2014_strength_calibration.md section 10.4)?

This script reads no branch record and changes nothing the kernel reads. The
2013 and 2014 real seasons are post-divergence (January 15, 2013); their pairs
are computed only as a league-population check and are labelled so. The
protagonist's own real post-divergence lines are excluded from those seasons
entirely (EXCLUDE_POST_DIVERGENCE: not a qualifier row, not a pair, not a
reliability input) so no real post-divergence outcome of his enters any number
or table here.

Rule fixed before the first run (PREREGISTERED below): dropbacks = pass
attempts + sacks suffered (two-point tries excluded, as the production
evidence file defines); qualifier = 200 dropbacks in each season of a pair;
outcome = the t+1 raw rate, weight = t+1 dropbacks; predictors = the season-t
raw rate and the season-t shrunk rate, each as a deviation from the season-t
league mean; shrinkage k from the binomial-noise-corrected variance ratio of
season t; weighted least squares with intercept; prior N(0, 1^2) on the
dimensionless slope (the punter continuous prior); leave-one-pair-out skill
= 1 - (rmse / null rmse)^2 against the weighted league-mean baseline; a term
has skill only when that is positive with a positive slope. Pre-divergence
pairs (2010->2011, 2011->2012) are the result; pooled over both is the
headline; 2012->2013 and 2013->2014 are for information only.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library/data/passer_interception_persistence.json"
SEASONS = (2010, 2011, 2012, 2013, 2014)
PRE_DIVERGENCE = (2010, 2011, 2012)
DIVERGENCE = "2013-01-15"
BASE = "https://github.com/nflverse/nflverse-data/releases/download/"
SOURCES = {
    **{f"stats_player_reg_{s}.csv": BASE + f"stats_player/stats_player_reg_{s}.csv" for s in SEASONS},
    **{f"play_by_play_{s}.csv.gz": BASE + f"pbp/play_by_play_{s}.csv.gz" for s in SEASONS},
}
# The protagonist's quarterback (nflverse gsis id). His real 2013 and 2014
# lines are post-divergence outcomes of a real person and are not read, not
# even as one of 35 rows in a league-population regression.
EXCLUDE_POST_DIVERGENCE = {"00-0029604": "Kirk Cousins"}
MIN_DROPBACKS = 200
PRIOR_SD = 1.0
PREREGISTERED = {
    "written_before_first_run": "2026-10-02",
    "dropbacks": "pass attempts + sacks suffered; two-point tries excluded; spikes counted as attempts "
                 "(the production evidence file's definition)",
    "interceptions": "passing_interceptions (stats file); play-by-play: interception == 1 on the passer's "
                     "pass plays, two-point tries excluded",
    "qualifier": "%d dropbacks in each season of a pair" % MIN_DROPBACKS,
    "outcome": "season t+1 raw interception rate; weight: t+1 dropbacks",
    "predictors": {
        "raw": "season-t raw rate minus the season-t league mean (dropback-weighted mean over qualifiers)",
        "shrunk": "season-t shrunk rate minus the season-t league mean, shrunk = (n x raw + k x mean) / (n + k)"},
    "reliability": "k = p(1-p) / signal variance, signal variance = dropback-weighted variance of qualifier rates "
                   "minus the dropback-weighted mean binomial variance p(1-p)/n, p the league mean; "
                   "a non-positive signal variance means no measurable spread beyond the binomial draw (k infinite)",
    "fit": "weighted least squares with intercept; prior N(0, %s^2) on the slope; leave-one-pair-out skill "
           "= 1 - (rmse / null rmse)^2, null = the weighted league mean of the other pairs" % PRIOR_SD,
    "keep_rule": "a term has skill only when the leave-one-pair-out skill is positive and the slope is positive",
    "pairs": {"pre_divergence": ["2010->2011", "2011->2012"], "pooled": "both pre-divergence pairs",
              "post_divergence_population_only": ["2012->2013", "2013->2014"]},
    "verification": "every count recomputed from the play-by-play file by gsis id; counts must be exact",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ------------------------------------------------------------- statistics
def wmean(xs, ws):
    return sum(x * w for x, w in zip(xs, ws)) / sum(ws)


def wls(x, y, w):
    """y = a + b x, weights normalised to mean 1. Returns a, b, se_b, r2."""
    k = len(w) / sum(w)
    w = [wi * k for wi in w]
    mx, my = wmean(x, w), wmean(y, w)
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


def shrink(b, se, prior=PRIOR_SD):
    tau2 = prior ** 2
    return b * tau2 / (tau2 + se * se), math.sqrt(tau2 * se * se / (tau2 + se * se))


def loo(x, y, w):
    errors, null = [], []
    for i in range(len(x)):
        xs = x[:i] + x[i + 1:]
        ys = y[:i] + y[i + 1:]
        ws = w[:i] + w[i + 1:]
        a, b, _, _ = wls(xs, ys, ws)
        errors.append(y[i] - (a + b * x[i]))
        null.append(y[i] - wmean(ys, ws))
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    rmse0 = math.sqrt(sum(e * e for e in null) / len(null))
    return {"rmse": rmse, "null_rmse": rmse0, "skill": 1 - (rmse / rmse0) ** 2}


def corr(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    num_ = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num_ / den if den else 0.0


def reliability(rows):
    """Binomial-noise-corrected variance ratio for one season's qualifiers."""
    n = [r["dropbacks"] for r in rows]
    p = [r["rate"] for r in rows]
    mean = sum(r["interceptions"] for r in rows) / sum(n)
    observed = wmean([(pi - mean) ** 2 for pi in p], n)
    binomial = wmean([mean * (1 - mean) / ni for ni in n], n)
    signal = observed - binomial
    k = (mean * (1 - mean) / signal) if signal > 0 else None
    n_mean = sum(n) / len(n)
    return {"qualifiers": len(rows), "league_mean": mean, "observed_variance": observed,
            "mean_binomial_variance": binomial, "signal_variance": signal, "signal_sd": math.sqrt(max(signal, 0.0)),
            "k": k, "mean_dropbacks": n_mean,
            "reliability_at_mean_dropbacks": (n_mean / (n_mean + k)) if k else 0.0}


# ------------------------------------------------------------- passes
def research_pass(stats_rows, season):
    out = {}
    for r in stats_rows:
        if r.get("season_type") != "REG":
            continue
        attempts = int(num(r["attempts"]))
        sacks = int(num(r["sacks_suffered"]))
        n = attempts + sacks
        if n < MIN_DROPBACKS:
            continue
        pid = r["player_id"]
        if season not in PRE_DIVERGENCE and pid in EXCLUDE_POST_DIVERGENCE:
            continue  # a real post-divergence line of the protagonist's player: never read
        out[pid] = {"player_id": pid, "name": r["player_display_name"], "club": r["recent_team"],
                    "position": r["position"], "season": season, "attempts": attempts, "sacks": sacks,
                    "dropbacks": n, "interceptions": int(num(r["passing_interceptions"])),
                    "rate": num(r["passing_interceptions"]) / n}
    return out


def verification_pass(pbp_rows):
    acc = defaultdict(lambda: defaultdict(int))
    dates = set()
    for r in pbp_rows:
        if r["season_type"] != "REG":
            continue
        dates.add(r["game_date"])
        passer = r["passer_player_id"]
        if not passer or r["two_point_attempt"] == "1":
            continue
        ptype = r["play_type"]
        if ptype == "pass":
            if r["sack"] == "1":
                acc[passer]["sacks"] += 1
            else:
                acc[passer]["attempts"] += 1
            if r["interception"] == "1":
                acc[passer]["interceptions"] += 1
        elif ptype == "qb_spike":
            acc[passer]["attempts"] += 1
    return acc, max(dates)


def pair_rows(seasons, t, exclude):
    a, b = seasons[t], seasons[t + 1]
    rel = reliability(list(a.values()))
    mean_t = rel["league_mean"]
    k = rel["k"]
    rows = []
    for pid in sorted(set(a) & set(b)):
        if pid in exclude:
            continue
        x, y = a[pid], b[pid]
        shrunk = ((x["dropbacks"] * x["rate"] + k * mean_t) / (x["dropbacks"] + k)) if k else mean_t
        rows.append({"player_id": pid, "name": x["name"], "seasons": [t, t + 1],
                     "prior_rate": x["rate"], "prior_dropbacks": x["dropbacks"], "prior_interceptions": x["interceptions"],
                     "prior_deviation_raw": x["rate"] - mean_t, "prior_deviation_shrunk": shrunk - mean_t,
                     "next_rate": y["rate"], "next_dropbacks": y["dropbacks"], "next_interceptions": y["interceptions"]})
    return rows, rel


def fit_pairs(rows):
    out = {"pairs": len(rows)}
    if len(rows) < 8:
        out["reason"] = "fewer than 8 season pairs"
        return out
    y = [r["next_rate"] for r in rows]
    w = [r["next_dropbacks"] for r in rows]
    for name, key in (("raw", "prior_deviation_raw"), ("shrunk", "prior_deviation_shrunk")):
        x = [r[key] for r in rows]
        a, b, se, r2 = wls(x, y, w)
        sb, ssd = shrink(b, se)
        lo = loo(x, y, w)
        out[name] = {"intercept": a, "slope": b, "se": se, "shrunk_slope": sb, "shrunk_sd": ssd, "prior_sd": PRIOR_SD,
                     "r2": r2, "correlation_unweighted": corr(x, y), "loo": lo,
                     "keep": lo["skill"] > 0 and b > 0}
    kept = [n for n in ("raw", "shrunk") if out[n]["keep"]]
    out["verdict"] = ("term with skill: " + max(kept, key=lambda n: out[n]["loo"]["skill"])) if kept \
        else "no predictor with positive leave-one-pair-out skill and a positive slope"
    # Next-season rate by prior-season tercile of the raw rate (information only).
    order = sorted(rows, key=lambda r: r["prior_rate"])
    third = len(order) // 3
    groups = {"lowest_third": order[:third], "middle_third": order[third:len(order) - third],
              "highest_third": order[len(order) - third:]}
    out["next_rate_by_prior_tercile"] = {
        g: {"pairs": len(v), "prior_weighted_mean": wmean([r["prior_rate"] for r in v], [r["prior_dropbacks"] for r in v]),
            "next_weighted_mean": wmean([r["next_rate"] for r in v], [r["next_dropbacks"] for r in v])}
        for g, v in groups.items() if v}
    return out


def main(source):
    source = Path(source)
    seasons, verification, public_dates, discrepancies = {}, {}, {}, []
    for s in SEASONS:
        stats = read(source / f"stats_player_reg_{s}.csv")
        seasons[s] = research_pass(stats, s)
        acc, last = verification_pass(read(source / f"play_by_play_{s}.csv.gz"))
        public_dates[s] = last
        confirmed = corrected = 0
        for pid, row in seasons[s].items():
            chk = acc.get(pid, {})
            pb = {"attempts": chk.get("attempts", 0), "sacks": chk.get("sacks", 0),
                  "interceptions": chk.get("interceptions", 0)}
            same = all(pb[k] == row[k] for k in pb)
            row["verification"] = "Confirmed two-pass" if same else "Corrected"
            row["verification_detail"] = {k: [row[k], pb[k]] for k in pb}
            if same:
                confirmed += 1
            else:
                corrected += 1
                discrepancies.append({"season": s, "player_id": pid, "name": row["name"],
                                      "stats_file": {k: row[k] for k in pb}, "play_by_play": pb})
                row.update(pb)
                row["dropbacks"] = pb["attempts"] + pb["sacks"]
                row["rate"] = pb["interceptions"] / row["dropbacks"]
        # Second-pass qualifier set from the play-by-play alone (anyone the stats file missed).
        pbp_only = [pid for pid, c in acc.items()
                    if c.get("attempts", 0) + c.get("sacks", 0) >= MIN_DROPBACKS and pid not in seasons[s]
                    and not (s not in PRE_DIVERGENCE and pid in EXCLUDE_POST_DIVERGENCE)]
        verification[s] = {"confirmed": confirmed, "corrected": corrected, "play_by_play_only_qualifiers": pbp_only,
                           "last_regular_season_game": last,
                           "admissible_pre_divergence": last < DIVERGENCE}

    exclude_post = set(EXCLUDE_POST_DIVERGENCE)
    results, pair_tables = {}, {}
    for t in (2010, 2011, 2012, 2013):
        label = "%d->%d" % (t, t + 1)
        exclude = exclude_post if (t + 1) not in PRE_DIVERGENCE else set()
        rows, rel = pair_rows(seasons, t, exclude)
        pair_tables[label] = rows
        results[label] = {"population": "pre-divergence" if (t + 1) in PRE_DIVERGENCE else
                          "post-divergence league population, information only",
                          "excluded_player_ids": sorted(exclude & (set(seasons[t]) | set(seasons[t + 1]))),
                          "season_t_reliability": rel, **fit_pairs(rows)}
    pooled_rows = pair_tables["2010->2011"] + pair_tables["2011->2012"]
    results["pooled_2010_2012"] = {"population": "pre-divergence, both pairs pooled", **fit_pairs(pooled_rows)}
    pooled_rel = {}
    for s in PRE_DIVERGENCE:
        pooled_rel[str(s)] = reliability(list(seasons[s].values()))
    all_pre = [dict(r, rate=r["rate"] - reliability(list(seasons[r["season"]].values()))["league_mean"])
               for s in PRE_DIVERGENCE for r in seasons[s].values()]
    # pooled reliability on within-season deviations (league mean 0 by construction; use pooled mean rate)
    n = [r["dropbacks"] for r in all_pre]
    mean = sum(r["interceptions"] for s in PRE_DIVERGENCE for r in seasons[s].values()) / sum(n)
    observed = wmean([r["rate"] ** 2 for r in all_pre], n)
    binomial = wmean([mean * (1 - mean) / ni for ni in n], n)
    signal = observed - binomial
    pooled_rel["2010_2012_pooled_deviations"] = {
        "qualifier_seasons": len(all_pre), "league_mean": mean, "observed_variance": observed,
        "mean_binomial_variance": binomial, "signal_variance": signal, "signal_sd": math.sqrt(max(signal, 0.0)),
        "k": (mean * (1 - mean) / signal) if signal > 0 else None}

    out = {
        "schema_version": 1,
        "built_by": "scripts/research/build_passer_interception_persistence.py",
        "status": "research only; read by nothing in runtime/",
        "fetch_date": date.today().isoformat(),
        "divergence": DIVERGENCE,
        "excluded_post_divergence": EXCLUDE_POST_DIVERGENCE,
        "preregistered": PREREGISTERED,
        "sources": {name: {"url": url, "sha256": sha(source / name)} for name, url in SOURCES.items()},
        "seasons": {str(s): {"qualifiers": len(seasons[s]), "verification": verification[s],
                             "reliability": reliability(list(seasons[s].values())),
                             "rows": sorted(seasons[s].values(), key=lambda r: r["name"])} for s in SEASONS},
        "reliability_pre_divergence": pooled_rel,
        "discrepancies": discrepancies,
        "results": results,
        "pair_tables": pair_tables,
    }
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for label, r in results.items():
        print(label, r.get("population"), "pairs", r["pairs"])
        for name in ("raw", "shrunk"):
            if name in r:
                f = r[name]
                print("  %-6s corr %.3f slope %.3f (se %.3f) shrunk %.3f int %.4f r2 %.3f loo %.3f keep %s"
                      % (name, f["correlation_unweighted"], f["slope"], f["se"], f["shrunk_slope"], f["intercept"],
                         f["r2"], f["loo"]["skill"], f["keep"]))
        if "season_t_reliability" in r:
            rel = r["season_t_reliability"]
            print("  reliability: mean %.4f obs var %.2e binom var %.2e signal %.2e k %s" % (
                rel["league_mean"], rel["observed_variance"], rel["mean_binomial_variance"], rel["signal_variance"],
                "%.0f" % rel["k"] if rel["k"] else "inf"))
        print("  verdict:", r.get("verdict"))
    print("discrepancies:", len(discrepancies))
    for s in SEASONS:
        print(s, "qualifiers", len(seasons[s]), verification[s])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
