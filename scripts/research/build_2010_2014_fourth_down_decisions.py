#!/usr/bin/env python3
"""Build the kernel 2014.6 batch B9F fourth-down artifact (data only).

  python scripts/research/build_2010_2014_fourth_down_decisions.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_fourth_down_decisions.json and the generated tables of
library/2010_2014_fourth_down_calibration.md (between its generated markers). Sources come
only through scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR. Rules: library/2014_6_fourth_down_specification.md (frozen before
this builder counted any row; its sha256 and the pre-build specification's are in the
header).

What it holds, every value counted here:
- the league fourth-down decision chart (go, field goal, punt) by distance bin, field zone
  and game state, collapsed by the specification's ladder at MIN_CELL decision rows, with the
  cell of every reachable key;
- the conversion pairs by distance bin and goal to go (collapsed to the distance bin below
  MIN_CELL attempts) and the anonymous fourth-down attempt records the kernel replays;
- the field-goal snap offset (the modal kick distance minus the line of fourth-down kicks);
- the band centres (go share, attempts and decisions per team-game, conversion rate, kick
  shares), per-season counts with their drift tests;
- the second pass: the same quantities recounted from nflscrapR by separately written code,
  compared against pass 1 by the specification's agreement rule.

Team, game and player identifiers are read only to count games; nothing club-, game-,
player- or date-keyed is written. Stdlib only; deterministic.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fourth_down_specification  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library" / "data"
OUT = DATA / "2010_2014w4_fourth_down_decisions.json"
RECORD = ROOT / "library" / "2010_2014_fourth_down_calibration.md"
SCHEMA = "2010-2014w4-nfl-fourth-down-decisions-v1"
SEASONS = (2010, 2011, 2012, 2013, 2014)

SPEC = fourth_down_specification.frozen_rules()
PRE = pre_build_specification.frozen_rules()
MIN_CELL = PRE["thresholds"]["MIN_CELL"]
LATE_BUCKETS = PRE["end_of_half"]["LATE_TIME_BUCKETS"]
NEEDS = PRE["end_of_half"]["NEEDS"]
DIST_BINS = [tuple(b) for b in SPEC["distance_bins"]]
ZONES = [tuple(z) for z in SPEC["zones"]]
COARSE_ZONES = [tuple(z) for z in SPEC["coarse_zones"]]
COARSE_DIST = [tuple(d) for d in SPEC["coarse_distances"]]
H1_SECONDS = SPEC["states"]["h1_seconds"]
Q4_SECONDS = SPEC["states"]["q4_seconds"]
OT_MARGINS = SPEC["states"]["ot_margins"]
OT_FROM = SPEC["data"]["overtime_from_season"]
ACTIONS = tuple(SPEC["actions"])
RECORD_FIELDS = ("distance", "goal_to_go", "kind", "yards", "converted")
# The disclosure example of amendment F1 (its counts are read from the data, never typed).
EXAMPLE_STATE = "q4|le120|trail4_8"
EXAMPLE_KEY = "5-7|40-49|" + EXAMPLE_STATE
# The disclosure example of amendment F2 (fourth and 1 in the club's own territory,
# trailing by 4-8 in the last 2:00; counts read from the data).
F2_EXAMPLE_STATE = EXAMPLE_STATE
F2_EXAMPLE_KEY = "1|70-99|" + F2_EXAMPLE_STATE


# ============================================================================ the frozen keys

def label(edge):
    lo, hi = edge
    return str(lo) if lo == hi else "%d-%d" % (lo, hi)


def find(edges, value):
    for edge in edges:
        if edge[0] <= value <= edge[1]:
            return edge
    raise ValueError("%r outside %r" % (value, edges))


def need_label(diff):
    for name, (lo, hi) in NEEDS.items():
        if lo <= diff <= hi:
            return name
    raise ValueError("score difference %r outside the needs" % diff)


def late_bucket(seconds):
    for name, (lo, hi) in LATE_BUCKETS.items():
        if lo <= seconds <= hi:
            return name
    raise ValueError("%r seconds is not a late window" % seconds)


def ot_margin(diff):
    for name, (lo, hi) in OT_MARGINS.items():
        if lo <= diff <= hi:
            return name
    raise ValueError("score difference %r outside the overtime margins" % diff)


def state_label(*, overtime, q4_seconds_left, h1_seconds_left, diff):
    """The specification's game state: ot|<margin>, q4|<bucket>|<need>, h1_le120 or neutral.
    ``q4_seconds_left`` is the game seconds left when the snap is in the fourth quarter (None
    otherwise), ``h1_seconds_left`` the half's seconds left when it is in the first half."""
    if overtime:
        return "ot|%s" % ot_margin(diff)
    if q4_seconds_left is not None and q4_seconds_left <= Q4_SECONDS:
        return "q4|%s|%s" % (late_bucket(q4_seconds_left), need_label(diff))
    if h1_seconds_left is not None and h1_seconds_left <= H1_SECONDS:
        return "h1_le%d" % H1_SECONDS
    return "neutral"


def all_states():
    states = ["neutral", "h1_le%d" % H1_SECONDS]
    states += ["q4|%s|%s" % (b, n) for b in LATE_BUCKETS for n in NEEDS]
    states += ["ot|%s" % m for m in OT_MARGINS]
    return states


def key_of(distance, line, state):
    return "%s|%s|%s" % (label(find(DIST_BINS, distance)), label(find(ZONES, line)), state)


def merged_state(state):
    """A late state with its time buckets merged (q4|le600|<need>), an overtime state with its
    margins merged (ot|any); the first-half and neutral states are their own merge."""
    if state.startswith("q4|"):
        return "q4|le%d|%s" % (Q4_SECONDS, state.split("|")[2])
    if state.startswith("ot|"):
        return "ot|any"
    return state


