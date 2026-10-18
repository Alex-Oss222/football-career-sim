#!/usr/bin/env python3
"""Build the 2014 listed player identity (reader data only).

  python scripts/research/build_2014_listed_player_identity.py [SOURCE_DIR] [--check]

SOURCE_DIR (default $LISTED_IDENTITY_SOURCES) holds three pinned public
nflverse files: the two the in-season rails pin (library/2014_inseason_rails.md)
and the 2013 season roster the league player database pins
(career/2014/League/personnel/league_database_report.md):

  nflverse/roster_weekly_2014.csv  sha256 331022cd3b0c69d99c581f02b6fde6853e87ac431739c4b49841ee6e02893d6c
  nflverse/players.csv             sha256 e85b2736908bd6701b038d18d98025e2b31e6e9db7cebf6f21e71fb0c88f9ba1
  nflverse/roster_2013.csv         sha256 abf73c2b1ef10914af78f6b7397338508bd0c9f0372d2f0667a630e06a4484ed

Writes library/data/2014_listed_player_identity.json: for each gsis id, the
listed height (inches), weight (lb), college and jersey number that the
league player cards (runtime/player_cards.py) show. Rules:

- Information gate: only 2014 regular-season rows of Weeks 1 to 4 are read
  from the weekly roster file; later weeks are never opened into the output.
- Height, weight and college: the player's latest Weeks 1-4 row carrying the
  field (college falls back to the public player file when every Weeks 1-4
  row leaves it blank). A player with no Weeks 1-4 row takes his 2013 season
  roster listing, the row of his latest 2013 week (``listing: "roster_2013"``);
  with neither, the public player file (``listing: "player_file"``): its
  college, and its height and weight only when his last listed season there
  is 2013 or earlier, so that no listing later than the record is shown.
  Fallback listings are kept only for gsis ids that a committed identity
  source of this repository names (the 2014 identity map, the birth-date
  registry, the 2014 Week 1 rosters, the league player database). Text is
  HTML-unescaped ("Texas A&amp;M" in the weekly file reads "Texas A&M").
  Heights outside 60-90 inches and weights outside 150-400 lb are dropped as
  unusable.
- Number: the jersey number of his latest Weeks 1-4 row, with that row's club
  (``number_basis``, club codes normalized to the repository's codes) and
  week; and, when a Weeks 1-4 row lists him with the real 2014 Jaguars, that
  number as ``jaguars_number``. Which number a card shows is the runtime's
  rule (runtime/player_cards.py); Jacksonville has not recorded jersey numbers
  of its own.
- 2013 number: for every listed player in the 2013 season roster, the jersey
  number of his latest 2013 week's row (``number_2013``), with that row's club
  (normalized) and week (``number_2013_basis``). The career tables' "#"
  column reads it for a 2013 season row only when the club matches.

No statistic, grade or football judgement is read or written. --check
rebuilds from the sources and compares with the committed file. The runtime
reads only the committed JSON. Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library" / "data" / "2014_listed_player_identity.json"
ROSTER = ("nflverse/roster_weekly_2014.csv", "331022cd3b0c69d99c581f02b6fde6853e87ac431739c4b49841ee6e02893d6c")
PLAYERS = ("nflverse/players.csv", "e85b2736908bd6701b038d18d98025e2b31e6e9db7cebf6f21e71fb0c88f9ba1")
ROSTER_2013 = ("nflverse/roster_2013.csv", "abf73c2b1ef10914af78f6b7397338508bd0c9f0372d2f0667a630e06a4484ed")
SOURCES = (ROSTER, PLAYERS, ROSTER_2013)
# The player file's height and weight are its latest listing: shown only when that listing
# cannot postdate the record (his last listed season there is 2013 or earlier).
PLAYER_FILE_LAST_SEASON = 2013
SEASON = 2014
THROUGH_WEEK = 4
# nflverse weekly-roster club codes that differ from the repository's codes.
CODE_FIX = {"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "SL": "STL"}
KNOWN_ID_SOURCES = (
    "career/2014/League/personnel/branch_identity.json",
    "library/data/player_birth_dates.json",
    "library/data/2014_week1_rosters_branch_adjusted.json",
    "career/2014/League/personnel/league_players.json",
)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified(source_dir, name, pin):
    path = Path(source_dir) / name
    actual = sha256_file(path)
    if actual != pin:
        raise SystemExit("%s: sha256 %s differs from the pin %s" % (name, actual, pin))
    return path


def known_ids(root=ROOT):
    """gsis ids named by the repository's committed identity sources."""
    ids = set()
    branch = json.loads((root / KNOWN_ID_SOURCES[0]).read_text(encoding="utf-8"))
    ids.update(v for v in branch["by_player_id"].values() if v)
    births = json.loads((root / KNOWN_ID_SOURCES[1]).read_text(encoding="utf-8"))
    ids.update(v.get("gsis_id") for v in births["players"].values() if v.get("gsis_id"))
    week1 = json.loads((root / KNOWN_ID_SOURCES[2]).read_text(encoding="utf-8"))
    ids.update(p.get("gsis_id") for club in week1["clubs"].values() for p in club["players"] if p.get("gsis_id"))
    league = json.loads((root / KNOWN_ID_SOURCES[3]).read_text(encoding="utf-8"))
    ids.update(p.get("player_id") for p in league["players"] if p.get("player_id"))
    return {i for i in ids if i}


