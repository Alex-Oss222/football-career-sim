#!/usr/bin/env python3
"""Build the 2010-2012 public-honours evidence receipts (E1 first league pass).

  python scripts/research/build_2010_2012_honours_evidence.py HONOURS_JSON SOURCE_DIR

HONOURS_JSON is the verified honours research file (a list of three seasons,
each with ``entries`` and the verification-pass ``notes``). SOURCE_DIR holds
the pinned nflverse identity files named in SOURCES. The output is
library/data/2010_2012_honours_evidence.json; every source digest is recorded
and the season notes are carried verbatim so the source keys stay defined.

Policy (runtime/2014_engine_decisions.md E1; user choice "Honours + role"):
these are expert judgements announced before the January 15, 2013
divergence. Nothing here reads a 2013 or later result, award or statistic.
The identity files are used only to attach the stable gsis player_id.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library/data/2010_2012_honours_evidence.json"
DIVERGENCE = "2013-01-15"
SOURCES = {
    "players.csv": "https://github.com/nflverse/nflverse-data/releases/download/players/players.csv",
    "roster_2010.csv": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2010.csv",
    "roster_2011.csv": "https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2011.csv",
    "roster_weekly_2012.csv": "https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2012.csv",
}
# Announcement (public) date of each list. Located by dated articles found in
# a search on 2026-09-29; each is recorded with its locator and confidence.
PUBLIC_DATES = {
    (2010, "AP"): ("2011-01-24", "boston.com 'Tom Brady unanimous selection to AP NFL All-Pro team' (/2011/01/24/) and Deseret News 2011-01-24; earliest dated article found, single search", "medium"),
    (2011, "AP"): ("2012-01-06", "Victoria Advocate '2011 All-Pro Team' dated 2012-01-06 ('announced Friday'); single search", "medium"),
    (2012, "AP"): ("2013-01-12", "NFL.com 'All-Pro Team headlined by Adrian Peterson, J.J. Watt' / Wikipedia '2012 All-Pro Team' search summary; single search", "medium"),
    (2010, "PB"): ("2010-12-28", "PFT/NBC 'Tom Brady, Michael Vick lead 2011 Pro Bowl rosters' search summary", "medium"),
    (2011, "PB"): ("2011-12-27", "honours verification notes 2011 V10 ('announced 2011-12-27')", "medium"),
    (2012, "PB"): ("2012-12-26", "House of Sparky 'AFC Pro Bowl roster 2013' (/2012/12/26/) search result", "medium"),
}
PRO_BOWL_GAME = {2010: "2011-01-30", 2011: "2012-01-29", 2012: "2013-01-27"}
CLUB = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL", "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR", "Chicago Bears": "CHI", "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL", "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX", "Kansas City Chiefs": "KC",
    "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN", "New England Patriots": "NE", "New Orleans Saints": "NO",
    "New York Giants": "NYG", "New York Jets": "NYJ", "Oakland Raiders": "OAK", "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT", "San Diego Chargers": "SD", "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA",
    "St. Louis Rams": "STL", "Tampa Bay Buccaneers": "TB", "Tennessee Titans": "TEN", "Washington Redskins": "WAS",
}
CODE_FIX = {"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "SL": "STL", "LA": "STL"}
# AP entries the 2011 verification pass says it did NOT independently re-check.
AP2011_NOT_RECHECKED = {
    ("AP All-Pro 1st team", "Carl Nicks"), ("AP All-Pro 1st team", "Jahri Evans"),
    ("AP All-Pro 1st team", "Jason Peters"), ("AP All-Pro 1st team", "Joe Thomas"),
    ("AP All-Pro 1st team", "Andy Lee"), ("AP All-Pro 1st team", "Vonta Leach"),
    ("AP All-Pro 2nd team", "John Kuhn"), ("AP All-Pro 2nd team", "Jimmy Graham"),
    ("AP All-Pro 2nd team", "Marshal Yanda"), ("AP All-Pro 2nd team", "Logan Mankins"),
    ("AP All-Pro 2nd team", "Shane Lechler"),
}
# Pro Bowl originals the 2011 verification pass names as corroborated.
PB2011_CORROBORATED = {"DeMarcus Ware", "Clay Matthews", "Lance Briggs", "Ryan Kalil", "Scott Wells",
                       "Davin Joseph", "Ray Lewis", "Derrick Johnson", "Champ Bailey", "Brandon Marshall"}
SPECIAL = {"K", "P", "KR", "PR", "LS", "ST"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def norm(name):
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    name = re.sub(r"[.'`]", "", name)
    name = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", name)
    return re.sub(r"[^a-z]+", " ", name).strip()


def base_position(text):
    text = text.strip()
    token = re.split(r"[ (/-]", text)[0].upper()
    if text.lower().startswith("special teamer") or token == "ST":
        return "ST"
    if token.startswith("KR"):
        return "KR"
    return token


def honour_kind(honour):
    if honour.startswith("AP All-Pro 1st"):
        return "AP1"
    if honour.startswith("AP All-Pro 2nd"):
        return "AP2"
    if honour == "Pro Bowl selection":
        return "PB"
    return "PB_ALT"


def verification(season, kind, entry, notes_defined):
    """Return (label, basis). Labels preserved from the research notes."""
    has_v = any(key.startswith("V") for key in entry["sources"])
    name = entry["player"]
    if kind in ("AP1", "AP2"):
        if season == 2011 and (entry["honour"], name) in AP2011_NOT_RECHECKED:
            return "Single-pass", "2011 verification notes: not independently re-checked; rests on research pass"
        if season == 2012:
            return "Confirmed two-pass", "2012 verification notes: 'Treat the AP All-Pro entries as verified'"
        if season == 2011:
            return "Confirmed two-pass", "2011 verification notes: all AP entries re-checked, none changed"
        return "Confirmed two-pass", ("2010 AP block treated as checked twice (caller brief); second-pass key attached"
                                      if has_v else "2010 AP block treated as checked twice (caller brief); no second-pass key attached to this entry")
    if season == 2012:
        return "Single-pass", "2012 verification notes: Pro Bowl originals and replacements not re-checked"
    if has_v or (season == 2011 and kind == "PB" and name in PB2011_CORROBORATED):
        return "Confirmed two-pass", "independent verification-pass key or named corroboration in the season notes"
    return "Single-pass", "no verification-pass corroboration recorded for this entry"


def source_definitions(notes):
    keys = {}
    for match in re.finditer(r"^((?:V|R)\d+) = (.+)$", notes, flags=re.M):
        keys[match.group(1)] = match.group(2).strip()
    return keys


def main():
    honours_path, source = Path(sys.argv[1]), Path(sys.argv[2])
    seasons = json.loads(honours_path.read_text(encoding="utf-8"))
    players = read(source / "players.csv")
    rosters = {2010: read(source / "roster_2010.csv"), 2011: read(source / "roster_2011.csv"),
               2012: read(source / "roster_weekly_2012.csv")}
    by_name = {}
    for row in players:
        by_name.setdefault(norm(row["display_name"]), []).append(row)
        if row.get("football_name") and row.get("last_name"):
            by_name.setdefault(norm(row["football_name"] + " " + row["last_name"]), []).append(row)
    club_ids = {}
    for season, rows in rosters.items():
        for row in rows:
            team = CODE_FIX.get(row["team"], row["team"])
            for label in {row["full_name"], (row.get("football_name") or row["first_name"]) + " " + row["last_name"]}:
                club_ids.setdefault((season, team, norm(label)), set()).add(row["gsis_id"])
    info = {row["gsis_id"]: row for row in players}

    records, unmatched, key_table = [], [], {}
    for block in seasons:
        season, notes = block["season"], block["notes"]
        defined = source_definitions(notes)
        key_table[str(season)] = defined
        for index, entry in enumerate(block["entries"]):
            club = CLUB[entry["club"]]
            key = norm(entry["player"])
            ids = set(club_ids.get((season, club, key), set()))
            method = f"nflverse {season} roster, club {club}"
            if len(ids) != 1:
                candidates = {row["gsis_id"] for row in by_name.get(key, [])}
                seen = {g for g in candidates if any((s, club, key) in club_ids for s in rosters)}
                ids = seen if len(seen) == 1 else candidates
                method = "players.csv name match" + (" confirmed on any 2010-2012 club roster" if len(seen) == 1 else "")
            ids = {i for i in ids if i}
            kind = honour_kind(entry["honour"])
            label, basis = verification(season, kind, entry, defined)
            family = "AP" if kind in ("AP1", "AP2") else "PB"
            public_date, date_locator, date_conf = PUBLIC_DATES[(season, family)]
            contamination = ["Expert/selector judgement, not a direct observation; Pro Bowl selection mixes fan, player and coach votes"
                             if family == "PB" else "Expert judgement of a 50-member AP media panel, not a direct observation"]
            if kind == "PB_ALT":
                public_date = None
                contamination.append(f"Replacement/alternate: announcement date not pinned (between {PUBLIC_DATES[(season, 'PB')][0]} and the game on {PRO_BOWL_GAME[season]}); "
                                     "carries no tier effect")
                if PRO_BOWL_GAME[season] > DIVERGENCE:
                    contamination.append("May have been announced after the 2013-01-15 divergence; excluded from all use")
            if season == 2012 and family == "PB":
                contamination.append("Pro Bowl entry is research-pass only (2012 notes)")
            if base_position(entry["position"]) in SPECIAL:
                contamination.append("Specialist honour: special-teams evidence only, not an offense/defense composite input")
            note_flags = [flag for flag in ("UNCONFIRMED", "thinly sourced", "weakly sourced", "single search-summary", "not verified")
                          if flag.lower() in entry["position"].lower()]
            record = {
                "evidence_id": f"honour-{season}-{index:03d}",
                "season": season,
                "player": entry["player"],
                "player_id": sorted(ids)[0] if len(ids) == 1 else None,
                "match": method if len(ids) == 1 else ("ambiguous: " + ",".join(sorted(ids)) if ids else "unmatched"),
                "honour": entry["honour"],
                "honour_kind": kind,
                "position_text": entry["position"],
                "position": base_position(entry["position"]),
                "club": club,
                "sources": entry["sources"],
                "source_locator": [f"{season}:{k}" for k in entry["sources"]],
                "source_locator_unresolved": [k for k in entry["sources"] if k not in defined],
                "verification": label,
                "verification_basis": basis,
                "entry_flags": note_flags,
                "public_date": public_date,
                "public_date_locator": date_locator if public_date else None,
                "public_date_confidence": date_conf if public_date else "unpinned",
                "observation_scope": f"{season} NFL regular season (whole-season selection)",
                "observation_type": "expert_judgement",
                "confidence": ("medium" if label == "Confirmed two-pass" else "low") if not note_flags else "low",
                "contamination": contamination,
                "branch_cutoff": DIVERGENCE,
                "admissible_pre_divergence": bool(public_date and public_date < DIVERGENCE),
            }
            if not record["player_id"]:
                unmatched.append({"season": season, "player": entry["player"], "club": club, "match": record["match"]})
            else:
                row = info.get(record["player_id"], {})
                record["gsis_display_name"] = row.get("display_name")
            records.append(record)

    output = {
        "schema_version": 1,
        "built_by": "scripts/research/build_2010_2012_honours_evidence.py",
        "policy": "runtime/2014_engine_decisions.md E1; user choice 'Honours + role' (first league-wide pass)",
        "divergence": DIVERGENCE,
        "sources": {"honours_research": {"file": honours_path.name, "sha256": sha(honours_path)},
                    **{name: {"url": url, "sha256": sha(source / name)} for name, url in SOURCES.items()}},
        "public_dates": {f"{s}-{f}": {"date": d, "locator": l, "confidence": c} for (s, f), (d, l, c) in PUBLIC_DATES.items()},
        "source_keys": {"defined": key_table,
                        "undefined_note": "Research-pass keys (A*, P*, R*, AP*, PB*) are referenced by entries but not defined in the verified input; see each entry's source_locator_unresolved."},
        "season_notes": {str(block["season"]): block["notes"] for block in seasons},
        "summary": {
            "entries": len(records),
            "matched": sum(1 for r in records if r["player_id"]),
            "unmatched": unmatched,
            "by_verification": {label: sum(1 for r in records if r["verification"] == label) for label in ("Confirmed two-pass", "Single-pass")},
        },
        "entries": records,
    }
    OUT.write_text(json.dumps(output, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=1))


if __name__ == "__main__":
    main()