def ladder_frozen(dbin, zone, state):
    """(rung, cell label) for one key under the specification's frozen ladder (section 3), kept
    for the record: amendment F1 replaced it before any kernel use (ladder)."""
    rungs = [("full", "%s/%s/%s" % (label(dbin), label(zone), state))]
    merged = "q4|le%d|%s" % (Q4_SECONDS, state.split("|")[2]) if state.startswith("q4|") else state
    if state.startswith("q4|"):
        rungs.append(("time_merged", "%s/%s/%s" % (label(dbin), label(zone), merged)))
    if state != "neutral":
        rungs.append(("zone_coarse", "%s/Z%s/%s" % (label(dbin), label(find(COARSE_ZONES, zone[0])), merged)))
    return rungs + _neutral_rungs(dbin, zone)


def _neutral_rungs(dbin, zone):
    return [("neutral", "%s/%s/neutral" % (label(dbin), label(zone))),
            ("distance_coarse", "D%s/%s/neutral" % (label(find(COARSE_DIST, dbin[0])), label(zone))),
            ("zone_only", "*/%s/neutral" % label(zone))]


# Amendment F1 (made after the frozen ladder was run and printed, before any kernel use; the
# artifact's amendments block discloses it): a late, first-half or overtime state is kept,
# with its distance and field zone coarsened, before it gives way to the neutral state, and a
# field zone (at least its coarse zone) is kept on every rung, so a field-goal decision always
# follows the kick's distance.
LADDER_F1 = ("full", "coarse", "zone_state", "coarse_merged", "zone_merged", "neutral", "distance_coarse",
             "zone_only")


def ladder_f1(dbin, zone, state):
    """(rung, cell label) for one key under amendment F1, most specific first
    (kept for the record: amendment F2 replaced it before any kernel use)."""
    rungs = [("full", "%s/%s/%s" % (label(dbin), label(zone), state))]
    if state != "neutral":
        dc, zc = label(find(COARSE_DIST, dbin[0])), label(find(COARSE_ZONES, zone[0]))
        rungs += [("coarse", "D%s/Z%s/%s" % (dc, zc, state)), ("zone_state", "*/Z%s/%s" % (zc, state))]
        merged = merged_state(state)
        if merged != state:
            rungs += [("coarse_merged", "D%s/Z%s/%s" % (dc, zc, merged)),
                      ("zone_merged", "*/Z%s/%s" % (zc, merged))]
    return rungs + _neutral_rungs(dbin, zone)


# Amendment F2 (made after the acceptance runs of the F1 chart, before any kernel
# release; the artifact's amendments block discloses it with the readings that
# prompted it and the alternative considered): the last two minutes' states
# (q4|le120|<need>) widen their field zone to the field-goal-range boundary,
# within that state, before their time bucket is merged with the earlier ones;
# every merged state then widens its zone the same way before it gives way to
# the neutral state. The two wide zones split the field at the opponent's 40
# (the line inside which nearly every fourth-down field goal is kicked; the
# counts are in the amendment), so a field-goal decision still follows the
# kick distance. Amendment F2 also applies the pre-build specification's R14
# to the chart: a trailing overtime offense's punt share moves to go (MASKS).
WIDE_ZONES = ((1, 39), (40, 99))
LADDER_F2 = ("full", "coarse", "zone_state", "wide_state", "coarse_merged", "zone_merged", "wide_merged", "neutral",
             "distance_coarse", "zone_only")
assert LATE_BUCKETS["le120"] == [0, 120], "the last two minutes' late time bucket"
LAST_TWO_MINUTES = "q4|le120|"
MASKS = ({"state": "ot|trail", "from": "punt", "to": "go",
          "rule": "pre-build specification R14: a trailing overtime offense's punt is masked, its weight moved "
                  "to going for it (0 punts in the real trailing overtime decisions)"},)


def _wide_label(zone):
    return label(find(WIDE_ZONES, zone[0]))


def _ladder_wide(dbin, zone, state, wide_states):
    rungs = [("full", "%s/%s/%s" % (label(dbin), label(zone), state))]
    if state != "neutral":
        dc, zc, zw = label(find(COARSE_DIST, dbin[0])), label(find(COARSE_ZONES, zone[0])), _wide_label(zone)
        rungs += [("coarse", "D%s/Z%s/%s" % (dc, zc, state)), ("zone_state", "*/Z%s/%s" % (zc, state))]
        if wide_states(state):
            rungs.append(("wide_state", "*/W%s/%s" % (zw, state)))
        merged = merged_state(state)
        if merged != state:
            rungs += [("coarse_merged", "D%s/Z%s/%s" % (dc, zc, merged)),
                      ("zone_merged", "*/Z%s/%s" % (zc, merged)), ("wide_merged", "*/W%s/%s" % (zw, merged))]
    return rungs + _neutral_rungs(dbin, zone)


def ladder(dbin, zone, state):
    """(rung, cell label) for one key under amendment F2, most specific first."""
    return _ladder_wide(dbin, zone, state, lambda s: s.startswith(LAST_TWO_MINUTES))


def ladder_wide_all(dbin, zone, state):
    """The alternative amendment F2 considered, for the record: every late,
    first-half and overtime state widens its zone before its time bucket (or
    margin) is merged."""
    return _ladder_wide(dbin, zone, state, lambda s: True)


def masked(key, counts):
    """A key's chart counts with amendment F2's masks applied (R14)."""
    counts = list(counts)
    for m in MASKS:
        if key.endswith("|" + m["state"]):
            i, j = ACTIONS.index(m["from"]), ACTIONS.index(m["to"])
            counts[j] += counts[i]
            counts[i] = 0
    return counts


