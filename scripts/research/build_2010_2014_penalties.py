#!/usr/bin/env python3
"""Build the kernel 2014.6 batch B11 penalty artifact (data only).

  python scripts/research/build_2010_2014_penalties.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_penalties.json and the generated tables of
library/2010_2014_penalty_calibration.md (between its generated markers). Sources come only
through scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR. The committed 2010-2014 field-position artifact (pinned by sha256 in
the header) supplies the penalty-type vocabulary and the nominal yards the drive tuples carry;
the drive clauses are re-derived here with the committed annotation (league_base_2010_2014
.penalties_of), so they are exactly the tuples' ``pen`` records.

What it holds, every value counted here (pass 1 nflverse, pass 2 nflscrapR by separately
written code):

- the automatic-first-down class of each defensive foul type, from the accepted defensive
  clauses on single-clause no-play drive rows whose yards fall short of the line to gain:
  automatic when the two passes' pooled share carrying the source's first-down-by-penalty
  flag is at least one half, yardage only when it is below one half, and replay (the record's
  own real flag) when no such clause exists or the two passes fall on opposite sides of one
  half;
- the half-distance rule's evidence: an accepted record REDUCED_BELOW_NOMINAL or more yards
  below its type's nominal yards is a half-distance enforcement (placed only where half the
  distance to the goal it moves toward, floor or ceiling in whole yards, equals its yards);
  the counts of such no-play clauses that sit at half the distance at their own real spot,
  of those whose full nominal yards would have been legal there, and of the one-yard-short
  records (the feed's whole-yard spots: half are half distances, half full enforcements, so
  they keep the full rule) in both passes;
- the sourced fouler group shares by type and side (single-clause scrimmage and no-play drive
  rows, the fouler's position group on that season's roster), credit only;
- the first-down convention: the scrimmage plays of drives flagged first_down_penalty and how
  many of them also carry the rushing or passing first-down flag (the source credits both, so
  the engine's walk does: an automatic foul on a play that made its own first down is still a
  first down by penalty), in both passes;
- the band centres of the B11 rows (pre-build specification section 5) in the engine's scope:
  the drive clauses the engine replays (every clause on a drive's own rows except those after
  or on the terminal snap of a touchdown, turnover, safety or downs drive and those on its punt
  or field-goal row: runtime.penalties.classify on the same records) plus the clauses on the
  kick rows the engine draws (punts; kickoffs from the 35 from 2011 and free kicks; onside
  kicks and return touchdowns left out): accepted penalties, penalty yards and penalty first
  downs per team-game with their team-game dispersion and standard deviation; informational:
  the defense share of accepted drive penalties, declined and offsetting clauses and kick-play
  penalties per team-game, and the clauses left out of the scope;
- the second pass: the same rows from nflscrapR's own penalty columns (one accepted penalty
  per row), compared within AGREE_SE standard errors.

Team, game and player identifiers are read only to count team-games, fouling clubs and
position groups; nothing club-, game-, player- or date-keyed is written. Stdlib only;
deterministic.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (str(HERE), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import build_2012_field_position_model as fp  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402
from runtime import penalties as rp  # noqa: E402

DATA = ROOT / "library" / "data"
OUT = DATA / "2010_2014w4_penalties.json"
RECORD = ROOT / "library" / "2010_2014_penalty_calibration.md"
FIELD_POSITION = DATA / "2010_2014w4_nfl_field_position_model.json"
SEASONS = lb.SEASONS
KICKOFF_FROM = 2011          # kickoffs from the 35 (the 2011 rule change; pre-build spec 1B.1)
SCRIMMAGE_ROWS = ("run", "pass", "qb_kneel", "qb_spike", "no_play")
# Classification rules (batch B11, written after the design phase's table and the half-distance
# match rates were seen; disclosed in runtime/2014_engine_decisions.md and the library record).
AUTO_MAJORITY = 0.5
REDUCED_BELOW_NOMINAL = 2
AGREE_SE = 2.0
REVERSED = re.compile(r"REVERSED\.", re.I)


def counted(desc):
    parts = REVERSED.split(desc or "")
    return parts[-1] if len(parts) > 1 else (desc or "")


def pair(k, n):
    return [int(k), int(n)]


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================================ pass 1 (nflverse, committed loader)

def _clubs_of_game(rows):
    clubs = collections.defaultdict(set)
    for r in rows:
        for key in ("home_team", "away_team"):
            if r.get(key):
                clubs[r["game_id"]].add(fp.alias(r[key]))
    return clubs


def _kick_scope(d, season):
    """The kick row before drive d the engine's pools hold (lb.transition_records' scope), as
    (row, site, kicking club) or None."""
    kind, det = fp.start_type(d)
    if kind in ("kickoff", "safety_free_kick"):
        if kind == "kickoff" and season < KICKOFF_FROM:
            return None
        k = det["kick_row"]
        outcome = fp.kickoff_outcome(k)
        spot = fp.kick_spot_own(k)
        if outcome in ("onside", "return_td") or lb.flag_td(k) or spot != (35 if kind == "kickoff" else 20):
            return None
        kicking = k["defteam"] if k["play_type"] == "kickoff" or fp.is_kick_row(k) else k["posteam"]
        return k, "kickoff" if kind == "kickoff" else "free_kick", fp.alias(kicking)
    if kind == "punt":
        t = d["prev"]["terminal"]
        return t, "punt", fp.alias(t["posteam"])
    if kind == "same_team_continuation" and d["prev"] is not None and d["prev"]["category"] == "punt":
        t = d["prev"]["terminal"]
        if lb.flag_td(t):
            return None
        return t, "punt", fp.alias(t["posteam"])
    return None


def pass1_season(season, dest, codes, nominal):
    name = lb.pbp_name(season, "nflverse")
    fouler_of = {}
    for raw in sources.rows(name, dest):
        if raw.get("season_type") != "REG":
            continue
        pid = raw.get("penalty_player_id")
        if pid and pid != "NA":
            fouler_of[(raw["game_id"], _num(raw.get("play_id")))] = pid
    rows = lb.load_rows(season, "nflverse", dest)
    pos_map = lb.positions(season, dest)
    lb.repair_split_drives(rows)
    path = sources.source_path(name, dest)
    with lb._committed_load(rows):
        ex = fp.extract(path, "nflverse", pos_map)
    clubs = _clubs_of_game(rows)
    team_games = {(g, c) for g, cs in clubs.items() for c in cs}
    drives = []
    auto = collections.defaultdict(lambda: [0, 0])
    half = []
    groups = collections.defaultdict(collections.Counter)
    kicks = []
    flagged = [0, 0]   # scrimmage plays flagged first_down_penalty: also a scrimmage first down, all
    for d in ex["drives"]:
        game = d["first"]["game_id"]
        offense = fp.alias(d["posteam"])
        others = [c for c in clubs[game] if c != offense]
        defense = others[0] if others else None
        pen = []
        for p in lb.penalties_of(d, pos_map)["pen"]:
            if p[1] not in codes:
                raise ValueError("%s penalty type %r is not in the field-position vocabulary" % (season, p[1]))
            pen.append([p[0], codes[p[1]], p[2], p[3], p[4], p[5], p[6], p[7], p[8], nominal.get(p[1])])
        drives.append({"game": game, "offense": offense, "defense": defense, "category": d["category"],
                       "plays": d["plays"], "pen": pen})
        for r in lb.drive_rows(d):
            if r["play_type"] in ("run", "pass") and r.get("first_down_penalty") == 1:
                flagged[1] += 1
                flagged[0] += int(r.get("first_down_rush") == 1 or r.get("first_down_pass") == 1)
            found, _ = lb.clauses(r)
            if not found:
                continue
            pt = r["play_type"]
            if len(found) == 1 and pt in SCRIMMAGE_ROWS:
                team, kind, status, yards = found[0]
                side = "O" if lb.same_club(team, d["posteam"]) else "D"
                pid = fouler_of.get((r["game_id"], r["play_id"]))
                groups["%s|%s" % (side, kind)][lb.group_of(pos_map, pid) or "unknown"] += 1
            if pt != "no_play":
                continue
            accepted = [c for c in found if c[2] == "A" and c[3] is not None]
            if len(found) != 1 or len(accepted) != 1:
                continue
            team, kind, status, yards = accepted[0]
            defensive = not lb.same_club(team, d["posteam"])
            if defensive and r.get("ydstogo") is not None and yards < r["ydstogo"]:
                cell = auto[kind]
                cell[1] += 1
                cell[0] += int(r.get("first_down_penalty") == 1)
            if nominal.get(kind) is not None and yards < nominal[kind] and r.get("yardline_100") is not None:
                spot = int(round(r["yardline_100"]))
                half.append((kind, spot if defensive else 100 - spot, yards))
        scope = _kick_scope(d, season)
        if scope is not None:
            k, site, kicking = scope
            receiving = next((c for c in clubs[game] if c != kicking), None)
            kicks.append({"game": game, "site": site, "kicking": kicking, "receiving": receiving,
                          "pen": lb._kick_penalties(k)})
    return {"games": ex["games"], "team_games": sorted(team_games), "drives": drives, "auto": dict(auto),
            "half_rows": half, "groups": {k: dict(v) for k, v in groups.items()}, "kicks": kicks,
            "flagged": flagged}


# ============================================================================ pass 2 (nflscrapR, separate code)

def _f(r, key):
    return (r.get(key) or "").strip() == "1"


def _team(r, key):
    value = (r.get(key) or "").strip()
    return fp.alias(value) if value and value != "NA" else ""


def _int(r, key):
    value = _num(r.get(key))
    return None if value is None else int(round(value))


SCRIM2 = ("run", "pass", "qb_kneel", "qb_spike")
TERMINAL2 = ("touchdown", "interception", "fumble_lost", "safety", "downs")


def _category2(rows, posteam):
    """The second pass's own reading of a drive's category from its last offensive play."""
    own = [r for r in rows if _team(r, "posteam") == posteam and not _f(r, "two_point_attempt")
           and (r.get("play_type") or "").strip() in SCRIM2 + ("punt", "field_goal")]
    if not own:
        return "clock", -1
    last = own[-1]
    play = last["play_type"].strip()
    index = rows.index(last)
    if play == "punt":
        return "punt", index
    if play == "field_goal":
        return "field_goal_attempt", index
    if _f(last, "touchdown") and _team(last, "td_team") == posteam:
        return "touchdown", index
    if _f(last, "interception"):
        return "interception", index
    if _f(last, "fumble_lost"):
        return "fumble_lost", index
    if _f(last, "safety"):
        return "safety", index
    if _f(last, "fourth_down_failed"):
        return "downs", index
    return "clock", index


def pass2_season(season, dest):
    name = lb.pbp_name(season, "nflscrapr")
    by_game = collections.OrderedDict()
    for r in sources.rows(name, dest):
        by_game.setdefault(r.get("game_id"), []).append(r)
    c = collections.Counter()
    acc = collections.Counter()
    yards = collections.Counter()
    pfd = collections.Counter()
    auto = collections.defaultdict(lambda: [0, 0])
    halves = []
    flagged = [0, 0]
    team_games = set()
    for game, rows in by_game.items():
        clubs = {_team(r, "home_team") for r in rows} | {_team(r, "away_team") for r in rows}
        clubs.discard("")
        for club in clubs:
            team_games.add((game, club))
        drives = collections.OrderedDict()
        for r in rows:
            play = (r.get("play_type") or "").strip()
            if play == "kickoff":
                continue
            key = (r.get("drive") or "").strip()
            if key and key != "NA":
                drives.setdefault(key, []).append(r)
        for key, drows in drives.items():
            teams = collections.Counter(_team(r, "posteam") for r in drows if _team(r, "posteam"))
            if not teams:
                continue
            posteam = teams.most_common(1)[0][0]
            category, last_index = _category2(drows, posteam)
            for index, r in enumerate(drows):
                play = (r.get("play_type") or "").strip()
                if _team(r, "posteam") != posteam or _f(r, "two_point_attempt") or play in ("extra_point",):
                    continue
                if play in ("run", "pass") and _f(r, "first_down_penalty"):
                    flagged[1] += 1
                    flagged[0] += int(_f(r, "first_down_rush") or _f(r, "first_down_pass"))
                if not _f(r, "penalty"):
                    continue
                fouler = _team(r, "penalty_team")
                py = _int(r, "penalty_yards") or 0
                if not fouler:
                    continue
                if play == "punt":
                    if not _f(r, "return_touchdown"):
                        acc[(game, fouler)] += 1
                        yards[(game, fouler)] += abs(py)
                        c["kick_accepted"] += 1
                    continue
                if play == "field_goal":
                    c["kick_row_excluded"] += 1
                    continue
                if play not in SCRIM2 + ("no_play",):
                    continue
                if category in TERMINAL2 and index >= last_index:
                    c["post_terminal_excluded"] += 1
                    continue
                acc[(game, fouler)] += 1
                yards[(game, fouler)] += abs(py)
                c["drive_accepted"] += 1
                c["drive_defense"] += fouler != posteam
                if _f(r, "first_down_penalty"):
                    pfd[(game, posteam)] += 1
                if play == "no_play" and fouler != posteam:
                    togo = _int(r, "ydstogo")
                    if togo is not None and abs(py) < togo:
                        cell = auto[(r.get("penalty_type") or "").strip()]
                        cell[1] += 1
                        cell[0] += int(_f(r, "first_down_penalty"))
                if play == "no_play":
                    spot = _int(r, "yardline_100")
                    if spot is not None:
                        # (type, distance to the goal the foul moves toward, yards); read
                        # against the nominal table in half_block.
                        distance = spot if fouler != posteam else 100 - spot
                        halves.append(((r.get("penalty_type") or "").strip(), distance, abs(py)))
        for r in rows:
            play = (r.get("play_type") or "").strip()
            if play != "kickoff" or not _f(r, "penalty"):
                continue
            spot = _int(r, "yardline_100")
            text = (r.get("desc") or "").lower()
            if "onside" in text or _f(r, "return_touchdown") or _f(r, "own_kickoff_recovery_td"):
                continue
            if spot == 35 and season < KICKOFF_FROM:
                continue
            if spot not in (35, 20):
                continue
            fouler = _team(r, "penalty_team")
            if fouler:
                acc[(game, fouler)] += 1
                yards[(game, fouler)] += abs(_int(r, "penalty_yards") or 0)
                c["kick_accepted"] += 1
    return {"games": len(by_game), "team_games": sorted(team_games), "counts": dict(c), "accepted": dict(acc),
            "yards": dict(yards), "first_downs": dict(pfd), "auto": dict(auto), "half_rows": halves,
            "flagged": flagged}


# ============================================================================ analysis

def _share(cell):
    k, n = cell
    return k / n if n else None


def auto_classes(p1, p2):
    """Each defensive type's automatic-first-down class (module docstring)."""
    t1, t2 = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    for s in SEASONS:
        for kind, (k, n) in p1[s]["auto"].items():
            t1[kind][0] += k
            t1[kind][1] += n
        for kind, (k, n) in p2[s]["auto"].items():
            t2[kind][0] += k
            t2[kind][1] += n
    out = {}
    for kind in sorted(set(t1) | set(t2)):
        a, b = list(t1.get(kind, [0, 0])), list(t2.get(kind, [0, 0]))
        pooled = [a[0] + b[0], a[1] + b[1]]
        sides = {_share(x) >= AUTO_MAJORITY for x in (a, b) if x[1]}
        entry = {"nflverse": a, "nflscrapr": b}
        if not pooled[1]:
            entry["class"] = "replay"
        elif len(sides) > 1:
            entry["class"] = "replay"
            entry["note"] = "the passes fall on opposite sides of one half"
        else:
            entry["class"] = "automatic" if _share(pooled) >= AUTO_MAJORITY else "yardage"
        out[kind] = entry
    return out


