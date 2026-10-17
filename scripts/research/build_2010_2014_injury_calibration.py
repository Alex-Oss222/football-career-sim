#!/usr/bin/env python3
"""Build the 2010-2014 (2014 Weeks 1-4) injury calibration (plan batch B3d; data only).

  python scripts/research/build_2010_2014_injury_calibration.py [--sources DIR] [--check]

Writes library/data/2010_2014w4_nfl_injury_calibration.json. Sources come only through
scripts/research/sources_2010_2014.py (the batch B2 gate); DIR defaults to
$SOURCES_2010_2014_DIR.

Method. The extraction is the committed 2012 builder's (scripts/research/
build_2012_injury_calibration.py: report onsets, in-game stoppage notes, footprints,
games missed, vanishes), ported with the season as a parameter and run on each season's
official injury reports, play-by-play and weekly roster. The 2012 port must reproduce the
committed builder's data block exactly. Seasons pool by event:
- 2014 Weeks 1-4 contribute onsets and stoppages only. Their severity needs later games that
  lie beyond the cut, so severity pools 2010-2013.
- Body-part labels new in 2010-2014 map through a versioned vocabulary extension (2014.6,
  the anatomical first-named-part rule), and the committed 2012 vocabulary is unchanged.

Recommended parameters. The committed 2012 calibration's stated assumptions are carried as
its own ratios, read from that file and never typed here:
- the game-attributable share of report onsets and its range;
- the head and neck under-listing adjustment;
- the severity censoring correction;
- the removal probabilities and day ranges;
- the specialists' relative risk.
They are applied to the pooled counts. Relative risks use the declared on-field slot mix
(runtime/participation.py SCRIMMAGE_SLOT_MIX, unchanged: decision 1B.4), labelled "on
Unverified slots", and validate() enforces that mix. The acceptance bands for kernel 2014.6
carry the 2012 bands' relative widths around the pooled values.

No club, game, player or date field is written.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (HERE, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import build_2012_injury_calibration as ic  # noqa: E402
import league_base_2010_2014 as lb  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

OUT = ROOT / "library" / "data" / "2010_2014w4_nfl_injury_calibration.json"
COMMITTED_2012 = ROOT / "library" / "data" / "2012_nfl_injury_calibration.json"
SEASONS = (2010, 2011, 2012, 2013, 2014)
SEVERITY_SEASONS = (2010, 2011, 2012, 2013)
SCHEMA = "2010-2014w4-nfl-injury-calibration-v1"

# Versioned vocabulary extension (2014.6): labels first seen in the 2010-2014 reports, by the
# anatomical first-named-part rule. The committed 2012 sets are unchanged.
VOCABULARY_VERSION = "2014.6"
VOCABULARY_EXTENSION = {
    "head_neck": ("nose", "chin", "tooth", "migraines", "(migraines)", "headaches"),
    "upper_extremity": ("tricep", "l. arm", "upper arm", "l. hand", "rt. thumb", "shoulders", "finger and neck"),
    "lower_extremity": ("fibula", "arch", "quad", "quadriceps", "lower leg", "lf. calf", "feet", "hips", "toes",
                        "ankle and foot", "hip and back", "hamstring illness"),
    "trunk_other": ("kidney", "lacerated kidney", "lung", "stomach", "hernia", "qblique", "low back", "lower back"),
    "excluded": ("infection", "flu", "heat cramps"),
}


def class_of(part, extended=True):
    try:
        return ic.class_of(part)
    except SystemExit:
        if not extended:
            raise
    for name, members in VOCABULARY_EXTENSION.items():
        if part in members:
            return None if name == "excluded" else name
    raise SystemExit("unmapped body part: %r" % part)


def gated(name, dest, season=None, game_type_key=None):
    for r in sources.rows(name, dest):
        yield r


def season_records(season, dest, extended=True):
    """The committed main()'s per-season extraction, ported with the season as a parameter.
    Returns the record lists its aggregation reads (no identifiers are kept beyond them)."""
    year = str(season)
    tag = lb.TAG[season]
    rows = [r for r in gated("injuries_%s.csv" % tag, dest) if r["season"] == year and r["game_type"] == "REG"]
    roster = [r for r in gated("roster_weekly_%s.csv" % tag, dest) if r["season"] == year and r["game_type"] == "REG"]
    plays = [r for r in gated(lb.pbp_name(season, "nflverse"), dest) if r["season_type"] == "REG"]
    id_cols = [c for c in plays[0] if c.endswith("player_id") and c != "fantasy_player_id"]
    team = ic.team

    group_of, jersey = {}, {}
    full_name = {r["gsis_id"]: r["full_name"].lower() for r in roster}
    for r in roster:
        g = ic.GROUPS.get(r["position"]) or ic.GROUPS.get(r["depth_chart_position"])
        if g:
            group_of.setdefault(r["gsis_id"], g)
        if r["jersey_number"]:
            jersey.setdefault((team(r["team"]), int(r["week"]), r["jersey_number"]), []).append(r)
    for r in rows:
        if ic.GROUPS.get(r["position"]):
            group_of.setdefault(r["gsis_id"], ic.GROUPS[r["position"]])

    def jersey_player(club, week, number, name):
        cands = jersey.get((club, week, number), [])
        surname = name.split(".", 1)[-1].strip().lower()
        for r in cands:
            if surname and surname in r["full_name"].lower():
                return r["gsis_id"]
        active = [r for r in cands if r["status"] == "ACT"]
        return (active or cands or [{"gsis_id": None}])[-1]["gsis_id"]

    games = {}
    seen = collections.defaultdict(set)
    play_types = collections.Counter()
    order = collections.defaultdict(list)
    notes = []
    for i, p in enumerate(plays):
        gid, week = p["game_id"], int(p["week"])
        games[gid] = (week, team(p["home_team"]), team(p["away_team"]))
        play_types[p["play_type"] or "(none)"] += 1
        if p["play_type"] == "no_play" and ic.SNAPPED.search(p["desc"].split("PENALTY")[0]):
            play_types["no_play_snapped"] += 1
        ids = {p[c] for c in id_cols if p[c]}
        order[gid].append((i, ids))
        for pid in ids:
            for club in (team(p["home_team"]), team(p["away_team"])):
                seen[(club, pid)].add(week)
        start = 0
        for m in ic.NOTE.finditer(p["desc"]):
            who = ic.NOTE_PLAYER.match(p["desc"][start:m.start()])
            start = m.end()
            club = team(who.group(1))
            pid = jersey_player(club, week, who.group(2), who.group(3))
            disp = m.group(2) or m.group(3) or "(none)"
            surname = who.group(3).split(".", 1)[-1].strip().lower()
            notes.append({"game": gid, "week": week, "club": club, "pid": pid,
                          "name_ok": bool(pid) and surname in full_name.get(pid, ""),
                          "index": i, "play_type": p["play_type"] or "(none)",
                          "side": "possession" if club == team(p["posteam"]) else "other",
                          "disposition": disp})
    team_games = 2 * len(games)
    club_weeks = collections.defaultdict(list)
    for week, home, away in games.values():
        club_weeks[home].append(week)
        club_weeks[away].append(week)
    club_weeks = {c: sorted(ws) for c, ws in club_weeks.items()}
    on_club = collections.defaultdict(set)
    for r in roster:
        on_club[(team(r["team"]), r["gsis_id"])].add(int(r["week"]))
    seen = {k: v & on_club.get(k, set()) for k, v in seen.items()}

    def footprint_player(club, pid, before_week):
        prior = [w for w in club_weeks[club] if w < before_week]
        if len(prior) < 3 or group_of.get(pid) == "OL":
            return False
        hits = len(seen.get((club, pid), set()) & set(prior))
        return hits >= 0.75 * len(prior)

    def games_missed(club, pid, onset_game_week):
        later = [w for w in club_weeks[club] if w > onset_game_week]
        for n, w in enumerate(later):
            if w in seen.get((club, pid), set()):
                return n, False
        return len(later), True

    def severity_record(club, pid, onset_game_week):
        if not footprint_player(club, pid, onset_game_week + 1):
            return None
        missed, never = games_missed(club, pid, onset_game_week)
        if never and missed < 9:
            return "censored"
        return ic.severity_of(missed)

    report = collections.defaultdict(dict)
    report_weeks = collections.defaultdict(set)
    for r in rows:
        report_weeks[r["team"]].add(int(r["week"]))
        report[(r["team"], int(r["week"]))][r["gsis_id"]] = r
    report_weeks = {t: sorted(ws) for t, ws in report_weeks.items()}

    def parts(row):
        return {ic.part_of(row["report_primary_injury"]), ic.part_of(row["report_secondary_injury"])} - {""}

    onsets, pairs = [], 0
    for club, weeks in report_weeks.items():
        pairs += len(weeks) - 1
        for i in range(1, len(weeks)):
            prev = weeks[i - 1]
            for pid, row in report[(club, weeks[i])].items():
                part = ic.part_of(row["report_primary_injury"])
                klass = class_of(part, extended)
                if klass is None:
                    continue
                prev_row = report[(club, prev)].get(pid)
                if prev_row and part in parts(prev_row):
                    continue
                listed = []
                for w2 in weeks[i:]:
                    r2 = report[(club, w2)].get(pid)
                    if not r2 or part not in parts(r2):
                        break
                    listed.append(r2["report_status"])
                onsets.append({"group": group_of.get(pid), "class": klass, "part": part,
                               "first_status": listed[0] or "(none)",
                               "severity": severity_record(club, pid, prev)})
    strict, strict_pairs = 0, 0
    for club, weeks in report_weeks.items():
        strict_pairs += max(0, len(weeks) - 2)
        for i in range(2, len(weeks)):
            for pid, row in report[(club, weeks[i])].items():
                part = ic.part_of(row["report_primary_injury"])
                if class_of(part, extended) is None:
                    continue
                if any(report[(club, weeks[j])].get(pid) and
                       part in parts(report[(club, weeks[j])][pid]) for j in (i - 1, i - 2)):
                    continue
                strict += 1
    for n in notes:
        n["group"] = group_of.get(n["pid"])
        later = [ids for idx, ids in order[n["game"]] if idx > n["index"]]
        n["returned_same_game"] = any(n["pid"] in ids for ids in later) if n["pid"] else None
        n["footprint"] = bool(n["pid"]) and footprint_player(n["club"], n["pid"], n["week"])
        n["severity"] = severity_record(n["club"], n["pid"], n["week"]) if n["pid"] else None
        nxt = [w for w in report_weeks.get(n["club"], []) if w > n["week"]]
        row = report[(n["club"], nxt[0])].get(n["pid"]) if nxt and n["pid"] else None
        n["next_report_part"] = ic.part_of(row["report_primary_injury"]) if row else None
        n["next_report_class"] = (class_of(n["next_report_part"], extended) or "(excluded)") \
            if n["next_report_part"] is not None else None
    listed_after = collections.defaultdict(set)
    for (club, w), players in report.items():
        for pid in players:
            listed_after[(club, pid)].add(w)
    vanish = collections.Counter()
    vanish_group = collections.Counter()
    for (club, pid), weeks_seen in seen.items():
        if not weeks_seen or club not in club_weeks:
            continue
        last = max(weeks_seen)
        later = [w for w in club_weeks[club] if w > last]
        if len(later) < 3 or not footprint_player(club, pid, last + 1):
            continue
        if any(w > last for w in listed_after.get((club, pid), ())):
            continue
        if later[0] not in on_club.get((club, pid), set()):
            continue
        band = "long_term" if len(later) >= 9 else "multi_week_or_longer"
        vanish[band] += 1
        vanish_group[group_of.get(pid)] += 1
    for n in notes:      # identifiers dropped once the per-note facts are derived
        n["matched"] = bool(n["pid"])
        for key in ("game", "club", "pid", "index"):
            n.pop(key, None)
    return {"season": season, "team_games": team_games, "games": len(games), "pairs": pairs, "strict": strict,
            "strict_pairs": strict_pairs, "play_types": play_types, "onsets": onsets, "notes": notes,
            "vanish": vanish, "vanish_group": vanish_group}


def merge(records):
    out = {"team_games": 0, "games": 0, "pairs": 0, "strict": 0, "strict_pairs": 0,
           "play_types": collections.Counter(), "onsets": [], "notes": [], "vanish": collections.Counter(),
           "vanish_group": collections.Counter()}
    for r in records:
        for k in ("team_games", "games", "pairs", "strict", "strict_pairs"):
            out[k] += r[k]
        for k in ("play_types", "vanish", "vanish_group"):
            out[k].update(r[k])
        out["onsets"] += r["onsets"]
        out["notes"] += r["notes"]
    return out


def summarise(rec, severity_rec=None, season_label="2012", season_type="REG weeks 1-17"):
    """The committed main()'s aggregation. `severity_rec` supplies the severity rows when they
    pool other seasons than the counts (2014 Weeks 1-4 carry no severity)."""
    severity_rec = severity_rec or rec
    onsets, notes = rec["onsets"], rec["notes"]
    pairs, team_games = rec["pairs"], rec["team_games"]
    play_types = rec["play_types"]
    n_on = len(onsets)
    by_group = collections.Counter(o["group"] for o in onsets)
    note_group = collections.Counter(n["group"] or "(unmatched)" for n in notes)
    by_class = collections.Counter(o["class"] for o in onsets)
    by_part = collections.Counter(o["part"] for o in onsets)
    class_sh, class_total = ic.shares(by_class, ic.CLASSES)
    sev_onsets = severity_rec["onsets"]
    sev_notes = severity_rec["notes"]
    sev = collections.Counter(o["severity"] for o in sev_onsets if o["severity"])
    sev_sh, sev_n = ic.shares(sev, ic.SEVERITY)
    sev_by_class = {k: ic.shares(collections.Counter(o["severity"] for o in sev_onsets
                                                     if o["class"] == k and o["severity"]), ic.SEVERITY)[0]
                    for k in ic.CLASSES}
    note_sev = collections.Counter(n["severity"] for n in sev_notes if n["severity"])
    note_sev_sh, note_sev_n = ic.shares(note_sev, ic.SEVERITY)
    footprint_notes = [n for n in notes if n["footprint"]]
    note_parts = collections.Counter(n["next_report_class"] for n in notes if n["next_report_part"] is not None)
    note_class_sh, note_class_n = ic.shares(note_parts, ic.CLASSES)
    scrimmage = play_types["run"] + play_types["pass"]
    exposure_plays = sum(play_types[t] for t in ic.EXPOSURE_TYPES) + play_types["no_play_snapped"]
    groups = {}
    for g in ic.GROUP_ORDER:
        groups[g] = {
            "report_onsets": by_group[g],
            "report_onsets_per_team_game": round(by_group[g] / pairs, 4),
            "report_share": round(by_group[g] / n_on, 4),
            "ingame_stoppages": note_group[g],
            "ingame_stoppages_per_team_game": round(note_group[g] / team_games, 4),
            "ingame_share": round(note_group[g] / len(notes), 4),
        }
    vanish = rec["vanish"]
    return {
        "season": season_label,
        "season_type": season_type,
        "denominators": {
            "team_games": team_games,
            "report_pairs": pairs,
            "scrimmage_plays_run_pass": scrimmage,
            "play_types": dict(play_types.most_common()),
            "exposure_plays": exposure_plays,
            "player_plays_per_team_game": round(11 * exposure_plays / rec["games"], 1),
        },
        "report_onsets": {
            "count": n_on,
            "per_team_game": round(n_on / pairs, 4),
            "per_team_game_strict_two_report_rule": round(rec["strict"] / rec["strict_pairs"], 4),
            "first_listed_status": dict(collections.Counter(o["first_status"] for o in onsets)),
            "unmatched_position": by_group[None],
        },
        "ingame_stoppages": {
            "count": len(notes),
            "per_team_game": round(len(notes) / team_games, 4),
            "per_1000_scrimmage_plays_run_pass": round(
                1000 * sum(n["play_type"] in ("run", "pass") for n in notes) / scrimmage, 3),
            "per_1000_kickoffs": round(1000 * sum(n["play_type"] == "kickoff" for n in notes) / play_types["kickoff"], 3),
            "per_1000_punts": round(1000 * sum(n["play_type"] == "punt" for n in notes) / play_types["punt"], 3),
            "by_play_type": dict(collections.Counter(n["play_type"] for n in notes)),
            "by_side": dict(collections.Counter(n["side"] for n in notes)),
            "announced_disposition": dict(collections.Counter(n["disposition"] for n in notes)),
            "player_matched": sum(n["matched"] for n in notes),
            "player_matched_surname_agrees": sum(n["name_ok"] for n in notes),
            "footprint_players": len(footprint_notes),
            "footprint_returned_same_game": sum(bool(n["returned_same_game"]) for n in footprint_notes),
            "footprint_return_by_disposition": {
                d: [sum(bool(n["returned_same_game"]) for n in footprint_notes if n["disposition"] == d),
                    sum(1 for n in footprint_notes if n["disposition"] == d)]
                for d in ("Probable", "Questionable", "Doubtful", "Out", "(none)")},
            "on_next_report": sum(1 for n in notes if n["next_report_part"] is not None),
            "next_report_class_shares": note_class_sh,
            "next_report_class_n": note_class_n,
            "severity_shares_footprint": note_sev_sh,
            "severity_n_footprint": note_sev_n,
            "severity_censored": note_sev["censored"],
        },
        "unreported_vanish_upper_bound": {
            "count": sum(vanish.values()),
            "per_team_game": round(sum(vanish.values()) / team_games, 4),
            "by_band": dict(vanish),
            "by_group": {g: rec["vanish_group"][g] for g in ic.GROUP_ORDER},
        },
        "by_group": groups,
        "class_shares_report_onsets": class_sh,
        "class_counts_report_onsets": {k: by_class[k] for k in ic.CLASSES},
        "concussion_report_onsets": by_part["concussion"],
        "concussion_share_report_onsets": round(by_part["concussion"] / class_total, 4),
        "top_parts_report_onsets": dict(by_part.most_common(15)),
        "severity_report_onsets_footprint": {
            "shares": sev_sh, "n": sev_n, "censored": sev["censored"],
            "counts": {k: sev[k] for k in ic.SEVERITY},
            "by_class": sev_by_class,
            "definition": "minor 0 games missed; short 1-2; multi_week 3-8; long_term 9+ (incl. not seen again with 9+ club games left)",
        },
    }


# ============================================================================ recommended

def slot_mix():
    from runtime.participation import SCRIMMAGE_SLOT_MIX
    return dict(SCRIMMAGE_SLOT_MIX)


def relative_risks(data, mix):
    """Group onset share over its declared slot share, from the report onsets and from the
    in-game stoppages; the recommended value is their mean (the 2012 rule, unrounded)."""
    total_slots = sum(mix.values())
    out = {}
    for g in ("QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB"):
        slot = mix[g] / total_slots
        report = data["by_group"][g]["report_share"] / slot
        ingame = data["by_group"][g]["ingame_share"] / slot
        out[g] = {"report": round(report, 4), "in_game": round(ingame, 4), "value": round((report + ingame) / 2, 4)}
    return out


def recommended(pooled, committed):
    """The 2014.6 parameters: the committed 2012 assumptions carried as ratios onto the pooled
    counts (see the module docstring); each value names its basis."""
    rec12, data12 = committed["recommended"], committed["data"]
    per_tg = pooled["report_onsets"]["per_team_game"]
    per_tg12 = data12["report_onsets"]["per_team_game"]
    game12 = rec12["game_onsets_per_team_game"]
    share = game12["value"] / per_tg12
    share_range = [game12["range"][0] / per_tg12, game12["range"][1] / per_tg12]
    game = per_tg * share
    game_range = [per_tg * share_range[0], per_tg * share_range[1]]
    snaps = 11 * pooled["denominators"]["exposure_plays"] / (pooled["denominators"]["team_games"] / 2)
    hazard = game / snaps
    mix = slot_mix()
    rr = relative_risks(pooled, mix)
    rr_values = {g: v["value"] for g, v in rr.items()}
    rr_values["K/P/LS"] = rec12["position_relative_risk_per_snap"]["values"]["K/P/LS"]
    # Head and neck: report head/neck onsets per team-game plus the 2012 under-listing
    # adjustment, over game onsets (game-origin assumption carried, Unverified).
    hn_report = pooled["class_counts_report_onsets"]["head_neck"] / pooled["denominators"]["report_pairs"]
    hn_report12 = data12["class_counts_report_onsets"]["head_neck"] / data12["denominators"]["report_pairs"]
    adjustment = rec12["head_neck_share"]["game_onsets"] * game12["value"] - hn_report12
    hn_share = (hn_report + adjustment) / game
    others = {k: pooled["class_counts_report_onsets"][k] for k in ("lower_extremity", "upper_extremity", "trunk_other")}
    total_other = sum(others.values())
    class_mix = {k: (1 - hn_share) * v / total_other for k, v in others.items()}
    class_mix["head_neck"] = hn_share
    # Between-game mix: report class totals minus game onsets at the game mix.
    report_class = {k: pooled["class_counts_report_onsets"][k] / pooled["denominators"]["report_pairs"]
                    for k in ic.CLASSES}
    between = {k: max(0.0, report_class[k] - game * class_mix[k]) for k in ic.CLASSES}
    between_total = sum(between.values())
    between_mix = {k: v / between_total for k, v in between.items()}
    # Severity: the pooled footprint report shares times the 2012 censoring correction
    # (2012 recommended mix over 2012 footprint shares), renormalised.
    mix12, report12 = rec12["severity_mix_all_onsets"]["values"], data12["severity_report_onsets_footprint"]["shares"]
    raw = {k: pooled["severity_report_onsets_footprint"]["shares"][k] * mix12[k] / report12[k] for k in ic.SEVERITY}
    total = sum(raw.values())
    severity_mix = {k: v / total for k, v in raw.items()}
    removal = dict(rec12["in_game_removal"]["removal_probability_by_severity"])
    label = removal.pop("label", None)
    implied = game * (class_mix["head_neck"] * 1.0 + (1 - class_mix["head_neck"]) * sum(
        severity_mix[k] * removal[k] for k in ic.SEVERITY))
    return {
        "label_key": rec12["label_key"],
        "structure": rec12["structure"],
        "basis": "The committed 2012 calibration's assumptions (library/data/2012_nfl_injury_calibration.json, "
                 "recommended) carried as its own ratios onto the 2010-2014 Weeks 1-4 pooled counts; severity pools "
                 "2010-2013.",
        "game_onsets_per_team_game": {
            "value": game, "range": game_range, "label": "Pattern",
            "basis": "pooled report onsets per team-game times the 2012 game-attributable share (2012 value and range "
                     "over 2012 report onsets: %.4f, %.4f-%.4f)" % (share, share_range[0], share_range[1])},
        "between_game_onsets_per_club_week": {
            "value": per_tg - game, "range": [per_tg - game_range[1], per_tg - game_range[0]], "label": "Pattern",
            "basis": "report onsets minus game onsets"},
        "player_snaps_per_team_game": {"value": snaps, "label": "Confirmed",
                                       "basis": "11 x pooled exposure plays per game (committed definition)"},
        "mean_game_onset_hazard_per_player_snap": {"value": hazard, "label": "Pattern",
                                                   "basis": "game onsets per team-game / player snaps per team-game"},
        "position_relative_risk_per_snap": {
            "values": rr_values, "label": "Pattern on Unverified slots",
            "components": rr, "slot_mix": mix,
            "basis": "group onset share (report onsets and in-game stoppages, pooled) over the declared on-field slot "
                     "share (runtime/participation.py SCRIMMAGE_SLOT_MIX, unchanged; no depth-chart x snap join "
                     "exists, decision 1B.4); the value is the unrounded mean of the two; K/P/LS carries the 2012 "
                     "value (a judgment there, not refit)"},
        "head_neck_share": {"game_onsets": hn_share, "label": "Pattern",
                            "basis": "(pooled report head/neck onsets per team-game + the 2012 under-listing "
                                     "adjustment %.4f) / game onsets; game-origin assumption carried (Unverified)"
                                     % adjustment},
        "class_mix_game_onsets": {"values": class_mix, "label": "Pattern",
                                  "basis": "head/neck as above; the rest split in the pooled report ratio"},
        "class_mix_between_game_onsets": {"values": between_mix, "label": "Pattern",
                                          "basis": "pooled report class totals minus game onsets at the game mix"},
        "severity_bands": rec12["severity_bands"],
        "severity_mix_all_onsets": {"values": severity_mix, "label": "Pattern",
                                    "basis": "pooled 2010-2013 footprint report severity shares times the 2012 "
                                             "censoring correction (2012 recommended mix over 2012 footprint shares), "
                                             "renormalised"},
        "severity_by_class_confirmed": "data.severity_report_onsets_footprint.by_class",
        "in_game_removal": {
            "removal_probability_by_severity": dict(removal, label=label),
            "implied_rest_of_game_removals_per_team_game": implied,
            "label": "Pattern (the 2012 removal probabilities carried; the implied removals recomputed)"},
    }


def acceptance_bands(rec, committed):
    """The 2012 bands' relative widths around the 2014.6 values (2012 band / 2012 value)."""
    rec12 = committed["recommended"]
    bands12 = rec12["acceptance_bands_for_kernel_2014_4"]
    game12 = rec12["game_onsets_per_team_game"]["value"]
    hn12 = rec12["head_neck_share"]["game_onsets"]
    lower12 = rec12["class_mix_game_onsets"]["values"]["lower_extremity"]
    sev12 = rec12["severity_mix_all_onsets"]["values"]
    removal12 = rec12["in_game_removal"]["rest_of_game_removals_per_team_game"]["value"]
    game = rec["game_onsets_per_team_game"]["value"]
    hn = rec["head_neck_share"]["game_onsets"]
    lower = rec["class_mix_game_onsets"]["values"]["lower_extremity"]
    sev = rec["severity_mix_all_onsets"]["values"]
    removal = rec["in_game_removal"]["implied_rest_of_game_removals_per_team_game"]

    def scale(band, old, new):
        return [round(band[0] * new / old, 4), round(band[1] * new / old, 4)]
    time_loss12 = sev12["short"] + sev12["multi_week"] + sev12["long_term"]
    time_loss = sev["short"] + sev["multi_week"] + sev["long_term"]
    return {
        "game_onsets_per_team_game": [round(v, 4) for v in rec["game_onsets_per_team_game"]["range"]],
        "rest_of_game_removals_per_team_game": scale(bands12["rest_of_game_removals_per_team_game"], removal12, removal),
        "head_neck_share_game_onsets": scale(bands12["head_neck_share_game_onsets"], hn12, hn),
        "head_neck_game_onsets_per_team_game": scale(bands12["head_neck_game_onsets_per_team_game"], hn12 * game12,
                                                     hn * game),
        "lower_extremity_share_game_onsets": scale(bands12["lower_extremity_share_game_onsets"], lower12, lower),
        "time_loss_share_(short+)": scale(bands12["time_loss_share_(short+)"], time_loss12, time_loss),
        "long_term_share": scale(bands12["long_term_share"], sev12["long_term"], sev["long_term"]),
        "concussions_per_team_game_if_kernel_labels_concussion": bands12[
            "concussions_per_team_game_if_kernel_labels_concussion"],
        "position_order_checks": bands12["position_order_checks"],
        "rule": "each band is the 2012 band scaled by the 2014.6 value over the 2012 value (the same relative width); "
                "the concussion band (literature) and the order checks are carried unchanged",
    }