def cell_members(cell):
    """The predicate of a cell label on (dbin, zone, state) of a decision row."""
    d, z, s = cell.split("/", 2)

    def dist_ok(dbin):
        if d == "*":
            return True
        if d.startswith("D"):
            return find(COARSE_DIST, dbin[0]) == _parse(d[1:])
        return dbin == _parse(d)

    def zone_ok(zone):
        if z.startswith("Z"):
            return find(COARSE_ZONES, zone[0]) == _parse(z[1:])
        if z.startswith("W"):
            return find(WIDE_ZONES, zone[0]) == _parse(z[1:])
        return zone == _parse(z)

    def state_ok(state):
        if s == state:
            return True
        if s.startswith("q4|le%d|" % Q4_SECONDS) and state.startswith("q4|"):
            return state.split("|")[2] == s.split("|")[2]
        if s == "ot|any":
            return state.startswith("ot|")
        return False
    return lambda dbin, zone, state: dist_ok(dbin) and zone_ok(zone) and state_ok(state)


def _parse(text):
    parts = [int(p) for p in text.split("-")]
    return (parts[0], parts[-1])


def reachable():
    """Every (dbin, zone, state) key a kernel state can produce: a distance never exceeds the
    line (goal to go), so a bin starting beyond a zone's far edge is unreachable; overtime
    states in every zone."""
    for dbin in DIST_BINS:
        for zone in ZONES:
            if dbin[0] > zone[1]:
                continue
            for state in all_states():
                yield dbin, zone, state


# ============================================================================ pass 1 (nflverse, the committed loader)

def _flag_text(value):
    return str(value).strip() in ("1", "1.0")


def pass1_rows(season, dest):
    """Decision rows of one season from nflverse through the committed loader projection
    (league_base_2010_2014.load_rows, REG only, every row re-gated)."""
    rows = lb.load_rows(season, "nflverse", dest)
    games = set()
    out, skipped = [], collections.Counter()
    for r in rows:
        games.add(r["game_id"])
        if r.get("down") != 4:
            continue
        play = r["play_type"]
        if play not in SPEC["data"]["decision_play_types"]:
            if play in SPEC["data"]["excluded_play_types"]:
                skipped[play] += 1
            elif play:
                skipped["other:" + play] += 1
            continue
        qtr = int(r["qtr"])
        if qtr >= 5 and season < OT_FROM:
            skipped["overtime before %d" % OT_FROM] += 1
            continue
        if r["yardline_100"] is None or r["ydstogo"] is None or r.get("score_differential") is None:
            skipped["missing state"] += 1
            continue
        distance, line = int(r["ydstogo"]), int(r["yardline_100"])
        diff = int(r["score_differential"])
        game_left = r.get("game_seconds_remaining")
        half_left = r.get("half_seconds_remaining")
        state = state_label(overtime=qtr >= 5, q4_seconds_left=int(game_left) if qtr == 4 else None,
                            h1_seconds_left=int(half_left) if qtr <= 2 else None, diff=diff)
        decision = {"punt": "punt", "field_goal": "field_goal"}.get(play, "go")
        row = {"season": season, "decision": decision, "distance": distance, "line": line,
               "goal_to_go": distance == line, "state": state}
        if decision == "field_goal" and r.get("kick_distance") is not None:
            row["fg_offset"] = int(r["kick_distance"]) - line
        if decision == "go":
            row["penalty"] = bool(r.get("penalty"))
            interception = _flag_text(r.get("interception"))
            lost = _flag_text(r.get("fumble_lost")) and not interception
            yards = 0 if interception else int(r.get("yards_gained") or 0)
            touchdown = _flag_text(r.get("touchdown")) and r.get("td_team") == r.get("posteam")
            if interception:
                kind = "interception"
            elif play == "run":
                kind = "fumble_run" if lost else "run"
            elif r.get("sack") == 1:
                kind = "fumble_sack" if lost else "sack"
            elif r.get("complete_pass") == 1:
                kind = "fumble_catch" if lost else "complete"
            else:
                kind = "fumble_sack" if lost else "incomplete"
            row.update(kind=kind, yards=yards,
                       converted=not interception and not lost and (touchdown or yards >= distance))
        out.append(row)
    return out, len(games), skipped


# ============================================================================ pass 2 (nflscrapR, separate code)

def _int(text):
    text = (text or "").strip()
    if text in ("", "NA"):
        return None
    return int(float(text))


