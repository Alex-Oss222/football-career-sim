#!/usr/bin/env python3
"""Build the kernel 2014.6 batch B10 ball-security artifact (data only).

  python scripts/research/build_2010_2014_ball_security.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_ball_security.json and the generated tables of
library/2010_2014_ball_security_calibration.md (between its generated markers). Sources come
only through scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR. The rules are the pre-build specification's (section 4, Ball security
and penalties; section 5, the B10 band rows); its sha256 is in the header.

What it holds, every value counted here:

- the band centres of the B10 rows (pre-build specification section 5): fumbles and lost
  fumbles per team-game in the modelled scope (every nflverse fumble less the defense's own
  fumbles after a turnover, which the engine does not model), the offense-kept share of
  scrimmage fumbles, the sack share of lost scrimmage fumbles, the kicking-team recoveries per
  team-game in the scope the engine draws (punts; kickoffs from the 35 from 2011, onside kicks
  and touchdowns left out), the muffer role share, and the informational rows (the forced share
  of lost non-aborted scrimmage fumbles, the forcer also recovering, muffs per punt and the
  receiving club's keep share of punt muffs), each with per-season counts and a drift test;
- the sourced shares the engine's credit draws read (credit only, never player evidence): an
  aborted snap's fumbler (quarterback or centre), a kick-return fumble's forced share and
  forcer-also-recovers share, the recoverer of a kept kick fumble or muff being the fumbler,
  and the scrimmage fallbacks (forced share, forcer and recoverer groups by kind) for a lost
  fumble the replayed drive does not describe (a fourth-down attempt's fumble, batch B9F);
- the pool-scope counts read from the committed 2010-2014 field-position artifact (pinned by
  sha256): its retained kick records by season and the muffer roles of its kick records;
- the second pass: the same rows recounted from nflscrapR by separately written code and
  compared against pass 1 (pooled rates within 2 standard errors).

Team, game and player identifiers are read only to count games, team-games and position
groups; nothing club-, game-, player- or date-keyed is written. Stdlib only; deterministic.
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
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2012_field_position_model as fp  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "library" / "data"
OUT = DATA / "2010_2014w4_ball_security.json"
RECORD = ROOT / "library" / "2010_2014_ball_security_calibration.md"
FIELD_POSITION = DATA / "2010_2014w4_nfl_field_position_model.json"
SCHEMA = "2010-2014w4-nfl-ball-security-v1"
SEASONS = lb.SEASONS
KICKOFF_FROM = 2011          # kickoffs from the 35 (the 2011 rule change; pre-build spec 1B.1)
SCRIMMAGE_KINDS = ("run", "reception", "sack", "aborted")
DEFENSE_GROUPS = ("DL", "LB", "DB")
OFFENSE_GROUPS = ("QB", "OL", "RB", "WR", "TE")
REVERSED = re.compile(r"REVERSED\.", re.I)
# The pass-2 agreement rule: a pooled rate or share of pass 2 agrees with pass 1 when the two
# differ by at most AGREE_SE standard errors of their difference.
AGREE_SE = 2.0


def counted(desc):
    parts = REVERSED.split(desc or "")
    return parts[-1] if len(parts) > 1 else (desc or "")


def pair(k, n):
    return [int(k), int(n)]


def pooled(by_season):
    return [sum(v[0] for v in by_season.values()), sum(v[1] for v in by_season.values())]


# ============================================================================ pass 1 (nflverse, committed loader)

def _kick_teams(r):
    """(kicking club, receiving club) of a kick row. nflverse gives a kickoff's posteam as the
    receiving club and a punt's posteam as the punting club."""
    if r["play_type"] == "punt":
        return r["posteam"], r["defteam"]
    return r["defteam"], r["posteam"]


def _outcome(r):
    """lost, oob or kept, as the committed annotation reads it (league_base_2010_2014.fumbles_of)."""
    if r.get("fumble_lost") == "1" or fp.flag(r, "fumble_lost"):
        return "lost"
    if r.get("fumble_out_of_bounds") == 1:
        return "oob"
    return "kept"


