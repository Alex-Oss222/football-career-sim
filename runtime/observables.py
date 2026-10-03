"""Kernel 2014.6 (batch B7): the weekly participation observables.

What the branch can honestly observe about every player on a weekly slate,
written from the frozen package at each closure (scripts/close_week.py) to
career/YEAR/league/personnel/observables/week_NN.json: for every club, each
roster row's club, player id, gsis id, kernel group, depth rank, availability,
hold reason (the package's medical note, else "unavailable") and whether he
dressed. These are the inputs the player policy's feedback (P5) would read:
role held (depth rank), availability and snaps (from the receipts, not here).
The fitted P5 weights travel with each file for the record; the applied
feedback F is 0 in 2014 (library/data/2010_2014_player_state_model.json,
feedback.applied), so nothing here changes any value.

Weeks closed before this record existed (2014 Weeks 1-4) are backfilled by a
deterministic rebuild of their packages from committed data, which must
reproduce the frozen packets: each club's dressed list must equal the player
rows of its closed receipt, else the rebuild fails closed and no file is
written. No value, grade or state appears in an observables file.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .seasons import SeasonPaths
from .usage import group

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "participation-observables-v1"


def observables_path(week, season, root=ROOT):
    return SeasonPaths(int(season), root).record("league/personnel/observables/week_%02d.json" % int(week))


def feedback_record():
    from .player_state import model
    fb = model().get("feedback", {})
    return {"applied": fb.get("applied"), "weights": fb.get("reconciled")}


def club_rows(team_input, identities=None):
    """One club's observable rows from its TeamInput dict."""
    record = ((team_input.get("strength") or {}).get("players") or {})
    active = {str(a).split(":", 1)[-1] for a in (team_input.get("active_players") or ())}
    roster = team_input.get("roster")
    if roster is None:
        # Legacy synthetic inputs name their players "POS:id" in active_players.
        roster = [{"player_id": str(a).split(":", 1)[-1], "position": str(a).split(":", 1)[0] if ":" in str(a) else "",
                   "available": True} for a in (team_input.get("active_players") or ())]
    rows = []
    for p in roster:
        pid = p["player_id"]
        gsis = (record.get(pid) or {}).get("gsis_id") or p.get("gsis_id") or (identities or {}).get(pid)
        hold = p.get("medical_limitation")
        rows.append({"player_id": pid, "gsis_id": gsis, "group": group(p["position"]), "position": p["position"],
                     "depth": p.get("depth"), "available": bool(p["available"]),
                     "hold": hold if hold else (None if p["available"] else "unavailable"),
                     "active": pid in active})
    return rows


def from_package(package, identities=None):
    """The observables record of a frozen weekly package."""
    clubs = {}
    events = {}
    for game in package["games"]:
        for side in ("away", "home"):
            team = game[side]
            clubs[team] = club_rows(game[side + "_input"], identities)
            events[team] = game["event_id"]
    return {"schema": SCHEMA, "season": int(package["season"]), "week": int(package["week"]),
            "basis": "frozen weekly TeamInput package at closure",
            "events": dict(sorted(events.items())), "clubs": dict(sorted(clubs.items())),
            "feedback": feedback_record()}


def season_identities(season, root=ROOT):
    """{player_id: gsis_id}: the branch identity table plus the Week 1
    library's own ids (a club outside a later slate, such as a bye-week club,
    is in the library only); the two must agree where both hold a name."""
    from . import depth_library, week_inputs
    out = dict(week_inputs.identity_map(season, root))
    path = SeasonPaths(int(season), root).background_depth
    if path.is_file():
        for club in depth_library.load(path)["clubs"].values():
            for p in club["players"]:
                gsis = p.get("gsis_id")
                if not gsis:
                    continue
                if out.get(p["player_id"], gsis) != gsis:
                    raise ValueError("identity conflict for %s: %s (identity table) against %s (Week 1 library)"
                                     % (p["player_id"], out[p["player_id"]], gsis))
                out.setdefault(p["player_id"], gsis)
    return out