def pass2_rows(season, dest):
    """The same rows recounted from nflscrapR reg_pbp with separately written parsing: the
    raw rows of the gated file, the source's own goal_to_go column, its own flags."""
    name = lb.pbp_name(season, "nflscrapr")
    games = set()
    out, skipped = [], collections.Counter()
    for r in sources.rows(name, dest):
        games.add(r.get("game_id"))
        if _int(r.get("down")) != 4:
            continue
        play = (r.get("play_type") or "").strip()
        if play not in ("punt", "field_goal", "run", "pass"):
            skipped[play or "NA"] += 1
            continue
        quarter = _int(r.get("qtr"))
        overtime = quarter >= 5
        if overtime and season < OT_FROM:
            skipped["overtime before %d" % OT_FROM] += 1
            continue
        togo, yl, sd = _int(r.get("ydstogo")), _int(r.get("yardline_100")), _int(r.get("score_differential"))
        if None in (togo, yl, sd):
            skipped["missing state"] += 1
            continue
        game_left, half_left = _int(r.get("game_seconds_remaining")), _int(r.get("half_seconds_remaining"))
        if overtime:
            state = "ot|" + ("trail" if sd < 0 else "tied" if sd == 0 else "lead")
        elif quarter == 4 and game_left is not None and game_left <= Q4_SECONDS:
            bucket = next(b for b, (lo, hi) in LATE_BUCKETS.items() if lo <= game_left <= hi)
            need = next(n for n, (lo, hi) in NEEDS.items() if lo <= sd <= hi)
            state = "q4|%s|%s" % (bucket, need)
        elif quarter in (1, 2) and half_left is not None and half_left <= H1_SECONDS:
            state = "h1_le%d" % H1_SECONDS
        else:
            state = "neutral"
        gtg = (r.get("goal_to_go") or "").strip() == "1"
        decision = "go" if play in ("run", "pass") else play
        row = {"season": season, "decision": decision, "distance": togo, "line": yl, "goal_to_go": gtg,
               "goal_to_go_equal": gtg == (togo == yl), "state": state}
        if decision == "field_goal":
            kd = _int(r.get("kick_distance"))
            if kd is not None:
                row["fg_offset"] = kd - yl
        if decision == "go":
            pick = (r.get("interception") or "").strip() == "1"
            fumbled = (r.get("fumble_lost") or "").strip() == "1" and not pick
            gained = 0 if pick else (_int(r.get("yards_gained")) or 0)
            scored = (r.get("touchdown") or "").strip() == "1" and (r.get("td_team") or "") == (r.get("posteam") or "")
            if pick:
                kind = "interception"
            elif play == "run":
                kind = "fumble_run" if fumbled else "run"
            elif (r.get("sack") or "").strip() == "1":
                kind = "fumble_sack" if fumbled else "sack"
            elif (r.get("complete_pass") or "").strip() == "1":
                kind = "fumble_catch" if fumbled else "complete"
            else:
                kind = "fumble_sack" if fumbled else "incomplete"
            row.update(penalty=(r.get("penalty") or "").strip() == "1", kind=kind, yards=gained,
                       converted=not pick and not fumbled and (scored or gained >= togo))
        out.append(row)
    return out, len(games), skipped


# ============================================================================ analysis

def triple(rows):
    c = collections.Counter(r["decision"] for r in rows)
    return [c["go"], c["field_goal"], c["punt"]]