def classify1(r):
    """(context, kind) of a fumble row (nflverse fumble = 1; a nullified play carries 0).

    context: scrimmage, kickoff, punt (the receiving club's fumble or muff on a kick play),
    defense_after_turnover (the defense's own fumble on a scrimmage play), kicking_club (the
    kicking club's fumble on its own kick play), fg_xp (field goals and tries), other."""
    pt = r["play_type"]
    text = counted(r.get("desc")).upper()
    if pt == "punt" or fp.is_kick_row(r):
        kicking, receiving = _kick_teams(r)
        if lb.same_club(r.get("fumbled_1_team"), kicking):
            return "kicking_club", None
        return ("punt" if pt == "punt" else "kickoff"), ("muff" if "MUFF" in text else "return")
    if pt in ("field_goal", "extra_point"):
        return "fg_xp", None
    if pt in ("run", "pass", "qb_kneel", "qb_spike"):
        if r.get("fumbled_1_team") and not lb.same_club(r["fumbled_1_team"], r["posteam"]):
            return "defense_after_turnover", None
        return "scrimmage", lb.fumble_kind(r)
    return "other", None


def pass1_season(season, dest):
    rows = lb.load_rows(season, "nflverse", dest)
    pos_map = lb.positions(season, dest)
    games = set()
    c = collections.Counter()
    per_team_game = collections.Counter()
    groups = collections.Counter()
    for r in rows:
        games.add(r["game_id"])
        pt = r["play_type"]
        text = counted(r.get("desc")).upper()
        if pt == "punt" and r.get("punt_attempt") == 1:
            c["punts"] += 1
        if pt == "punt" and "MUFF" in text and r.get("fumble") == 1:
            # A punt muff the feed counts as a fumble, by who kept the ball.
            c["punt_muffs"] += 1
            c["punt_muffs_receiving_kept"] += _outcome(r) != "lost"
        if r.get("fumble") != 1:
            continue
        context, kind = classify1(r)
        outcome = _outcome(r)
        forced = r.get("fumble_forced") == 1
        fumbler = r.get("fumbled_1_player_id") or ""
        forcer = r.get("forced_fumble_player_1_player_id") or ""
        recoverer = r.get("fumble_recovery_1_player_id") or ""
        c["all"] += 1
        c["all_lost"] += outcome == "lost"
        c["context:%s" % context] += 1
        c["context:%s|%s" % (context, outcome)] += 1
        if context not in ("defense_after_turnover",):
            per_team_game[(r["game_id"], fp.alias(r.get("fumbled_1_team") or r["posteam"]))] += 1
        if context == "scrimmage":
            c["scrim|%s|%s" % (kind, outcome)] += 1
            c["scrim|%s|forced" % kind] += forced
            if outcome == "lost":
                c["scrim|%s|lost_forced" % kind] += forced
                if forced and forcer:
                    c["scrim|%s|lost_forced_named" % kind] += 1
                    c["scrim|%s|lost_forcer_recovers" % kind] += bool(recoverer) and recoverer == forcer
                if forced:
                    groups["forcer|%s|%s" % (kind, lb.group_of(pos_map, forcer))] += 1
                if recoverer:
                    groups["lost_recoverer|%s|%s" % (kind, lb.group_of(pos_map, recoverer))] += 1
            elif outcome == "kept":
                groups["kept_recoverer|%s|%s" % (kind, "self" if recoverer and recoverer == fumbler
                                                 else lb.group_of(pos_map, recoverer))] += 1
            if kind == "aborted":
                groups["aborted_fumbler|%s" % lb.group_of(pos_map, fumbler)] += 1
        elif context in ("kickoff", "punt"):
            c["kick|%s|%s" % (kind, outcome)] += 1
            c["kick|%s|forced" % kind] += forced
            if outcome == "kept":
                c["kick|%s|kept_self" % kind] += bool(recoverer) and recoverer == fumbler
                c["kick|%s|kept_named" % kind] += bool(recoverer)
            if outcome == "lost" and forced and forcer:
                c["kick|%s|lost_forced_named" % kind] += 1
                c["kick|%s|lost_forcer_recovers" % kind] += bool(recoverer) and recoverer == forcer
            returner = r.get("punt_returner_player_id") if context == "punt" else r.get("kickoff_returner_player_id")
            if kind == "muff" and fumbler:
                c["muff_role|%s" % ("returner" if returner and fumbler == returner else "other")] += 1
    team_games = 2 * len(games)
    counts = [per_team_game.get(key, 0) for key in per_team_game]
    zeros = team_games - len(counts)
    values = counts + [0] * max(0, zeros)
    mean = sum(values) / len(values) if values else 0.0
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1) if len(values) > 1 else 0.0
    return {"games": len(games), "team_games": team_games, "counts": dict(c), "groups": dict(groups),
            "team_game_moments": [len(values), sum(values), sum(v * v for v in values)],
            "dispersion": var / mean if mean else 1.0}


