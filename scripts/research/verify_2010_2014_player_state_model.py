#!/usr/bin/env python3
"""Pass 2 of the 2010-2014 player-state model (kernel 2014.6, plan batch B4b; research only).

  python scripts/research/verify_2010_2014_player_state_model.py [--sources DIR] [--check]

An independent recomputation, used by the pass-1 builder for its two-pass rules and runnable
on its own. Independent in data and in estimator:
- lines come from the nflscrapR regular-season play-by-play (not the nflverse weekly
  statistics), positions from each season's weekly roster (not the seasonal roster), and
  sacks are credited from the tackle columns of the sack play (nflscrapR has no sacker
  column); the noise moment splits each season into its first and second halves
  (chronological), not odd and even games;
- the lag moments weight every player equally (each player's own mean product at a lag,
  then the mean over players), where pass 1 weights every pair equally;
- the bootstrap draws its own resamples (seeded by family);
- the feedback roles are distinct weeks at depth_team 1 over the season's 16 games
  (4 for 2014 Weeks 1-4), where pass 1 divides by the club's charted weeks.
The grid rule for the carry, the floors and the centring are the specification's and are
shared.

--check recomputes pass 2 and compares it with the second_pass block recorded in
library/data/2010_2014_player_state_model.json, and checks the manifest's digests and the
public table's internal invariants (no club field, append-only shape, the U5 fallback).
The Railway image test reads only the manifest and those invariants. Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2010_2014_player_state_model as ps  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DEF_CREDIT = ("solo_tackle_1_player_id", "solo_tackle_2_player_id", "assist_tackle_1_player_id",
              "assist_tackle_2_player_id", "assist_tackle_3_player_id", "assist_tackle_4_player_id",
              "tackle_for_loss_1_player_id", "tackle_for_loss_2_player_id", "qb_hit_1_player_id", "qb_hit_2_player_id",
              "interception_player_id", "pass_defense_1_player_id", "pass_defense_2_player_id",
              "forced_fumble_player_1_player_id", "forced_fumble_player_2_player_id")
BANDS = ((0, 19, "0_19"), (20, 29, "20_29"), (30, 39, "30_39"), (40, 49, "40_49"), (50, 59, "50_59"), (60, 99, "60_"))


def _id(r, col):
    v = r.get(col) or ""
    return "" if v == "NA" else v


def _f(r, col):
    v = r.get(col)
    try:
        return float(v) if v not in ("", "NA", None) else 0.0
    except ValueError:
        return 0.0


def weekly_positions(season, dest):
    name = "roster_weekly_%s.csv" % lb.TAG[season]
    counts = defaultdict(Counter)
    for r in sources.rows(name, dest):
        if r.get("gsis_id") and r.get("position"):
            counts[r["gsis_id"]][r["position"].strip().upper()] += 1
    return {pid: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for pid, c in counts.items()}


def extract_pass2(dest, log=print):
    raw = {}
    kb = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    kw = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0])))
    for season in ps.SEASONS:
        log("player states pass 2: %s" % lb.TAG[season])
        pos = weekly_positions(season, dest)
        fam_of = lambda pid: ps.family_of_position(pos.get(pid))  # noqa: E731

        def add(fam, pid, game, n, s, club):
            acc = raw.setdefault((fam, pid, season), {"weeks": {}, "clubs": Counter()})
            w = acc["weeks"].setdefault(game, [0.0, 0.0])
            w[0] += n
            w[1] += s
            acc["clubs"][club] += n

        games_seen = set()
        disrupt = defaultdict(float)
        for r in sources.rows(lb.pbp_name(season, "nflscrapr"), dest):
            if r.get("two_point_attempt") == "1" or r.get("play_type") in ("no_play", "", "NA"):
                continue
            ps.assert_cut(season, None, r.get("game_date"))
            game, off, dfn = r["game_id"], r.get("posteam") or "", r.get("defteam") or ""
            epa = _f(r, "epa")
            ptype = r.get("play_type")
            passer, rusher, receiver = _id(r, "passer_player_id"), _id(r, "rusher_player_id"), _id(r, "receiver_player_id")
            if ptype == "pass" and passer and fam_of(passer) == "QB" and (r.get("pass_attempt") == "1" or r.get("sack") == "1"):
                add("QB", passer, game, 1, epa, off)
            if ptype == "run" and r.get("rush_attempt") == "1" and rusher and fam_of(rusher) in ("RB", "WR", "TE"):
                add(fam_of(rusher), rusher, game, 1, epa, off)
            if ptype == "pass" and r.get("pass_attempt") == "1" and r.get("sack") != "1" and receiver \
                    and fam_of(receiver) in ("RB", "WR", "TE"):
                add(fam_of(receiver), receiver, game, 1, epa, off)
            for col in DEF_CREDIT:
                pid = _id(r, col)
                if pid and fam_of(pid) in ("DL", "LB", "DB"):
                    games_seen.add((pid, game, dfn))
            if r.get("sack") == "1":
                solo, a1, a2, hit = (_id(r, "solo_tackle_1_player_id"), _id(r, "assist_tackle_1_player_id"),
                                     _id(r, "assist_tackle_2_player_id"), _id(r, "qb_hit_1_player_id"))
                if solo:
                    disrupt[(solo, game)] += 1.0
                elif a1 or a2:
                    for a in (a1, a2):
                        if a:
                            disrupt[(a, game)] += 0.5
                elif hit:
                    disrupt[(hit, game)] += 1.0
            for col, w in (("qb_hit_1_player_id", 0.5), ("qb_hit_2_player_id", 0.5),
                           ("tackle_for_loss_1_player_id", 1.0), ("tackle_for_loss_2_player_id", 1.0),
                           ("interception_player_id", 1.0), ("pass_defense_1_player_id", 0.5),
                           ("pass_defense_2_player_id", 0.5)):
                pid = _id(r, col)
                if pid:
                    disrupt[(pid, game)] += w
            kicker = _id(r, "kicker_player_id")
            if r.get("field_goal_attempt") == "1" and kicker and fam_of(kicker) == "K" and r.get("kick_distance") not in ("", "NA"):
                d = _f(r, "kick_distance")
                band = next(b for lo, hi, b in BANDS if lo <= d <= hi)
                made = 1 if r.get("field_goal_result") == "made" else 0
                kb[season][band][0] += made
                kb[season][band][1] += 1
                kw[(kicker, season, off)][game][band][0] += made
                kw[(kicker, season, off)][game][band][1] += 1
            punter = _id(r, "punter_player_id")
            if r.get("punt_attempt") == "1" and punter and fam_of(punter) == "P" and r.get("punt_blocked") != "1":
                tb = r.get("touchback") == "1"
                # nflscrapR leaves kick_distance empty on a touchback: the gross is then the
                # distance to the goal line (yardline_100); a punt with neither is not counted.
                gross = (_f(r, "kick_distance") if r.get("kick_distance") not in ("", "NA")
                         else (_f(r, "yardline_100") if tb else None))
                if gross is not None:
                    add("P", punter, game, 1, gross - _f(r, "return_yards") - 20 * tb, off)
            kr = _id(r, "kickoff_returner_player_id")
            if r.get("kickoff_attempt") == "1" and kr:
                add("KR", kr, game, 1, _f(r, "return_yards"), dfn)
            pr = _id(r, "punt_returner_player_id")
            if r.get("punt_attempt") == "1" and pr and r.get("punt_fair_catch") != "1":
                add("PR", pr, game, 1, _f(r, "return_yards"), dfn)
        for pid, game, club in sorted(games_seen):
            add(fam_of(pid), pid, game, 1, disrupt.get((pid, game), 0.0), club)
        rate = {b: (m / a if a else 0.0) for b, (m, a) in kb[season].items()}
        for (kicker, s, club), games in list(kw.items()):
            if s != season:
                continue
            for game, bands in games.items():
                att = sum(a for _, a in bands.values())
                made = sum(m for m, _ in bands.values())
                add("K", kicker, game, att, made - sum(a * rate[b] for b, (_, a) in bands.items()), club)
    return raw


def player_mean_moments(fam_lines):
    """Pass 2's estimator: per player, his mean product at each lag; returned as per-player
    [[mean_k, 1]] so that summing over players gives the equal-player-weight moment."""
    per = ps.player_moments(fam_lines)
    return {pid: [[s / c, 1] if c else [0.0, 0] for s, c in acc] for pid, acc in per.items()}


def fit2(fam, fam_lines):
    moments = player_mean_moments(fam_lines)
    tot = ps.total_moments(moments)
    sb2, su2, rho, sse = ps.fit_covariance(tot)
    boot = ps.bootstrap_su2(moments, "player-state-pass2-" + fam)
    return {"sb2": sb2, "su2": su2, "rho": rho, "sse": sse, "bootstrap": boot, "players": len(moments),
            "lag_moments": [{"lag": k, "moment": (s / c if c else None), "players": c,
                             "fitted": sb2 + (rho ** k) * su2} for k, (s, c) in zip(ps.LAGS, tot)]}


def pass2(dest, info, log=print):
    raw = extract_pass2(dest, log)
    lines, centres, noise = ps.season_lines(raw, split="chrono")
    fams, record = {}, {}
    for fam in ps.FAMILIES:
        f = fit2(fam, lines[fam])
        priors = ps.draft_priors(ps.rookie_lines(lines[fam], info, fam))
        fams[fam] = f
        record[fam] = {"centres": {lb.TAG[s]: centres[(fam, s)] for s in ps.SEASONS if (fam, s) in centres},
                       "noise": {lb.TAG[s]: noise[(fam, s)] for s in ps.SEASONS if (fam, s) in noise},
                       "fit": f, "draft_priors": priors}
    return {"families": fams, "lines": lines, "info": info,
            "record": {"source": "nflscrapR reg_pbp 2010-2014 Weeks 1-4; weekly-roster positions",
                       "estimator": "equal weight per player; chronological split-half noise",
                       "families": record}}


def roles_pass2(dest):
    out = {}
    for season in ps.SEASONS:
        name = "depth_charts_%s.csv" % lb.TAG[season]
        weeks = defaultdict(set)
        for r in sources.rows(name, dest):
            if r.get("game_type") == "REG" and r["depth_team"].strip() == "1" and r.get("gsis_id"):
                weeks[r["gsis_id"]].add(int(r["week"]))
        games = 4 if season == 2014 else 16
        for pid, w in weeks.items():
            out[(pid, season)] = min(1.0, len(w) / games)
    return out


def feedback_pass2(second, caps, dest, families=ps.FAMILIES):
    roles = roles_pass2(dest)
    rows = []
    for fam in families:
        f = second["families"][fam]
        params = {"sb2": f["sb2"], "su2": f["su2"] if f["bootstrap"]["su2_interval"][0] > 0 else 0.0}
        params["rho"] = f["rho"] if params["su2"] > 0 else 0.0
        if params["su2"] == 0:
            moments = player_mean_moments(second["lines"][fam])
            tot = ps.total_moments(moments)
            w = sum(c for _, c in tot)
            params["sb2"] = max(0.0, sum(s for s, _ in tot) / w) if w else 0.0
        priors = second["record"]["families"][fam]["draft_priors"]
        rows += ps.feedback_rows(fam, second["lines"], second["info"], priors, params, roles)
    return ps.feedback_fit(rows, q=caps)


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def invariant_errors(model=None, public=None, manifest=None):
    """Checks that need no source data (the Railway image test reads only these)."""
    model = model if model is not None else json.loads(ps.MODEL_OUT.read_text())
    public = public if public is not None else json.loads(ps.PUBLIC_OUT.read_text())
    manifest = manifest if manifest is not None else json.loads(ps.MANIFEST_OUT.read_text())
    errors = []
    if manifest.get("model_sha256") != hashlib.sha256(ps.MODEL_OUT.read_bytes()).hexdigest():
        errors.append("manifest model digest differs")
    if manifest.get("public_table_sha256") != hashlib.sha256(ps.PUBLIC_OUT.read_bytes()).hexdigest():
        errors.append("manifest public-table digest differs")
    if "kernel" in json.dumps(manifest).lower():
        errors.append("the manifest names a kernel")
    for fam, block in model["families"].items():
        if block["aging"]["adopted"] != "Z":
            errors.append("%s: aging other than Z under the U5 fallback" % fam)
        if block["draft_priors"]["log_pick_slope"]["applied"] != 0.0:
            errors.append("%s: a draft-slot slope is applied under the U5 fallback" % fam)
    for gsis, row in public["players"].items():
        if any(k in row for k in ("club", "team", "name")):
            errors.append("%s: a club or name field in the public table" % gsis)
        for src in row.get("source_rows", ()):
            if src["season"] not in ps.RECORD_SEASONS:
                errors.append("%s: a source row outside 2010-2012" % gsis)
        if "tier" in json.dumps(row):
            errors.append("%s: a tier in the public table (held under U5)" % gsis)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    errors = invariant_errors()
    if args.sources is None or not Path(args.sources).is_dir():
        for e in errors:
            print("INVARIANT FAILURE: " + e, file=sys.stderr)
        print("sources not present: invariants only (%s)" % ("pass" if not errors else "FAIL"))
        return 1 if errors else 0
    info = ps.career_info(args.sources)
    second = pass2(args.sources, info, log=lambda m: print(m, file=sys.stderr))
    recorded = json.loads(ps.MODEL_OUT.read_text())["second_pass"]
    if render(recorded) != render(second["record"]):
        errors.append("the recomputed pass 2 differs from the recorded second_pass block")
    for e in errors:
        print("FAILURE: " + e, file=sys.stderr)
    print("pass 2 %s" % ("reproduced" if not errors else "DIFFERS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
