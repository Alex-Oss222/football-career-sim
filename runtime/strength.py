"""Kernel 2014.4 candidate, defect register item 1 (E1, second pass): unit
strength from dated public honours, dated pre-divergence production and the
actual available lineup.

Policy: runtime/2014_engine_decisions.md E1. Calibration:
library/2014_strength_calibration.md (section 9) and
library/data/2014_strength_calibration_v2.json (the first pass remains in
library/data/2014_strength_calibration.json). Evidence:
library/data/2010_2012_honours_evidence.json (honours) and
library/data/2010_2012_production_evidence.json (production).

Honours tier rule (unchanged from the first pass, preregistered):

* window: the two most recent completed pre-divergence seasons before the
  season being played (2014 branch: 2011-2012; 2012 study target:
  2010-2011). The real 2013 season is post-divergence and never read.
* Elite: an AP All-Pro 1st team in the window; Plus: AP 2nd team or an
  original Pro Bowl selection. Alternates and replacements have no effect.
* honours value = max over admissible honours of (tier value - 2) x evidence
  weight (Elite 4, Plus 3; weight 1 two-pass, 0.5 single-pass); never below 0.
* an honour is admissible only when its public date is known, before the
  divergence (2013-01-15) and before the date the input is built for.
* specialist honours are special-teams evidence only.

Production tier rule (second pass, preregistered in the production file):

* each qualifying season's metric (QB EPA per dropback; RB/WR/TE EPA per
  opportunity; DL/LB/DB disruption per game; K and P carried for special
  teams) is shrunk to the league mean and cut at fixed percentiles among that
  season's qualifiers in the group: top 10% Elite, next 20% Plus, middle 40%
  Average, next 20% Below-Average, bottom 10% Replacement-Level. Offensive
  linemen carry starts and games only (job evidence) and no tier.
* a player's production tier is the best tier over the same two-season
  window; the season before the window (2010 for the 2014 branch) counts
  only when neither window season qualifies, discounted one tier.
* production value = Elite 2, Plus 1, Average 0, Below-Average -1,
  Replacement-Level -2, times the evidence weight (1 for a season the
  play-by-play recomputation confirmed or corrected, 0.5 unverified).
* a season's statistics are admissible only when its public date (the last
  regular-season game) is before the divergence and before the input date.

Player value (preregistered before the second fit; calibration section 9):

    value = max(honours value, production value) with an admissible honour,
            production value (negative tiers included) without one

with the side rule: a QB honour or QB production tier counts only in the
passer slot (weight 3); a non-QB honour or tier never counts there; an
offensive tier counts only on offense and a defensive tier only on defense.
The age shrink on stale honours was fitted and not adopted (it lowered the
offense leave-one-club-out skill), so no age enters a value.

Composite (per drive, per side, from the drive's ACTUAL lineup: the live
roster after injuries and removals, through participation.emergency_view):

* offense starters: the drive's passer (weight 3), the five linemen of
  usage.protection_front, RB1, WR1, WR2, TE1, and FB1 when the club dressed
  a fullback, else WR3;
* defense starters: DL1-4, LB1-3, DB1-4 by club depth order;
* unit composite = sum of position weight x player value (a Below-Average or
  Replacement-Level starter lowers it).

Edge for an offense against a defense (TD-share shift per drive, fed to
drive_model.apply_edge through field_position.category_mix):

    edge = OFFENSE_SLOPE * (off_comp - OFFENSE_CENTRE)
         - DEFENSE_SLOPE * (def_comp - DEFENSE_CENTRE)
         + HOME_EDGE (home offense at a home venue only)

clamped to +/-EDGE_CLAMP. The slopes are the second study's shrunk per-side
TD-share slopes for the combined composite and the centres its 2012
composite means. A club whose TeamInput carries no strength record (old
synthetic inputs, closed 2013 inputs) keeps the legacy anchor path, one side
at a time: (anchor - 2) x 0.025.

Attribution (defect register item 19): each player's record also carries
his `attribution_tier` (the tier his own value maps to on his own side);
runtime/usage.py tilts carry, target and sack credit by it. That tilt reads
this record only after the possession is resolved and can change no score.

Nothing here reads a club name or which side is the protagonist; Jacksonville
is scored from the same evidence files by the same rule.
"""
from __future__ import annotations

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

from . import usage
from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "library/data/2010_2012_honours_evidence.json"
PRODUCTION = ROOT / "library/data/2010_2012_production_evidence.json"
CALIBRATION = ROOT / "library/data/2014_strength_calibration_v2.json"
FIRST_PASS_CALIBRATION = ROOT / "library/data/2014_strength_calibration.json"