# ============================================================================ pass 2 (nflscrapR, separate code)

def _f(r, key):
    return (r.get(key) or "").strip() == "1"


def _team(r, key):
    return fp.alias((r.get(key) or "").strip())


def classify2(r):
    """The second pass's own reading of a fumble row: kind from the description and the
    source's own play flags (not the committed annotation's helper)."""
    play = (r.get("play_type") or "").strip()
    desc = counted(r.get("desc") or "")
    upper = desc.upper()
    posteam, defteam = _team(r, "posteam"), _team(r, "defteam")
    fumbler_team = _team(r, "fumbled_1_team")
    if play in ("kickoff", "punt"):
        kicking = posteam if play == "punt" else defteam
        if fumbler_team and fumbler_team == kicking:
            return "kicking_club", None
        return play, ("muff" if "MUFF" in upper else "return")
    if play in ("field_goal", "extra_point"):
        return "fg_xp", None
    if play in ("run", "pass", "qb_kneel", "qb_spike"):
        if fumbler_team and fumbler_team != posteam:
            return "defense_after_turnover", None
        if "(ABORTED)" in upper or _f(r, "aborted_play"):
            return "scrimmage", "aborted"
        if _f(r, "sack") or " SACKED " in upper:
            return "scrimmage", "sack"
        if play == "pass":
            return "scrimmage", "reception"
        return "scrimmage", "run"
    return "other", None


def pass2_season(season, dest):
    name = lb.pbp_name(season, "nflscrapr")
    games = set()
    c = collections.Counter()
    for r in sources.rows(name, dest):
        games.add(r.get("game_id"))
        play = (r.get("play_type") or "").strip()
        upper = counted(r.get("desc") or "").upper()
        if play == "punt" and _f(r, "punt_attempt"):
            c["punts"] += 1
        if not _f(r, "fumble"):
            continue
        context, kind = classify2(r)
        fumbler_team = _team(r, "fumbled_1_team")
        recovery_team = _team(r, "fumble_recovery_1_team")
        if _f(r, "fumble_lost"):
            outcome = "lost"
        elif _f(r, "fumble_out_of_bounds") or not recovery_team:
            outcome = "oob"
        else:
            outcome = "kept" if recovery_team == fumbler_team else "lost"
        forced = _f(r, "fumble_forced")
        forcer = (r.get("forced_fumble_player_1_player_id") or "").strip()
        recoverer = (r.get("fumble_recovery_1_player_id") or "").strip()
        c["all"] += 1
        c["all_lost"] += outcome == "lost"
        c["context:%s" % context] += 1
        c["context:%s|%s" % (context, outcome)] += 1
        if play == "punt" and "MUFF" in upper:
            c["punt_muffs"] += 1
            c["punt_muffs_receiving_kept"] += outcome != "lost"
        if context == "scrimmage":
            c["scrim|%s|%s" % (kind, outcome)] += 1
            if outcome == "lost" and kind != "aborted":
                c["scrim|lost_non_aborted"] += 1
                c["scrim|lost_non_aborted_forced"] += forced
            if outcome == "lost" and forced and forcer:
                c["scrim|lost_forced_named"] += 1
                c["scrim|lost_forcer_recovers"] += recoverer == forcer
    return {"games": len(games), "team_games": 2 * len(games), "counts": dict(c)}


# ============================================================================ analysis

def _by(passes, fn):
    return {lb.TAG[s]: fn(passes[s]) for s in SEASONS}


def modelled(c):
    """Fumbles and lost fumbles in the modelled scope: every fumble less the defense's own
    fumbles after a turnover."""
    k = c.get("all", 0) - c.get("context:defense_after_turnover", 0)
    lost = c.get("all_lost", 0) - c.get("context:defense_after_turnover|lost", 0)
    return k, lost


def scrimmage_totals(c):
    total = sum(c.get("scrim|%s|%s" % (k, o), 0) for k in SCRIMMAGE_KINDS for o in ("kept", "oob", "lost"))
    lost = sum(c.get("scrim|%s|lost" % k, 0) for k in SCRIMMAGE_KINDS)
    return total, lost


