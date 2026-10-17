#!/usr/bin/env python3
"""Build the 2010-2014 (2014 Weeks 1-4) position-usage baseline (plan batch B3d; data only).

  python scripts/research/build_2010_2014_usage_baseline.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_nfl_position_usage_baseline.json. Sources come only through
scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR.

The accumulation is the committed 2012 builder's (scripts/research/build_2012_usage_baseline.py
build and drives), run per season with that season's own positions: the seasonal roster for
2010-2013 and the cut Week 1-4 weekly roster for 2014 (never the current player database).
The 2012 season must reproduce the committed builder's output exactly. Pooling is equal
weight per event: shares from summed counts, rank shapes and per-team-game means from the
pooled team-games. Every share carries a per-season homogeneity test; the fullback rushing
share's trend is flagged. The team-game top-share centres (top receiver's share of targets,
top non-quarterback rusher's share of carries) are added for the 2014.6 band rows.

No club, game, player or date field is written.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2012_usage_baseline as ub  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / "library" / "data" / "2010_2014w4_nfl_position_usage_baseline.json"
COMMITTED_2012 = ROOT / "library" / "data" / "2012_nfl_position_usage_baseline.json"
SEASONS = (2010, 2011, 2012, 2013, 2014)
SCHEMA = "2010-2014w4-nfl-position-usage-baseline-v1"


def raw_rows(season, source, dest):
    """The gated rows as the committed reader yields them (raw strings, REG only)."""
    for r in sources.rows(lb.pbp_name(season, source), dest):
        if source == "nflverse" and r.get("season_type") != "REG":
            continue
        yield r


def positions(season, dest):
    path = sources.source_path(lb.roster_name(season), dest)
    return lb.fp.positions_map(path)


class Patched:
    """Run a committed function with its module's readers bound to one gated season."""

    def __init__(self, season, dest):
        self.season, self.dest = season, dest

    def __enter__(self):
        self.saved = (ub.positions, ub.rows)
        pos = positions(self.season, self.dest)
        ub.positions = lambda _: pos
        ub.rows = lambda _, source: raw_rows(self.season, source, self.dest)
        return self

    def __exit__(self, *exc):
        ub.positions, ub.rows = self.saved


def accumulate(season, source, dest):
    """The committed build loop's accumulators for one season (counts, per-team-game
    counters), so seasons pool by event."""
    pos = positions(season, dest)
    group = lambda pid: ub.GROUPS.get((pos.get(pid) or "").upper(), "OTHER")  # noqa: E731
    T = collections.Counter()
    loss = collections.Counter()
    usage = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    tackles = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    top = {"targets": collections.defaultdict(collections.Counter), "carries": collections.defaultdict(collections.Counter)}
    team_games = set()
    ok, num = ub.ok, ub.num
    for r in raw_rows(season, source, dest):
        play_type = r["play_type"]
        if ok(r.get("posteam")):
            team_games.add((r["game_id"], r["posteam"]))
        T["third_conv"] += num(r, "third_down_converted")
        T["third_fail"] += num(r, "third_down_failed")
        T["first_downs_scrimmage"] += num(r, "first_down_rush") + num(r, "first_down_pass")
        T["first_downs_penalty"] += num(r, "first_down_penalty")
        # Team-game top shares (two-point tries excluded; kneels count as carries).
        if num(r, "two_point_attempt") != 1:
            key = (r["game_id"], r["posteam"])
            if play_type == "pass" and ok(r.get("receiver_player_id")):
                top["targets"][key][r["receiver_player_id"]] += 1
            elif play_type in ("run", "qb_kneel") and ok(r.get("rusher_player_id")) \
                    and (pos.get(r["rusher_player_id"]) or "").upper() != "QB":
                top["carries"][key][r["rusher_player_id"]] += 1
        if play_type not in ("pass", "run"):
            continue
        off = (r["game_id"], r["posteam"])
        dfn = (r["game_id"], r["defteam"])
        if play_type == "run" and ok(r.get("rusher_player_id")):
            pid = r["rusher_player_id"]
            usage[off]["rush:" + group(pid)][pid] += 1
            T["rush"] += 1
            T["rush_" + group(pid)] += 1
            yards = num(r, "yards_gained")
            if yards < 0:
                T["run_negative"] += 1
                loss[min(int(-yards), 6)] += 1
            if num(r, "tackled_for_loss") == 1:
                T["run_tfl_plays"] += 1
        if play_type == "pass" and num(r, "pass_attempt") == 1 and num(r, "sack") != 1 and ok(r.get("passer_player_id")):
            usage[off]["pass"][r["passer_player_id"]] += 1
            if ok(r.get("receiver_player_id")):
                pid = r["receiver_player_id"]
                usage[off]["target:" + group(pid)][pid] += 1
                T["target"] += 1
                T["target_" + group(pid)] += 1
        if ok(r.get("sack_player_id")):
            T["sack_" + group(r["sack_player_id"])] += 1
            T["sack_credit"] += 1
        for key in ("half_sack_1_player_id", "half_sack_2_player_id"):
            if ok(r.get(key)):
                T["sack_" + group(r[key])] += 0.5
                T["sack_credit"] += 0.5
        if ok(r.get("interception_player_id")):
            T["int_" + group(r["interception_player_id"])] += 1
            T["int_credit"] += 1
        for key in ("pass_defense_1_player_id", "pass_defense_2_player_id"):
            if ok(r.get(key)):
                T["pd_" + group(r[key])] += 1
                T["pd_credit"] += 1
        solo = [r.get(f"solo_tackle_{i}_player_id") for i in (1, 2)]
        assist = [r.get(f"assist_tackle_{i}_player_id") for i in (1, 2, 3, 4)]
        assist += [r.get(f"tackle_with_assist_{i}_player_id") for i in (1, 2)]
        solo = [x for x in solo if ok(x)]
        assist = [x for x in assist if ok(x)]
        if solo or assist:
            T["tackled_plays"] += 1
            T["assisted_plays"] += bool(assist)
        for pid in solo + assist:
            T["tackle_" + group(pid)] += 1
            T["tackle_credit"] += 1
            tackles[dfn][group(pid)][pid] += 1
        for key in ("tackle_for_loss_1_player_id", "tackle_for_loss_2_player_id"):
            if ok(r.get(key)):
                T["tfl_" + group(r[key])] += 1
                T["tfl_credit"] += 1
    return {"T": T, "loss": loss, "usage": dict(usage), "tackles": dict(tackles), "team_games": team_games,
            "top": top}


