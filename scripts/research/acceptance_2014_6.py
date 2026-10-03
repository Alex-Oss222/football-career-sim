#!/usr/bin/env python3
"""Kernel 2014.6 acceptance runs (batch B5 onward), committed.

Resolves synthetic games under a kernel profile (default PROFILE_2014_6)
through runtime.kernel.resolve_game with kernel entropy derived exactly as
the production runner derives it from an opaque event reference (the label
is the event id; seed_sweep.entropy), turns each closed result into a public
receipt (runtime.statbook.make_receipt, compact_stats, with the possession
list attached so the result-only rows are measurable) and grades the cohort
with runtime.bands (usage and volume, drive model, field position and late
game, injuries, ledger coherence).

Blocks (library/2014_6_pre_build_specification.md, section 6):

  a1      acc-2014.6-0 .. acc-2014.6-999: the 1,000-game block. Fixture by
          the label's index only: an even index plays the synthetic sample
          clubs without strength records (tests/synthetic_games.py
          sample_teams), an odd index the same clubs with symmetric
          synthetic strength records (Plus honours for each club's QB1, WR1,
          OL1, DL1, LB1 and DB1); every fifth index at a neutral site.
  a2      acc-2014.6-x0 .. acc-2014.6-x1999: the 2,000-game block for the
          end-of-half rows (sample clubs, no strength records, home venue).
  slate   the 512-game real 2014 inventory slate: the 31 background clubs'
          2014 Week 1 game-day units (runtime.depth_library, 46 actives by
          week_inputs.game_day_actives) and Jacksonville's current game
          depth chart with its frozen Week 4 call sheet
          (week_inputs.jacksonville_input as of the Week 4 game day), each
          club with its dated strength record (runtime.strength.team_strength
          as of September 7, 2014); each club hosts the next 16 clubs in
          name order. Labels slate-2014.6-0 .. -511 (not a specification
          block: the specification names no slate labels; the fixture
          depends on the index only).
  dev     dev-2014.6-<i>: development labels, never an acceptance reading.

The 12,000-game sweep is scripts/research/seed_sweep.py --block a6.

Nothing is written unless --out names a file. Synthetic seeds only: no
private service, no career state is changed (the slate reads committed
career files).

  python scripts/research/acceptance_2014_6.py --block a1 --jobs 4 --out /tmp/a1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "tests", ROOT / "scripts" / "research"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

BLOCKS = {"a1": ("acc-2014.6-", 1000), "a2": ("acc-2014.6-x", 2000), "slate": ("slate-2014.6-", 512),
          "dev": ("dev-2014.6-", None)}
STRENGTH_SLOTS = (("QB", "offense"), ("WR", "offense"), ("OL", "offense"), ("DL", "defense"), ("LB", "defense"),
                  ("DB", "defense"))
DIAGNOSTICS = ("chain_layout_failed", "chain_layout_resampled", "chain_layout_resample_exhausted",
               "fallback_zero_tuple", "fallback_fit_drive", "fallback_need_union", "fallback_clock_tuple",
               "h1_fit_fallback", "h1_late_match_fallback", "h1_late_cell_fallback", "h1_late_union_fallback",
               "h1_late_infeasible", "h1_neutral_infeasible", "clock_expiry_zero", "timeout_unavailable_kept",
               "ot_leading_offense",
               # batch B6: the W3 closable fallback and the W5a stamp exemptions
               "fg_fourth_down_relaxed", "clock_gap_exempt", "timeout_seat_fallback")


def entropy(label):
    from seed_sweep import entropy as derive
    return derive(label)


def _strength_record(team):
    """Symmetric synthetic honours (Plus) for six starters of a club."""
    from runtime import strength, usage
    players = {}
    for grp, unit in STRENGTH_SLOTS:
        first = usage.depth_order(team.roster, grp)
        if first:
            players[first[0].player_id] = {"offdef": {
                "tier": "Plus", "tier_value": 3, "evidence_weight": 1.0, "value": 1.0, "unit": unit,
                "honour_position": grp, "honour_group": grp, "evidence_ids": ["synthetic-" + grp]},
                "special": None}
    return {"model": strength.MODEL, "season": 2014, "as_of": "2014-09-07", "honour_seasons": [2011, 2012],
            "players": players}


def a1_fixture(index):
    from dataclasses import replace
    from synthetic_games import sample_teams
    home, away = sample_teams()
    if index % 2:
        home, away = replace(home, strength=_strength_record(home)), replace(away, strength=_strength_record(away))
    return home, away, ("neutral" if index % 5 == 0 else "home")


_SLATE = None


def slate_clubs():
    """{club: TeamInput} of the 512-game slate (built once per process)."""
    global _SLATE
    if _SLATE is not None:
        return _SLATE
    from datetime import date
    from runtime import depth_library, strength, week_inputs
    from runtime.kernel import TeamInput
    from runtime.player_evidence import normalize_players
    from runtime.seasons import SeasonPaths
    anchors = dict(offense_anchor=2.0, defense_anchor=2.0, special_teams_anchor=2.0)
    library = depth_library.load(SeasonPaths(2014).background_depth)
    inputs = {}
    for team in sorted(library["clubs"]):
        data = depth_library.team_input(team, week=1, season=2014, **anchors)
        data["active_players"] = week_inputs.game_day_actives(data["roster"])
        data["strength"], _ = strength.team_strength(team, data["roster"], 2014, date(2014, 9, 7))
        inputs[team] = data
    sheet = json.loads((ROOT / "career/2014/05_Regular_Season/Games/Week_04/call_sheet.json").read_text())
    from scripts.render_season_stats import load_receipts
    receipts = [r for r in load_receipts(SeasonPaths(2014).receipts) if int(r["week"]) <= 4]
    jax = week_inputs.jacksonville_input(receipts, date(2014, 10, 5), anchors, sheet["offensive_call_sheet"], 2014)
    rows = week_inputs.strength_identities(jax["roster"], 2014, protagonist=True)
    jax["strength"], _ = strength.team_strength(week_inputs.PROTAGONIST, rows, 2014, date(2014, 9, 7))
    inputs[week_inputs.PROTAGONIST] = jax
    out = {}
    for team, data in inputs.items():
        fields = {k: v for k, v in data.items() if k in TeamInput.__dataclass_fields__}
        fields["active_players"] = tuple(fields["active_players"])
        fields["roster"] = tuple(fields["roster"])
        fields["offensive_call_sheet"] = tuple(fields.get("offensive_call_sheet", ()))
        team_input = TeamInput(**fields)
        normalize_players(team_input)
        out[team] = team_input
    _SLATE = out
    return out


def slate_fixture(index):
    clubs = slate_clubs()
    names = sorted(clubs)
    home = names[index // 16]
    away = names[(names.index(home) + 1 + index % 16) % len(names)]
    return clubs[home], clubs[away], "home"


def fixture(block, index):
    if block == "a1":
        return a1_fixture(index)
    if block == "slate":
        return slate_fixture(index)
    from synthetic_games import sample_teams
    home, away = sample_teams()
    return home, away, "home"


def play(job):
    block, index, version = job
    from runtime.kernel import resolve_game, validate_result
    from runtime.profiles import profile_for
    from runtime.statbook import make_receipt
    prefix = BLOCKS[block][0]
    label = "%s%d" % (prefix, index)
    home, away, venue = fixture(block, index)
    try:
        result = resolve_game(home, away, seed=entropy(label), event_id=label, venue=venue,
                              _test_profile=profile_for(version))
    except Exception as exc:  # a refused game is a finding
        return {"label": label, "refused": ["%s: %s" % (type(exc).__name__, exc)]}
    errors = validate_result(result)
    receipt = make_receipt(result, week=5, matchup="%s at %s" % (away.team_id, home.team_id), detail="compact_stats")
    receipt["possessions"] = result["possessions"]
    return {"label": label, "refused": errors[:5], "receipt": receipt,
            "digest": hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest(),
            "diagnostics": {k: result["diagnostics"].get(k, 0) for k in DIAGNOSTICS}}


def run(block, version, count=None, start=0, jobs=1):
    total = BLOCKS[block][1]
    stop = (start + count) if count is not None else total
    if total is not None:
        stop = min(stop, total)
    work = [(block, i, version) for i in range(start, stop)]
    if jobs > 1:
        with multiprocessing.Pool(jobs) as pool:
            rows = pool.map(play, work, chunksize=4)
    else:
        rows = [play(job) for job in work]
    return rows


def grade(receipts, version, provisional=True):
    """Graded tables with each row's registry status. provisional=False is
    the B17 re-grade: provisional detections (runtime.bands
    PROVISIONAL_DETECTIONS) are graded as unregistered rows."""
    from runtime import bands
    out = {}
    for name, fn in (("usage", bands.audit), ("drive_model", bands.audit_drive_model),
                     ("field_position", bands.audit_field_position), ("injuries", bands.audit_injuries)):
        team_games, rows = fn(receipts, cohort=version)
        out[name] = {"team_games": team_games,
                     "rows": [[m, o, c, t, bands.known_status((m, o, c, t, s), version, provisional)]
                              for m, o, c, t, s in rows]}
    checked, counts = bands.coherence(receipts, cohort=version)
    out["coherence"] = {"checked": checked, "violations": {cls: n for cls, n, _ in counts if n}}
    # Batch B6: audit-only classes are reported, never gated.
    checked, counts = bands.audit_only_coherence(receipts, cohort=version)
    out["coherence"]["audit_only"] = {cls: n for cls, n, _ in counts}
    return out


def summary(rows, version, provisional=True):
    receipts = [r["receipt"] for r in rows if "receipt" in r]
    refused = [r for r in rows if r["refused"]]
    diagnostics = {k: sum(r.get("diagnostics", {}).get(k, 0) for r in rows) for k in DIAGNOSTICS}
    out = {"kernel_profile": version, "games": len(rows), "refused_games": len(refused),
           "refused": [{"label": r["label"], "refused": r["refused"]} for r in refused[:50]],
           "diagnostics": diagnostics, "digests": {r["label"]: r.get("digest") for r in rows}}
    out["bands"] = grade(receipts, version, provisional)
    outside = [(table, row[0], row[4]) for table, block in out["bands"].items() if table != "coherence"
               for row in block["rows"] if str(row[4]).startswith("OUTSIDE")]
    out["outside"] = outside
    out["provisional_regrade"] = not provisional
    # The gate reads: a row OUTSIDE that is neither a carried known detection
    # inside its bound nor a provisional detection; provisional rows are listed
    # apart so the B17 re-grade can see them with their status removed.
    out["outside_ungated"] = [row for row in outside if "known detection, within" not in row[2]
                              and "provisional detection" not in row[2]]
    out["outside_provisional"] = [row for row in outside if "provisional detection" in row[2]]
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--block", choices=sorted(BLOCKS), required=True)
    parser.add_argument("--count", type=int)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--profile", default="2014.6")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--regrade-provisional", action="store_true",
                        help="the B17 view: grade provisional detections as unregistered rows")
    args = parser.parse_args()
    if args.block == "dev" and args.count is None:
        parser.error("the dev block needs --count")
    rows = run(args.block, args.profile, args.count, args.start, args.jobs)
    result = summary(rows, args.profile, provisional=not args.regrade_provisional)
    result["block"] = args.block
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print("acceptance %s, kernel profile %s: %d games, %d refused; coherence violations %s; audit-only %s" % (
        args.block, args.profile, result["games"], result["refused_games"],
        result["bands"]["coherence"]["violations"] or "none",
        result["bands"]["coherence"].get("audit_only") or "none"))
    print("diagnostics: " + ", ".join("%s %d" % kv for kv in sorted(result["diagnostics"].items()) if kv[1]))
    for table, block in result["bands"].items():
        if table == "coherence":
            continue
        print("\n[%s] team-games %d" % (table, block["team_games"]))
        for metric, observed, centre, tolerance, status in block["rows"]:
            fmt = lambda v: "-" if v is None else ("%.4f" % v)
            print("  %-96s %10s %10s %10s  %s" % (metric[:96], fmt(observed), fmt(centre), fmt(tolerance), status))
    print("\nOUTSIDE rows: %d (ungated %d, provisional %d%s)" % (
        len(result["outside"]), len(result["outside_ungated"]), len(result["outside_provisional"]),
        "; provisional status removed" if result["provisional_regrade"] else ""))
    for row in result["outside"]:
        print("  %s: %s (%s)" % row)
    return 1 if result["refused_games"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