def retained_counts(fp_art):
    """Retained kick records of the committed field-position artifact by season tag
    (kickoffs, free kicks, punts) and the muffer roles of every kick record."""
    K = {n: i for i, n in enumerate(fp_art["kick_fields"])}
    P = {n: i for i, n in enumerate(fp_art["punt_fields"])}
    tags = [str(t) for t in fp_art["band_centres"]["team_games"]]
    season_of = {int(str(t)[:4]): t for t in tags}
    out = {"kickoff": collections.Counter(), "free_kick": collections.Counter(), "punt": collections.Counter()}
    for kind, records in fp_art["retained_kick_pools"].items():
        index = P if kind == "punt" else K
        for r in records:
            out[kind][season_of[r[index["season"]]]] += 1
    roles = collections.Counter()
    for name, index in (("kickoff_pool", K), ("free_kick_pool", K), ("punt_pool", P)):
        for r in fp_art[name]:
            fumble = r[index["fumble"]]
            if fumble and fumble[0] == "muff":
                roles[fumble[2] or "unrecorded"] += 1
    return {kind: dict(sorted(v.items())) for kind, v in out.items()}, dict(sorted(roles.items()))


def analyse(p1, p2, fp_art):
    team_games = {lb.TAG[s]: p1[s]["team_games"] for s in SEASONS}
    c1 = {lb.TAG[s]: p1[s]["counts"] for s in SEASONS}
    c2 = {lb.TAG[s]: p2[s]["counts"] for s in SEASONS}
    centres = {}

    def rate_entry(fn, seasons=None):
        tags = [lb.TAG[s] for s in (seasons or SEASONS)]
        by = {t: pair(fn(c1[t]), team_games[t]) for t in tags}
        return {"by_season": by, "pooled": pooled(by), "drift": lb.rate_drift(list(by.values()))}

    def share_entry(fn):
        by = {t: pair(*fn(c1[t])) for t in c1}
        return {"by_season": by, "pooled": pooled(by), "drift": lb.share_drift(list(by.values()))}

    moments = [0, 0, 0]
    for s in SEASONS:
        m = p1[s]["team_game_moments"]
        moments = [a + b for a, b in zip(moments, m)]
    n, total, squares = moments
    mean = total / n
    var = (squares - n * mean * mean) / (n - 1)
    centres["fumbles_per_team_game"] = dict(rate_entry(lambda c: modelled(c)[0]),
                                            dispersion=round(var / mean, 6),
                                            excluded={"defense_after_turnover": pooled({t: pair(
                                                c1[t].get("context:defense_after_turnover", 0), team_games[t])
                                                for t in c1})},
                                            not_modelled={name: sum(c1[t].get("context:%s" % name, 0) for t in c1)
                                                          for name in ("kicking_club", "fg_xp", "other")})
    centres["lost_per_team_game"] = rate_entry(lambda c: modelled(c)[1])
    centres["offense_kept_share_of_scrimmage_fumbles"] = share_entry(
        lambda c: (scrimmage_totals(c)[0] - scrimmage_totals(c)[1], scrimmage_totals(c)[0]))
    centres["sack_share_of_lost_scrimmage_fumbles"] = share_entry(
        lambda c: (c.get("scrim|sack|lost", 0), scrimmage_totals(c)[1]))
    centres["forced_share_of_lost_non_aborted_scrimmage_fumbles"] = share_entry(
        lambda c: (sum(c.get("scrim|%s|lost_forced" % k, 0) for k in ("run", "reception", "sack")),
                   sum(c.get("scrim|%s|lost" % k, 0) for k in ("run", "reception", "sack"))))
    centres["forcer_also_recovers"] = share_entry(
        lambda c: (sum(c.get("scrim|%s|lost_forcer_recovers" % k, 0) for k in SCRIMMAGE_KINDS),
                   sum(c.get("scrim|%s|lost_forced_named" % k, 0) for k in SCRIMMAGE_KINDS)))
    centres["muffs_per_punt"] = share_entry(lambda c: (c.get("punt_muffs", 0), c.get("punts", 0)))
    centres["punt_muff_receiving_keep_share"] = share_entry(
        lambda c: (c.get("punt_muffs_receiving_kept", 0), c.get("punt_muffs", 0)))
    retained, roles = retained_counts(fp_art)
    punt_by = {t: pair(retained["punt"].get(t, 0), team_games[t]) for t in team_games}
    kick_tags = [lb.TAG[s] for s in SEASONS if s >= KICKOFF_FROM]
    kick_by = {t: pair(retained["kickoff"].get(t, 0) + retained["free_kick"].get(t, 0), team_games[t])
               for t in kick_tags}
    punt_rate, kick_rate = pooled(punt_by), pooled(kick_by)
    centres["kicking_team_recoveries_per_team_game"] = {
        "punt": {"by_season": punt_by, "pooled": punt_rate, "drift": lb.rate_drift(list(punt_by.values()))},
        "kickoff": {"by_season": kick_by, "pooled": kick_rate, "drift": lb.rate_drift(list(kick_by.values()))},
        "centre": round(punt_rate[0] / punt_rate[1] + kick_rate[0] / kick_rate[1], 6),
        "scope": "the committed field-position artifact's retained kick records (punts, all seasons; kickoffs "
                 "from the 35 from 2011; touchdowns and onside kicks left out), per team-game of their seasons",
        "per_play_cross_check": {t: c1[t].get("context:punt|lost", 0) + c1[t].get("context:kickoff|lost", 0)
                                 for t in c1},
    }
    known = {k: v for k, v in roles.items() if k != "unrecorded"}
    centres["muffer_role_share"] = {
        "returner": pair(known.get("returner", 0), sum(known.values())),
        "unrecorded": roles.get("unrecorded", 0),
        "scope": "the muffed kick records of the committed field-position artifact (kickoffs, free kicks and "
                 "punts, the receiving club's and the kicking club's), muffer recorded",
        "per_play_cross_check": {t: [c1[t].get("muff_role|returner", 0),
                                     c1[t].get("muff_role|returner", 0) + c1[t].get("muff_role|other", 0)]
                                 for t in c1},
    }

    # Credit shares (sourced; credit only).
    g = collections.Counter()
    for s in SEASONS:
        g.update(p1[s]["groups"])
    total = collections.Counter()
    for t in c1:
        total.update(c1[t])
    aborted = {grp: g.get("aborted_fumbler|%s" % grp, 0) for grp in ("QB", "OL")}
    aborted["other"] = sum(v for k, v in g.items() if k.startswith("aborted_fumbler|")) - sum(aborted.values())
    by_kind = {}
    for kind in SCRIMMAGE_KINDS:
        by_kind[kind] = {
            "lost_forced": pair(total.get("scrim|%s|lost_forced" % kind, 0), total.get("scrim|%s|lost" % kind, 0)),
            "forcer_recovers": pair(total.get("scrim|%s|lost_forcer_recovers" % kind, 0),
                                    total.get("scrim|%s|lost_forced_named" % kind, 0)),
            "forcer_group": {grp: g.get("forcer|%s|%s" % (kind, grp), 0) for grp in DEFENSE_GROUPS},
            "lost_recoverer_group": {grp: g.get("lost_recoverer|%s|%s" % (kind, grp), 0) for grp in DEFENSE_GROUPS},
            "kept_recoverer": {grp: g.get("kept_recoverer|%s|%s" % (kind, grp), 0)
                               for grp in ("self",) + OFFENSE_GROUPS},
        }
    kick = {}
    for kind in ("muff", "return"):
        kick[kind] = {
            "forced": pair(total.get("kick|%s|forced" % kind, 0),
                           sum(total.get("kick|%s|%s" % (kind, o), 0) for o in ("kept", "oob", "lost"))),
            "kept_self": pair(total.get("kick|%s|kept_self" % kind, 0), total.get("kick|%s|kept_named" % kind, 0)),
            "lost_forcer_recovers": pair(total.get("kick|%s|lost_forcer_recovers" % kind, 0),
                                         total.get("kick|%s|lost_forced_named" % kind, 0)),
        }
    credit = {"aborted_fumbler": aborted, "scrimmage": by_kind, "kick": kick}

    # Pass 2 comparison.
    comparison, disagreements = [], []

    def compare(metric, k1, n1, k2, n2, rate=False):
        p, q = (k1 / n1 if n1 else 0.0), (k2 / n2 if n2 else 0.0)
        if rate:
            se = math.sqrt(max(k1, 1)) / n1 if n1 else 0.0
            se = math.sqrt(se * se + (math.sqrt(max(k2, 1)) / n2 if n2 else 0.0) ** 2)
        else:
            se = math.sqrt(max(p * (1 - p), 1e-9) / max(n1, 1) + max(q * (1 - q), 1e-9) / max(n2, 1))
        ok = abs(p - q) <= AGREE_SE * se
        comparison.append({"metric": metric, "nflverse": [k1, n1], "nflscrapr": [k2, n2], "within_2se": ok})
        if not ok:
            disagreements.append(metric)

    t1 = collections.Counter()
    t2 = collections.Counter()
    for t in c1:
        t1.update(c1[t])
        t2.update(c2[t])
    tg = sum(team_games.values())
    tg2 = sum(p2[s]["team_games"] for s in SEASONS)
    m1, m2 = modelled(t1), modelled(t2)
    compare("fumbles per team-game (modelled scope)", m1[0], tg, m2[0], tg2, rate=True)
    compare("lost fumbles per team-game (modelled scope)", m1[1], tg, m2[1], tg2, rate=True)
    s1, s2 = scrimmage_totals(t1), scrimmage_totals(t2)
    compare("offense-kept share of scrimmage fumbles", s1[0] - s1[1], s1[0], s2[0] - s2[1], s2[0])
    compare("sack share of lost scrimmage fumbles", t1.get("scrim|sack|lost", 0), s1[1],
            t2.get("scrim|sack|lost", 0), s2[1])
    for kind in SCRIMMAGE_KINDS:
        compare("%s fumbles lost per team-game" % kind, t1.get("scrim|%s|lost" % kind, 0), tg,
                t2.get("scrim|%s|lost" % kind, 0), tg2, rate=True)
    nonab1 = sum(t1.get("scrim|%s|lost" % k, 0) for k in ("run", "reception", "sack"))
    compare("forced share of lost non-aborted scrimmage fumbles",
            sum(t1.get("scrim|%s|lost_forced" % k, 0) for k in ("run", "reception", "sack")), nonab1,
            t2.get("scrim|lost_non_aborted_forced", 0), t2.get("scrim|lost_non_aborted", 0))
    compare("forcer also recovers", sum(t1.get("scrim|%s|lost_forcer_recovers" % k, 0) for k in SCRIMMAGE_KINDS),
            sum(t1.get("scrim|%s|lost_forced_named" % k, 0) for k in SCRIMMAGE_KINDS),
            t2.get("scrim|lost_forcer_recovers", 0), t2.get("scrim|lost_forced_named", 0))
    compare("muffs per punt", t1.get("punt_muffs", 0), t1.get("punts", 0), t2.get("punt_muffs", 0), t2.get("punts", 0))
    compare("punt muff receiving keep share", t1.get("punt_muffs_receiving_kept", 0), t1.get("punt_muffs", 0),
            t2.get("punt_muffs_receiving_kept", 0), t2.get("punt_muffs", 0))
    compare("receiving-club kick fumbles lost per team-game",
            t1.get("context:punt|lost", 0) + t1.get("context:kickoff|lost", 0), tg,
            t2.get("context:punt|lost", 0) + t2.get("context:kickoff|lost", 0), tg2, rate=True)
    per_season = {t: {"team_games": team_games[t], "fumbles_modelled": modelled(c1[t])[0],
                      "lost_modelled": modelled(c1[t])[1], "scrimmage": scrimmage_totals(c1[t])[0],
                      "scrimmage_lost": scrimmage_totals(c1[t])[1],
                      "pass2_fumbles_modelled": modelled(c2[t])[0], "pass2_lost_modelled": modelled(c2[t])[1]}
                  for t in c1}
    second = {"source": "nflscrapR reg_pbp 2010-2014 (2014 cut), parsed by separately written code (pass2_season)",
              "independence": "both files derive from the NFL GSIS feed; the second pass reads the raw rows, "
                              "classifies kinds from the description and the source's own flags, and reads "
                              "recovery from the recovering team",
              "rule": "a pooled rate or share agrees when the passes differ by at most %.0f standard errors of "
                      "their difference" % AGREE_SE,
              "comparison": comparison, "disagreements": disagreements, "agree": not disagreements,
              "explained": EXPLAINED}
    return {"team_games": team_games, "centres": centres, "credit": credit, "per_season": per_season,
            "counts_pass1": {t: dict(sorted(c1[t].items())) for t in c1},
            "counts_pass2": {t: dict(sorted(c2[t].items())) for t in c2},
            "second_pass": second, "retained": retained, "muff_roles": roles}