def half_evidence(rows, nominal):
    """[records, at half the distance (floor or ceiling), full nominal legal there] of the reduced
    records (REDUCED_BELOW_NOMINAL or more below nominal) and of the one-yard-short records."""
    out = {"reduced": [0, 0, 0], "one_short": [0, 0, 0]}
    by_type = collections.defaultdict(lambda: [0, 0, 0])
    for kind, distance, y in rows:
        nom = nominal.get(kind)
        if nom is None or y >= nom:
            continue
        key = "reduced" if nom - y >= REDUCED_BELOW_NOMINAL else "one_short"
        at_half = int(y in (distance // 2, (distance + 1) // 2))
        full = int(2 * nom <= distance)
        for cell in (out[key], by_type["%s|%s" % (key, kind)]):
            cell[0] += 1
            cell[1] += at_half
            cell[2] += full
    out["by_type"] = {k: by_type[k] for k in sorted(by_type)}
    return out


def half_block(p1, p2, nominal):
    rows1 = [row for s in SEASONS for row in p1[s]["half_rows"]]
    rows2 = [row for s in SEASONS for row in p2[s]["half_rows"]]
    return {
        "reduced_below_nominal": REDUCED_BELOW_NOMINAL,
        "rule": ("an accepted record of a type with nominal yards, %d or more yards below them, is a half-distance "
                 "enforcement: legal only where half the distance to the goal line it moves toward (floor or "
                 "ceiling in whole yards) equals its yards; every other record keeps the full rule (a defensive "
                 "foul at most half the distance to the goal, a defensive pass interference to the 1 at most, an "
                 "offensive foul at most half the distance to its own goal)" % REDUCED_BELOW_NOMINAL),
        "evidence_rows": "single-clause accepted no-play drive rows below their type's nominal yards, the distance "
                         "from that row's own spot",
        "nflverse": half_evidence(rows1, nominal),
        "nflscrapr": half_evidence(rows2, nominal),
    }


def fouler_shares(p1):
    total = collections.defaultdict(collections.Counter)
    for s in SEASONS:
        for key, counts in p1[s]["groups"].items():
            total[key].update(counts)
    return {key: dict(sorted(v.items())) for key, v in sorted(total.items())}


def _moments(values):
    return [len(values), sum(values), sum(v * v for v in values)]


def _drift(by):
    return lb.rate_drift(list(by.values()))


def centres(p1, model):
    """The B11 band centres in the engine's scope (module docstring)."""
    per = {}
    out_counts = collections.Counter()
    for s in SEASONS:
        tag = lb.TAG[s]
        acc = collections.Counter()
        yards = collections.Counter()
        pfd = collections.Counter()
        declined = collections.Counter()
        offsetting = collections.Counter()
        c = collections.Counter()
        for d in p1[s]["drives"]:
            plan = rp.classify(model, d["pen"], d["category"], d["plays"])
            c["post_terminal_excluded"] += len(plan.post)
            c["kick_row_excluded"] += len(plan.kick_row)
            rows = [e.records for e in plan.events] + [a.records for a in plan.attached]
            for rs in rows:
                if any(r.real_fd for r in rs):
                    pfd[(d["game"], d["offense"])] += 1
                for r in rs:
                    club = d["offense"] if r.side == "O" else d["defense"]
                    if r.status == "A":
                        acc[(d["game"], club)] += 1
                        yards[(d["game"], club)] += abs(r.yards)
                        c["drive_accepted"] += 1
                        c["drive_defense"] += r.side == "D"
                    elif r.status == "D":
                        declined[(d["game"], club)] += 1
                    else:
                        offsetting[(d["game"], club)] += 1
        for k in p1[s]["kicks"]:
            for kind, side, signed, status in k["pen"]:
                club = k["kicking"] if side == "K" else k["receiving"]
                if status == "A":
                    acc[(k["game"], club)] += 1
                    yards[(k["game"], club)] += abs(signed or 0)
                    c["kick_accepted"] += 1
                    c["kick_accepted:%s" % k["site"]] += 1
                elif status == "D":
                    declined[(k["game"], club)] += 1
                else:
                    offsetting[(k["game"], club)] += 1
        keys = p1[s]["team_games"]
        per[tag] = {
            "team_games": len(keys),
            "accepted": [acc.get(k, 0) for k in keys],
            "yards": [yards.get(k, 0) for k in keys],
            "first_downs": [pfd.get(k, 0) for k in keys],
            "declined": sum(declined.values()), "offsetting": sum(offsetting.values()),
            "counts": dict(sorted(c.items())),
        }
        out_counts.update(c)
    tags = [lb.TAG[s] for s in SEASONS]

    def rate(field):
        by = {t: pair(sum(per[t][field]), per[t]["team_games"]) for t in tags}
        return by

    def moments(field):
        return {t: _moments(per[t][field]) for t in tags}

    out = {}
    for name, field in (("accepted_penalties_per_team_game", "accepted"),
                        ("penalty_yards_per_team_game", "yards"),
                        ("penalty_first_downs_per_team_game", "first_downs")):
        by = rate(field)
        pooled = [sum(v[0] for v in by.values()), sum(v[1] for v in by.values())]
        m = [0, 0, 0]
        for v in moments(field).values():
            m = [a + b for a, b in zip(m, v)]
        n, total, squares = m
        mean = total / n
        var = (squares - n * mean * mean) / (n - 1)
        out[name] = {"by_season": by, "pooled": pooled, "drift": _drift(by), "moments": m,
                     "dispersion": round(var / mean, 6) if mean else 1.0, "sd": round(math.sqrt(var), 6)}
    def_by = {t: pair(per[t]["counts"].get("drive_defense", 0), per[t]["counts"].get("drive_accepted", 0))
              for t in tags}
    out["defense_share_of_accepted_drive_penalties"] = {
        "by_season": def_by, "pooled": [sum(v[0] for v in def_by.values()), sum(v[1] for v in def_by.values())],
        "drift": lb.share_drift(list(def_by.values()))}
    for name, field in (("declined_per_team_game", "declined"), ("offsetting_per_team_game", "offsetting")):
        by = {t: pair(per[t][field], per[t]["team_games"]) for t in tags}
        out[name] = {"by_season": by, "pooled": [sum(v[0] for v in by.values()), sum(v[1] for v in by.values())],
                     "drift": _drift(by)}
    kick_by = {t: pair(per[t]["counts"].get("kick_accepted", 0), per[t]["team_games"]) for t in tags}
    out["kick_play_penalties_per_team_game"] = {
        "by_season": kick_by, "pooled": [sum(v[0] for v in kick_by.values()), sum(v[1] for v in kick_by.values())],
        "drift": _drift(kick_by),
        "sites": {site: sum(per[t]["counts"].get("kick_accepted:%s" % site, 0) for t in tags)
                  for site in ("kickoff", "free_kick", "punt")}}
    out["excluded_per_team_game"] = {
        name: [sum(per[t]["counts"].get(name, 0) for t in tags), sum(per[t]["team_games"] for t in tags)]
        for name in ("post_terminal_excluded", "kick_row_excluded")}
    return out, per


def second_pass_compare(p1_centres, p2):
    tags = [lb.TAG[s] for s in SEASONS]
    seasons2 = {lb.TAG[s]: p2[s] for s in SEASONS}
    rows, disagreements = [], []

    def compare(metric, k1, n1, k2, n2, rate=True):
        p, q = k1 / n1, k2 / n2
        if rate:
            se = math.sqrt(max(k1, 1) / n1 ** 2 + max(k2, 1) / n2 ** 2)
        else:
            se = math.sqrt(max(p * (1 - p), 1e-9) / n1 + max(q * (1 - q), 1e-9) / n2)
        ok = abs(p - q) <= AGREE_SE * se
        rows.append({"metric": metric, "nflverse": [k1, n1], "nflscrapr": [k2, n2], "within_2se": ok})
        if not ok:
            disagreements.append(metric)

    n2 = sum(len(seasons2[t]["team_games"]) for t in tags)
    for metric, key, field in (("accepted penalties per team-game", "accepted_penalties_per_team_game", "accepted"),
                               ("penalty first downs per team-game", "penalty_first_downs_per_team_game",
                                "first_downs")):
        k1, n1 = p1_centres[key]["pooled"]
        k2 = sum(sum(seasons2[t][field].values()) for t in tags)
        compare(metric, k1, n1, k2, n2)
    # Yards: a mean per team-game, its standard error from each pass's own team-game SD.
    m1 = p1_centres["penalty_yards_per_team_game"]["moments"]
    values2 = [seasons2[t]["yards"].get(k, 0) for t in tags for k in seasons2[t]["team_games"]]
    m2 = _moments(values2)
    mean1, mean2 = m1[1] / m1[0], m2[1] / m2[0]
    var1 = (m1[2] - m1[0] * mean1 * mean1) / (m1[0] - 1)
    var2 = (m2[2] - m2[0] * mean2 * mean2) / (m2[0] - 1)
    se = math.sqrt(var1 / m1[0] + var2 / m2[0])
    ok = abs(mean1 - mean2) <= AGREE_SE * se
    rows.append({"metric": "penalty yards per team-game (mean, team-game SD)", "nflverse": [m1[1], m1[0]],
                 "nflscrapr": [m2[1], m2[0]], "within_2se": ok})
    if not ok:
        disagreements.append("penalty yards per team-game")
    d1 = p1_centres["defense_share_of_accepted_drive_penalties"]["pooled"]
    d2 = [sum(seasons2[t]["counts"].get("drive_defense", 0) for t in tags),
          sum(seasons2[t]["counts"].get("drive_accepted", 0) for t in tags)]
    compare("defense share of accepted drive penalties", d1[0], d1[1], d2[0], d2[1], rate=False)
    k1 = p1_centres["kick_play_penalties_per_team_game"]["pooled"]
    compare("kick-play penalties per team-game", k1[0], k1[1],
            sum(seasons2[t]["counts"].get("kick_accepted", 0) for t in tags), n2)
    return {"source": "nflscrapR reg_pbp 2010-2014 (2014 cut), its own penalty columns (penalty, penalty_team, "
                      "penalty_yards, penalty_type, first_down_penalty: one accepted penalty per row) and its own "
                      "drive key, read by separately written code (pass2_season)",
            "rule": "a pooled rate or share agrees when the passes differ by at most %.0f standard errors of their "
                    "difference" % AGREE_SE,
            "comparison": rows, "disagreements": disagreements, "agree": not disagreements,
            "single_pass": ["declined and offsetting clauses (nflscrapR flags accepted penalties only)",
                            "the fouler group shares (pass 1 only; the design's pass 2 read multi-clause rows "
                            "differently)"],
            "per_season": {t: {"team_games": len(seasons2[t]["team_games"]),
                               "accepted": sum(seasons2[t]["accepted"].values()),
                               "yards": sum(seasons2[t]["yards"].values()),
                               "first_downs": sum(seasons2[t]["first_downs"].values()),
                               "counts": dict(sorted(seasons2[t]["counts"].items()))} for t in tags}}


def build(dest, log=print):
    fp_text = FIELD_POSITION.read_bytes()
    fp_art = json.loads(fp_text)
    types = list(fp_art["penalty_types"])
    codes = {name: i for i, name in enumerate(types)}
    nominal = dict(fp_art["penalty_nominal_yards"])
    p1, p2 = {}, {}
    for s in SEASONS:
        log("penalties nflverse %s" % lb.TAG[s])
        p1[s] = pass1_season(s, dest, codes, nominal)
        log("penalties nflscrapr %s" % lb.TAG[s])
        p2[s] = pass2_season(s, dest)
    autos = auto_classes(p1, p2)
    halves = half_block(p1, p2, nominal)
    groups = fouler_shares(p1)
    artifact = {
        "schema": rp.SCHEMA,
        "seasons": [lb.TAG[s] for s in SEASONS],
        "season_type": "regular",
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; no club, game, player or date field. 2013 and 2014 Weeks 1-4 "
                                 "are an anonymous post-divergence league population (pooled only)."),
        "builder": "scripts/research/build_2010_2014_penalties.py",
        "pre_build_specification_sha256": pre_build_specification.digest(),
        "field_position_sha256": hashlib.sha256(fp_text).hexdigest(),
        "penalty_types": types,
        "auto_first_down": {
            "rule": ("accepted defensive clauses on single-clause no-play drive rows whose yards fall short of the "
                     "line to gain, by type: automatic when the two passes' pooled share carrying the "
                     "first-down-by-penalty flag is at least %.1f, yardage only below it; replay (the record's own "
                     "real flag) when no such clause exists or the passes fall on opposite sides" % AUTO_MAJORITY),
            "types": autos},
        "half_distance": halves,
        "fouler_groups": {
            "rule": ("single-clause scrimmage and no-play drive rows by type and side (O offense, D defense), the "
                     "fouler's position group on that season's roster (unknown when the feed names no player or "
                     "the roster holds none); credit only, never player evidence"),
            "shares": groups},
        "classification": {
            "events": "a no-play row before the drive's last scrimmage snap (movable) or after it in a punt, field "
                      "goal or clock drive (pre-kick tail)",
            "attached": "clauses on a counted scrimmage snap, ride on a laid-out host snap of their kind",
            "post_terminal": "a no-play row after, or a clause on, the terminal snap of a touchdown, turnover, "
                             "safety or downs drive: enforced after the possession; not replayed",
            "kick_row": "clauses on the drive's own punt or field-goal row: the punt row carries the punt record's "
                        "own clauses; a field-goal row's are not modelled",
            "function": "runtime.penalties.classify",
        },
        "kickoff_from": KICKOFF_FROM,
        "first_down_convention": {
            "rule": ("scrimmage plays of drives flagged first_down_penalty, and those also flagged first_down_rush "
                     "or first_down_pass: [both, all]; the source credits both first downs on one play"),
            "nflverse": [sum(p1[s]["flagged"][0] for s in SEASONS), sum(p1[s]["flagged"][1] for s in SEASONS)],
            "nflscrapr": [sum(p2[s]["flagged"][0] for s in SEASONS), sum(p2[s]["flagged"][1] for s in SEASONS)],
        },
    }
    model = rp.PenaltyModel(dict(artifact, band_centres={}), types)
    centre_block, per = centres(p1, model)
    artifact["band_centres"] = centre_block
    artifact["per_season"] = {t: {k: v for k, v in row.items() if k not in ("accepted", "yards", "first_downs")}
                              for t, row in per.items()}
    artifact["second_pass"] = second_pass_compare(centre_block, p2)
    errors = []
    tg = {lb.TAG[s]: len(p1[s]["team_games"]) for s in SEASONS}
    if tg != {lb.TAG[s]: v for s, v in zip(SEASONS, (512, 512, 512, 512, 122))}:
        errors.append("team-games per season %s differ from the data window" % tg)
    if not artifact["second_pass"]["agree"]:
        log("pass 2 disagrees on: %s" % ", ".join(artifact["second_pass"]["disagreements"]))
    manifest = sources.load_manifest()
    artifact["sources"] = {name: {"sha256": manifest["assets"][name]["sha256"]}
                           for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"),
                                                         lb.roster_name(s))}
    return artifact, errors


