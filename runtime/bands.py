"""Statistical band audit: closed-game receipts versus the 2012 shapes.

The audit is a detector for engine or TeamInput defects (a missing position
group, a backup quarterback taking starter snaps, inflated play volume). It
never changes, reruns or selects a game result. An OUTSIDE row is a reason to
inspect inputs and code, not a reason to reroll canon.
"""
from __future__ import annotations

from .calibration import load as load_calibration
from .usage import group, load as load_usage

MIN_TEAM_GAMES = 16

SHARE_TOLERANCE = 0.05
VOLUME_TOLERANCE = {
    "plays_per_team_game": 6.0,
    "yards_per_team_game": 40.0,
    "points_per_team_game": 5.0,
    "first_downs_per_team_game": 3.0,
    "third_down_attempts_per_team_game": 2.5,
    "third_down_rate": 0.06,
}


def _team_games(receipts):
    for receipt in receipts:
        for team_id, game in receipt.get("team_stats", {}).items():
            yield team_id, game


def _shares(counter, groups):
    total = sum(counter.values())
    return {g: (counter.get(g, 0) / total if total else None) for g in groups}


def expected():
    usage = load_usage()["values"]
    cal = load_calibration()
    rate = usage["assisted_tackle_play_rate"]
    return {
        "qb1_attempt_share": usage["passing"]["qb1_attempt_share"],
        "rush_share": usage["rush_share"],
        "target_share": usage["target_share"],
        "tackle_share": usage["tackle_share"],
        # Each assisted play carries two assist credits in the 2012 source.
        "assisted_credit_share": 2 * rate / (1 + rate),
        "plays_per_team_game": cal["model"]["plays_per_team_game"],
        "yards_per_team_game": cal["model"]["yards_per_team_game"],
        "points_per_team_game": cal["model"]["points_per_team_game"],
        "first_downs_per_team_game": (
            usage["scrimmage_first_downs_per_team_game"]
            + usage["penalty_first_downs_per_team_game"]
        ),
        "third_down_attempts_per_team_game": usage["third_down_attempts_per_team_game"],
        "third_down_rate": cal["model"]["third_down_rate"],
    }


def observe(receipts):
    team_games = 0
    qb1 = []
    rush, target, tackle = {}, {}, {}
    assisted = tackles = 0
    totals = dict(plays=0, yards=0, points=0, first_downs=0, third_att=0, third_conv=0)
    for _, game in _team_games(receipts):
        team_games += 1
        players = game.get("players", {})
        attempts = [line.get("pass_attempts", 0) for line in players.values()]
        if sum(attempts):
            qb1.append(max(attempts) / sum(attempts))
        for line in players.values():
            grp = group(line.get("position"))
            if not grp:
                continue
            rush[grp] = rush.get(grp, 0) + line.get("rushing_attempts", 0)
            target[grp] = target.get(grp, 0) + line.get("targets", 0)
            tackle[grp] = tackle.get(grp, 0) + line.get("tackles", 0)
            assisted += line.get("assisted_tackles", 0)
            tackles += line.get("tackles", 0)
            totals["plays"] += line.get("rushing_attempts", 0) + line.get("dropbacks", 0)
        totals["yards"] += game.get("passing_yards", 0) + game.get("rushing_yards", 0)
        totals["points"] += game.get("points", 0)
        totals["first_downs"] += game.get("first_downs", 0)
        totals["third_att"] += game.get("third_down_attempts", 0)
        totals["third_conv"] += game.get("third_down_conversions", 0)
    per = (lambda v: v / team_games) if team_games else (lambda v: None)
    return {
        "team_games": team_games,
        "qb1_attempt_share": sum(qb1) / len(qb1) if qb1 else None,
        "rush_share": _shares(rush, ("RB", "QB", "FB", "WR", "TE")),
        "target_share": _shares(target, ("WR", "TE", "RB", "FB")),
        "tackle_share": _shares(tackle, ("DB", "LB", "DL")),
        "assisted_credit_share": assisted / tackles if tackles else None,
        "plays_per_team_game": per(totals["plays"]),
        "yards_per_team_game": per(totals["yards"]),
        "points_per_team_game": per(totals["points"]),
        "first_downs_per_team_game": per(totals["first_downs"]),
        "third_down_attempts_per_team_game": per(totals["third_att"]),
        "third_down_rate": (
            totals["third_conv"] / totals["third_att"] if totals["third_att"] else None
        ),
    }


