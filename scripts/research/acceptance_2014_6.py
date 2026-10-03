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

Batch B7 (player states at runtime). Under a profile whose strength model is
player-state-v1 the strength records are player-state records with synthetic
latent draws: no private service is called. A synthetic season reference
R_k = player_state.season_reference(b"acc-2014.6-synthetic-reference", k) with
k = --latent-ref (default 0) stands in for the service's R_2014, and every
drawable player's z is drawn from it by the same keyed draw. The a1 block's
odd games give every player a synthetic state (family by position group; LB
held and offensive linemen without a state, as in the committed model) and
the same six Plus honours as before (now floors). The slate block builds each
club's real public states (runtime.strength.team_strength under a synthetic
binding stub; the committed public table) and applies the synthetic draws.
The summary adds the strength report: league mean edge, EDGE_CLAMP and
SACK_SHIFT_CLAMP shares, the club points and margin spread.

  a1z     acc-2014.6-z0 .. -z999 (B7, reported alongside a1, not a
          specification block): the a1 fixture with the synthetic states
          alone and no honours, so the symmetric records are centred on the
          fit's own scale (a1's six Plus floors lift both clubs' passing
          composite about 4.3 units above the real target-set centre).

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
          "a1z": ("acc-2014.6-z", 1000), "dev": ("dev-2014.6-", None)}
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


LATENT_REF = 0
SYNTHETIC_REFERENCE = b"acc-2014.6-synthetic-reference"
FAMILY_OF_GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "DL": "DL", "LB": "LB", "DB": "DB",
                   "K": "K", "P": "P"}


def synthetic_reference(k=None):
    from runtime import player_state
    return player_state.season_reference(SYNTHETIC_REFERENCE, LATENT_REF if k is None else k)


def _strength_record(team, version, honours=True):
    """Symmetric synthetic honours (Plus) for six starters of a club; under
    the player-state model every player also carries a synthetic state with
    a draw from the synthetic reference (keyed by player id, as the service
    keys by gsis id)."""
    from runtime import player_state, strength, usage
    from runtime.profiles import profile_for
    players = {}
    for grp, unit in (STRENGTH_SLOTS if honours else ()):
        first = usage.depth_order(team.roster, grp)
        if first:
            players[first[0].player_id] = {"offdef": {
                "tier": "Plus", "tier_value": 3, "evidence_weight": 1.0, "value": 1.0, "unit": unit,
                "honour_position": grp, "honour_group": grp, "evidence_ids": ["synthetic-" + grp]},
                "special": None}
    model = profile_for(version).strength
    record = {"model": model, "season": 2014, "as_of": "2014-09-07", "honour_seasons": [2011, 2012],
              "players": players}
    if model == strength.PLAYER_STATE_MODEL:
        ref = synthetic_reference()
        keys = []
        for p in team.roster:
            fam = FAMILY_OF_GROUP.get(usage.group(p.position))
            drawn = fam is not None and player_state.family_scale(fam) > 0
            row = players.setdefault(p.player_id, {"offdef": None, "special": None, "production": None})
            row["state"] = {"family": fam, "basis": "synthetic" if drawn else ("held" if fam == "LB" else "no_state"),
                            "expected": 0.0, "drawn": drawn}
            if drawn:
                k = player_state.key(2014, p.player_id, "b")
                keys.append(k)
                row["latent_value"] = player_state.draw_z(ref, k)
        record.update({"league_year": 2014, "manifest_sha256": player_state.manifest_sha256(),
                       "commitment": "synthetic-reference-%d" % LATENT_REF,
                       "latent_keys": sorted(keys, key=player_state.key_text)})
    return record


def a1_fixture(index, version="2014.6", honours=True):
    from dataclasses import replace
    from synthetic_games import sample_teams
    home, away = sample_teams()
    if index % 2:
        home, away = (replace(home, strength=_strength_record(home, version, honours)),
                      replace(away, strength=_strength_record(away, version, honours)))
    return home, away, ("neutral" if index % 5 == 0 else "home")


_SLATE = None


