#!/usr/bin/env python3
"""Branch identity table: every 2014 TeamInput player to an nflverse gsis id (kernel 2014.6, plan batch B4a).

  python scripts/research/build_2014_branch_identity.py [--sources DIR] [--week N] [--check]

Writes career/2014/League/personnel/branch_identity.json. Data only: nothing in runtime/
reads it until batch B7. An identity join is not an evaluation; the table holds no
statistic, grade or state value.

What it covers. The required set is every roster row of a dry build of week N's slate
(default Week 5), made in memory with runtime.week_inputs.build_package from the
current branch records, with the Week 4 call sheet standing in only for sheet validation
(the rosters, not the sheet, set coverage). Nothing is frozen, drawn or written under
.sim_cache, no service is called, and nothing under career/ is written except this
table. The global index adds every player the in-season rails can bring in (their
newcomer identities and the base practice squads) and Jacksonville's controlled
players (roster.md, through the identity registry), so the Pro Bowl and later entrants
join through the same gsis index.

The join rule (players review R9). A row's gsis id comes from the branch record that
carries the player (the rails entry for a background club, the identity registry for
Jacksonville). The table accepts it only when one of these holds:
- unique_name: the display name (a trailing club tag such as "(PIT)" removed) belongs
  to exactly one gsis id across the dated 2010-2014 roster files (2010-2013 seasonal
  and weekly rosters, 2014 weekly rosters cut at Week 4), and it is the row's id;
- dated_roster: the row's id is on a dated roster file under a name that shares the
  display name's surname (a non-unique name, a nickname or a club tag); the branch
  record supplies the id, the dated roster confirms it;
- draft_record: the row's id is a 2014-or-earlier draft selection in players.csv or
  draft_picks.csv (names are not in the allowlisted columns, so the branch signing
  record supplies the name and the draft record confirms the id);
- manual: a sourced row in MANUAL below (Jacksonville's 2014 undrafted signings who
  appear on no dated roster at Week 4 or earlier, and the Dietrich-Smith alias).
A unique name that resolves to a different id than the branch record's blocks the
build (a conflict), as does a display name carrying two ids or a slate with one id on
two rows. The player database (players.csv) contributes no names: its allowlist
(batch B2) keeps gsis_id, birth_date and the draft fields only.

Rookie class and draft slot (U4: the real selection for every club, Jacksonville
included): players.csv draft fields, cross-checked with draft_picks.csv; an undrafted
player's class is his first dated roster season (censored at 2010, the window's
first season). Preseason opponents are outside the required set: an unresolved
preseason player is listed as a fallback with no state (the listed-fallback policy).

Sources come only through scripts/research/sources_2010_2014.py (the B2 gate).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(HERE), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

OUT = ROOT / "career/2014/League/personnel/branch_identity.json"
SCHEMA = "branch-identity-v1"
SEASON = 2014
ROSTER_FILES = (["roster_%d.csv" % s for s in (2010, 2011, 2012, 2013)]
                + ["roster_weekly_%d.csv" % s for s in (2010, 2011, 2012, 2013)] + ["roster_weekly_2014w4.csv"])
GSIS = re.compile(r"^\d{2}-\d{7}$")
CLUB_TAG = re.compile(r"\s*\([A-Z]{2,3}\)\s*$")

# Sourced manual rows. Each names the branch record and the public identity source.
MANUAL = {
    "00-0030957": {"display_name": "Casey Kreiter", "class": 2014, "draft": None,
                   "reason": "2014 undrafted signing; on no dated roster at Week 4 or earlier",
                   "sources": ["career/2014/03_Draft/udfa_signings.md (signed May 10, 2014, row 24)",
                               "library/data/player_birth_dates.json (nflverse players, checked 2026-09-30)"]},
    "00-0031427": {"display_name": "Todd Davis", "class": 2014, "draft": None,
                   "reason": "2014 undrafted signing; on no dated roster at Week 4 or earlier",
                   "sources": ["career/2014/03_Draft/udfa_signings.md (signed May 10, 2014, row 10)",
                               "library/data/player_birth_dates.json (nflverse players and contracts, checked "
                               "2026-09-30)"]},
    "00-0031404": {"display_name": "Adrian Phillips", "class": 2014, "draft": None,
                   "reason": "2014 undrafted signing; on no dated roster at Week 4 or earlier",
                   "sources": ["career/2014/03_Draft/udfa_signings.md (signed May 10, 2014, row 7)",
                               "career/2014/00_Team_Operations/Free_Agency/signings.md (re-signed September 8, 2014)",
                               "library/data/player_birth_dates.json (nflverse players, checked 2026-09-30)"]},
    "00-0026784": {"display_name": "Evan Smith", "class": None, "draft": None,
                   "reason": "alias: the dated rosters list him as Evan Dietrich-Smith (pfr_id DietEv00)",
                   "sources": ["nflverse rosters 2010-2013 (full_name Evan Dietrich-Smith)",
                               "players.csv pfr_id DietEv00",
                               "library/data/player_birth_dates.json (corroborated, nflverse roster 2013 and ESPN)"]},
}


def norm(name):
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[.'`]", "", text)
    text = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", text)
    return re.sub(r"[^a-z]+", " ", text).strip()


def display_key(player_id):
    return norm(CLUB_TAG.sub("", player_id))


def surname(key):
    parts = key.split()
    return parts[-1] if parts else ""


# ------------------------------------------------------------------ league sources
def roster_index(dest):
    """name key -> set(gsis), gsis -> {seasons, name keys, positions by season}."""
    by_name = defaultdict(set)
    by_id = defaultdict(lambda: {"seasons": set(), "names": set(), "positions": defaultdict(lambda: defaultdict(int))})
    for name in ROSTER_FILES:
        for r in sources.rows(name, dest):
            gsis = r.get("gsis_id") or ""
            if not GSIS.match(gsis):
                continue
            season = int(r["season"])
            keys = {norm(r.get("full_name"))}
            if r.get("football_name") and r.get("last_name"):
                keys.add(norm(r["football_name"] + " " + r["last_name"]))
            for k in keys:
                if k:
                    by_name[k].add(gsis)
                    by_id[gsis]["names"].add(k)
            by_id[gsis]["seasons"].add(season)
            if r.get("position"):
                by_id[gsis]["positions"][season][r["position"].strip().upper()] += 1
    return by_name, by_id


def draft_index(dest):
    """gsis -> {year, round, pick, team} from players.csv, with draft_picks.csv as a cross-check."""
    out, conflicts = {}, []
    for r in sources.rows("players.csv", dest):
        if r.get("draft_year"):
            out[r["gsis_id"]] = {"year": int(r["draft_year"]), "round": int(r["draft_round"]),
                                 "pick": int(r["draft_pick"]), "team": r["draft_team"]}
    picks = {}
    for r in sources.rows("draft_picks.csv", dest):
        if GSIS.match(r.get("gsis_id") or ""):
            picks[r["gsis_id"]] = {"year": int(r["season"]), "round": int(r["round"]), "pick": int(r["pick"])}
    for gsis, p in picks.items():
        mine = out.get(gsis)
        if mine is None:
            out[gsis] = {**p, "team": None}
        elif (mine["year"], mine["pick"]) != (p["year"], p["pick"]):
            conflicts.append("draft fields differ for %s: players.csv %s/%s, draft_picks %s/%s"
                             % (gsis, mine["year"], mine["pick"], p["year"], p["pick"]))
    return out, conflicts


# ------------------------------------------------------------------ branch records
def dry_slate(week):
    """[(club, player_id, position, gsis)] for week's slate, built in memory (nothing frozen or written)."""
    from runtime import player_bios, rails, week_inputs
    from runtime.seasons import SeasonPaths
    from scripts.build_week_inputs import AVERAGE_ANCHORS, call_sheet_path
    from scripts.render_season_stats import load_receipts

    paths = SeasonPaths(SEASON, ROOT)
    sheet = call_sheet_path(week, SEASON) or call_sheet_path(week - 1, SEASON)
    call_sheet = json.loads(sheet.read_text(encoding="utf-8"))["offensive_call_sheet"]
    receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < week]
    games = week_inputs.schedule(week, SEASON)
    slate = week_inputs.rails_slate(week, SEASON, receipts, games)
    clubs, _ = week_inputs._rails_clubs(slate, games, SEASON)
    package = week_inputs.build_package(week, receipts, call_sheet, {"offense_anchor": 2.0, "defense_anchor": 2.0,
                                                                      "special_teams_anchor": 2.0}, SEASON)
    registry = player_bios.load()
    rows = []
    for game in package["games"]:
        for side in ("away", "home"):
            team = game[side]
            roster = game[side + "_input"]["roster"]
            if team == week_inputs.PROTAGONIST:
                ids = {r["player_id"]: (registry.get(r["player_id"]) or {}).get("gsis_id") for r in roster}
            else:
                club = clubs.get((rails.game_key(game), team))
                ids = {p["player_id"]: p.get("gsis_id") for p in club["players"]}
            for r in roster:
                rows.append((team, r["player_id"], r.get("position"), ids.get(r["player_id"])))
    return rows, {"week": week, "call_sheet": str(sheet.relative_to(ROOT)), "games": len(package["games"])}