def analyse(by_season):
    rows = [r for s in sorted(by_season) for r in by_season[s]["rows"]]
    team_games = {lb.TAG[s]: 2 * by_season[s]["games"] for s in sorted(by_season)}
    keyed = collections.defaultdict(list)
    for r in rows:
        keyed[(find(DIST_BINS, r["distance"]), find(ZONES, r["line"]), r["state"])].append(r)
    cells = {}

    def assign(ladder_fn):
        """(cell map, rung counts) of every reachable key under one ladder; cell counts are
        computed once per label, by membership."""
        cell_map, rungs = {}, collections.Counter()
        for dbin, zone, state in reachable():
            chosen = None
            for rung, cell in ladder_fn(dbin, zone, state):
                if cell not in cells:
                    member = cell_members(cell)
                    cells[cell] = triple([r for (d, z, s), rs in keyed.items() if member(d, z, s) for r in rs])
                if sum(cells[cell]) >= MIN_CELL:
                    chosen = (rung, cell)
                    break
            if chosen is None:
                raise AssertionError("no rung serves %s|%s|%s" % (label(dbin), label(zone), state))
            cell_map["%s|%s|%s" % (label(dbin), label(zone), state)] = chosen[1]
            rungs[chosen[0]] += 1
        return cell_map, rungs
    cell_map, rungs = assign(ladder)
    frozen_map, frozen_rungs = assign(ladder_frozen)
    f1_map, f1_rungs = assign(ladder_f1)
    wide_map, wide_rungs = assign(ladder_wide_all)
    chart = {cell: cells[cell] for cell in sorted(set(cell_map.values()))}

    def reproduction(mapping):
        """Each state group's real decisions against the sum, over its own rows, of their
        adopted cells' probabilities (amendment F2's masks applied): the chart read back on
        the rows it was counted from. Values rounded to 0.1 of a decision."""
        out = {}
        for r in rows:
            key = key_of(r["distance"], r["line"], r["state"])
            counts = masked(key, cells[mapping[key]])
            n = sum(counts)
            parts = r["state"].split("|")
            group = "|".join(parts[:2]) if parts[0] == "q4" else parts[0]
            for name in (group, "all"):
                e = out.setdefault(name, [0, 0.0, 0, 0.0, 0, 0.0])
                for i, action in enumerate(ACTIONS):
                    e[2 * i] += r["decision"] == action
                    e[2 * i + 1] += counts[i] / n
        return {k: [v if i % 2 == 0 else round(v, 1) for i, v in enumerate(e)] for k, e in sorted(out.items())}
    far = [r for r in rows if r["line"] >= WIDE_ZONES[1][0]]
    near = [r for r in rows if r["line"] <= WIDE_ZONES[0][1]]
    wide_basis = {"field_goals_at_40_99": sum(r["decision"] == "field_goal" for r in far),
                  "decisions_at_40_99": len(far),
                  "field_goals_at_1_39": sum(r["decision"] == "field_goal" for r in near),
                  "decisions_at_1_39": len(near)}
    go_rows = [r for r in rows if r["decision"] == "go"]
    conv_rows = [r for r in go_rows if not r["penalty"]]
    pairs = {}
    for dbin in DIST_BINS:
        for gtg in (True, False):
            sel = [r for r in conv_rows if find(DIST_BINS, r["distance"]) == dbin and r["goal_to_go"] == gtg]
            pairs["%s|%s" % (label(dbin), "goal" if gtg else "field")] = [sum(r["converted"] for r in sel), len(sel)]
        sel = [r for r in conv_rows if find(DIST_BINS, r["distance"]) == dbin]
        pairs["%s|any" % label(dbin)] = [sum(r["converted"] for r in sel), len(sel)]
    conversion_map = {}
    for dbin in DIST_BINS:
        for split in ("goal", "field"):
            key = "%s|%s" % (label(dbin), split)
            conversion_map[key] = key if pairs[key][1] >= MIN_CELL else "%s|any" % label(dbin)
    records = {label(dbin): sorted([r["distance"], int(r["goal_to_go"]), r["kind"], r["yards"], int(r["converted"])]
                                   for r in conv_rows if find(DIST_BINS, r["distance"]) == dbin)
               for dbin in DIST_BINS}
    offsets = collections.Counter(r["fg_offset"] for r in rows if r["decision"] == "field_goal" and "fg_offset" in r)
    modal = max(sorted(offsets), key=lambda k: offsets[k]) if offsets else None
    per_season = {}
    for s in sorted(by_season):
        rs = by_season[s]["rows"]
        go = [r for r in rs if r["decision"] == "go" and not r["penalty"]]
        per_season[lb.TAG[s]] = {"decisions": triple(rs), "conversion": [sum(r["converted"] for r in go), len(go)],
                                 "team_games": 2 * by_season[s]["games"]}
    totals = triple(rows)
    n_team_games = sum(team_games.values())
    centres = {
        "go_share": [totals[0], sum(totals)],
        "field_goal_share": [totals[1], sum(totals)],
        "punt_share": [totals[2], sum(totals)],
        "attempts_per_team_game": [totals[0], n_team_games],
        "decisions_per_team_game": [sum(totals), n_team_games],
        "conversion_rate": [sum(r["converted"] for r in conv_rows), len(conv_rows)],
    }
    drift = {
        "go_share": lb.share_drift([v["decisions"][0:1] + [sum(v["decisions"])] for v in per_season.values()]),
        "conversion_rate": lb.share_drift([v["conversion"] for v in per_season.values()]),
        "attempts_per_team_game": lb.rate_drift([[v["decisions"][0], v["team_games"]] for v in per_season.values()]),
    }
    return {
        "rows": len(rows), "team_games": team_games, "chart": chart, "cell_map": cell_map, "rungs": dict(rungs),
        "frozen_ladder": {"rungs": dict(frozen_rungs),
                          "keys_moved": sum(1 for k in f1_map if frozen_map[k] != f1_map[k]),
                          "example": {"key": EXAMPLE_KEY, "frozen_cell": frozen_map[EXAMPLE_KEY],
                                      "frozen_counts": cells[frozen_map[EXAMPLE_KEY]],
                                      "adopted_cell": f1_map[EXAMPLE_KEY],
                                      "adopted_counts": cells[f1_map[EXAMPLE_KEY]],
                                      "state_counts": triple([r for r in rows if r["state"] == EXAMPLE_STATE])}},
        "f1_ladder": {"rungs": dict(f1_rungs), "keys_moved": sum(1 for k in cell_map if f1_map[k] != cell_map[k]),
                      "example": {"key": F2_EXAMPLE_KEY, "f1_cell": f1_map[F2_EXAMPLE_KEY],
                                  "f1_counts": cells[f1_map[F2_EXAMPLE_KEY]],
                                  "adopted_cell": cell_map[F2_EXAMPLE_KEY],
                                  "adopted_counts": cells[cell_map[F2_EXAMPLE_KEY]],
                                  "state_counts": triple([r for r in rows if r["state"] == F2_EXAMPLE_STATE])}},
        "wide_all_ladder": {"rungs": dict(wide_rungs),
                            "keys_moved": sum(1 for k in cell_map if wide_map[k] != cell_map[k])},
        "reproduction": {"frozen": reproduction(frozen_map), "F1": reproduction(f1_map),
                         "wide_all": reproduction(wide_map), "F2": reproduction(cell_map)},
        "wide_basis": wide_basis,
        "conversion_pairs": pairs, "conversion_map": conversion_map, "records": records,
        "fg_offsets": {str(k): offsets[k] for k in sorted(offsets)}, "fg_offset_modal": modal,
        "per_season": per_season, "centres": centres, "drift": drift,
        "penalty_go_rows_excluded": len(go_rows) - len(conv_rows),
        "state_totals": {state: triple([r for r in rows if r["state"] == state]) for state in all_states()},
        "goal_to_go_equal": all(r.get("goal_to_go_equal", True) for r in rows),
        "skipped": {},
    }


def second_pass_block(a, b):
    """Pass 2 against pass 1 by the specification's agreement rule (section 11)."""
    tol = SPEC["agreement"]
    comparison, disagreements = [], []

    def pooled(name, x, y):
        ok = abs(x - y) <= tol["pooled_relative"] * max(x, 1)
        comparison.append({"metric": name, "nflverse": x, "nflscrapr": y, "within_1pct": ok})
        if not ok:
            disagreements.append(name)
    for action in ACTIONS:
        key = "%s_share" % action
        pooled("%s decisions" % action, a["centres"][key][0], b["centres"][key][0])
    pooled("decision rows", a["centres"]["go_share"][1], b["centres"]["go_share"][1])
    pooled("conversion attempts", a["centres"]["conversion_rate"][1], b["centres"]["conversion_rate"][1])
    pooled("conversions", a["centres"]["conversion_rate"][0], b["centres"]["conversion_rate"][0])
    cells = []
    for cell, counts in sorted(a["chart"].items()):
        n = sum(counts)
        other = b["cells_all"].get(cell)
        if other is None or not sum(other):
            cells.append({"cell": cell, "pass1": counts, "pass2": other, "within_2se": False})
            disagreements.append("cell " + cell)
            continue
        m = sum(other)
        ok = True
        for i in range(3):
            p, q = counts[i] / n, other[i] / m
            se = math.sqrt(max(p * (1 - p), 1e-9) / n + max(q * (1 - q), 1e-9) / m)
            if abs(p - q) > tol["cell_share_se"] * se:
                ok = False
        cells.append({"cell": cell, "pass1": counts, "pass2": other, "within_2se": ok})
        if not ok:
            disagreements.append("cell " + cell)
    pairs = []
    for key, (k, n) in sorted(a["conversion_pairs"].items()):
        k2, n2 = b["conversion_pairs"][key]
        ok = True
        if n and n2:
            p, q = k / n, k2 / n2
            se = math.sqrt(max(p * (1 - p), 1e-9) / n + max(q * (1 - q), 1e-9) / n2)
            ok = abs(p - q) <= tol["cell_share_se"] * se
        elif n != n2:
            ok = False
        pairs.append({"pair": key, "pass1": [k, n], "pass2": [k2, n2], "within_2se": ok})
        if not ok:
            disagreements.append("conversion " + key)
    return {"source": "nflscrapR reg_pbp 2010-2014 (2014 cut), parsed by separately written code (pass2_rows)",
            "independence": "both files derive from the NFL GSIS feed; the second pass reads the raw rows, the "
                            "source's own goal_to_go column and its own flags",
            "comparison": comparison, "cells": cells, "conversion_pairs": pairs,
            "fg_offset_modal": {"nflverse": a["fg_offset_modal"], "nflscrapr": b["fg_offset_modal"]},
            "goal_to_go_column_equals_distance_at_line": b["goal_to_go_equal"],
            "disagreements": disagreements, "agree": not disagreements}


