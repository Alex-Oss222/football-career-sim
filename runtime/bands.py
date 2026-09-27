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


def _kneels_by_team(receipt):
    """Kneel carries per club from a 2013.7-or-later drives summary (else 0)."""
    out = {}
    for d in _drives(receipt):
        if d.get("kneels"):
            out[d["team"]] = out.get(d["team"], 0) + d["kneels"]
    return out


def observe(receipts):
    team_games = 0
    qb1 = []
    rush, target, tackle = {}, {}, {}
    assisted = tackles = 0
    totals = dict(plays=0, yards=0, points=0, first_downs=0, third_att=0, third_conv=0)
    kneels = {}
    for index, receipt in enumerate(receipts):
        for team_id, count in _kneels_by_team(receipt).items():
            kneels[(index, team_id)] = count
    games = [(index, team_id, game) for index, receipt in enumerate(receipts)
             for team_id, game in receipt.get("team_stats", {}).items()]
    for index, team_id, game in games:
        team_games += 1
        # Kernel 2013.7: kneel carries (always by the game passer) are
        # excluded from the carry shares, as in the 2012 baseline.
        rush["QB"] = rush.get("QB", 0) - kneels.get((index, team_id), 0)
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


# ---- kernel cohorts ------------------------------------------------------------
#
# Receipts are audited in three cohorts by kernel version:
# - legacy (kernels 2013.4/2013.5, Weeks 1-3): known ledger defects (Entries
#   35/38); no drives summary, so drive-model rows and coherence are not
#   measurable. Detection only, never grounds to rerun.
# - kernel 2013.6 (Weeks 4-5): drive-model rows and the 15 original ledger
#   classes; known field-position, label and late-game defects (Entries 40-41
#   and the 2013.7 entry). Detection only, never grounds to rerun.
# - current (kernel 2013.7 onward): every row, including the field-position
#   rows and the 17 spot and label classes.
# Tolerances are three standard errors at the observed sample, not constants:
# 3*sqrt(p(1-p)/n) for rates, 3*sqrt(lambda/n) for per-team-game counts and
# 3*sd/sqrt(n) for means, with the 2012 sd from the artifact.

import math

from . import drive_model
from .statbook import DRIVE_MODEL_FROM_KERNEL, FIELD_POSITION_FROM_KERNEL, kernel_at_least

LEGACY_LABEL = (
    "legacy kernel, known ledger defects (Entries 35/38), detection only; "
    "never grounds to rerun"
)
KERNEL_2013_6_LABEL = (
    "known field-position, label and late-game defects (Entries 40-41 and the 2013.7 entry); "
    "detection only; never grounds to rerun"
)
MIN_BIN_ATTEMPTS = 30
MIN_EVENTS = 30


def cohorts(receipts):
    """(legacy, kernel_2013_6, current): receipts before kernel 2013.6, under
    kernel 2013.6, and from kernel 2013.7."""
    legacy, kernel_2013_6, current = [], [], []
    for receipt in receipts:
        version = receipt.get("kernel_version")
        if kernel_at_least(version, FIELD_POSITION_FROM_KERNEL):
            current.append(receipt)
        elif kernel_at_least(version, DRIVE_MODEL_FROM_KERNEL):
            kernel_2013_6.append(receipt)
        else:
            legacy.append(receipt)
    return legacy, kernel_2013_6, current


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
    """Rows (metric, observed, centre, tolerance, status) for one kernel cohort
    (2013.6 or 2013.7); never mixed across cohorts."""
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


def _grader(enough):
    rows = []

    def add(metric, observed, centre, tolerance, *, events=None, graded=True):
        if observed is None or centre is None or not enough or (events is not None and events < MIN_EVENTS):
            status = "INSUFFICIENT SAMPLE"
        elif not graded or tolerance is None:
            status = "INFORMATIONAL"
        else:
            status = "WITHIN" if abs(observed - centre) <= tolerance else "OUTSIDE"
        rows.append((metric, observed, centre, tolerance if graded else None, status))
    return rows, add


def _rate(made, n, centre):
    return (made / n if n else None), (3 * math.sqrt(centre * (1 - centre) / n) if n else None)


