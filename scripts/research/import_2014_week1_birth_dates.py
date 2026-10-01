#!/usr/bin/env python3
"""Import the 2014 Week 1 depth library's birth dates into the registry.

Usage: python scripts/research/import_2014_week1_birth_dates.py [--write]

Adds a registry row for every player in
library/data/2014_week1_depth_charts.json who has no row yet and whose
library entry carries a `birth_date` and `gsis_id`. The row's evidence class
is `library_week1_source`: one provider (the user's nflverse-derived
`user_nfl_2014_week1.json`, carried into the library as data only), not
corroborated by a second publisher. A name already registered under another
spelling of the same gsis id is added as an alias row only when both dates
agree. A name already registered to a different gsis id is never touched; it
is reported as an identity collision for review. Birth date and identity
only: no later outcome is read. Idempotent; prints a summary.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "library/data/player_birth_dates.json"
LIBRARY = ROOT / "library/data/2014_week1_depth_charts.json"
SOURCE_KEY = "library_week1_source_2014"
EVIDENCE = "library_week1_source"
SOURCE_NOTE = ("library/data/2014_week1_depth_charts.json bio fields (birth_date, gsis_id), carried from the "
               "user's nflverse-derived user_nfl_2014_week1.json (library/2014_week1_depth_charts.md, "
               "sources table, Player bio fields); imported October 1, 2026. One provider: no second "
               "publisher was fetched, so the row is library_week1_source, never corroborated.")


def plan(registry, library):
    players = registry["players"]
    by_gsis = {row["gsis_id"]: name for name, row in players.items()}
    added, aliases, unverified, collisions = {}, [], [], []
    for team, club in sorted(library["clubs"].items()):
        for player in club["players"]:
            name, gsis, born = player["player_id"], player.get("gsis_id"), player.get("birth_date")
            if name in players:
                if players[name]["gsis_id"] != gsis:
                    collisions.append((name, team, gsis, players[name]["gsis_id"]))
                continue
            if name in added:
                continue
            if not born or not gsis:
                unverified.append((name, team))
                continue
            row = {"gsis_id": gsis, "birth_date": born, "evidence": EVIDENCE, "sources": [SOURCE_KEY]}
            if gsis in by_gsis:
                other = players[by_gsis[gsis]]
                if other["birth_date"] != born:
                    collisions.append((name, team, gsis, "date differs from %s" % by_gsis[gsis]))
                    continue
                row["alias_of"] = by_gsis[gsis]
                aliases.append((name, by_gsis[gsis]))
            added[name] = row
    return added, aliases, unverified, collisions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    added, aliases, unverified, collisions = plan(registry, library)
    print("rows to add: %d (aliases of a registered gsis id: %d)" % (len(added), len(aliases)))
    for name, other in aliases:
        print("  alias %s -> %s" % (name, other))
    print("left unverified (no library birth date): %d" % len(unverified))
    for name, team in unverified:
        print("  %s (%s)" % (name, team))
    print("identity collisions, not imported: %d" % len(collisions))
    for name, team, gsis, note in collisions:
        print("  %s (%s) library gsis %s; registry: %s" % (name, team, gsis, note))
    if args.write and added:
        registry["sources"].setdefault(SOURCE_KEY, {"path": "library/data/2014_week1_depth_charts.json",
                                                    "note": SOURCE_NOTE})
        registry["players"].update(added)
        REGISTRY.write_text(json.dumps(registry, indent=1) + "\n", encoding="utf-8")
        print("written: %s" % REGISTRY.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