def slate_clubs(version="2014.6"):
    """{club: TeamInput} of the 512-game slate (built once per process).
    Under the player-state model each club's public states come from the
    committed table through a synthetic binding stub, and its latent values
    from the synthetic reference (no service call)."""
    global _SLATE
    if _SLATE is not None:
        return _SLATE
    from contextlib import ExitStack
    from datetime import date
    from unittest import mock
    from runtime import depth_library, player_state, strength, week_inputs
    from runtime.profiles import profile_for
    model = profile_for(version).strength
    stack = ExitStack()
    if model == strength.PLAYER_STATE_MODEL:
        stub = {"schema": player_state.BINDING_SCHEMA, "league_year": 2014,
                "manifest_sha256": player_state.manifest_sha256(), "commitment": "synthetic-reference-%d" % LATENT_REF}
        stack.enter_context(mock.patch.object(player_state, "binding", return_value=stub))
    stack.__enter__()
    from runtime.kernel import TeamInput
    from runtime.player_evidence import normalize_players
    from runtime.seasons import SeasonPaths
    anchors = dict(offense_anchor=2.0, defense_anchor=2.0, special_teams_anchor=2.0)
    library = depth_library.load(SeasonPaths(2014).background_depth)
    identities = week_inputs.identity_map(2014)
    inputs = {}
    for team in sorted(library["clubs"]):
        data = depth_library.team_input(team, week=1, season=2014, **anchors)
        data["active_players"] = week_inputs.game_day_actives(data["roster"])
        rows = data["roster"]
        if model == strength.PLAYER_STATE_MODEL:
            club = library["clubs"][team]
            rows = week_inputs.strength_identities(rows, 2014, club=club, identities=identities, strict=True)
        data["strength"], _ = strength.team_strength(team, rows, 2014, date(2014, 9, 7), model=model)
        inputs[team] = data
    sheet = json.loads((ROOT / "career/2014/05_Regular_Season/Games/Week_04/call_sheet.json").read_text())
    from scripts.render_season_stats import load_receipts
    receipts = [r for r in load_receipts(SeasonPaths(2014).receipts) if int(r["week"]) <= 4]
    jax = week_inputs.jacksonville_input(receipts, date(2014, 10, 5), anchors, sheet["offensive_call_sheet"], 2014)
    rows = week_inputs.strength_identities(jax["roster"], 2014, protagonist=True, identities=identities,
                                           strict=model == strength.PLAYER_STATE_MODEL)
    jax["strength"], _ = strength.team_strength(week_inputs.PROTAGONIST, rows, 2014, date(2014, 9, 7), model=model)
    inputs[week_inputs.PROTAGONIST] = jax
    stack.close()
    out = {}
    for team, data in inputs.items():
        fields = {k: v for k, v in data.items() if k in TeamInput.__dataclass_fields__}
        fields["active_players"] = tuple(fields["active_players"])
        fields["roster"] = tuple(fields["roster"])
        fields["offensive_call_sheet"] = tuple(fields.get("offensive_call_sheet", ()))
        team_input = TeamInput(**fields)
        normalize_players(team_input)
        if model == strength.PLAYER_STATE_MODEL:
            ref = synthetic_reference()
            draws = {player_state.key_text(k): player_state.z_text(player_state.draw_z(ref, k))
                     for k in team_input.strength["latent_keys"]}
            team_input = player_state.apply_latent(team_input, draws)
        out[team] = team_input
    _SLATE = out
    return out