def _f1_disclosure(a):
    frozen = a["frozen_ladder"]
    ex = frozen["example"]
    late = sum(v for k, v in frozen["rungs"].items() if k in ("full", "time_merged", "zone_coarse"))
    return ("the frozen ladder served %d of %d reachable keys from the neutral state and kept a late, first-half "
            "or overtime state for only %d; for %s (fourth and 5-7 at the opponent's 40-49, trailing by 4-8 in the "
            "last 2:00) it read the neutral cell %s (go/field goal/punt %s) where the real clubs of that state "
            "decided %s; amendment F1 reads %s (%s). The amendment changes the rung order on structural grounds "
            "(the game state before the field geometry for late decisions; the zone always kept so a field-goal "
            "decision follows the kick distance); MIN_CELL, the bins, the states and the counts are unchanged, "
            "and no target rate was used"
            % (frozen["rungs"].get("neutral", 0), sum(a["rungs"].values()), late, ex["key"], ex["frozen_cell"],
               "/".join(map(str, ex["frozen_counts"])), "/".join(map(str, ex["state_counts"])), ex["adopted_cell"],
               "/".join(map(str, ex["adopted_counts"]))))


def _f2_disclosure(a):
    f1, rep, wb = a["f1_ladder"], a["reproduction"], a["wide_basis"]
    ex = f1["example"]

    def go(name, group):
        e = rep[name][group]
        return "%s %s against %d real" % (name, e[1], e[0])
    return ("the F1 chart read back on its own rows decided fewer gos than the real clubs: in the last two minutes "
            "of the fourth quarter %s, overall %s; for %s (fourth and 1 in the club's own territory, trailing by 4-8 "
            "in the last 2:00) F1 read %s (go/field goal/punt %s) where the real clubs of that state decided %s, "
            "because merging the last two minutes with the earlier time buckets brought in clubs that still had "
            "time to punt; amendment F2 reads %s (%s). Wide zones split the field at the opponent's 40: %d of the %d "
            "real fourth-down decisions at the opponent's 40 or beyond were field goals, against %d of %d inside it. "
            "The alternative of widening every late state before merging (for the record) reads %s and %s; F2 was "
            "chosen over it by this read-back on the 2010-2014 rows (its earlier time buckets read closer under F1's "
            "merge), not by an acceptance reading. R14's mask moves a trailing overtime offense's punt share to go. "
            "MIN_CELL, the bins, the states and the counts are unchanged"
            % (go("F1", "q4|le120"), go("F1", "all"), ex["key"], ex["f1_cell"], "/".join(map(str, ex["f1_counts"])),
               "/".join(map(str, ex["state_counts"])), ex["adopted_cell"], "/".join(map(str, ex["adopted_counts"])),
               wb["field_goals_at_40_99"], wb["decisions_at_40_99"], wb["field_goals_at_1_39"],
               wb["decisions_at_1_39"], go("wide_all", "q4|le120"), go("wide_all", "all")))