def global_rows():
    """[(source, player_id, position, gsis)] beyond the slate: rails newcomers and base
    practice squads, and Jacksonville's controlled players."""
    from runtime import player_bios, rails
    from runtime.seasons import SeasonPaths
    from scripts.check_week_input_exclusivity import controlled_players_from_roster

    out = []
    data = rails.load(SEASON, ROOT)
    if data is not None:
        for pid, info in sorted(rails.identities(data).items()):
            out.append(("rails", pid, None, info["gsis_id"]))
    registry = player_bios.load()
    for name in sorted(controlled_players_from_roster(SeasonPaths(SEASON, ROOT).roster)):
        out.append(("jacksonville", name, None, (registry.get(name) or {}).get("gsis_id")))
    return out


# ------------------------------------------------------------------ the join
def join(player_id, gsis, by_name, by_id, drafts=None):
    """(basis, error or None) for one branch row."""
    if gsis in MANUAL:
        return "manual", None
    if not gsis or not GSIS.match(gsis):
        return None, "%s: no gsis id in the branch record" % player_id
    key = display_key(player_id)
    candidates = by_name.get(key, set())
    tagged = bool(CLUB_TAG.search(player_id))
    if len(candidates) == 1 and gsis not in candidates and not tagged:
        return None, "%s: conflict, the unique dated-roster name is %s but the branch record says %s" % (
            player_id, sorted(candidates)[0], gsis)
    if candidates == {gsis} and not tagged:
        return "unique_name", None
    entry = by_id.get(gsis)
    if entry and (gsis in candidates or any(surname(n) == surname(key) for n in entry["names"])):
        return "dated_roster", None
    if drafts and gsis in drafts and drafts[gsis]["year"] <= SEASON:
        return "draft_record", None
    return None, "%s (%s): on no dated roster under that surname and no sourced manual row" % (player_id, gsis)


