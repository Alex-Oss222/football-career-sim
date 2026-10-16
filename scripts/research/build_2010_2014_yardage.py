#!/usr/bin/env python3
"""Build the kernel 2014.6 batch B13 yardage artifact (data only).

  python scripts/research/build_2010_2014_yardage.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_yardage.json and the generated tables of
library/2010_2014_yardage_calibration.md (between its generated markers). Sources come only
through scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR. The committed 2010-2014 aggregate baseline (pinned by sha256 in the
header) must hold the same carries, rushing yards, attempts, completions and sacks as pass 1,
or the build fails: the B13 centres and the base's own aggregate are one count.

What it holds (the R16c band rows of the plan, B13; every value counted here, pass 1 nflverse
through the committed loader, pass 2 nflscrapR by separately written code):

- yards per carry, kneels included (the NFL.com definition): the pooled pair, the team-game
  residual standard deviation of (rushing yards - pooled yards per carry x carries) and the
  mean carries per team-game (the ratio's tolerance 3 x SD / (mean carries x sqrt(n)));
- the completion rate, spikes counted as attempts, and the run share of scrimmage plays,
  (carries + kneels) / (carries + kneels + attempts + spikes + sacks), each with its
  team-game Pearson dispersion (the tolerance 3 x sqrt(phi x p(1-p) / N));
- rushing yards per team-game with its team-game standard deviation;
- the per-snap shape of non-kneel runs: the shares losing yards, gaining 0, 1-3, 4-9, 10-19 and
  20 or more yards (graded rows: losing, 1-3, 20 or more), and completions of 20 or more yards
  per attempt (informational);
- per-season pairs and a drift test for each; the second pass's pooled values against pass
  1's within AGREE_SE standard errors.

Team and game identifiers are read only to count team-games; nothing club-, game-, player- or
date-keyed is written. Stdlib only; deterministic.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (str(HERE), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import build_2012_field_position_model as fp  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402
from runtime import yard_split  # noqa: E402

DATA = ROOT / "library" / "data"
OUT = DATA / "2010_2014w4_yardage.json"
RECORD = ROOT / "library" / "2010_2014_yardage_calibration.md"
AGGREGATE = DATA / "2010_2014w4_nfl_aggregate_baseline.json"
SEASONS = lb.SEASONS
AGREE_SE = 2.0
FIELDS = ("carries", "rush_yards", "attempts", "completions", "sacks")
BINS = yard_split.RUN_BINS
LONG = yard_split.LONG_COMPLETION


def run_bin(yards):
    if yards < 0:
        return 0
    if yards == 0:
        return 1
    if yards <= 3:
        return 2
    if yards <= 9:
        return 3
    if yards <= 19:
        return 4
    return 5


def pair(k, n):
    return [int(k), int(n)]


# ============================================================================ pass 1 (nflverse, committed loader)

def pass1_season(season, dest):
    rows = lb.load_rows(season, "nflverse", dest)
    games = collections.defaultdict(set)
    tg = collections.defaultdict(collections.Counter)
    bins = [0] * len(BINS)
    long_completions = 0
    for r in rows:
        for key in ("home_team", "away_team"):
            if r.get(key):
                games[r["game_id"]].add(fp.alias(r[key]))
        pt = r["play_type"]
        if not (fp.is_off(r) and pt != "no_play"):
            continue
        c = tg[(r["game_id"], fp.alias(r["posteam"]))]
        y = int(r["yards_gained"] or 0)
        if pt == "run":
            c["carries"] += 1
            c["rush_yards"] += y
            bins[run_bin(y)] += 1
        elif pt == "qb_kneel":
            c["carries"] += 1
            c["rush_yards"] += y
        elif pt == "qb_spike":
            c["attempts"] += 1
        elif pt == "pass" and r["sack"] == 1:
            c["sacks"] += 1
        elif pt == "pass":
            c["attempts"] += 1
            if r.get("complete_pass") == 1:
                c["completions"] += 1
                long_completions += y >= LONG
    keys = sorted((g, club) for g, clubs in games.items() for club in clubs)
    return {"team_games": [[tg[k][f] for f in FIELDS] for k in keys], "bins": bins,
            "long_completions": long_completions}


# ============================================================================ pass 2 (nflscrapR, separate code)

def _flag(r, key):
    return (r.get(key) or "").strip() == "1"


def _int(r, key):
    try:
        return int(round(float(r.get(key) or "")))
    except ValueError:
        return 0


def pass2_season(season, dest):
    name = lb.pbp_name(season, "nflscrapr")
    teams_of = collections.defaultdict(set)
    per = collections.defaultdict(lambda: [0] * len(FIELDS))
    bins = [0] * len(BINS)
    long_completions = 0
    for r in sources.rows(name, dest):
        game = (r.get("game_id") or "").strip()
        for key in ("home_team", "away_team"):
            value = (r.get(key) or "").strip()
            if value and value != "NA":
                teams_of[game].add(value)
        play = (r.get("play_type") or "").strip()
        posteam = (r.get("posteam") or "").strip()
        if not posteam or posteam == "NA" or _flag(r, "two_point_attempt"):
            continue
        if play not in ("run", "pass", "qb_kneel", "qb_spike"):
            continue
        line = per[(game, posteam)]
        y = _int(r, "yards_gained")
        if play in ("run", "qb_kneel"):
            line[0] += 1
            line[1] += y
            if play == "run":
                bins[run_bin(y)] += 1
        elif play == "qb_spike":
            line[2] += 1
        elif _flag(r, "sack"):
            line[4] += 1
        else:
            line[2] += 1
            if _flag(r, "complete_pass"):
                line[3] += 1
                long_completions += y >= LONG
    keys = sorted((g, t) for g, ts in teams_of.items() for t in ts)
    return {"team_games": [per[k] if k in per else [0] * len(FIELDS) for k in keys], "bins": bins,
            "long_completions": long_completions}


# ============================================================================ centres

def _sums(lines):
    return [sum(line[i] for line in lines) for i in range(len(FIELDS))]


def _dispersion(lines, k_of, n_of, p):
    """Team-game Pearson dispersion of a binomial share at the pooled p."""
    stat, used = 0.0, 0
    for line in lines:
        n = n_of(line)
        if n <= 0:
            continue
        stat += (k_of(line) - p * n) ** 2 / (p * (1 - p) * n)
        used += 1
    return stat / (used - 1) if used > 1 else 1.0


def centres(p1):
    tags = [lb.TAG[s] for s in SEASONS]
    lines = [line for s in SEASONS for line in p1[s]["team_games"]]
    n = len(lines)
    carries, rush, attempts, completions, sacks = _sums(lines)
    plays = carries + attempts + sacks
    ypc = rush / carries
    residual = [line[1] - ypc * line[0] for line in lines]
    resid_sd = math.sqrt(sum(v * v for v in residual) / (n - 1))
    mean_rush = rush / n
    rush_sd = math.sqrt(sum((line[1] - mean_rush) ** 2 for line in lines) / (n - 1))
    p_comp, p_run = completions / attempts, carries / plays
    by = {t: _sums(p1[s]["team_games"]) + [len(p1[s]["team_games"])] for s, t in zip(SEASONS, tags)}
    bins_by = {t: list(p1[s]["bins"]) for s, t in zip(SEASONS, tags)}
    runs_by = {t: sum(v) for t, v in bins_by.items()}
    bins = [sum(bins_by[t][i] for t in tags) for i in range(len(BINS))]
    runs = sum(bins)
    long_by = {t: p1[s]["long_completions"] for s, t in zip(SEASONS, tags)}
    out = {
        "yards_per_carry": {
            "by_season": {t: pair(v[1], v[0]) for t, v in by.items()}, "pooled": pair(rush, carries),
            "drift": lb.rate_drift([(v[1], v[0]) for v in by.values()]),
            "residual_sd_per_team_game": round(resid_sd, 6), "carries_per_team_game": round(carries / n, 6),
            "definition": "rushing yards per carry, kneels included (the NFL.com definition)"},
        "completion_rate": {
            "by_season": {t: pair(v[3], v[2]) for t, v in by.items()}, "pooled": pair(completions, attempts),
            "drift": lb.share_drift([(v[3], v[2]) for v in by.values()]),
            "dispersion": round(_dispersion(lines, lambda l: l[3], lambda l: l[2], p_comp), 6),
            "definition": "completions per pass attempt, spikes counted as attempts (the pool's own level; "
                          "batch B12 is not built, so no 2014 target)"},
        "run_share": {
            "by_season": {t: pair(v[0], v[0] + v[2] + v[4]) for t, v in by.items()},
            "pooled": pair(carries, plays),
            "drift": lb.share_drift([(v[0], v[0] + v[2] + v[4]) for v in by.values()]),
            "dispersion": round(_dispersion(lines, lambda l: l[0], lambda l: l[0] + l[2] + l[4], p_run), 6),
            "definition": "(carries + kneels) / (carries + kneels + pass attempts + spikes + sacks)"},
        "rushing_yards_per_team_game": {
            "by_season": {t: pair(v[1], v[5]) for t, v in by.items()}, "pooled": pair(rush, n),
            "drift": lb.mean_drift([[len(p1[s]["team_games"]), sum(l[1] for l in p1[s]["team_games"]),
                                     sum(l[1] * l[1] for l in p1[s]["team_games"])] for s in SEASONS]),
            "sd": round(rush_sd, 6), "definition": "rushing yards per team-game, kneels included"},
        "run_bins": {
            "labels": list(BINS), "by_season": bins_by, "pooled": bins,
            "drift": {label: lb.share_drift([(bins_by[t][i], runs_by[t]) for t in tags])
                      for i, label in enumerate(BINS)},
            "definition": "non-kneel runs (play type run, scrambles included) by yards gained"},
        "completions_20_per_attempt": {
            "by_season": {t: pair(long_by[t], by[t][2]) for t in tags},
            "pooled": pair(sum(long_by.values()), attempts),
            "drift": lb.share_drift([(long_by[t], by[t][2]) for t in tags]),
            "definition": "completions of 20 or more yards per pass attempt (spikes counted)"},
        "team_games": n,
    }
    return out


def second_pass_compare(c1, p2):
    lines = [line for s in SEASONS for line in p2[s]["team_games"]]
    carries, rush, attempts, completions, sacks = _sums(lines)
    bins = [sum(p2[s]["bins"][i] for s in SEASONS) for i in range(len(BINS))]
    runs2 = sum(bins)
    long2 = sum(p2[s]["long_completions"] for s in SEASONS)
    rows, disagreements = [], []

    def share(metric, k1, n1, k2, n2):
        p, q = k1 / n1, k2 / n2
        se = math.sqrt(max(p * (1 - p), 1e-9) / n1 + max(q * (1 - q), 1e-9) / n2)
        ok = abs(p - q) <= AGREE_SE * se
        rows.append({"metric": metric, "nflverse": [k1, n1], "nflscrapr": [k2, n2], "within_2se": ok})
        if not ok:
            disagreements.append(metric)

    def ratio(metric, k1, n1, k2, n2, sd1):
        # A per-unit mean (yards per carry, rushing yards per team-game): the
        # standard error from pass 1's team-game spread.
        p, q = k1 / n1, k2 / n2
        se = sd1 * math.sqrt(2.0)
        ok = abs(p - q) <= AGREE_SE * se
        rows.append({"metric": metric, "nflverse": [k1, n1], "nflscrapr": [k2, n2], "within_2se": ok})
        if not ok:
            disagreements.append(metric)

    y = c1["yards_per_carry"]
    n1 = c1["team_games"]
    ratio("yards per carry", y["pooled"][0], y["pooled"][1], rush, carries,
          y["residual_sd_per_team_game"] / (y["carries_per_team_game"] * math.sqrt(n1)))
    r = c1["rushing_yards_per_team_game"]
    ratio("rushing yards per team-game", r["pooled"][0], r["pooled"][1], rush, len(lines), r["sd"] / math.sqrt(n1))
    k, n = c1["completion_rate"]["pooled"]
    share("completion rate", k, n, completions, attempts)
    k, n = c1["run_share"]["pooled"]
    share("run share of scrimmage plays", k, n, carries, carries + attempts + sacks)
    runs1 = sum(c1["run_bins"]["pooled"])
    for i, label in enumerate(BINS):
        share("share of runs %s" % label, c1["run_bins"]["pooled"][i], runs1, bins[i], runs2)
    k, n = c1["completions_20_per_attempt"]["pooled"]
    share("completions of 20+ per attempt", k, n, long2, attempts)
    return {"source": "nflscrapR reg_pbp 2010-2014 (2014 cut), its own play_type, yards_gained, sack, "
                      "complete_pass and two_point_attempt columns, read by separately written code "
                      "(pass2_season)",
            "rule": "a pooled value agrees when the passes differ by at most %.0f standard errors of their "
                    "difference" % AGREE_SE,
            "team_games": len(lines), "comparison": rows, "disagreements": disagreements,
            "agree": not disagreements}


def aggregate_check(c1, aggregate):
    """The B13 pairs against the committed aggregate baseline's (one count)."""
    derived = aggregate["derived"]
    errors = []
    checks = (("yards_per_carry", c1["yards_per_carry"]["pooled"], derived["yards_per_carry"]["pooled"]),
              ("completion_rate", c1["completion_rate"]["pooled"], derived["completion_rate"]["pooled"]),
              ("sacks", [c1["run_share"]["pooled"][1] - c1["yards_per_carry"]["pooled"][1]
                         - c1["completion_rate"]["pooled"][1]], [derived["sack_rate"]["pooled"][0]]))
    for name, mine, theirs in checks:
        if list(mine) != list(theirs):
            errors.append("%s %s differs from the aggregate baseline's %s" % (name, mine, theirs))
    return errors