# ============================================================================ build, validate

def validate(artifact):
    errors = []
    mix = slot_mix()
    rec = artifact["recommended"]
    if rec["position_relative_risk_per_snap"]["slot_mix"] != mix:
        errors.append("the declared slot mix differs from runtime/participation.py SCRIMMAGE_SLOT_MIX")
    for name, keys in (("class_mix_game_onsets", ic.CLASSES), ("severity_mix_all_onsets", ic.SEVERITY),
                       ("class_mix_between_game_onsets", ic.CLASSES)):
        values = rec[name]["values"]
        if set(values) != set(keys) or abs(sum(values.values()) - 1) > 1e-9 or min(values.values()) < 0:
            errors.append("%s invalid" % name)
    lo, hi = rec["game_onsets_per_team_game"]["range"]
    if not lo <= rec["game_onsets_per_team_game"]["value"] <= hi:
        errors.append("game onsets outside their range")
    if not 0 < rec["mean_game_onset_hazard_per_player_snap"]["value"] < 0.01:
        errors.append("hazard invalid")
    if "acceptance_bands_for_kernel_2014_6" not in artifact:
        errors.append("acceptance_bands_for_kernel_2014_6 missing")
    if artifact["data"]["season"] != "2010-2014w4":
        errors.append("pooled data block mislabelled")
    return errors