def build(dest, log=print):
    passes = {}
    skipped = {}
    for source, reader in (("nflverse", pass1_rows), ("nflscrapr", pass2_rows)):
        by_season = {}
        skipped[source] = {}
        for s in SEASONS:
            log("fourth downs %s %s" % (source, lb.TAG[s]))
            rows, games, skip = reader(s, dest)
            by_season[s] = {"rows": rows, "games": games}
            skipped[source][lb.TAG[s]] = dict(sorted(skip.items()))
        passes[source] = by_season
    a = analyse(passes["nflverse"])
    b = analyse(passes["nflscrapr"])
    rows2 = [r for season in sorted(passes["nflscrapr"]) for r in passes["nflscrapr"][season]["rows"]]
    b["cells_all"] = {}
    for cell in a["chart"]:
        member = cell_members(cell)
        b["cells_all"][cell] = triple([r for r in rows2 if member(find(DIST_BINS, r["distance"]),
                                                                  find(ZONES, r["line"]), r["state"])])
    errors = []
    if a["fg_offset_modal"] not in SPEC["field_goal_offset"]["allowed"]:
        errors.append("the modal field-goal offset %s lies outside %s" % (a["fg_offset_modal"],
                                                                          SPEC["field_goal_offset"]["allowed"]))
    for dbin in DIST_BINS:
        lab = label(dbin)
        if not any(r[4] for r in a["records"][lab]) or not any(not r[4] for r in a["records"][lab]):
            errors.append("distance bin %s lacks converted or failed attempt records" % lab)
    if a["team_games"] != {lb.TAG[s]: v for s, v in zip(SEASONS, (512, 512, 512, 512, 122))}:
        errors.append("team-games per season %s differ from the data window" % a["team_games"])
    manifest = sources.load_manifest()
    artifact = {
        "schema": SCHEMA,
        "seasons": [lb.TAG[s] for s in SEASONS],
        "season_type": "regular",
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; no club, game, player or date field. 2013 and 2014 Weeks 1-4 "
                                 "are an anonymous post-divergence league population (pooled only)."),
        "builder": "scripts/research/build_2010_2014_fourth_down_decisions.py",
        "specification_sha256": fourth_down_specification.digest(),
        "pre_build_specification_sha256": pre_build_specification.digest(),
        "sources": {name: {"sha256": manifest["assets"][name]["sha256"]}
                    for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"))},
        "rules": {
            "actions": list(ACTIONS),
            "distance_bins": [list(b) for b in DIST_BINS], "zones": [list(z) for z in ZONES],
            "coarse_zones": [list(z) for z in COARSE_ZONES], "coarse_distances": [list(d) for d in COARSE_DIST],
            "states": {"h1_seconds": H1_SECONDS, "q4_seconds": Q4_SECONDS, "ot_margins": OT_MARGINS,
                       "late_time_buckets": LATE_BUCKETS, "needs": NEEDS},
            "min_cell": MIN_CELL, "collapse_ladder": list(LADDER_F2), "wide_zones": [list(z) for z in WIDE_ZONES],
            "masks": list(MASKS), "frozen_collapse_ladder": SPEC["collapse_ladder"],
            "decision_rows": "regular-season snaps at down 4 with play_type punt, field_goal, run or pass; "
                             "no_play rows, kneels and spikes excluded; overtime from %d" % OT_FROM,
            "conversion_rows": "go rows with no penalty flag; converted = an offensive touchdown or yards at least "
                               "the distance, with no interception or lost fumble",
            "goal_to_go": "the distance equals the line (pass 2 confirms the source's goal_to_go column)",
            "call_families": SPEC["call_families"],
        },
        "amendments": [
            {"id": "F1",
             "what": "the collapse ladder: a late (fourth quarter, 600 s or less), first-half (120 s or less) or "
                     "overtime state is kept, with coarse distance and zone, then any distance and coarse zone, then "
                     "with its time buckets (overtime margins) merged, before it gives way to the neutral state; a "
                     "field zone, at least its coarse zone, is kept on every rung",
             "rungs": list(LADDER_F1),
             "when": "after the frozen ladder (specification section 3) was run and printed, before any kernel use",
             "disclosure": _f1_disclosure(a),
             "frozen_ladder_for_the_record": a["frozen_ladder"]},
            {"id": "F2",
             "what": "the collapse ladder and one mask: a last-two-minutes state (q4|le120|<need>) widens its field "
                     "zone to the field-goal-range boundary (wide zones 1-39 and 40-99) within that state before its "
                     "time bucket is merged with the earlier ones, and every merged state widens its zone the same way "
                     "before it gives way to the neutral state; the pre-build specification's R14 applies to the "
                     "chart (a trailing overtime offense's punt share moves to go)",
             "rungs": list(LADDER_F2), "wide_zones": [list(z) for z in WIDE_ZONES], "masks": list(MASKS),
             "when": "after the acceptance runs of the F1 chart (October 16, 2026: three trailing-overtime punts "
                     "against R14's zero-tolerance row, and the late trailing-punt rows; runtime/README.md, batch "
                     "B9F), before any kernel release",
             "disclosure": _f2_disclosure(a),
             "f1_ladder_for_the_record": a["f1_ladder"], "wide_all_ladder_for_the_record": a["wide_all_ladder"],
             "reproduction": a["reproduction"], "wide_basis": a["wide_basis"]},
        ],
        "team_games": a["team_games"],
        "chart": {"fields": list(ACTIONS), "cells": a["chart"], "cell_map": a["cell_map"], "rungs": a["rungs"]},
        "conversion": {"pairs": a["conversion_pairs"], "map": a["conversion_map"],
                       "penalty_go_rows_excluded": a["penalty_go_rows_excluded"]},
        "records": {"fields": list(RECORD_FIELDS), "by_distance_bin": a["records"]},
        "field_goal_offset": {"counts": a["fg_offsets"], "modal": a["fg_offset_modal"]},
        "centres": a["centres"],
        "state_totals": a["state_totals"],
        "per_season": a["per_season"],
        "drift": a["drift"],
        "skipped_rows": skipped,
        "second_pass": second_pass_block(a, b),
    }
    return artifact, errors


# ============================================================================ the library record

BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def _rate(pair):
    return pair[0] / pair[1] if pair[1] else float("nan")