def audit_field_position(receipts):
    """Rows (metric, observed, centre, tolerance, status) for the kernel 2013.7
    cohort: kick and punt transitions, late-game punts, real chains, sacks per
    dropback, and informational field-position shapes. Centres come from the
    2012 field-position artifact's band_centres."""
    from . import field_position as fp
    from .usage import group

    centres = fp.load()["band_centres"]
    team_games = sum(len(r.get("team_stats", {})) for r in receipts)
    rows, add = _grader(team_games >= MIN_TEAM_GAMES)
    drives = [d for r in receipts for d in _drives(r)]
    spotted = [d for d in drives if d.get("start_spot") is not None]

    # Kickoffs (every kickoff is followed by the receiving club's drive).
    kick_starts = [d for d in spotted if d.get("start_kind") in ("kickoff", "kickoff_touchback")]
    touchbacks = sum(d["start_kind"] == "kickoff_touchback" for d in kick_starts)
    made, n = centres["kickoff_touchback_share"]
    observed, tolerance = _rate(touchbacks, len(kick_starts), made / n)
    add("kickoff touchback share", observed, made / n, tolerance, events=len(kick_starts))
    returned = [d["start_spot"] for d in kick_starts if d["start_kind"] == "kickoff"]
    c = centres["kickoff_nontouchback_start"]
    add("mean start after a non-touchback kickoff (yardline_100)",
        sum(returned) / len(returned) if returned else None, c["mean"],
        3 * c["sd"] / math.sqrt(len(returned)) if returned else None, events=len(returned))

    # Realized punt net by line of scrimmage.
    punts = [d for d in spotted if d["category"] == "punt" and d.get("next_start") is not None]
    for label, c in centres["punt_net_by_los_bin"].items():
        nets = [d["end_spot"] - (100 - d["next_start"]) for d in punts if c["low"] <= d["end_spot"] <= c["high"]]
        add("mean realized punt net, LOS %s" % label, sum(nets) / len(nets) if nets else None, c["mean"],
            3 * c["sd"] / math.sqrt(len(nets)) if nets else None, events=len(nets))

    # Late trailing punts (possessions ending in Q4's last 5:00 / 2:00 or OT).
    for key, seconds, text in (("late_punt_share_last5_trail1_8", 300, "last 5:00"),
                               ("late_punt_share_le120_trail1_8", 120, "last 2:00")):
        cell = [d for d in spotted if isinstance(d.get("score_diff"), int) and -8 <= d["score_diff"] <= -1
                and (d["half"] == "OT" or (d["half"] == 2 and d["end_clock"] <= seconds))]
        made, n = centres[key]
        observed, tolerance = _rate(sum(d["category"] == "punt" for d in cell), len(cell), made / n)
        add("punt share of possessions ending in Q4's %s or OT, offense trailing 1-8" % text,
            observed, made / n, tolerance, events=len(cell))

    # Real chains: third-down attempts per punt drive.
    thirds = [d["chains"][2] for d in punts if d.get("chains")]
    c = centres["third_down_attempts_per_punt_drive"]
    add("third-down attempts per punt drive", sum(thirds) / len(thirds) if thirds else None, c["mean"],
        3 * c["sd"] / math.sqrt(len(thirds)) if thirds else None, events=len(thirds))

    # Sacks per dropback and defensive sack credit by group.
    sacks = dropbacks = 0
    credit = {}
    for receipt in receipts:
        for game in receipt.get("team_stats", {}).values():
            sacks += game.get("sacks_allowed", 0)
            for line in game.get("players", {}).values():
                dropbacks += line.get("dropbacks", 0)
                if line.get("sacks"):
                    grp = group(line.get("position"))
                    credit[grp] = credit.get(grp, 0) + line["sacks"]
    made, n = centres["sacks_per_dropback"]
    observed, tolerance = _rate(sacks, dropbacks, made / n)
    add("sacks per dropback", observed, made / n, tolerance, events=dropbacks)
    total_credit = sum(credit.values())
    for grp, share in sorted((load_usage()["values"]["sack_share"] or {}).items()):
        observed, tolerance = _rate(credit.get(grp, 0), total_credit, share)
        add("%s share of sack credits" % grp, observed, share, tolerance, events=total_credit)

    # Informational shapes.
    starts = [d["start_spot"] for d in spotted]
    c = centres["start_all"]
    add("mean drive start, all drives (2012 all-drive centre)", sum(starts) / len(starts) if starts else None,
        c["mean"], None, graded=False)
    c = centres["start_modelled_transitions"]
    add("mean drive start (2012 centre over modelled transitions)", sum(starts) / len(starts) if starts else None,
        c["mean"], None, graded=False)
    bins = fp.load()["preregistration"]["start_bins"]
    total = sum(centres["start_bin_counts"])
    for (low, high), n2012 in zip(bins, centres["start_bin_counts"]):
        mine = sum(low <= s <= high for s in starts)
        add("start-bin share %d-%d" % (low, high), mine / len(starts) if starts else None, n2012 / total, None,
            graded=False)
    coarse = {"own 1-20": (80, 99), "own 21-50": (50, 79), "opp 49-1": (1, 49)}
    for label, cell in centres["outcome_by_coarse_start"].items():
        low, high = coarse[label]
        mine = [d for d in spotted if low <= d["start_spot"] <= high]
        for category in ("touchdown", "punt"):
            made, n = cell[category]
            add("%s share, start %s" % (category, label),
                sum(d["category"] == category for d in mine) / len(mine) if mine else None, made / n, None,
                graded=False)
    for label, (points, n) in centres["points_per_drive_by_start_bin"].items():
        low, high = (int(v) for v in label.split("-"))
        mine = [d.get("points", 0) for d in spotted if low <= d["start_spot"] <= high]
        add("points per drive, start %s" % label, sum(mine) / len(mine) if mine else None, points / n, None,
            graded=False)
    qb_carries = scrambles = 0
    for receipt in receipts:
        for row in receipt.get("play_ledger", ()):
            if row.get("play_type") == "run" and row.get("carrier_group") == "QB" and not row.get("kneel"):
                qb_carries += 1
                scrambles += bool(row.get("scramble"))
    made, n = centres["scramble_share_of_qb_rushes"]
    add("QB scramble share of QB carries (label stream; nflscrapR 643/1,228)",
        scrambles / qb_carries if qb_carries else None, made / n, None, graded=False)
    attempts, conversions, games = centres["fourth_down_per_team_game"]
    fourth = [d["chains"] for d in spotted if d.get("chains")]
    add("fourth-down attempts per team game (drive chains)",
        sum(ch[4] for ch in fourth) / team_games if team_games else None, attempts / games, None, graded=False)
    add("fourth-down conversions per team game (drive chains)",
        sum(ch[5] for ch in fourth) / team_games if team_games else None, conversions / games, None, graded=False)
    kneels, games = centres["kneels_per_team_game"]
    add("kneels per team game", sum(d.get("kneels") or 0 for d in spotted) / team_games if team_games else None,
        kneels / games, None, graded=False)
    ot = [d for d in spotted if d["half"] == "OT"]
    made, n = centres["ot_punt_share"]
    add("overtime punt share", sum(d["category"] == "punt" for d in ot) / len(ot) if ot else None, made / n,
        None, graded=False)
    return team_games, rows


def coherence(receipts):
    """Zero-tolerance ledger-coherence counts over the given receipts.

    Returns (receipts checked, [(class, count, measurable receipts)]). A class
    with no measurable receipt reads 'not measurable' in the renderers."""
    from .play_detail import COHERENCE_CLASSES, check_ledger, coherence_counts, measurable_classes

    errors = []
    checked = 0
    measurable = {cls: 0 for cls in COHERENCE_CLASSES}
    for receipt in receipts:
        if not receipt.get("drives"):
            continue
        checked += 1
        for cls in measurable_classes(receipt):
            measurable[cls] += 1
        errors += check_ledger(receipt)
    counts = coherence_counts(errors)
    return checked, [(cls, counts.get(cls, 0), measurable[cls]) for cls in COHERENCE_CLASSES]