def build(dest, log=print):
    errors = []
    committed = json.loads(COMMITTED_2012.read_text())
    # Regression: the port on 2012, with the committed vocabulary only, is the committed data block.
    rec12 = season_records(2012, dest, extended=False)
    if summarise(rec12, season_label=2012) != committed["data"]:
        errors.append("the 2012 port does not reproduce the committed data block")
    records = {}
    for s in SEASONS:
        log("injury %s" % lb.TAG[s])
        records[s] = season_records(s, dest)
    pooled_counts = merge([records[s] for s in SEASONS])
    severity = merge([records[s] for s in SEVERITY_SEASONS])
    data = summarise(pooled_counts, severity_rec=severity, season_label="2010-2014w4",
                     season_type="REG 2010-2013 weeks 1-17 and 2014 weeks 1-4; severity 2010-2013")
    by_season = {lb.TAG[s]: summarise(records[s], season_label=lb.TAG[s],
                                      season_type="REG weeks 1-4" if s == 2014 else "REG weeks 1-17")
                 for s in SEASONS}
    for s in SEASONS:     # 2014 Weeks 1-4 severity is censored by the cut: not reported
        if s == 2014:
            by_season[lb.TAG[s]]["severity_report_onsets_footprint"] = "not used (games after the cut)"
    drift = {
        "report_onsets_per_team_game": lb.rate_drift([(len(records[s]["onsets"]), records[s]["pairs"]) for s in SEASONS]),
        "ingame_stoppages_per_team_game": lb.rate_drift([(len(records[s]["notes"]), records[s]["team_games"])
                                                          for s in SEASONS]),
        "head_neck_share_report_onsets": lb.share_drift([
            (sum(o["class"] == "head_neck" for o in records[s]["onsets"]), len(records[s]["onsets"])) for s in SEASONS]),
    }
    rec = recommended(data, committed)
    manifest = sources.load_manifest()["assets"]
    artifact = {
        "artifact": "2010_2014w4_nfl_injury_calibration",
        "schema": SCHEMA,
        "status": "RESEARCH ARTIFACT for kernel 2014.6 (batch B3d); not read by any runtime module until B5",
        "builder": "scripts/research/build_2010_2014_injury_calibration.py",
        "specification_sha256": pre_build_specification.digest(),
        "information_boundary": ("NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games and reports through "
                                 "September 29, 2014; the October 1-3 Week 5 reports are refused), cut at fetch; the "
                                 "committed 2012 calibration's literature-based assumptions carried as ratios; no "
                                 "club, game, player or date field."),
        "sources": {name: {"sha256": manifest[name]["sha256"]} for s in SEASONS
                    for name in ("injuries_%s.csv" % lb.TAG[s], "roster_weekly_%s.csv" % lb.TAG[s],
                                 lb.pbp_name(s, "nflverse"))},
        "carried_from": {"file": str(COMMITTED_2012.relative_to(ROOT)),
                         "sha256": sources.sha256_file(COMMITTED_2012)},
        "vocabulary": {"version": VOCABULARY_VERSION, "rule": "anatomical first-named-part",
                       "extension": {k: list(v) for k, v in VOCABULARY_EXTENSION.items()},
                       "base": "the committed 2012 sets (build_2012_injury_calibration.py), unchanged"},
        "data": data,
        "data_by_season": by_season,
        "drift": drift,
        "recommended": rec,
        "acceptance_bands_for_kernel_2014_6": acceptance_bands(rec, committed),
        "limitations": committed["limitations"] + [
            "2014 Weeks 1-4 contribute onsets and stoppages only; severity pools 2010-2013.",
            "The relative risks rest on the declared slot mix, which no depth-chart x snap join verifies (labelled "
            "on Unverified slots)."],
        "regression_2012": "the season-parameter port on 2012 with the committed vocabulary reproduces the committed "
                           "data block exactly",
    }
    errors += validate(artifact)
    return artifact, errors


def render(obj):
    return json.dumps(obj, sort_keys=True, indent=1) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=sources.default_dest())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.sources is None or not Path(args.sources).is_dir():
        print("sources not present (set $SOURCES_2010_2014_DIR or --sources); nothing built", file=sys.stderr)
        return 2
    artifact, errors = build(args.sources, log=lambda m: print(m, file=sys.stderr))
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