# Explained, never repaired by hand (a reading of the two sources, not a correction).
EXPLAINED = [
    "nflscrapR's 2014 Weeks 1-4 file leaves eight offense-retained fumbles (aborted snaps and fumbles out of "
    "bounds) without its fumble flag; lost fumbles agree (design pass 2, October 2, 2026).",
    "Pass 2 reads an out-of-bounds fumble from fumble_out_of_bounds or a missing recovery team; nflscrapR does "
    "not separate the kept fumble that went out of bounds, so the kept/out-of-bounds split is single-pass.",
]


def build(dest, log=print):
    p1, p2 = {}, {}
    for s in SEASONS:
        log("ball security nflverse %s" % lb.TAG[s])
        p1[s] = pass1_season(s, dest)
        log("ball security nflscrapr %s" % lb.TAG[s])
        p2[s] = pass2_season(s, dest)
    fp_text = FIELD_POSITION.read_bytes()
    fp_art = json.loads(fp_text)
    a = analyse(p1, p2, fp_art)
    errors = []
    if a["team_games"] != {lb.TAG[s]: v for s, v in zip(SEASONS, (512, 512, 512, 512, 122))}:
        errors.append("team-games per season %s differ from the data window" % a["team_games"])
    if a["retained"]["punt"] and sum(a["retained"]["punt"].values()) != len(fp_art["retained_kick_pools"]["punt"]):
        errors.append("retained punt records miscounted")
    manifest = sources.load_manifest()
    artifact = {
        "schema": SCHEMA,
        "seasons": [lb.TAG[s] for s in SEASONS],
        "season_type": "regular",
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, "
                                 "2014), cut at fetch; no club, game, player or date field. 2013 and 2014 Weeks 1-4 "
                                 "are an anonymous post-divergence league population (pooled only)."),
        "builder": "scripts/research/build_2010_2014_ball_security.py",
        "pre_build_specification_sha256": pre_build_specification.digest(),
        "field_position_sha256": hashlib.sha256(fp_text).hexdigest(),
        "sources": {name: {"sha256": manifest["assets"][name]["sha256"]}
                    for s in SEASONS for name in (lb.pbp_name(s, "nflverse"), lb.pbp_name(s, "nflscrapr"),
                                                  lb.roster_name(s))},
        "rules": {
            "fumble": "a play with the source's fumble flag (0 on a play a penalty nullified)",
            "modelled_scope": "every fumble less the defense's own fumbles after a turnover (not modelled); the "
                              "kicking club's fumbles on its own kick plays and fumbles on field goals and tries "
                              "are counted in the centre and listed as not modelled",
            "contexts": "scrimmage (run, reception, sack, aborted snap: the committed annotation's kind), kickoff "
                        "and punt (the receiving club's muff or return fumble), defense_after_turnover, "
                        "kicking_club, fg_xp, other",
            "outcome": "lost (the fumbling club lost the ball), oob (out of bounds), kept (the fumbling club "
                       "recovered); the offense-kept share counts kept and out of bounds",
            "kicking_team_recoveries": "the retained kick records of the committed field-position artifact "
                                       "(their scope is the engine's draw)",
            "muffs_per_punt": "punt plays whose counted description says MUFF and carry the fumble flag, over "
                              "punt attempts",
            "kickoff_from": KICKOFF_FROM,
        },
        "team_games": a["team_games"],
        "band_centres": a["centres"],
        "credit_shares": a["credit"],
        "per_season": a["per_season"],
        "counts_pass1": a["counts_pass1"],
        "counts_pass2": a["counts_pass2"],
        "second_pass": a["second_pass"],
    }
    if not a["second_pass"]["agree"]:
        log("pass 2 disagrees on: %s" % ", ".join(a["second_pass"]["disagreements"]))
    return artifact, errors


