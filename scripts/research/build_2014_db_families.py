#!/usr/bin/env python3
"""Build the 2014 defensive-back families (kernel 2014.6 batch B15, W2b; data only).

  python scripts/research/build_2014_db_families.py [--sources DIR] [--check]

Writes library/data/2014_db_families.json: for every defensive back a 2014
background TeamInput can carry from Week 5 (the Week 1 library, the in-season
rails base and rows), his position family, corner or safety, and the
contemporaneous label the TeamInput takes; and the nickel roles the clubs'
Week 1 charts label. runtime.depth_library.relabel_defensive_backs applies it
from the in-season rails' first week (2014 Week 5) under a kernel that seats
defensive backs by family (profile flag db_slots); Weeks 1 to 4 and the Week 1
library itself are unchanged (the in-season rails pin the library's clubs
block, and the closed weeks' packages must rebuild unchanged).

The rule (plan batch B15, W2b; library/2014_6_pre_build_specification.md
section 4, "Inputs and participation"): the chart slot first (LCB, RCB, CB,
NB, NCB, NKL a corner; SS, FS, S a safety), then the contemporaneous 2014
weekly-roster label; never the nflverse depth-chart ``position`` column (a
back-filled field) or players.csv. A player neither source settles keeps the
in-season rails' stated position (the Week 1 chart's, the weekly roster's or
the source's, runtime/rails.py), counted.

- Pass 1: the committed Week 1 library's ``slots`` field
  (library/data/2014_week1_depth_charts.json), by gsis id.
- Pass 2, independent: the gated nflverse depth chart
  (depth_charts_2014w4.csv through scripts/research/sources_2010_2014.py,
  Week 1, regular season, defense rows), its slot labels read afresh by gsis
  id. It must give every library player the family pass 1 gives (the builder
  stops otherwise) and supplies the clubs of the nickel labels.
- The weekly label: the gated weekly roster (roster_weekly_2014w4.csv, regular
  season, Weeks 1 to 4), the player's latest week (ties by club code).

The verification block counts each basis and lists every player whose chart
slot and weekly label disagree (the slot decides). No statistic, grade or
football judgement is read or written. Stdlib only.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sources_2010_2014 as sources  # noqa: E402
from runtime.usage import group  # noqa: E402

OUT = ROOT / "library" / "data" / "2014_db_families.json"
LIBRARY = ROOT / "library" / "data" / "2014_week1_depth_charts.json"
RAILS = ROOT / "library" / "data" / "2014_inseason_rails"
DEPTH_SOURCE = "depth_charts_2014w4.csv"
ROSTER_SOURCE = "roster_weekly_2014w4.csv"
CORNER_SLOTS = ("LCB", "RCB", "CB", "NB", "NCB", "NKL")
SAFETY_SLOTS = ("SS", "FS", "S")
NICKEL_SLOTS = ("NB", "NCB", "NKL")
CORNER_LABELS = ("CB",)
SAFETY_LABELS = ("S", "SS", "FS", "SAF")
SLOT = re.compile(r"^([A-Z]+?)(\d+)$")


def slot_family(label):
    if label in CORNER_SLOTS:
        return "corner"
    if label in SAFETY_SLOTS:
        return "safety"
    return None


def label_family(label):
    label = str(label or "").upper()
    if label in CORNER_LABELS:
        return "corner"
    if label in SAFETY_LABELS:
        return "safety"
    return None


def best_slot(slots):
    """(label, depth) of the best-ranked family slot among (label, depth)
    pairs (lowest depth, then the listed order), or None."""
    ranked = [(depth, i, label) for i, (label, depth) in enumerate(slots) if slot_family(label)]
    if not ranked:
        return None
    depth, _, label = min(ranked)
    return label, depth


def library_slots(library):
    """{gsis: (club code, player id, library position, [(label, depth)])}: pass 1."""
    out = {}
    for club in library["clubs"].values():
        for p in club["players"]:
            if not p.get("gsis_id"):
                continue
            pairs = []
            for token in str(p.get("slots") or "").split(","):
                m = SLOT.match(token.strip())
                if m:
                    pairs.append((m.group(1), int(m.group(2))))
            out[p["gsis_id"]] = (club["code"], p["player_id"], p["position"], pairs)
    return out


def chart_slots(dest):
    """{gsis: [(label, depth, club code)]} from the Week 1 defense rows of
    the gated depth chart: pass 2."""
    out = collections.defaultdict(list)
    for r in sources.rows(DEPTH_SOURCE, dest):
        if r.get("game_type") != "REG" or int(r["week"]) != 1 or r.get("formation") != "Defense":
            continue
        label = (r.get("depth_position") or "").strip()
        if label and r.get("gsis_id"):
            out[r["gsis_id"]].append((label, int(r["depth_team"]), r["club_code"]))
    return out


def weekly_labels(dest):
    """{gsis: (week, club, label)}: the latest regular-season week of 2014
    Weeks 1-4 on the gated weekly roster (ties by club code)."""
    out = {}
    for r in sources.rows(ROSTER_SOURCE, dest):
        if r.get("game_type") != "REG" or not r.get("gsis_id"):
            continue
        key = (int(r["week"]), r.get("team") or "", (r.get("position") or "").strip())
        if r["gsis_id"] not in out or key > out[r["gsis_id"]]:
            out[r["gsis_id"]] = key
    return out


def rails_positions():
    """{gsis: (player id, position)} of the in-season rails' base corrections,
    practice squads and rows (the newcomers a background TeamInput may carry)."""
    manifest = json.loads((RAILS / "manifest.json").read_text(encoding="utf-8"))
    base = json.loads((RAILS / manifest["base"]["path"]).read_text(encoding="utf-8"))
    out = {}
    for corr in base.get("corrections", ()):
        out.setdefault(corr["uid"], (corr["player_id"], corr["position"]))
    for club in base["clubs"].values():
        for p in club.get("practice_squad", ()):
            out.setdefault(p["uid"], (p["player_id"], p["position"]))
    for shard in manifest["shards"]:
        for row in json.loads((RAILS / shard["path"]).read_text(encoding="utf-8"))["rows"]:
            if row.get("uid") and row.get("position") and row.get("player_id"):
                out.setdefault(row["uid"], (row["player_id"], row["position"]))
    return out, manifest


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(dest):
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    pass1 = library_slots(library)
    pass2 = chart_slots(dest)
    weekly = weekly_labels(dest)
    rails, manifest = rails_positions()
    # Every library or rails player whose kernel group is the defensive backs.
    universe = {}
    for gsis, (code, pid, position, _) in pass1.items():
        if group(position) == "DB":
            universe[gsis] = (pid, position, "library")
    for gsis, (pid, position) in rails.items():
        if group(position) == "DB" and gsis not in universe:
            universe[gsis] = (pid, position, "rails")
    players, disagree, stops = {}, [], []
    basis_count = collections.Counter()
    for gsis in sorted(universe):
        pid, fallback, origin = universe[gsis]
        chart = best_slot(pass1[gsis][3]) if gsis in pass1 else None
        if gsis in pass1:
            # Pass 2 must agree on the family of every library player.
            raw = best_slot([(label, depth) for label, depth, _ in pass2.get(gsis, ())])
            if (slot_family(chart[0]) if chart else None) != (slot_family(raw[0]) if raw else None):
                stops.append("%s (%s): library slot %s, raw chart slot %s" % (pid, gsis, chart, raw))
        week = weekly.get(gsis)
        weekly_label = week[2] if week else None
        if chart is not None:
            family, basis = slot_family(chart[0]), "chart_slot"
            position = "CB" if family == "corner" else chart[0]
            if label_family(weekly_label) and label_family(weekly_label) != family:
                disagree.append({"player_id": pid, "gsis_id": gsis, "chart_slot": "%s%d" % chart,
                                 "weekly_label": weekly_label})
        elif label_family(weekly_label):
            family, basis = label_family(weekly_label), "weekly_roster"
            position = "CB" if family == "corner" else weekly_label.upper()
        elif label_family(fallback):
            family, basis = label_family(fallback), "rails_position"
            position = "CB" if family == "corner" else str(fallback).upper()
        else:
            family, basis, position = None, "none", None
        basis_count[basis] += 1
        if family is None:
            continue
        players[gsis] = {"player_id": pid, "family": family, "position": position, "basis": basis,
                         "chart_slot": "%s%d" % chart if chart else None, "weekly_label": weekly_label,
                         "weekly_week": week[0] if week else None, "origin": origin}
    if stops:
        raise SystemExit("pass 2 disagrees with pass 1 on %d families:\n  " % len(stops) + "\n  ".join(stops[:20]))
    nickel = collections.defaultdict(list)
    for gsis, rows in sorted(pass2.items()):
        for label, depth, code in rows:
            if label in NICKEL_SLOTS and gsis in pass1 and pass1[gsis][0] == code and gsis in players:
                if gsis not in nickel[code]:
                    nickel[code].append(gsis)
    relabelled = sum(1 for gsis, rec in players.items()
                     if rec["origin"] == "library" and rec["position"] != universe[gsis][1])
    return {
        "schema_version": 1,
        "season": 2014,
        "status": "PREPARED, GATED",
        "effective_from_week": int(manifest["effective_from_week"]),
        "builder": "scripts/research/build_2014_db_families.py",
        "rule": ("chart slot first (LCB, RCB, CB, NB, NCB, NKL a corner; SS, FS, S a safety: the best-ranked "
                 "family slot of the player's Week 1 chart rows), then the 2014 weekly-roster label of his latest "
                 "regular-season week in Weeks 1-4 (CB a corner; S, SS, FS, SAF a safety), then the in-season "
                 "rails' stated position; never the depth chart's position column or players.csv. A corner's "
                 "label is CB; a safety keeps his deciding safety label. Nickel: a Week 1 chart NB, NCB or NKL "
                 "slot at the player's own branch club. No chart in the source labels an outside reserve."),
        "sources": {
            "week1_library": {"path": "library/data/2014_week1_depth_charts.json",
                              "sha256": sha256_file(LIBRARY)},
            "inseason_rails_manifest": {"path": "library/data/2014_inseason_rails/manifest.json",
                                        "sha256": sha256_file(RAILS / "manifest.json")},
            DEPTH_SOURCE: {"sha256": sha256_file(sources.source_path(DEPTH_SOURCE, dest)),
                           "scope": "2014 Week 1, REG, Defense rows (pass 2)"},
            ROSTER_SOURCE: {"sha256": sha256_file(sources.source_path(ROSTER_SOURCE, dest)),
                            "scope": "2014 REG Weeks 1-4, the latest week per player"},
        },
        "players": players,
        "nickel": {code: ids for code, ids in sorted(nickel.items())},
        "outside_reserve": {},
        "verification": {
            "basis": dict(sorted(basis_count.items())),
            # The build stops on any difference, so every library player agrees.
            "pass2_family_agreement": "%d library defensive backs, every family the same in both passes" % (
                sum(1 for g in universe if g in pass1)),
            "chart_and_weekly_disagree": disagree,
            "library_positions_relabelled": relabelled,
        },
    }


def render(data):
    return json.dumps(data, indent=1, sort_keys=True) + "\n"


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
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print("wrote %s (%d bytes)" % (OUT.relative_to(ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