def first_season(entry):
    return min(entry["seasons"]) if entry and entry["seasons"] else None


def build(dest, week, log=print):
    by_name, by_id = roster_index(dest)
    drafts, draft_conflicts = draft_index(dest)
    slate, dry = dry_slate(week)
    extra = global_rows()
    errors = list(draft_conflicts)
    unresolved = []
    players, names = {}, {}
    seen_in_slate = defaultdict(list)
    for origin, pid, position, gsis in [("slate:" + t, p, pos, g) for t, p, pos, g in slate] + list(extra):
        basis, error = join(pid, gsis, by_name, by_id, drafts)
        if error:
            if origin.startswith("slate:"):
                errors.append(error)
            elif not any(u["player_id"] == pid for u in unresolved):
                # Outside the required set: listed, never guessed. B7 blocks a
                # week whose slate carries an unresolved player.
                unresolved.append({"player_id": pid, "origin": origin, "gsis_id": gsis, "reason": error})
            continue
        if origin.startswith("slate:"):
            seen_in_slate[gsis].append(pid)
        if names.setdefault(pid, gsis) != gsis:
            errors.append("%s carries two gsis ids: %s and %s" % (pid, names[pid], gsis))
            continue
        row = players.get(gsis)
        if row is None:
            entry = by_id.get(gsis)
            draft = drafts.get(gsis)
            manual = MANUAL.get(gsis)
            if draft and draft["year"] <= SEASON:
                klass, class_basis = draft["year"], "draft"
                slot = {"round": draft["round"], "overall": draft["pick"]}
            else:
                slot = "undrafted"
                if manual and manual.get("class"):
                    klass, class_basis = manual["class"], "manual"
                else:
                    first = first_season(entry)
                    klass = first
                    class_basis = ("first_dated_roster_censored" if first == 2010 else "first_dated_roster")
            row = players[gsis] = {
                "display_names": [], "basis": basis, "class": klass, "class_basis": class_basis,
                "real_slot": slot, "dated_roster_seasons": sorted(entry["seasons"]) if entry else [],
                "required": False}
            if manual:
                row["manual"] = {k: manual[k] for k in ("reason", "sources")}
        if pid not in row["display_names"]:
            row["display_names"].append(pid)
        if position and position not in row.setdefault("branch_positions", []):
            row["branch_positions"].append(position)
        if origin.startswith("slate:"):
            row["required"] = True
    for gsis, pids in seen_in_slate.items():
        if len(pids) > 1:
            errors.append("gsis %s is on %d slate rows: %s" % (gsis, len(pids), ", ".join(pids)))
    for row in players.values():
        row["display_names"].sort()
        row.setdefault("branch_positions", []).sort()
    required = sum(1 for _, _, _, _ in slate)
    resolved = sum(1 for _, pid, _, g in slate if names.get(pid) == g and g in players)
    basis_counts = defaultdict(int)
    for _, pid, _, g in slate:
        if g in players:
            basis_counts[players[g]["basis"]] += 1
    artifact = {
        "schema": SCHEMA,
        "season": SEASON,
        "builder": "scripts/research/build_2014_branch_identity.py",
        "specification_sha256": pre_build_specification.digest(),
        "purpose": ("Identity join from every 2014 TeamInput player to an nflverse gsis id, for the kernel 2014.6 "
                    "player-state table. An identity join, not an evaluation: no statistic, grade or state value."),
        "join_rule": ("unique_name: the display name (club tag removed) has exactly one gsis id across the dated "
                      "2010-2014 roster files and it is the branch record's; dated_roster: the branch record's id is "
                      "on a dated roster under the same surname; draft_record: the id is a 2014-or-earlier draft "
                      "selection (players.csv or draft_picks.csv); manual: a sourced row. A unique name resolving to "
                      "another id, a name with two ids, or one id on two slate rows blocks the build."),
        "preseason_policy": ("listed fallback: a preseason opponent who does not resolve is listed with no state; "
                             "preseason rows are not part of the required set"),
        "class_rule": ("draft class and real selection slot from players.csv (cross-checked with draft_picks.csv), "
                       "for every club, Jacksonville included (U4); an undrafted player's class is his first dated "
                       "roster season, censored at 2010"),
        "sources": {name: {"sha256": sources.load_manifest()["assets"][name]["sha256"]}
                    for name in ROSTER_FILES + ["players.csv", "draft_picks.csv"]},
        "dry_build": {**dry, "note": "built in memory; nothing frozen, drawn or written; no service call"},
        "coverage": {"required_rows": required, "resolved_rows": resolved,
                     "by_basis": dict(sorted(basis_counts.items())),
                     "indexed_players": len(players)},
        "unresolved_outside_required": sorted(unresolved, key=lambda u: u["player_id"]),
        "by_player_id": dict(sorted(names.items())),
        "players": dict(sorted(players.items())),
    }
    if resolved != required:
        errors.append("coverage %d of %d required rows" % (resolved, required))
    log("identity: %d of %d slate rows resolved; %d players indexed" % (resolved, required, len(players)))
    return artifact, errors


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--week", type=int, default=5)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    artifact, errors = build(args.sources, args.week, log=lambda m: print(m, file=sys.stderr))
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
