#!/usr/bin/env python3
"""Build the 2013-2014 participation structure (plan batch B3d; data only, informational).

  python scripts/research/build_2013_2014_participation_structure.py [--sources DIR] [--check]

Writes library/data/2013_2014_participation_structure.json: anonymous league structure of who
takes the snaps within a position group, from the nflverse snap counts. These are published
from 2013, so the window is the 2013 regular season and 2014 Weeks 1-4. Sources come only
through scripts/research/sources_2010_2014.py (the batch B2 gate).

Informational centres only: no kernel coefficient reads this file. The participation slot
convention (runtime/participation.py SCRIMMAGE_SLOT_MIX) is unchanged (decision 1B.4), and
no per-rank snap vector is derived from it. Positions are contemporaneous: each player's
position on that season-week's weekly roster, joined by the PFR id or, where the
roster has none, by club and normalised name. They never come from the
depth-chart position or the current player database. A player without a weekly-roster join
keeps the snap-count file's own label, and those rows are counted. The second pass recomputes
the defensive-back structure with the snap-count file's own labels.

Contents:
- the snap share by rank within each position group per team-game;
- the family (corner or safety) of the fifth and sixth defensive backs;
- the corner and safety make-up of the top four defensive backs;
- absence absorption: when a top-four defensive back of a club's previous game plays no
  defensive snap, who enters the top four (same family or not; moved up from the previous
  game's rotation, or new).

No club, game, player or date field is written.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
OUT = ROOT / "library" / "data" / "2013_2014_participation_structure.json"
SEASONS = (2013, 2014)
GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "HB": "RB", "WR": "WR", "TE": "TE", "T": "OL", "G": "OL", "C": "OL",
         "OT": "OL", "OG": "OL", "OL": "OL", "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "LB": "LB", "OLB": "LB",
         "ILB": "LB", "MLB": "LB", "CB": "DB", "DB": "DB", "S": "DB", "SS": "DB", "FS": "DB", "SAF": "DB"}
FAMILY = {"CB": "CB", "DB": "CB", "S": "S", "SS": "S", "FS": "S", "SAF": "S"}
DEPTH = {"QB": 2, "RB": 3, "WR": 6, "TE": 3, "OL": 7, "DL": 7, "LB": 5, "DB": 7}
SIDE = {g: ("offense" if g in ("QB", "RB", "WR", "TE", "OL") else "defense") for g in DEPTH}


SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv|v)\b")


def norm_name(name):
    text = re.sub(r"[^a-z ]", "", (name or "").lower().replace("-", " "))
    return " ".join(SUFFIX.sub("", text).split())


def weekly_positions(season, dest):
    """Contemporaneous positions: (week, PFR id) and, where the weekly roster has no PFR id,
    (week, club, normalised name)."""
    by_id, by_name = {}, {}
    for r in sources.rows(lb.roster_name(season) if season == 2014 else "roster_weekly_%d.csv" % season, dest):
        if r.get("game_type") not in ("REG", None, ""):
            continue
        week = int(r["week"])
        if r.get("pfr_id"):
            by_id[(week, r["pfr_id"])] = r.get("position") or ""
        by_name[(week, lb.fp.alias(r.get("team") or ""), norm_name(r.get("full_name")))] = r.get("position") or ""
    return by_id, by_name


def team_games(season, dest, label_source):
    """{(club, week): [(player key, position, offense snaps, defense snaps, team offense, team defense)]}"""
    by_id, by_name = weekly_positions(season, dest)
    name = "snap_counts_2014w4.csv" if season == 2014 else "snap_counts_%d.csv" % season
    games = collections.defaultdict(list)
    joined = unjoined = 0
    for r in sources.rows(name, dest):
        if r.get("game_type") != "REG":
            continue
        week = int(r["week"])
        label = by_id.get((week, r.get("pfr_player_id") or "")) or by_name.get(
            (week, lb.fp.alias(r["team"]), norm_name(r.get("player"))))
        if label_source == "weekly_roster" and label:
            joined += 1
        else:
            if label_source == "weekly_roster":
                unjoined += 1
            label = r.get("position") or ""
        off = float(r.get("offense_snaps") or 0)
        dfn = float(r.get("defense_snaps") or 0)
        off_pct = float(r.get("offense_pct") or 0)
        def_pct = float(r.get("defense_pct") or 0)
        games[(lb.fp.alias(r["team"]), week)].append(
            (r.get("pfr_player_id") or r.get("player"), label, off, dfn, off / off_pct if off_pct >= 0.5 else None,
             dfn / def_pct if def_pct >= 0.5 else None))
    return games, joined, unjoined


def team_total(players, index):
    values = sorted(p[index] for p in players if p[index] is not None)
    return values[len(values) // 2] if values else None


def structure(games_by_season):
    rank = {g: [[0.0, 0] for _ in range(DEPTH[g])] for g in DEPTH}
    db5 = collections.Counter()
    db6 = collections.Counter()
    top4 = collections.Counter()
    absorb = collections.Counter()
    team_game_count = 0
    for season, games in games_by_season.items():
        previous = {}
        for (club, week) in sorted(games, key=lambda k: (k[0], k[1])):
            players = games[(club, week)]
            team_game_count += 1
            totals = {"offense": team_total(players, 4), "defense": team_total(players, 5)}
            for g in DEPTH:
                side = SIDE[g]
                total = totals[side]
                if not total:
                    continue
                snaps = sorted((p[2] if side == "offense" else p[3] for p in players
                                if GROUP.get(p[1]) == g), reverse=True)
                for i in range(DEPTH[g]):
                    rank[g][i][0] += (snaps[i] if i < len(snaps) else 0) / total
                    rank[g][i][1] += 1
            dbs = sorted(((p[3], p[0], FAMILY.get(p[1], "CB")) for p in players
                          if GROUP.get(p[1]) == "DB" and p[3] > 0), reverse=True)
            if len(dbs) >= 5:
                db5[dbs[4][2]] += 1
            if len(dbs) >= 6:
                db6[dbs[5][2]] += 1
            if len(dbs) >= 4:
                top4["%d CB / %d S" % (sum(f == "CB" for _, _, f in dbs[:4]), sum(f == "S" for _, _, f in dbs[:4]))] += 1
            current_top = {k: f for _, k, f in dbs[:4]}
            played = {k for _, k, _ in dbs}
            prev = previous.get(club)
            if prev is not None:
                prev_top, prev_played = prev
                absent = [k for k in prev_top if k not in played]
                entrants = [k for k in current_top if k not in prev_top]
                for k in absent:
                    family = prev_top[k]
                    if not entrants:
                        absorb["no top-four entrant"] += 1
                        continue
                    same = [e for e in entrants if current_top[e] == family]
                    entrant = same[0] if same else entrants[0]
                    absorb["%s family, %s" % ("same" if same else "other",
                                              "moved up" if entrant in prev_played else "new")] += 1
            previous[club] = (current_top, played)
    return {
        "team_games": team_game_count,
        "rank_shares": {g: [round(s / n, 4) if n else None for s, n in rank[g]] for g in DEPTH},
        "db5_family": dict(sorted(db5.items())),
        "db6_family": dict(sorted(db6.items())),
        "top4_make_up": dict(sorted(top4.items())),
        "absence_absorption": dict(sorted(absorb.items())),
    }


def build(dest):
    primary, joins = {}, {}
    for s in SEASONS:
        games, joined, unjoined = team_games(s, dest, "weekly_roster")
        primary[s] = games
        joins[lb.TAG[s]] = {"weekly_roster_joined": joined, "snap_file_label": unjoined}
    second = {s: team_games(s, dest, "snap_file")[0] for s in SEASONS}
    a = structure(primary)
    b = structure(second)
    by_season = {lb.TAG[s]: structure({s: primary[s]}) for s in SEASONS}
    return {
        "schema": "2013-2014-participation-structure-v1",
        "builder": "scripts/research/build_2013_2014_participation_structure.py",
        "specification_sha256": pre_build_specification.digest(),
        "status": "informational centres only: no kernel coefficient reads this file; SCRIMMAGE_SLOT_MIX unchanged "
                  "(decision 1B.4)",
        "information_boundary": ("nflverse snap counts, 2013 regular season and 2014 Weeks 1-4 (cut at fetch); "
                                 "contemporaneous weekly-roster positions; anonymous league structure; no club, game, "
                                 "player or date field."),
        "sources": {name: {"sha256": sources.load_manifest()["assets"][name]["sha256"]}
                    for name in ("snap_counts_2013.csv", "snap_counts_2014w4.csv", "roster_weekly_2013.csv",
                                 "roster_weekly_2014w4.csv")},
        "definitions": {
            "rank_shares": "per team-game, the group's players ranked by their side's snaps; each rank's snaps over "
                           "the club's team snaps (the median of snaps / share over players at 50% or more)",
            "db_family": "corner (CB, DB) or safety (S, SS, FS, SAF) from the weekly roster label",
            "absence_absorption": "a defensive back in the club's previous game's top four with no defensive snap in "
                                  "this game; the top-four entrant of his family if any, else another entrant; moved up "
                                  "= the entrant played in the previous game",
        },
        "position_joins": joins,
        "pooled": a,
        "by_season": by_season,
        "second_pass_snap_file_labels": b,
    }


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
    text = render(build(args.sources))
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        return 0 if ok else 1
    OUT.write_text(text)
    print("wrote %s (%d bytes)" % (OUT.relative_to(ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