def audit(receipts):
    """Return (team_games, rows); each row is (metric, observed, band, tolerance, status)."""
    obs = observe(receipts)
    exp = expected()
    enough = obs["team_games"] >= MIN_TEAM_GAMES
    rows = []

    def add(metric, observed, band, tolerance):
        if observed is None or not enough:
            status = "INSUFFICIENT SAMPLE"
        else:
            status = "WITHIN" if abs(observed - band) <= tolerance else "OUTSIDE"
        rows.append((metric, observed, band, tolerance, status))

    add("QB1 share of team pass attempts", obs["qb1_attempt_share"], exp["qb1_attempt_share"], SHARE_TOLERANCE)
    for name, label in (("rush_share", "carries"), ("target_share", "targets"), ("tackle_share", "tackle credits")):
        for grp, band in exp[name].items():
            add(f"{grp} share of {label}", obs[name].get(grp), band, SHARE_TOLERANCE)
    add("Assisted share of tackle credits", obs["assisted_credit_share"], exp["assisted_credit_share"], SHARE_TOLERANCE)
    for key, tolerance in VOLUME_TOLERANCE.items():
        add(key.replace("_", " "), obs[key], exp[key], tolerance)
    return obs["team_games"], rows


# ---- kernel 2013.6 cohort ------------------------------------------------------
#
# The drive-model rows below are computed only on receipts closed under kernel
# 2013.6 or later. Weeks 1-3 (kernels 2013.4/2013.5) form a legacy cohort:
# known ledger defects (Entries 35/38), detection only, never grounds to rerun.
# Tolerances are three standard errors at the observed sample, not constants:
# 3*sqrt(p(1-p)/n) for rates and 3*sqrt(lambda/n) for per-team-game counts.

import math

from . import drive_model
from .statbook import kernel_at_least

LEGACY_LABEL = (
    "legacy kernel, known ledger defects (Entries 35/38), detection only; "
    "never grounds to rerun"
)
MIN_BIN_ATTEMPTS = 30


def cohorts(receipts):
    """(legacy, current): receipts before and from kernel 2013.6."""
    legacy, current = [], []
    for receipt in receipts:
        (current if kernel_at_least(receipt.get("kernel_version")) else legacy).append(receipt)
    return legacy, current


def _drives(receipt):
    from .play_detail import DRIVE_SUMMARY_FIELDS
    return [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in receipt.get("drives", ())]


SHARE_GROUPS = (
    ("touchdown", ("touchdown",)),
    ("field goal attempt", ("field_goal_attempt",)),
    ("punt", ("punt",)),
    ("turnover (INT + fumble lost)", ("interception", "fumble_lost")),
    ("downs", ("downs",)),
    ("safety", ("safety",)),
    ("clock", ("clock",)),
)


def drive_model_expected():
    data = drive_model.load()
    cal = load_calibration()
    totals = cal["period_totals"]
    counts = data["category_counts"]
    drives = sum(counts.values())
    team_games = totals["team_games"]
    rates = data["rates"]
    return {
        "fg_accuracy": rates["field_goal"][0] / rates["field_goal"][1],
        "fg_by_distance": {
            label: rates["fg_by_distance"][label][0] / rates["fg_by_distance"][label][1]
            for label, _, _ in rates["fg_bin_edges"]
        },
        "xp_accuracy": rates["extra_point"][0] / rates["extra_point"][1],
        "fga_per_team_game": totals["field_goal_attempts"] / team_games,
        "fgm_per_team_game": totals["field_goals_made"] / team_games,
        "drives_per_team_game": drives / team_games,
        "punts_per_team_game": counts["punt"] / team_games,
        "drive_share": {label: sum(counts[c] for c in cats) / drives for label, cats in SHARE_GROUPS},
        "clock_expired_drives_per_team_game": counts["clock"] / team_games,
        "offensive_drive_turnovers_per_team_game": (counts["interception"] + counts["fumble_lost"]) / team_games,
        "interception_share_of_turnovers": counts["interception"] / (counts["interception"] + counts["fumble_lost"]),
        "kickoffs_per_team_game": totals["kickoffs"] / team_games,
        "kick_returns_per_team_game": totals["kickoff_returns"] / team_games,
    }