def tables(art):
    lines = ["Generated by `scripts/research/build_2010_2014_fourth_down_decisions.py` from the artifact; do not edit.",
             ""]
    c = art["centres"]
    lines.append("| Centre | Count | Of | Value |")
    lines.append("|---|---|---|---|")
    for name in ("go_share", "field_goal_share", "punt_share", "attempts_per_team_game", "decisions_per_team_game",
                 "conversion_rate"):
        k, n = c[name]
        lines.append("| %s | %d | %d | %.4f |" % (name.replace("_", " "), k, n, k / n))
    lines += ["", "| Season | Go | Field goal | Punt | Converted | Attempts (no flag) | Team-games |",
              "|---|---|---|---|---|---|---|"]
    for s, v in art["per_season"].items():
        lines.append("| %s | %d | %d | %d | %d | %d | %d |" % ((s,) + tuple(v["decisions"]) + tuple(v["conversion"])
                                                              + (v["team_games"],)))
    d = art["drift"]
    lines += ["", "Season drift: go share chi-square %.3f on %d df, p %.3f; conversion rate p %.3f; attempts per "
              "team-game (Poisson) p %.3f." % (d["go_share"]["stat"], d["go_share"]["df"], d["go_share"]["p"],
                                              d["conversion_rate"]["p"], d["attempts_per_team_game"]["p"]), ""]
    lines.append("**Conversion pairs** (converted / attempts; `field` is not goal to go; a split under %d attempts "
                 "reads its distance bin's pooled pair):" % art["rules"]["min_cell"])
    lines += ["", "| Distance | Goal to go | Field | Pooled | Adopted for goal / field |", "|---|---|---|---|---|"]
    pairs, cmap = art["conversion"]["pairs"], art["conversion"]["map"]
    for dbin in art["rules"]["distance_bins"]:
        lab = label(tuple(dbin))
        g, f, p = pairs[lab + "|goal"], pairs[lab + "|field"], pairs[lab + "|any"]
        lines.append("| %s | %d/%d | %d/%d | %d/%d (%.3f) | %s / %s |" % (
            lab, g[0], g[1], f[0], f[1], p[0], p[1], _rate(p), cmap[lab + "|goal"], cmap[lab + "|field"]))
    lines += ["", "Go rows with a penalty flag left out of the conversion rows: %d." %
              art["conversion"]["penalty_go_rows_excluded"], ""]
    off = art["field_goal_offset"]
    lines.append("Field-goal snap offset (kick distance less the line, fourth-down kicks): modal %d; counts %s." % (
        off["modal"], ", ".join("%s: %d" % kv for kv in off["counts"].items())))
    lines += ["", "**Chart cells, neutral state** (go / field goal / punt; the adopted cell of each distance and zone):",
              "", "| Distance \\ zone | " + " | ".join(label(tuple(z)) for z in art["rules"]["zones"]) + " |",
              "|---|" + "---|" * len(art["rules"]["zones"])]
    cells, cmap2 = art["chart"]["cells"], art["chart"]["cell_map"]
    for dbin in art["rules"]["distance_bins"]:
        row = []
        for zone in art["rules"]["zones"]:
            key = "%s|%s|neutral" % (label(tuple(dbin)), label(tuple(zone)))
            if key not in cmap2:
                row.append("-")
                continue
            g, f, p = cells[cmap2[key]]
            row.append("%d/%d/%d" % (g, f, p))
        lines.append("| %s | %s |" % (label(tuple(dbin)), " | ".join(row)))
    rungs = art["chart"]["rungs"]
    f1, f2 = art["amendments"][0], art["amendments"][1]
    frozen = f1["frozen_ladder_for_the_record"]
    f1_rec = f2["f1_ladder_for_the_record"]
    lines += ["", "Reachable keys by the rung that served them (amendment F2, adopted): %s; %d distinct cells. Under "
              "amendment F1, for the record: %s (%d keys moved by F2). Under the frozen ladder, for the record: %s "
              "(%d keys moved by F1)." % (
                  ", ".join("%s %d" % (r, rungs.get(r, 0)) for r in art["rules"]["collapse_ladder"]), len(cells),
                  ", ".join("%s %d" % (r, f1_rec["rungs"].get(r, 0)) for r in f1["rungs"]), f1_rec["keys_moved"],
                  ", ".join("%s %d" % (r, frozen["rungs"].get(r, 0)) for r in art["rules"]["frozen_collapse_ladder"]),
                  frozen["keys_moved"]), "",
              "**Amendment F1** (%s): %s. Disclosure: %s." % (f1["when"], f1["what"], f1["disclosure"]), "",
              "**Amendment F2** (%s): %s. Disclosure: %s." % (f2["when"], f2["what"], f2["disclosure"]), "",
              "**The chart read back on its own rows** (each state group's real decisions, then the sum over its "
              "rows of their adopted cells' probabilities, the masks applied; go / field goal / punt):", "",
              "| State group | Real | Frozen ladder | F1 | Every state widened (alternative) | F2 (adopted) |",
              "|---|---|---|---|---|---|"]
    rep = f2["reproduction"]
    for group in rep["F2"]:
        e = rep["F2"][group]
        cols = ["%s / %s / %s" % (rep[name][group][1], rep[name][group][3], rep[name][group][5])
                for name in ("frozen", "F1", "wide_all", "F2")]
        lines.append("| %s | %d / %d / %d | %s |" % (group, e[0], e[2], e[4], " | ".join(cols)))
    lines += ["", "**Decisions by game state** (go / field goal / punt):", "", "| State | Go | Field goal | Punt |",
              "|---|---|---|---|"]
    for state, (g, f, p) in art["state_totals"].items():
        lines.append("| %s | %d | %d | %d |" % (state, g, f, p))
    lines.append("")
    sp = art["second_pass"]
    lines += ["**Second pass (nflscrapR)**", "", "| Metric | nflverse | nflscrapR | Within 1% |", "|---|---|---|---|"]
    for row in sp["comparison"]:
        lines.append("| %s | %d | %d | %s |" % (row["metric"], row["nflverse"], row["nflscrapr"],
                                              "yes" if row["within_1pct"] else "no"))
    cells_ok = sum(1 for c_ in sp["cells"] if c_["within_2se"])
    pairs_ok = sum(1 for p_ in sp["conversion_pairs"] if p_["within_2se"])
    lines += ["", "Adopted cells within 2 SE: %d of %d. Conversion pairs within 2 SE: %d of %d. Modal field-goal "
              "offset: nflverse %s, nflscrapR %s. The source's goal_to_go column equals distance at the line: %s. "
              "Disagreements: %s." % (cells_ok, len(sp["cells"]), pairs_ok, len(sp["conversion_pairs"]),
                                      sp["fg_offset_modal"]["nflverse"], sp["fg_offset_modal"]["nflscrapr"],
                                      sp["goal_to_go_column_equals_distance_at_line"],
                                      ", ".join(sp["disagreements"]) or "none")]
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
    spec_errors = fourth_down_specification.check()
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