# ============================================================================ the library record

BEGIN, END = "<!-- generated:begin -->", "<!-- generated:end -->"


def _r(p):
    return p[0] / p[1] if p[1] else float("nan")


def tables(art):
    c = art["band_centres"]
    lines = ["Generated by `scripts/research/build_2010_2014_ball_security.py` from the artifact; do not edit.", "",
             "| Centre | Count | Of | Value | Season drift p |", "|---|---|---|---|---|"]
    for name in ("fumbles_per_team_game", "lost_per_team_game", "offense_kept_share_of_scrimmage_fumbles",
                 "sack_share_of_lost_scrimmage_fumbles", "forced_share_of_lost_non_aborted_scrimmage_fumbles",
                 "forcer_also_recovers", "muffs_per_punt", "punt_muff_receiving_keep_share"):
        e = c[name]
        lines.append("| %s | %d | %d | %.4f | %s |" % (name.replace("_", " "), e["pooled"][0], e["pooled"][1],
                                                       _r(e["pooled"]), "%.3f" % e["drift"]["p"] if e["drift"] else "-"))
    k = c["kicking_team_recoveries_per_team_game"]
    lines.append("| kicking-team recoveries per team-game (punts) | %d | %d | %.4f | %.3f |" % (
        k["punt"]["pooled"][0], k["punt"]["pooled"][1], _r(k["punt"]["pooled"]), k["punt"]["drift"]["p"]))
    lines.append("| kicking-team recoveries per team-game (kickoffs from %d) | %d | %d | %.4f | %.3f |" % (
        art["rules"]["kickoff_from"], k["kickoff"]["pooled"][0], k["kickoff"]["pooled"][1],
        _r(k["kickoff"]["pooled"]), k["kickoff"]["drift"]["p"]))
    m = c["muffer_role_share"]
    lines.append("| muffer role share (returner) | %d | %d | %.4f | - |" % (m["returner"][0], m["returner"][1],
                                                                          _r(m["returner"])))
    f = c["fumbles_per_team_game"]
    lines += ["", "Kicking-team recoveries per team-game, the centre (punts plus kickoffs): %.4f. Team-game "
              "dispersion of fumbles (variance over mean): %.3f. Left out of the modelled scope: %d defensive "
              "fumbles after a turnover; counted in the centre but not modelled: %s." % (
                  k["centre"], f["dispersion"], f["excluded"]["defense_after_turnover"][0],
                  ", ".join("%s %d" % kv for kv in f["not_modelled"].items())), "",
              "| Season | Team-games | Fumbles | Lost | Scrimmage | Scrimmage lost | Pass 2 fumbles | Pass 2 lost |",
              "|---|---|---|---|---|---|---|---|"]
    for s, v in art["per_season"].items():
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d |" % (
            s, v["team_games"], v["fumbles_modelled"], v["lost_modelled"], v["scrimmage"], v["scrimmage_lost"],
            v["pass2_fumbles_modelled"], v["pass2_lost_modelled"]))
    cr = art["credit_shares"]
    lines += ["", "**Credit shares** (credit only; never player evidence):", "",
              "Aborted-snap fumbler: quarterback %d, offensive line %d, other %d." % (
                  cr["aborted_fumbler"]["QB"], cr["aborted_fumbler"]["OL"], cr["aborted_fumbler"]["other"]), "",
              "| Scrimmage kind | Lost forced | Forcer recovers | Forcer DL/LB/DB | Lost recoverer DL/LB/DB | "
              "Kept recoverer self/QB/OL/RB/WR/TE |", "|---|---|---|---|---|---|"]
    for kind, v in cr["scrimmage"].items():
        lines.append("| %s | %d/%d | %d/%d | %s | %s | %s |" % (
            kind, v["lost_forced"][0], v["lost_forced"][1], v["forcer_recovers"][0], v["forcer_recovers"][1],
            "/".join(str(v["forcer_group"][g]) for g in DEFENSE_GROUPS),
            "/".join(str(v["lost_recoverer_group"][g]) for g in DEFENSE_GROUPS),
            "/".join(str(v["kept_recoverer"][g]) for g in ("self",) + OFFENSE_GROUPS)))
    lines += ["", "| Kick fumble | Forced | Kept, recovered by the fumbler | Lost, forcer recovers |",
              "|---|---|---|---|"]
    for kind, v in cr["kick"].items():
        lines.append("| %s | %d/%d | %d/%d | %d/%d |" % (kind, v["forced"][0], v["forced"][1], v["kept_self"][0],
                                                         v["kept_self"][1], v["lost_forcer_recovers"][0],
                                                         v["lost_forcer_recovers"][1]))
    sp = art["second_pass"]
    lines += ["", "**Second pass (nflscrapR)**", "", "| Metric | nflverse | nflscrapR | Within 2 SE |",
              "|---|---|---|---|"]
    for row in sp["comparison"]:
        lines.append("| %s | %d/%d | %d/%d | %s |" % (row["metric"], row["nflverse"][0], row["nflverse"][1],
                                                      row["nflscrapr"][0], row["nflscrapr"][1],
                                                      "yes" if row["within_2se"] else "no"))
    lines += ["", "Disagreements: %s." % (", ".join(sp["disagreements"]) or "none")]
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
