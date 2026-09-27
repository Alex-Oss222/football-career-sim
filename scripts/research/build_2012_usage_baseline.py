#!/usr/bin/env python3
"""Rebuild the 2012 position-usage baseline from public play-by-play.

Research tool only; the runtime never downloads anything. Fetch the inputs
first (they are large and are not committed):

  nflverse play-by-play (primary):
    https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz
  nflverse 2012 rosters (position map):
    https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2012.csv
  nflscrapR play-by-play (independent verification pass):
    https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_2012.csv

Usage:
  python scripts/research/build_2012_usage_baseline.py SOURCE_DIR > out.json

Only 2012 regular-season plays are read. Nothing from 2013 or later enters
the artifact.
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
import statistics
import sys
from pathlib import Path

GROUPS = {
    "QB": "QB", "RB": "RB", "HB": "RB", "FB": "FB", "WR": "WR", "TE": "TE",
    "T": "OL", "G": "OL", "C": "OL", "OT": "OL", "OG": "OL", "OL": "OL",
    "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL",
    "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
    "CB": "DB", "DB": "DB", "S": "DB", "SS": "DB", "FS": "DB", "SAF": "DB",
    "K": "ST", "P": "ST", "LS": "ST",
}


def ok(value):
    return bool(value) and value != "NA"


def num(row, key):
    value = row.get(key)
    return float(value) if value not in (None, "", "NA") else 0.0


def positions(source_dir):
    counts = collections.defaultdict(collections.Counter)
    with open(source_dir / "roster_2012.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["gsis_id"]:
                counts[row["gsis_id"]][row["position"]] += 1
    return {pid: c.most_common(1)[0][0] for pid, c in counts.items()}


def rows(source_dir, source):
    if source == "nflverse":
        handle = gzip.open(source_dir / "play_by_play_2012.csv.gz", "rt", newline="")
    else:
        handle = open(source_dir / "reg_pbp_2012.csv", newline="")
    with handle:
        for row in csv.DictReader(handle):
            if source == "nflverse" and row["season_type"] != "REG":
                continue
            yield row


def rank_shares(per_game, depth):
    acc = collections.defaultdict(list)
    for counter in per_game:
        values = sorted(counter.values(), reverse=True)
        total = sum(values)
        if total:
            for index in range(depth):
                acc[index].append((values[index] if index < len(values) else 0) / total)
    return [round(sum(acc[i]) / len(acc[i]), 4) for i in range(depth)]


def build(source_dir, source):
    pos = positions(source_dir)
    group = lambda pid: GROUPS.get((pos.get(pid) or "").upper(), "OTHER")
    T = collections.Counter()
    loss = collections.Counter()
    usage = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    tackles = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    team_games = set()
    for r in rows(source_dir, source):
        play_type = r["play_type"]
        if ok(r.get("posteam")):
            team_games.add((r["game_id"], r["posteam"]))
        T["third_conv"] += num(r, "third_down_converted")
        T["third_fail"] += num(r, "third_down_failed")
        T["first_downs_scrimmage"] += num(r, "first_down_rush") + num(r, "first_down_pass")
        T["first_downs_penalty"] += num(r, "first_down_penalty")
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

    n = len(team_games)
    passers = [u["pass"] for u in usage.values() if u["pass"]]
    share = lambda prefix, groups, denominator: {
        g: round(T[f"{prefix}_{g}"] / T[denominator], 4) for g in groups
    }
    return {
        "source": source,
        "team_games": n,
        "passing": {
            "qb1_attempt_share": round(statistics.mean(max(p.values()) / sum(p.values()) for p in passers), 4),
            "single_passer_team_game_rate": round(sum(len(p) == 1 for p in passers) / len(passers), 4),
        },
        "rush_share": share("rush", ("RB", "QB", "FB", "WR", "TE"), "rush"),
        "target_share": share("target", ("WR", "TE", "RB", "FB"), "target"),
        "tackle_share": share("tackle", ("DB", "LB", "DL"), "tackle_credit"),
        "tfl_share": share("tfl", ("DL", "LB", "DB"), "tfl_credit"),
        "sack_share": share("sack", ("DL", "LB", "DB"), "sack_credit") if T["sack_credit"] else None,
        "interception_share": share("int", ("DB", "LB", "DL"), "int_credit"),
        "pass_defensed_share": share("pd", ("DB", "LB", "DL"), "pd_credit"),
        "assisted_tackle_play_rate": round(T["assisted_plays"] / T["tackled_plays"], 4),
        "negative_run_rate": round(T["run_negative"] / T["rush"], 4),
        "run_tfl_play_rate": round(T["run_tfl_plays"] / T["rush"], 4),
        "negative_run_loss_distribution": {
            str(k) if k < 6 else "6+": round(loss[k] / sum(loss.values()), 4) for k in sorted(loss)
        },
        "rank_shares": {
            "rush_RB": rank_shares([u["rush:RB"] for u in usage.values()], 4),
            "target_WR": rank_shares([u["target:WR"] for u in usage.values()], 5),
            "target_TE": rank_shares([u["target:TE"] for u in usage.values()], 3),
            "target_RB": rank_shares([u["target:RB"] for u in usage.values()], 3),
            "tackle_DL": rank_shares([t["DL"] for t in tackles.values()], 7),
            "tackle_LB": rank_shares([t["LB"] for t in tackles.values()], 7),
            "tackle_DB": rank_shares([t["DB"] for t in tackles.values()], 7),
        },
        "third_down_attempts_per_team_game": round((T["third_conv"] + T["third_fail"]) / n, 3),
        "scrimmage_first_downs_per_team_game": round(T["first_downs_scrimmage"] / n, 3),
        "penalty_first_downs_per_team_game": round(T["first_downs_penalty"] / n, 3),
        "counts": {k: v for k, v in sorted(T.items())},
    }


def drives(source_dir):
    """Plays and clock per drive by terminal result (nflverse fixed drives)."""
    data = collections.defaultdict(lambda: [0, None, None])
    for r in rows(source_dir, "nflverse"):
        d = data[(r["game_id"], r["fixed_drive"])]
        if r["play_type"] in ("pass", "run", "qb_kneel", "qb_spike"):
            d[0] += 1
        d[1] = r["fixed_drive_result"]
        d[2] = r["drive_time_of_possession"]
    by = collections.defaultdict(list)
    secs = collections.defaultdict(list)
    for plays, result, top in data.values():
        if plays:
            by[result].append(plays)
            if top and ":" in top:
                m, s = top.split(":")
                secs[result].append(int(m) * 60 + int(s))
    return {
        result: {
            "drives": len(v),
            "plays_mean": round(statistics.mean(v), 3),
            "plays_sd": round(statistics.pstdev(v), 3),
            "seconds_per_play": round(sum(secs[result]) / sum(v), 2),
        }
        for result, v in sorted(by.items())
    }


if __name__ == "__main__":
    src = Path(sys.argv[1])
    print(json.dumps({
        "nflverse": build(src, "nflverse"),
        "nflscrapr": build(src, "nflscrapr"),
        "drives": drives(src),
    }, indent=1))