def inches(value):
    try:
        v = int(float(value))
    except (TypeError, ValueError):
        return None
    return v if 60 <= v <= 90 else None


def pounds(value):
    try:
        v = int(float(value))
    except (TypeError, ValueError):
        return None
    return v if 150 <= v <= 400 else None


def jersey(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def text(value):
    value = html.unescape(value or "").strip()
    return value or None


def season(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build(source_dir, root=ROOT):
    roster_path = verified(source_dir, *ROSTER)
    players_path = verified(source_dir, *PLAYERS)
    roster13_path = verified(source_dir, *ROSTER_2013)
    weekly = {}
    with open(roster_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                week = int(row["week"])
            except (TypeError, ValueError):
                continue
            if row.get("season") != str(SEASON) or row.get("game_type") != "REG" or not 1 <= week <= THROUGH_WEEK:
                continue
            if row.get("gsis_id"):
                weekly.setdefault(row["gsis_id"], []).append((week, row))
    with open(players_path, encoding="utf-8", newline="") as f:
        listing = {r["gsis_id"]: r for r in csv.DictReader(f) if r.get("gsis_id")}
    roster13 = {}
    with open(roster13_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("gsis_id") and row.get("season") == str(SEASON - 1):
                roster13.setdefault(row["gsis_id"], []).append((season(row.get("week")) or 0, row))
    wanted = set(weekly) | (known_ids(root) & (set(listing) | set(roster13)))
    out = {}
    counts = {"weeks_1_4": 0, "roster_2013": 0, "player_file": 0, "height": 0, "weight": 0, "college": 0,
              "number": 0, "jaguars_number": 0, "number_2013": 0}
    for gsis in sorted(wanted):
        rows = sorted(weekly.get(gsis, []), key=lambda x: x[0])  # stable: file order within a week
        entry = {}
        if rows:
            entry["listing"] = "weeks_1_4"
            for field, fn, key in (("height_in", inches, "height"), ("weight", pounds, "weight"),
                                   ("college", text, "college")):
                value = next((fn(r.get(key)) for _, r in reversed(rows) if fn(r.get(key)) is not None), None)
                entry[field] = value
            if entry["college"] is None and gsis in listing:  # the weekly rows leave it blank
                entry["college"] = text(listing[gsis].get("college_name"))
            week, last = rows[-1]
            entry["number"] = jersey(last.get("jersey_number"))
            club = CODE_FIX.get(last.get("team"), last.get("team"))
            entry["number_basis"] = {"club": club, "week": week} if entry["number"] is not None else None
            jax = [(w, r) for w, r in rows if r.get("team") == "JAX" and jersey(r.get("jersey_number")) is not None]
            if jax:
                entry["jaguars_number"] = jersey(jax[-1][1]["jersey_number"])
                entry["jaguars_week"] = jax[-1][0]
        elif gsis in roster13:
            _, q = sorted(roster13[gsis], key=lambda x: x[0])[-1]  # his latest 2013 week; file order on a tie
            entry = {"listing": "roster_2013", "height_in": inches(q.get("height")),
                     "weight": pounds(q.get("weight")), "college": text(q.get("college"))}
            if entry["college"] is None and gsis in listing:
                entry["college"] = text(listing[gsis].get("college_name"))
        else:
            q = listing[gsis]
            dated = (season(q.get("last_season")) or 9999) <= PLAYER_FILE_LAST_SEASON
            entry = {"listing": "player_file", "college": text(q.get("college_name")),
                     "height_in": inches(q.get("height")) if dated else None,
                     "weight": pounds(q.get("weight")) if dated else None}
        if gsis in roster13:
            week13, q13 = sorted(roster13[gsis], key=lambda x: x[0])[-1]  # his latest 2013 week
            entry["number_2013"] = jersey(q13.get("jersey_number"))
            if entry["number_2013"] is not None:
                entry["number_2013_basis"] = {"club": CODE_FIX.get(q13.get("team"), q13.get("team")), "week": week13}
        if not any(entry.get(f) is not None for f in ("height_in", "weight", "college", "number", "number_2013")):
            continue
        counts[entry["listing"]] += 1
        for f, c in (("height_in", "height"), ("weight", "weight"), ("college", "college"),
                     ("number", "number"), ("jaguars_number", "jaguars_number"), ("number_2013", "number_2013")):
            counts[c] += entry.get(f) is not None
        out[gsis] = {k: v for k, v in entry.items() if v is not None}  # absent = not listed
    return {
        "schema_version": 1,
        "builder": "scripts/research/build_2014_listed_player_identity.py",
        "scope": "Listed height, weight, college and jersey numbers (2014 and 2013) for the league player cards. Reader data "
                 "only: nothing in a game, an evaluation or a decision reads it.",
        "gate": "2014 regular season, Weeks 1 to %d of the weekly roster file; for a player with no Weeks 1-%d row, "
                "his 2013 season roster listing; with neither, the player file's college, and its height and weight "
                "only when his last listed season there is %d or earlier; and each listed player's 2013 season roster "
                "number (his latest 2013 week)" % (THROUGH_WEEK, THROUGH_WEEK, PLAYER_FILE_LAST_SEASON),
        "sources": {ROSTER[0]: {"sha256": ROSTER[1],
                                "url": "https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv"},
                    PLAYERS[0]: {"sha256": PLAYERS[1],
                                 "url": "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv"},
                    ROSTER_2013[0]: {"sha256": ROSTER_2013[1],
                                     "url": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv"}},
        "club_code_normalization": CODE_FIX,
        "counts": counts,
        "players": out,
    }


def render(data):
    """One player per line so a later rebuild diffs by player."""
    head = {k: v for k, v in data.items() if k != "players"}
    body = ",\n".join("  %s: %s" % (json.dumps(k), json.dumps(v, sort_keys=True, ensure_ascii=False))
                      for k, v in sorted(data["players"].items()))
    text = json.dumps(head, indent=1, sort_keys=True, ensure_ascii=False)
    return text[:-2] + ',\n "players": {\n' + body + "\n }\n}\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source_dir", type=Path, nargs="?",
                        default=Path(os.environ["LISTED_IDENTITY_SOURCES"]) if os.environ.get("LISTED_IDENTITY_SOURCES") else None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.source_dir is None or not all((args.source_dir / n).is_file() for n, _ in SOURCES):
        print("sources not present (pass SOURCE_DIR or set $LISTED_IDENTITY_SOURCES); nothing built", file=sys.stderr)
        return 2
    text = render(build(args.source_dir))
    if args.check:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print("wrote %s (%d players, %d bytes)" % (OUT.relative_to(ROOT), len(json.loads(text)["players"]), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