SHARES = {"rush_share": ("rush", ("RB", "QB", "FB", "WR", "TE"), "rush"),
          "target_share": ("target", ("WR", "TE", "RB", "FB"), "target"),
          "tackle_share": ("tackle", ("DB", "LB", "DL"), "tackle_credit"),
          "tfl_share": ("tfl", ("DL", "LB", "DB"), "tfl_credit"),
          "sack_share": ("sack", ("DL", "LB", "DB"), "sack_credit"),
          "interception_share": ("int", ("DB", "LB", "DL"), "int_credit"),
          "pass_defensed_share": ("pd", ("DB", "LB", "DL"), "pd_credit")}
RANKS = (("rush_RB", "rush:RB", 4, "usage"), ("target_WR", "target:WR", 5, "usage"), ("target_TE", "target:TE", 3, "usage"),
         ("target_RB", "target:RB", 3, "usage"), ("tackle_DL", "DL", 7, "tackles"), ("tackle_LB", "LB", 7, "tackles"),
         ("tackle_DB", "DB", 7, "tackles"))


def summarise(acc):
    """The committed build's formulas on (pooled) accumulators."""
    T, loss, usage, tackles = acc["T"], acc["loss"], acc["usage"], acc["tackles"]
    n = len(acc["team_games"])
    passers = [u["pass"] for u in usage.values() if u["pass"]]

    def share(prefix, groups, denominator):
        return {g: round(T[f"{prefix}_{g}"] / T[denominator], 4) for g in groups}
    values = {
        "passing": {
            "qb1_attempt_share": round(statistics.mean(max(p.values()) / sum(p.values()) for p in passers), 4),
            "single_passer_team_game_rate": round(sum(len(p) == 1 for p in passers) / len(passers), 4),
        },
        "assisted_tackle_play_rate": round(T["assisted_plays"] / T["tackled_plays"], 4),
        "negative_run_rate": round(T["run_negative"] / T["rush"], 4),
        "run_tfl_play_rate": round(T["run_tfl_plays"] / T["rush"], 4),
        "negative_run_loss_distribution": {
            str(k) if k < 6 else "6+": round(loss[k] / sum(loss.values()), 4) for k in sorted(loss)},
        "rank_shares": {name: ub.rank_shares([(u if src == "tackles" else u).get(key, collections.Counter())
                                              for u in (tackles if src == "tackles" else usage).values()], depth)
                        for name, key, depth, src in RANKS},
        "third_down_attempts_per_team_game": round((T["third_conv"] + T["third_fail"]) / n, 3),
        "scrimmage_first_downs_per_team_game": round(T["first_downs_scrimmage"] / n, 3),
        "penalty_first_downs_per_team_game": round(T["first_downs_penalty"] / n, 3),
    }
    for name, (prefix, groups, den) in SHARES.items():
        values[name] = share(prefix, groups, den) if T[den] else None
    return values