def league_players_path(season):
    """The season's league player inventory (identity joins), resolved
    through the season layout (`career/2014/league/personnel/...`)."""
    return SeasonPaths(int(season), ROOT).record("league/personnel/league_players.json")


def club_codes_path(season):
    """The season's rotation file, which carries the club code map."""
    return SeasonPaths(int(season), ROOT).record("schedule/rotation_%d.json" % int(season))

MODEL = "honours-production-v2"
# Second study (combined_max variant) shrunk TD-share slopes per composite
# unit and its 2012 composite means (library/data/2014_strength_calibration_v2.json,
# study_2012.variants.combined_max.fits.*; tests/test_strength.py checks
# these against the file).
OFFENSE_SLOPE = 0.005785739981127017
DEFENSE_SLOPE = 0.004587405854420489
OFFENSE_CENTRE = 4.296875
DEFENSE_CENTRE = 8.109375
# Home term per drive for the home offense at a home venue, none at a neutral
# site (user decision, September 29, 2026; library/2014_strength_calibration.md
# section 4: drive-level fit 0.0227, SE 0.0102). Replaces kernel 2013.11's 0.008.
HOME_EDGE = 0.023
# Widened from +/-0.06 (user decision, September 29, 2026).
EDGE_CLAMP = 0.12
# Legacy anchor path (TeamInputs without a strength record).
LEGACY_ANCHOR_SCALE = 0.025
LEGACY_ANCHOR_CENTRE = 2.0

DIVERGENCE = "2013-01-15"
LAST_PRE_DIVERGENCE_SEASON = 2012
TIERS = {"AP1": ("Elite", 4), "AP2": ("Plus", 3), "PB": ("Plus", 3)}
AVERAGE_VALUE = 2
EVIDENCE_WEIGHT = {"Confirmed two-pass": 1.0, "Single-pass": 0.5}
PRODUCTION_TIER_VALUE = {"Elite": 2, "Plus": 1, "Average": 0, "Below-Average": -1, "Replacement-Level": -2}
PRODUCTION_WEIGHT = {"Confirmed two-pass": 1.0, "Corrected": 1.0, "Unverified": 0.5}
TIER_STEP = ("Elite", "Plus", "Average", "Below-Average", "Replacement-Level")
QB_WEIGHT = 3
SPECIAL_POSITIONS = frozenset({"K", "P", "KR", "PR", "LS", "ST"})
OFFENSE_POSITIONS = frozenset({"QB", "RB", "HB", "FB", "WR", "TE", "T", "G", "C", "OT", "OG", "OL",
                               "LT", "LG", "RG", "RT"})
DEFENSE_POSITIONS = frozenset({"DE", "DT", "NT", "DL", "OLB", "ILB", "MLB", "LB", "CB", "S", "SS",
                               "FS", "DB"})
GROUP_SIDE = {"QB": "offense", "RB": "offense", "WR": "offense", "TE": "offense", "OL": "offense",
              "DL": "defense", "LB": "defense", "DB": "defense", "K": "special", "P": "special"}
DEFENSE_STARTERS = (("DL", 4), ("LB", 3), ("DB", 4))
GSIS = re.compile(r"^\d{2}-\d{7}$")


def unit_of(position):
    position = str(position or "").strip().upper()
    if position in SPECIAL_POSITIONS:
        return "special"
    if position in OFFENSE_POSITIONS:
        return "offense"
    if position in DEFENSE_POSITIONS:
        return "defense"
    return None


def honour_seasons(season):
    """The preregistered window: the two most recent completed
    pre-divergence seasons before `season`."""
    latest = min(int(season) - 1, LAST_PRE_DIVERGENCE_SEASON)
    return (latest - 1, latest)