def slate_fixture(index, version="2014.6"):
    clubs = slate_clubs(version)
    names = sorted(clubs)
    home = names[index // 16]
    away = names[(names.index(home) + 1 + index % 16) % len(names)]
    return clubs[home], clubs[away], "home"


def fixture(block, index, version="2014.6"):
    if block == "a1":
        return a1_fixture(index, version)
    if block == "a1z":
        return a1_fixture(index, version, honours=False)
    if block == "slate":
        return slate_fixture(index, version)
    from synthetic_games import sample_teams
    home, away = sample_teams()
    return home, away, "home"


def play(job):
    global LATENT_REF
    block, index, version, LATENT_REF = job
    from runtime.kernel import resolve_game, validate_result
    from runtime.profiles import profile_for
    from runtime.statbook import make_receipt
    prefix = BLOCKS[block][0]
    label = "%s%d" % (prefix, index)
    home, away, venue = fixture(block, index, version)
    strength_rows = []
    try:
        result = resolve_game(home, away, seed=entropy(label), event_id=label, venue=venue,
                              _test_profile=profile_for(version), _test_strength_receipt=strength_rows)
    except Exception as exc:  # a refused game is a finding
        return {"label": label, "refused": ["%s: %s" % (type(exc).__name__, exc)]}
    errors = validate_result(result)
    receipt = make_receipt(result, week=5, matchup="%s at %s" % (away.team_id, home.team_id), detail="compact_stats")
    receipt["possessions"] = result["possessions"]
    from runtime.strength import parameters
    params = parameters(profile_for(version).strength)
    scores = result["final_score"]
    return {"label": label, "refused": errors[:5], "receipt": receipt,
            "digest": hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest(),
            "diagnostics": {k: result["diagnostics"].get(k, 0) for k in DIAGNOSTICS},
            "strength": {"drives": len(strength_rows),
                         "with_record": bool(home.strength or away.strength),
                         "edge_sum": sum(r["edge"] for r in strength_rows),
                         "edge_clamped": sum(1 for r in strength_rows if abs(r["edge"]) >= params.edge_clamp),
                         "sack_clamped": sum(1 for r in strength_rows
                                             if abs(r["sack_shift"]) >= params.sack_shift_clamp),
                         "points": [scores[home.team_id], scores[away.team_id]]}}


def run(block, version, count=None, start=0, jobs=1):
    total = BLOCKS[block][1]
    stop = (start + count) if count is not None else total
    if total is not None:
        stop = min(stop, total)
    work = [(block, i, version, LATENT_REF) for i in range(start, stop)]
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


def strength_report(rows):
    """Batch B7 gate readings: league mean edge, clamp shares, club points
    and margin spread (informational), over the games with a record."""
    import statistics
    games = [r["strength"] for r in rows if r.get("strength") and r["strength"]["with_record"]]
    drives = sum(g["drives"] for g in games)
    points = [p for g in games for p in g["points"]]
    margins = [g["points"][0] - g["points"][1] for g in games]
    return {"games_with_record": len(games), "drives": drives,
            "mean_edge": (sum(g["edge_sum"] for g in games) / drives) if drives else None,
            "edge_clamp_share": (sum(g["edge_clamped"] for g in games) / drives) if drives else None,
            "sack_shift_clamp_share": (sum(g["sack_clamped"] for g in games) / drives) if drives else None,
            "points_mean": statistics.fmean(points) if points else None,
            "points_sd": statistics.pstdev(points) if len(points) > 1 else None,
            "margin_sd": statistics.pstdev(margins) if len(margins) > 1 else None,
            "latent_ref": LATENT_REF}


def summary(rows, version, provisional=True):
    receipts = [r["receipt"] for r in rows if "receipt" in r]
    refused = [r for r in rows if r["refused"]]
    diagnostics = {k: sum(r.get("diagnostics", {}).get(k, 0) for r in rows) for k in DIAGNOSTICS}
    out = {"kernel_profile": version, "games": len(rows), "refused_games": len(refused),
           "refused": [{"label": r["label"], "refused": r["refused"]} for r in refused[:50]],
           "diagnostics": diagnostics, "digests": {r["label"]: r.get("digest") for r in rows}}
    out["bands"] = grade(receipts, version, provisional)
    out["strength"] = strength_report(rows)
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
    parser.add_argument("--latent-ref", type=int, default=0,
                        help="batch B7: the synthetic season reference index for player-state draws")
    args = parser.parse_args()
    global LATENT_REF
    LATENT_REF = args.latent_ref
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
    sr = result["strength"]
    if sr["games_with_record"]:
        print("strength (ref %d): %d games with records, %d drives, mean edge %.5f, edge clamp share %.4f, "
              "sack-shift clamp share %.4f, points mean %.2f sd %.2f, margin sd %.2f" % (
                  sr["latent_ref"], sr["games_with_record"], sr["drives"], sr["mean_edge"], sr["edge_clamp_share"],
                  sr["sack_shift_clamp_share"], sr["points_mean"], sr["points_sd"], sr["margin_sd"]))
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