def drive_model_observe(receipts):
    team_games = 0
    sums = {k: 0 for k in ("field_goal_attempts", "field_goals", "extra_point_attempts",
                           "extra_points_made", "drives", "punts", "clock_expired_drives",
                           "turnovers", "kickoffs", "kick_returns")}
    categories = {}
    bins = {}
    interceptions = 0
    edges = drive_model.load()["rates"]["fg_bin_edges"]
    for receipt in receipts:
        for game in receipt.get("team_stats", {}).values():
            team_games += 1
            for key in sums:
                sums[key] += game.get(key, 0) or 0
        for d in _drives(receipt):
            category = "clock" if str(d["category"]).startswith("end_of_") else d["category"]
            categories[category] = categories.get(category, 0) + 1
            interceptions += category == "interception"
            if category == "field_goal_attempt" and d.get("fg_distance") is not None:
                label = next((lab for lab, _, high in edges if d["fg_distance"] <= high), edges[-1][0])
                cell = bins.setdefault(label, [0, 0])
                cell[1] += 1
                cell[0] += bool(d.get("fg_made"))
    drives = sum(categories.values())
    return {
        "team_games": team_games,
        "sums": sums,
        "categories": categories,
        "drives_observed": drives,
        "fg_bins": bins,
        "interceptions": interceptions,
    }


def audit_drive_model(receipts):
    """Rows (metric, observed, centre, tolerance, status) for the 2013.6 cohort."""
    obs = drive_model_observe(receipts)
    exp = drive_model_expected()
    n = obs["team_games"]
    enough = n >= MIN_TEAM_GAMES
    sums = obs["sums"]
    rows = []

    def add(metric, observed, centre, tolerance, ok=True, graded=True):
        if observed is None or tolerance is None or not enough or not ok:
            status = "INSUFFICIENT SAMPLE"
        elif not graded:
            status = "INFORMATIONAL"
        else:
            status = "WITHIN" if abs(observed - centre) <= tolerance else "OUTSIDE"
        rows.append((metric, observed, centre, tolerance, status))

    def rate_row(metric, made, attempts, centre, minimum=1):
        observed = made / attempts if attempts else None
        tolerance = 3 * math.sqrt(centre * (1 - centre) / attempts) if attempts else None
        add(metric, observed, centre, tolerance, attempts >= minimum)

    def count_row(metric, total, centre, graded=True):
        observed = total / n if n else None
        tolerance = 3 * math.sqrt(centre / n) if n else None
        add(metric, observed, centre, tolerance, graded=graded)

    rate_row("FG accuracy", sums["field_goals"], sums["field_goal_attempts"], exp["fg_accuracy"])
    for label, centre in exp["fg_by_distance"].items():
        made, attempts = obs["fg_bins"].get(label, [0, 0])
        rate_row("FG accuracy %s yd" % label, made, attempts, centre, MIN_BIN_ATTEMPTS)
    rate_row("XP accuracy (informational; partially verified)", sums["extra_points_made"],
             sums["extra_point_attempts"], exp["xp_accuracy"])
    count_row("FGA per team game", sums["field_goal_attempts"], exp["fga_per_team_game"])
    count_row("FGM per team game", sums["field_goals"], exp["fgm_per_team_game"])
    count_row("drives per team game (nflverse definition; PFR 10.47)", sums["drives"], exp["drives_per_team_game"])
    count_row("punts per team game (drive-ending)", sums["punts"], exp["punts_per_team_game"])
    drives = obs["drives_observed"]
    for label, cats in SHARE_GROUPS:
        made = sum(obs["categories"].get(c, 0) for c in cats)
        rate_row("drive share: %s" % label, made, drives, exp["drive_share"][label])
    count_row("clock-expired drives per team game", sums["clock_expired_drives"],
              exp["clock_expired_drives_per_team_game"])
    count_row("offensive-drive turnovers per team game", sums["turnovers"],
              exp["offensive_drive_turnovers_per_team_game"])
    turnovers = obs["categories"].get("interception", 0) + obs["categories"].get("fumble_lost", 0)
    rate_row("interception share of turnovers", obs["interceptions"], turnovers,
             exp["interception_share_of_turnovers"])
    # Informational, not graded: the 2012 centre (PFR 2,665; play-by-play
    # 2,620 unresolved) counts kickoffs the kernel does not model by design:
    # after non-offensive touchdowns, onside kicks and re-kicks, and after a
    # half-final score whose return ran out the clock.
    count_row("kickoffs per team game (informational; centre includes kicks not modelled: "
              "after non-offensive TDs, onside, re-kicks, after half-final scores)", sums["kickoffs"],
              exp["kickoffs_per_team_game"], graded=False)
    count_row("kick returns per team game", sums["kick_returns"], exp["kick_returns_per_team_game"])
    return n, rows


def coherence(receipts):
    """Zero-tolerance ledger-coherence counts over the given receipts."""
    from .play_detail import COHERENCE_CLASSES, check_ledger, coherence_counts

    errors = []
    checked = 0
    for receipt in receipts:
        if not receipt.get("drives"):
            continue
        checked += 1
        errors += check_ledger(receipt)
    counts = coherence_counts(errors)
    return checked, [(cls, counts.get(cls, 0)) for cls in COHERENCE_CLASSES]