def merge(accs):
    out = {"T": collections.Counter(), "loss": collections.Counter(), "usage": {}, "tackles": {},
           "team_games": set(), "top": {"targets": {}, "carries": {}}}
    for acc in accs:
        out["T"].update(acc["T"])
        out["loss"].update(acc["loss"])
        out["usage"].update(acc["usage"])
        out["tackles"].update(acc["tackles"])
        out["team_games"] |= acc["team_games"]
        for k in ("targets", "carries"):
            out["top"][k].update(acc["top"][k])
    return out


def top_shares(acc):
    out = {}
    for name, key in (("top_receiver_target_share", "targets"), ("top_rusher_carry_share", "carries")):
        shares = [max(c.values()) / sum(c.values()) for c in acc["top"][key].values() if sum(c.values())]
        out[name] = {"team_games": len(shares), "mean": statistics.mean(shares), "sd": statistics.pstdev(shares)}
    return out


# The committed 2012 block's categories, from the nflverse fixed_drive_result values (its
# 2012 figures are reproduced exactly; an opponent touchdown is left out, as there).
DRIVE_CATEGORY = {"Touchdown": "touchdown", "Field goal": "field_goal", "Punt": "punt", "Turnover": "turnover",
                  "Opp touchdown": None}


def drive_block(seasons, dest):
    """The committed drives() per-result plays and seconds-per-play, collapsed to the committed
    five categories and pooled by drive. Returns (block, raw result counts)."""
    data = collections.defaultdict(lambda: [0, None, None])
    for s in seasons:
        for r in raw_rows(s, "nflverse", dest):
            d = data[(r["game_id"], r["fixed_drive"])]
            if r["play_type"] in ("pass", "run", "qb_kneel", "qb_spike"):
                d[0] += 1
            d[1] = r["fixed_drive_result"]
            d[2] = r["drive_time_of_possession"]
    by = collections.defaultdict(list)
    secs = collections.defaultdict(list)
    raw = collections.Counter()
    for plays, result, top in data.values():
        if plays:
            raw[result] += 1
            category = DRIVE_CATEGORY.get(result, "other")
            if category is None:
                continue
            by[category].append(plays)
            if top and ":" in top:
                m, s_ = top.split(":")
                secs[category].append(int(m) * 60 + int(s_))
    block = {result: {"drives": len(v), "plays_mean": round(statistics.mean(v), 3),
                      "plays_sd": round(statistics.pstdev(v), 3),
                      "seconds_per_play": round(sum(secs[result]) / sum(v), 2)}
             for result, v in sorted(by.items())}
    return block, dict(sorted(raw.items()))


def homogeneity(accs, seasons):
    """Per-season drift of each count share (chi-square on counts) and the fullback trend."""
    out = {}
    for name, (prefix, groups, den) in SHARES.items():
        tests = {}
        for g in groups:
            pairs = [(round(acc["T"][f"{prefix}_{g}"]), round(acc["T"][den])) for acc in accs]
            tests[g] = {"by_season": {lb.TAG[s]: list(p) for s, p in zip(seasons, pairs)},
                        "drift": lb.share_drift(pairs)}
        out[name] = tests
    fb = [(acc["T"]["rush_FB"] / acc["T"]["rush"]) for acc in accs]
    x = list(range(len(fb)))
    mx, my = statistics.mean(x), statistics.mean(fb)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, fb)) / sum((a - mx) ** 2 for a in x)
    out["fullback_rush_share_trend"] = {
        "by_season": {lb.TAG[s]: round(v, 5) for s, v in zip(seasons, fb)},
        "slope_per_season": round(slope, 6),
        "flag": "the fullback rushing share declines across the window; the pooled share overstates 2014 use"
                if slope < 0 else "no decline"}
    return out