def build(dest, log=print):
    agg_text = AGGREGATE.read_bytes()
    aggregate = json.loads(agg_text)
    p1, p2 = {}, {}
    for s in SEASONS:
        log("yardage nflverse %s" % lb.TAG[s])
        p1[s] = pass1_season(s, dest)
        log("yardage nflscrapr %s" % lb.TAG[s])
        p2[s] = pass2_season(s, dest)
    errors = []
    tg = {lb.TAG[s]: len(p1[s]["team_games"]) for s in SEASONS}
    if tg != {lb.TAG[s]: v for s, v in zip(SEASONS, (512, 512, 512, 512, 122))}:
        errors.append("team-games per season %s differ from the data window" % tg)
    c1 = centres(p1)
    errors += aggregate_check(c1, aggregate)
    artifact = {
        "schema": yard_split.SCHEMA,
        "seasons": [lb.TAG[s] for s in SEASONS],
        "season_type": "regular",
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; no club, game, player or date field. 2013 and 2014 Weeks 1-4 "
                                 "are an anonymous post-divergence league population (pooled only)."),
        "builder": "scripts/research/build_2010_2014_yardage.py",
        "pre_build_specification_sha256": pre_build_specification.digest(),
        "aggregate_baseline_sha256": hashlib.sha256(agg_text).hexdigest(),
        "band_centres": c1,
        "tolerances": {
            "yards_per_carry": "3 x residual_sd_per_team_game / (carries_per_team_game x sqrt(team-games))",
            "completion_rate": "3 x sqrt(dispersion x p(1-p) / attempts)",
            "run_share": "3 x sqrt(dispersion x p(1-p) / plays)",
            "rushing_yards_per_team_game": "3 x sd / sqrt(team-games)",
            "run_bins": "3 x sqrt(p(1-p) / runs) (binomial)",
        },
        "graded_bins": ["loss", "1-3", "20+"],
        "second_pass": second_pass_compare(c1, p2),
    }
    if not artifact["second_pass"]["agree"]:
        log("pass 2 disagrees on: %s" % ", ".join(artifact["second_pass"]["disagreements"]))
    manifest = sources.load_manifest()
    artifact["sources"] = {name: {"sha256": manifest["assets"][name]["sha256"]}
                           for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"))}
    return artifact, errors


# ============================================================================ the library record

BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def _r(p):
    return p[0] / p[1] if p[1] else float("nan")


def tables(art):
    c = art["band_centres"]
    n = c["team_games"]
    lines = ["Generated by `scripts/research/build_2010_2014_yardage.py` from the artifact; do not edit.", "",
             "| Centre | Count | Of | Value | Spread | Tolerance at 500 team-games | Season drift p |",
             "|---|---|---|---|---|---|---|"]
    y = c["yards_per_carry"]
    lines.append("| yards per carry (kneels included) | %d | %d | %.4f | residual SD %.3f, %.3f carries per team-game "
                 "| %.4f | %s |" % (y["pooled"][0], y["pooled"][1], _r(y["pooled"]), y["residual_sd_per_team_game"],
                                    y["carries_per_team_game"],
                                    3 * y["residual_sd_per_team_game"] / (y["carries_per_team_game"] * math.sqrt(500)),
                                    "%.4f" % y["drift"]["p"]))
    for name, label in (("completion_rate", "completion rate (spikes as attempts)"),
                        ("run_share", "run share of scrimmage plays")):
        per500 = c[name]["pooled"][1] / n * 500
        e = c[name]
        p = _r(e["pooled"])
        lines.append("| %s | %d | %d | %.4f | dispersion %.3f | %.4f | %.4f |" % (
            label, e["pooled"][0], e["pooled"][1], p, e["dispersion"],
            3 * math.sqrt(e["dispersion"] * p * (1 - p) / per500), e["drift"]["p"]))
    r = c["rushing_yards_per_team_game"]
    lines.append("| rushing yards per team-game | %d | %d | %.3f | team-game SD %.3f | %.3f | %s |" % (
        r["pooled"][0], r["pooled"][1], _r(r["pooled"]), r["sd"], 3 * r["sd"] / math.sqrt(500),
        "%.4f" % r["drift"]["p"] if r["drift"]["p"] is not None else "-"))
    b = c["run_bins"]
    runs = sum(b["pooled"])
    per500 = runs / n * 500
    for i, label in enumerate(b["labels"]):
        p = b["pooled"][i] / runs
        graded = label in art["graded_bins"]
        lines.append("| share of non-kneel runs %s%s | %d | %d | %.4f | binomial | %s | %.4f |" % (
            label, "" if graded else " (informational)", b["pooled"][i], runs, p,
            "%.4f" % (3 * math.sqrt(p * (1 - p) / per500)) if graded else "-", b["drift"][label]["p"]))
    e = c["completions_20_per_attempt"]
    lines.append("| completions of 20+ yards per attempt (informational) | %d | %d | %.4f | - | - | %.4f |" % (
        e["pooled"][0], e["pooled"][1], _r(e["pooled"]), e["drift"]["p"]))
    lines += ["", "| Season | Team-games | Carries | Rushing yards | Attempts | Completions | Runs losing | Runs 20+ |",
              "|---|---|---|---|---|---|---|---|"]
    for t, ypc in y["by_season"].items():
        comp = c["completion_rate"]["by_season"][t]
        bins = b["by_season"][t]
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d |" % (
            t, r["by_season"][t][1], ypc[1], ypc[0], comp[1], comp[0], bins[0], bins[5]))
    sp = art["second_pass"]
    lines += ["", "**Second pass (nflscrapR)**, %d team-games." % sp["team_games"], "",
              "| Metric | nflverse | nflscrapR | Within 2 SE |", "|---|---|---|---|"]
    for row in sp["comparison"]:
        lines.append("| %s | %d/%d | %d/%d | %s |" % (row["metric"], row["nflverse"][0], row["nflverse"][1],
                                                      row["nflscrapr"][0], row["nflscrapr"][1],
                                                      "yes" if row["within_2se"] else "no"))
    lines += ["", "Disagreements: %s." % (", ".join(sp["disagreements"]) or "none")]
    return "\n".join(lines) + "\n"


def render_record(art, text):
    if BEGIN not in text or END not in text:
        raise ValueError("%s lacks its generated markers" % RECORD)
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + tables(art) + END + tail


def render(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    spec_errors = pre_build_specification.check()
    if spec_errors:
        for e in spec_errors:
            print("SPECIFICATION: " + e, file=sys.stderr)
        return 1
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    art, errors = build(args.sources, log=lambda m: print(m, file=sys.stderr))
    if errors:
        for e in errors:
            print("BUILD FAILURE: " + e, file=sys.stderr)
        return 1
    text = render(art)
    record = render_record(art, RECORD.read_text())
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        ok_md = RECORD.read_text() == record
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        print("%s %s (generated tables)" % ("reproduced" if ok_md else "DIFFERS", RECORD.relative_to(ROOT)))
        return 0 if ok and ok_md else 1
    OUT.write_text(text)
    RECORD.write_text(record)
    print("wrote %s (%d bytes) and the tables of %s" % (OUT.relative_to(ROOT), len(text), RECORD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