def write(record, root=ROOT):
    path = observables_path(record["week"], record["season"], root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return path


def rebuild_errors(package, receipts_dir, skip=()):
    """Why a rebuilt package does not reproduce the closed week: a club whose
    dressed list differs from its receipt's player rows (clubs in `skip`
    are not compared)."""
    errors = []
    for game in package["games"]:
        path = Path(receipts_dir) / game["receipt"]
        if not path.is_file():
            errors.append("%s: no closed receipt" % game["event_id"])
            continue
        receipt = json.loads(path.read_text(encoding="utf-8"))
        for side in ("away", "home"):
            team = game[side]
            if team in skip:
                continue
            dressed = set(game[side + "_input"]["active_players"])
            played = set((receipt["team_stats"].get(team) or {}).get("players") or {})
            if dressed != played:
                errors.append("%s: %s dressed %d, receipt holds %d (missing %s; extra %s)"
                              % (game["event_id"], team, len(dressed), len(played),
                                 ", ".join(sorted(played - dressed)[:3]) or "none",
                                 ", ".join(sorted(dressed - played)[:3]) or "none"))
    return errors


RECEIPT_BASIS = ("closed full receipt: the frozen Jacksonville package of this week was not retained "
                 "(.sim_cache is ephemeral) and the current roster and depth chart no longer reproduce it; "
                 "the 46 who dressed are listed with no depth rank, and the seven inactives and any hold "
                 "are not recoverable here")


def _jacksonville_from_receipt(receipt, team):
    """A Jacksonville input for a closed week from its full receipt: the
    dressed players and their positions only (labelled RECEIPT_BASIS)."""
    from .week_inputs import UNIT
    players = receipt["team_stats"][team]["players"]
    roster = [{"player_id": pid, "position": row["position"], "available": True,
               "unit": UNIT.get(group(row["position"]), "offense"), "roles": [], "depth": None}
              for pid, row in sorted(players.items())]
    return {"team_id": team, "active_players": [p["player_id"] for p in roster], "roster": roster,
            "offensive_call_sheet": []}


def rebuild_record(week, season, root=ROOT, strength_model=None):
    """The observables record of a closed week rebuilt from committed data.
    Background clubs must reproduce their closed receipts (else this fails
    closed). Jacksonville's rows come from its closed full receipt when the
    current controlled roster and depth chart no longer rebuild that week's
    frozen input, and the record says so (RECEIPT_BASIS)."""
    from unittest import mock
    from . import week_inputs
    from scripts.build_week_inputs import AVERAGE_ANCHORS, call_sheet_path
    from scripts.render_season_stats import load_receipts
    paths = SeasonPaths(int(season), root)
    sheet_path = call_sheet_path(int(week), int(season))
    if sheet_path is None:
        raise ValueError("no frozen call sheet for week %d" % int(week))
    sheet = json.loads(sheet_path.read_text(encoding="utf-8"))["offensive_call_sheet"]
    receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < int(week)]
    own = [r for r in load_receipts(paths.receipts) if int(r["week"]) == int(week)
           and week_inputs.PROTAGONIST in (r["away"], r["home"])]
    bases = {}
    try:
        package = week_inputs.build_package(int(week), receipts, sheet, AVERAGE_ANCHORS, int(season),
                                            strength_model=strength_model)
    except ValueError as exc:
        if not own or "Jacksonville" not in str(exc):
            raise
        receipt_input = _jacksonville_from_receipt(own[0], week_inputs.PROTAGONIST)
        with mock.patch.object(week_inputs, "jacksonville_input", return_value=dict(receipt_input)):
            package = week_inputs.build_package(int(week), receipts, sheet, AVERAGE_ANCHORS, int(season),
                                                strength_model=strength_model)
        bases[week_inputs.PROTAGONIST] = RECEIPT_BASIS
    errors = rebuild_errors(package, paths.receipts)
    if errors:
        raise ValueError("week %d rebuild does not reproduce the closed packets: %s" % (int(week), "; ".join(errors)))
    record = from_package(package, season_identities(season, root))
    record["basis"] = "deterministic rebuild of the closed week's package, reproducing its receipts"
    if bases:
        record["club_basis"] = bases
    return record


def backfill(week, season, root=ROOT, strength_model=None):
    """Rebuild a closed week's observables (rebuild_record) and write them."""
    record = rebuild_record(week, season, root, strength_model)
    return record, write(record, root)
