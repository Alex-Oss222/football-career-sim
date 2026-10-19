#!/usr/bin/env python3
"""Refresh the register's DOB/age columns and build the player ages page from Document 5's master date.

The ages page lists every player Jacksonville controls (from the roster record,
runtime/roster.py) and the other clubs' background players, each with his
birth date and age (runtime/player_bios.py), in clean football words; the
roster page shows its own ages (scripts/render_club_pages.py). Run after closing a
date or changing roster control. --check is read-only. It never advances the
clock, retires a player or changes a game packet.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime import roster as roster_record
from scripts.render_club_pages import long_date, status_text
from runtime.player_bios import biographies, load, master_date
from runtime.seasons import current_record
from runtime.season_layout import logical_path, rebase_markdown

STAMP = re.compile(r"^<!-- player-ages-as-of: [^\n]+ -->$", re.M)


def table_ages(text, day, players):
    """Update only tables with Player, position and a control status column."""
    output, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            header = None
            output.append(line)
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if "Player" in cells:
            header = cells if any(c in cells for c in ("Pos", "Pos.")) and any(
                c in cells for c in ("Status", "Primary status")) else None
        if header is None:
            output.append(line)
            continue
        # Rebuild columns so re-running is idempotent and parser positions hold.
        keep = [i for i, c in enumerate(header) if c not in {"DOB", "Age"}]
        clean = [cells[i] for i in keep]
        clean_header = [header[i] for i in keep]
        pos = next(i for i, c in enumerate(clean_header) if c in {"Pos", "Pos."}) + 1
        if "Player" in cells:
            extra = ["DOB", "Age"]
        elif set(cells[0]) <= {"-", ":"}:
            extra = ["---", "---:"]
        else:
            bio = biographies([cells[header.index("Player")]], day, players)
            row = next(iter(bio.values()))
            extra = [row["birth_date"], str(row["age"])]
        output.append("| " + " | ".join(clean[:pos] + extra + clean[pos:]) + " |")
    return STAMP.sub("<!-- player-ages-as-of: %s -->" % day, "\n".join(output) + "\n")


def controlled_rows(text):
    header = None
    for line in text.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if "Player" in cells:
            header = cells if "Pos" in cells and "Status" in cells else None
        elif header and not set(cells[0]) <= {"-", ":"}:
            yield cells[header.index("Player")], cells[header.index("Pos")], cells[header.index("Status")]


def render_views(root=ROOT):
    root = Path(root)
    day, players = master_date(root), load(root)
    result = {}
    for path in ("state/04_Roster_and_Staff_Register.md",):
        text = (root / path).read_text(encoding="utf-8")
        if len(STAMP.findall(text)) != 1:
            raise ValueError("Expected one age as-of marker in " + path)
        result[path] = table_ages(text, day, players)
    background = json.loads(current_record('background_depth', root).read_text())
    clubs = background["clubs"]
    controlled = [(p["name"], p["position"], status_text(p["status"]))
                  for p in roster_record.load(current_record('roster', root))["players"]]
    names = {n for n, _, _ in controlled}
    scope = "%d Week %d chart" % (background["season"], background["week"])
    sections = {team: [(p["player_id"], p["position"], scope)
                       for p in c["players"] if p["player_id"] not in names]
                for team, c in clubs.items()}
    sections["Jacksonville Jaguars"] = controlled
    lines = ["# Player ages", "", "As of %s. Ages count completed birthdays." % long_date(day), "",
             "Birth dates and their evidence: [verification notes](../../library/2013_player_birth_dates.md).", "",
             "Jacksonville lists every player the club controls, the practice squad included. The other clubs "
             "list the players on their %d Week %d depth charts." % (background["season"], background["week"]), ""]
    for team, rows in sorted(sections.items()):
        lines += ["## " + team, "", "| Player | Pos | DOB | Age | Roster scope |",
                  "|---|---|---|---:|---|"]
        bios = biographies([n for n, _, _ in rows], day, players)
        for name, pos, status in rows:
            bio = bios[name]
            lines.append("| %s | %s | %s | %s | %s |" % (name, pos, bio["birth_date"], bio["age"], status))
        lines.append("")
    target = current_record('player_ages', root).relative_to(root.resolve()).as_posix()
    year = int(target.split('/')[1])
    result[target] = rebase_markdown('\n'.join(lines), logical_path(year, 'player_ages.md'), target)
    return result


def check(root=ROOT):
    return ["Player ages stale: %s; run python scripts/render_player_ages.py" % path
            for path, expected in render_views(root).items()
            if not (Path(root) / path).exists() or (Path(root) / path).read_text(encoding="utf-8") != expected]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = check()
        print("\n".join(errors) if errors else "PASS: player ages match the simulation date")
        return bool(errors)
    for path, text in render_views().items():
        (ROOT / path).write_text(text, encoding="utf-8")
    print("Updated the register's ages and the player ages page from Document 5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