def build(dest, log=print):
    errors = []
    # The committed builder on 2012 against this accumulation (regression).
    with Patched(2012, dest):
        committed = ub.build(None, "nflverse")
    acc12 = accumulate(2012, "nflverse", dest)
    mine = summarise(acc12)
    for key, value in mine.items():
        if committed.get(key) != value:
            errors.append("2012 %s differs from the committed builder's output" % key)
    # The committed 2012 "other" row was combined from its results' rounded moments, so its
    # mean and SD can differ from the exact pooled value in the third decimal: counts exact,
    # moments within 0.0015.
    mine12, theirs12 = drive_block((2012,), dest)[0], json.loads(COMMITTED_2012.read_text())["drive_model"]
    if set(mine12) != set(theirs12) or any(
            mine12[k]["drives"] != theirs12[k]["drives"]
            or any(abs(mine12[k][f] - theirs12[k][f]) > 0.0015 for f in ("plays_mean", "plays_sd", "seconds_per_play"))
            for k in theirs12):
        errors.append("the 2012 drive block differs from the committed artifact's")
    block, raw_results = drive_block(SEASONS, dest)
    accs = []
    for s in SEASONS:
        log("usage %s" % lb.TAG[s])
        accs.append(accumulate(s, "nflverse", dest))
    pooled = merge(accs)
    values = summarise(pooled)
    second = merge([accumulate(s, "nflscrapr", dest) for s in SEASONS])
    values2 = summarise(second)
    comparison = []
    for name in SHARES:
        for g, v in (values[name] or {}).items():
            w = (values2.get(name) or {}).get(g)
            status = "within 0.01" if w is not None and abs(v - w) <= 0.01 else "UNEXPLAINED"
            if status == "UNEXPLAINED" and name != "sack_share":
                errors.append("usage second pass %s %s: %s against %s" % (name, g, v, w))
            comparison.append({"share": name, "group": g, "nflverse": v, "nflscrapr": w,
                               "status": status if name != "sack_share" else "informational"})
    artifact = {
        "schema": SCHEMA,
        "seasons": [lb.TAG[s] for s in SEASONS],
        "season_type": "regular",
        "builder": "scripts/research/build_2010_2014_usage_baseline.py",
        "specification_sha256": pre_build_specification.digest(),
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; positions from each season's own roster (2014: the cut Week "
                                 "1-4 weekly roster); no club, game, player or date field."),
        "purpose": json.loads(COMMITTED_2012.read_text())["purpose"],
        "definitions": json.loads(COMMITTED_2012.read_text())["definitions"],
        "sources": {name: {"sha256": sources.load_manifest()["assets"][name]["sha256"]}
                    for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"),
                                                  lb.roster_name(s))},
        "team_games": len(pooled["team_games"]),
        "team_games_by_season": {lb.TAG[s]: len(a["team_games"]) for s, a in zip(SEASONS, accs)},
        "values": values,
        "values_by_season": {lb.TAG[s]: summarise(a) for s, a in zip(SEASONS, accs)},
        "homogeneity": homogeneity(accs, SEASONS),
        "team_game_top_shares": {**top_shares(pooled),
                                 "definition": "per team-game, the top player's share of the club's targets (or non-QB "
                                               "carries, kneels included), two-point tries excluded; positions from "
                                               "each season's own roster"},
        "drive_model": block,
        "drive_model_results": {"counts": raw_results,
                                "rule": "nflverse fixed_drive_result collapsed to the committed categories: Touchdown, "
                                        "Field goal, Punt and Turnover by name; every other result is other; an "
                                        "opponent touchdown is left out (as in the committed 2012 block)"},
        "drive_model_note": json.loads(COMMITTED_2012.read_text())["drive_model_note"],
        "second_pass": {"source": "nflscrapR reg_pbp, the same accumulation", "comparison": comparison,
                        "rule": "pooled shares within 0.01 (sack shares informational: nflscrapR's half-sack "
                                "columns differ)", "result": "pass" if not errors else "fail"},
        "regression_2012": "the committed builder's 2012 output equals this accumulation's 2012 summary, and the 2012 "
                       "drive block equals the committed artifact's (counts exact, moments within 0.0015: the committed "
                       "other row was combined from rounded moments)",
    }
    return artifact, errors


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    artifact, errors = build(args.sources, log=lambda m: print(m, file=sys.stderr))
    if errors:
        for e in errors:
            print("BUILD FAILURE: " + e, file=sys.stderr)
        return 1
    text = render(artifact)
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        return 0 if ok else 1
    OUT.write_text(text)
    print("wrote %s (%d bytes)" % (OUT.relative_to(ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