@lru_cache(maxsize=1)
def evidence_file():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def production_file():
    return json.loads(PRODUCTION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def calibration_file():
    return json.loads(CALIBRATION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def first_pass_calibration_file():
    return json.loads(FIRST_PASS_CALIBRATION.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _by_player():
    index = {}
    for row in evidence_file()["entries"]:
        index.setdefault(row.get("player_id"), []).append(row)
    return index


def _iso(value):
    return value.isoformat() if isinstance(value, date) else str(value)


def player_evidence(player_id, season, as_of, entries=None):
    """(honours record or None, rejected receipts) for one nflverse gsis id.

    record = {"offdef": {...} | None, "special": {...} | None}; each part
    holds tier, value, evidence_weight, honour position/group/unit and the
    evidence ids used. Rejected receipts name every in-window honour that
    was not admissible and why (future-dated, undated, post-divergence,
    alternate/replacement)."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    cutoff = min(as_of, DIVERGENCE)
    if entries is None:
        rows = _by_player().get(player_id, ())
    else:
        rows = entries
    record = {"offdef": None, "special": None}
    rejected = []
    for row in rows:
        if row.get("player_id") != player_id or row.get("season") not in window:
            continue
        reason = None
        if row.get("honour_kind") not in TIERS:
            reason = "alternate_or_replacement_no_effect"
        elif not row.get("public_date"):
            reason = "public_date_unpinned"
        elif row["public_date"] >= as_of:
            reason = "future_dated"
        elif row["public_date"] >= cutoff or not row.get("admissible_pre_divergence", False):
            reason = "post_divergence"
        if reason:
            rejected.append({"evidence_id": row["evidence_id"], "reason": reason,
                             "public_date": row.get("public_date")})
            continue
        tier, tier_value = TIERS[row["honour_kind"]]
        weight = EVIDENCE_WEIGHT[row["verification"]]
        value = (tier_value - AVERAGE_VALUE) * weight
        unit = unit_of(row["position"]) or "unknown"
        key = "special" if unit == "special" else "offdef"
        best = record[key]
        part = {"tier": tier, "tier_value": tier_value, "evidence_weight": weight, "value": value,
                "unit": unit, "honour_position": row["position"],
                "honour_group": usage.group(row["position"]) or row["position"],
                "evidence_ids": [row["evidence_id"]]}
        if best is None or value > best["value"] or (value == best["value"] and tier_value > best["tier_value"]):
            if best is not None:
                part["evidence_ids"] = sorted(set(best["evidence_ids"]) | {row["evidence_id"]})
            record[key] = part
        else:
            best["evidence_ids"] = sorted(set(best["evidence_ids"]) | {row["evidence_id"]})
    if record["offdef"] is None and record["special"] is None:
        return None, rejected
    return record, rejected


def production_evidence(player_id, season, as_of, rows=None, season_meta=None):
    """(production part or None, rejected receipts) for one gsis id.

    part = {tier, value, evidence_weight, group, unit, season, discounted,
    evidence_ids}: the best tier over the window, else the season before it
    discounted one tier. A season is rejected (and listed) when its public
    date is not before both the divergence and the input date."""
    as_of = _iso(as_of)
    window = honour_seasons(season)
    fallback = window[0] - 1
    cutoff = min(as_of, DIVERGENCE)
    if rows is None:
        rows = (production_file()["players"].get(player_id) or {}).get("seasons", {})
    if season_meta is None:
        season_meta = production_file()["seasons"]
    rejected, admissible = [], {}
    for year, row in rows.items():
        year = int(year)
        if year not in window and year != fallback:
            continue
        meta = season_meta.get(str(year), {})
        public = meta.get("public_date")
        evidence_id = "production-%d-%s" % (year, player_id)
        if not public:
            rejected.append({"evidence_id": evidence_id, "reason": "public_date_unpinned", "public_date": None})
        elif public >= as_of:
            rejected.append({"evidence_id": evidence_id, "reason": "future_dated", "public_date": public})
        elif public >= cutoff or not meta.get("admissible_pre_divergence", False):
            rejected.append({"evidence_id": evidence_id, "reason": "post_divergence", "public_date": public})
        elif row.get("tier") is None:
            continue  # offensive-line job evidence or a non-qualifier: no tier
        else:
            admissible[year] = (row, evidence_id)
    best = None
    for year in window:
        if year in admissible:
            row, evidence_id = admissible[year]
            if best is None or TIER_STEP.index(row["tier"]) < TIER_STEP.index(best["tier"]):
                best = {"tier": row["tier"], "season": year, "discounted": False, "evidence_ids": [evidence_id],
                        "group": row["group"], "verification": row["verification"]}
    if best is None and fallback in admissible:
        row, evidence_id = admissible[fallback]
        best = {"tier": TIER_STEP[min(4, TIER_STEP.index(row["tier"]) + 1)], "season": fallback, "discounted": True,
                "undiscounted_tier": row["tier"], "evidence_ids": [evidence_id], "group": row["group"],
                "verification": row["verification"]}
    if best is None:
        return None, rejected
    weight = PRODUCTION_WEIGHT.get(best.pop("verification"), 0.5)
    best["evidence_weight"] = weight
    best["value"] = PRODUCTION_TIER_VALUE[best["tier"]] * weight
    best["unit"] = GROUP_SIDE.get(best["group"], "unknown")
    return best, rejected


def tier_for_value(value):
    """The five-tier label a combined player value maps to."""
    if value >= 2:
        return "Elite"
    if value >= 1:
        return "Plus"
    if value <= -2:
        return "Replacement-Level"
    if value <= -1:
        return "Below-Average"
    return "Average"


def player_record(player_id, season, as_of):
    """(record or None, rejected receipts): the honours parts, the production
    part and the player's attribution tier (his own value on his own side)."""
    honours, rejected = player_evidence(player_id, season, as_of)
    production, rejected_p = production_evidence(player_id, season, as_of)
    rejected = rejected + rejected_p
    if honours is None and production is None:
        return None, rejected
    record = dict(honours or {"offdef": None, "special": None})
    record["production"] = production
    h = record.get("offdef")
    prod_value = production["value"] if production and production["unit"] != "special" else 0.0
    value = max(h["value"], prod_value) if h else prod_value
    record["attribution_tier"] = tier_for_value(value)
    return record, rejected


# ---- identity -------------------------------------------------------------------

@lru_cache(maxsize=4)
def _league(season):
    path = league_players_path(season)
    if not path.is_file():
        return {"players": []}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def club_codes(season):
    """{club name: code} from the season's rotation file."""
    data = json.loads(club_codes_path(season).read_text(encoding="utf-8"))
    return {name: code for code, name in data["club_codes"].items()}


def resolve_id(row, club_code, season):
    """(gsis id or None, join note) for one TeamInput roster row."""
    gsis = row.get("gsis_id")
    if gsis:
        return gsis, "gsis_id"
    pid = str(row.get("player_id", ""))
    if GSIS.match(pid):
        return pid, "player_id"
    matches = [p for p in _league(season)["players"] if p.get("name") == pid]
    here = [p for p in matches if p.get("inventory_club") == club_code]
    if len(here) == 1:
        return here[0]["player_id"], "name_and_club"
    if len(matches) == 1:
        return matches[0]["player_id"], "unique_name"
    return None, "unresolved" if not matches else "ambiguous_name"


# ---- TeamInput strength record --------------------------------------------------

def team_strength(team_name, roster, season, as_of):
    """(strength record for TeamInput.strength, coverage receipt).

    The record carries only players with admissible evidence (honours or
    production); every other roster player is an Average low-confidence
    fallback, listed with the reason in the coverage receipt. Identical for
    every club."""
    code = club_codes(season).get(team_name, team_name)
    players, fallbacks, receipts = {}, [], []
    for row in roster:
        pid = row["player_id"] if isinstance(row, dict) else row.player_id
        data = row if isinstance(row, dict) else {"player_id": pid, "gsis_id": getattr(row, "gsis_id", None)}
        gsis, join = resolve_id(data, code, season)
        if gsis is None:
            fallbacks.append({"player_id": pid, "reason": "identity_" + join})
            continue
        record, rejected = player_record(gsis, season, as_of)
        if rejected:
            receipts.append({"player_id": pid, "gsis_id": gsis, "rejected": rejected})
        if record is None:
            fallbacks.append({"player_id": pid, "reason": "no_admissible_evidence"})
            continue
        players[pid] = {"gsis_id": gsis, "join": join, **record}
    strength = {"model": MODEL, "season": int(season), "as_of": _iso(as_of),
                "honour_seasons": list(honour_seasons(season)), "players": players}
    coverage = {"team": team_name, "code": code, "roster_players": len(roster),
                "with_evidence": sorted(players),
                "with_honours": sorted(p for p, r in players.items() if r.get("offdef") or r.get("special")),
                "with_production": sorted(p for p, r in players.items() if r.get("production")),
                "fallbacks": fallbacks, "rejected": receipts}
    return strength, coverage


def coverage_report(season, as_of, rosters=None):
    """Coverage for all 32 clubs: players with evidence, Average fallbacks
    (with reason) and rejected receipts. `rosters` maps club name to its
    roster rows; by default the 2014 league inventory (inventory_club),
    which is identity, not a depth chart."""
    if rosters is None:
        names = {code: name for name, code in club_codes(season).items()}
        rosters = {name: [] for name in names.values()}
        for p in _league(season)["players"]:
            if p.get("inventory_club") in names:
                rosters[names[p["inventory_club"]]].append({"player_id": p["player_id"]})
    clubs = {}
    for team, roster in sorted(rosters.items()):
        strength, coverage = team_strength(team, roster, season, as_of)
        clubs[team] = {**coverage, "strength": strength}
    return {"model": MODEL, "season": int(season), "as_of": _iso(as_of),
            "honour_seasons": list(honour_seasons(season)), "clubs": clubs,
            "summary": {"clubs": len(clubs),
                        "players": sum(c["roster_players"] for c in clubs.values()),
                        "with_evidence": sum(len(c["with_evidence"]) for c in clubs.values()),
                        "with_honours": sum(len(c["with_honours"]) for c in clubs.values()),
                        "with_production": sum(len(c["with_production"]) for c in clubs.values()),
                        "fallbacks": sum(len(c["fallbacks"]) for c in clubs.values())}}


# ---- per-drive composites and the edge --------------------------------------------

def offense_starters(view, passer):
    """[(slot, player)] for the drive's offensive eleven (module docstring)."""
    out = [("QB", passer)] if passer is not None else []
    out += [("OL", p) for p in usage.protection_front(view).values()]
    rb = usage.depth_order(view, "RB")
    wr = usage.depth_order(view, "WR")
    te = usage.depth_order(view, "TE")
    fb = usage.depth_order(view, "FB")
    out += [("RB", p) for p in rb[:1]] + [("WR", p) for p in wr[:2]] + [("TE", p) for p in te[:1]]
    out += [("FB", fb[0])] if fb else [("WR", p) for p in wr[2:3]]
    seen, unique = set(), []
    for slot, p in out:
        if p.player_id not in seen:
            seen.add(p.player_id)
            unique.append((slot, p))
    return unique


def defense_starters(view):
    return [(grp, p) for grp, count in DEFENSE_STARTERS for p in usage.depth_order(view, grp)[:count]]


def slot_value(record, slot, side):
    """(value, honours value, production value) of one player in one lineup
    slot under the preregistered max rule and the side/passer rule."""
    honours = 0.0
    part = (record or {}).get("offdef")
    if part and part["unit"] == side:
        if (slot == "QB") == (part["honour_group"] == "QB"):
            honours = part["value"]
    production = 0.0
    prod = (record or {}).get("production")
    if prod and prod["unit"] == side and (slot == "QB") == (prod["group"] == "QB"):
        production = prod["value"]
    # An honour can only lift: with one, the larger of the two; without one,
    # the production value stands, negative tiers included.
    return (max(honours, production) if honours > 0 else production), honours, production


def composite(strength, starters, side):
    """(unit composite, contributor receipts) for one side's starters."""
    players = (strength or {}).get("players", {})
    total, rows = 0.0, []
    for slot, player in starters:
        record = players.get(player.player_id)
        if not record:
            continue
        value, honours, production = slot_value(record, slot, side)
        if not value and not honours and not production:
            continue
        weight = QB_WEIGHT if slot == "QB" else 1
        contribution = weight * value
        total += contribution
        row = {"player_id": player.player_id, "slot": slot, "value": value, "position_weight": weight,
               "contribution": contribution}
        if honours:
            row["tier"] = record["offdef"]["tier"]
            row["evidence_weight"] = record["offdef"]["evidence_weight"]
        if production:
            row["production_tier"] = record["production"]["tier"]
        rows.append(row)
    return total, rows


def drive_edge(offense_team, defense_team, off_view, def_view, passer, home_offense):
    """(edge, receipt) for one drive. `home_offense` is True only for the
    designated home club's offense at a home venue."""
    receipt = {}
    if getattr(offense_team, "strength", None):
        comp, rows = composite(offense_team.strength, offense_starters(off_view, passer), "offense")
        off_part = OFFENSE_SLOPE * (comp - OFFENSE_CENTRE)
        receipt["offense_composite"], receipt["offense_contributors"] = comp, rows
    else:
        off_part = (offense_team.offense_anchor - LEGACY_ANCHOR_CENTRE) * LEGACY_ANCHOR_SCALE
    if getattr(defense_team, "strength", None):
        comp, rows = composite(defense_team.strength, defense_starters(def_view), "defense")
        def_part = DEFENSE_SLOPE * (comp - DEFENSE_CENTRE)
        receipt["defense_composite"], receipt["defense_contributors"] = comp, rows
    else:
        def_part = (defense_team.defense_anchor - LEGACY_ANCHOR_CENTRE) * LEGACY_ANCHOR_SCALE
    home = HOME_EDGE if home_offense else 0.0
    edge = max(-EDGE_CLAMP, min(EDGE_CLAMP, off_part - def_part + home))
    receipt.update({"offense_part": off_part, "defense_part": def_part, "home": home, "edge": edge})
    return edge, receipt