# ============================================================================ the library record

BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def _r(p):
    return p[0] / p[1] if p[1] else float("nan")


def tables(art):
    c = art["band_centres"]
    lines = ["Generated by `scripts/research/build_2010_2014_penalties.py` from the artifact; do not edit.", "",
             "| Centre | Count | Of | Value | Dispersion | SD | Season drift p |", "|---|---|---|---|---|---|---|"]
    for name in ("accepted_penalties_per_team_game", "penalty_yards_per_team_game",
                 "penalty_first_downs_per_team_game"):
        e = c[name]
        lines.append("| %s | %d | %d | %.4f | %.3f | %.3f | %s |" % (
            name.replace("_", " "), e["pooled"][0], e["pooled"][1], _r(e["pooled"]), e["dispersion"], e["sd"],
            "%.3f" % e["drift"]["p"] if e.get("drift") else "-"))
    for name in ("defense_share_of_accepted_drive_penalties", "declined_per_team_game", "offsetting_per_team_game",
                 "kick_play_penalties_per_team_game"):
        e = c[name]
        lines.append("| %s (informational) | %d | %d | %.4f | - | - | %s |" % (
            name.replace("_", " "), e["pooled"][0], e["pooled"][1], _r(e["pooled"]),
            "%.3f" % e["drift"]["p"] if e.get("drift") else "-"))
    ex = c["excluded_per_team_game"]
    lines += ["", "Left out of the scope (per team-game): clauses after or on the terminal snap of a touchdown, "
              "turnover, safety or downs drive %d/%d = %.4f; clauses on a drive's own punt or field-goal row %d/%d "
              "= %.4f. Kick-play accepted clauses by site: %s." % (
                  ex["post_terminal_excluded"][0], ex["post_terminal_excluded"][1], _r(ex["post_terminal_excluded"]),
                  ex["kick_row_excluded"][0], ex["kick_row_excluded"][1], _r(ex["kick_row_excluded"]),
                  ", ".join("%s %d" % kv for kv in sorted(c["kick_play_penalties_per_team_game"]["sites"].items()))),
              "", "| Season | Team-games | Accepted | Yards | First downs | Declined | Offsetting |",
              "|---|---|---|---|---|---|---|"]
    for t, row in c["accepted_penalties_per_team_game"]["by_season"].items():
        lines.append("| %s | %d | %d | %d | %d | %d | %d |" % (
            t, row[1], row[0], c["penalty_yards_per_team_game"]["by_season"][t][0],
            c["penalty_first_downs_per_team_game"]["by_season"][t][0], c["declined_per_team_game"]["by_season"][t][0],
            c["offsetting_per_team_game"]["by_season"][t][0]))
    lines += ["", "**Automatic first downs** (defensive no-play clauses short of the line to gain):", "",
              "| Type | nflverse | nflscrapR | Class |", "|---|---|---|---|"]
    for kind, e in art["auto_first_down"]["types"].items():
        lines.append("| %s | %d/%d | %d/%d | %s%s |" % (kind, e["nflverse"][0], e["nflverse"][1], e["nflscrapr"][0],
                                                        e["nflscrapr"][1], e["class"],
                                                        " (%s)" % e["note"] if e.get("note") else ""))
    hd = art["half_distance"]
    lines += ["", "**Half-distance enforcement** (single-clause accepted no-play clauses below nominal yards, at "
              "their own real spot): records / at half the distance (floor or ceiling) / full nominal legal there.",
              "", "| Records | nflverse | nflscrapR |", "|---|---|---|"]
    for key, label in (("reduced", "%d or more below nominal (half-distance records)" % hd["reduced_below_nominal"]),
                       ("one_short", "one yard below nominal (full rule)")):
        lines.append("| %s | %s | %s |" % (label, "/".join(str(v) for v in hd["nflverse"][key]),
                                           "/".join(str(v) for v in hd["nflscrapr"][key])))
    fd = art["first_down_convention"]
    lines += ["", "**First-down convention**: scrimmage plays flagged first_down_penalty that also carry the "
              "rushing or passing first-down flag: nflverse %d of %d, nflscrapR %d of %d." % (
                  fd["nflverse"][0], fd["nflverse"][1], fd["nflscrapr"][0], fd["nflscrapr"][1])]
    sp = art["second_pass"]
    lines += ["", "**Second pass (nflscrapR)**", "", "| Metric | nflverse | nflscrapR | Within 2 SE |",
              "|---|---|---|---|"]
    for row in sp["comparison"]:
        lines.append("| %s | %d/%d | %d/%d | %s |" % (row["metric"], row["nflverse"][0], row["nflverse"][1],
                                                      row["nflscrapr"][0], row["nflscrapr"][1],
                                                      "yes" if row["within_2se"] else "no"))
    lines += ["", "Disagreements: %s. Single pass: %s." % (", ".join(sp["disagreements"]) or "none",
                                                         "; ".join(sp["single_pass"]))]
    return "\n".join(lines) + "\n"


def render_record(art, text):
    if BEGIN not in text or END not in text:
        raise ValueError("%s lacks its generated markers" % RECORD)
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + "\n" + tables(art) + END + tail


def render(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    spec_errors = pre_build_specification.check()
    if spec_errors:
        for e in spec_errors:
            print("SPECIFICATION: " + e, file=sys.stderr)
        return 1
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    art, errors = build(args.sources, log=lambda m: print(m, file=sys.stderr))
    if errors:
        for e in errors:
            print("BUILD FAILURE: " + e, file=sys.stderr)
        return 1
    text = render(art)
    record = render_record(art, RECORD.read_text())
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        ok_md = RECORD.read_text() == record
        print("%s %s" % ("reproduced" if ok else "DIFFERS", OUT.relative_to(ROOT)))
        print("%s %s (generated tables)" % ("reproduced" if ok_md else "DIFFERS", RECORD.relative_to(ROOT)))
        return 0 if ok and ok_md else 1
    OUT.write_text(text)
    RECORD.write_text(record)
    print("wrote %s (%d bytes) and the tables of %s" % (OUT.relative_to(ROOT), len(text), RECORD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
