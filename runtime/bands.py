"""Statistical band audit: closed-game receipts versus the 2012 shapes.

The audit is a detector for engine or TeamInput defects (a missing position
group, a backup quarterback taking starter snaps, inflated play volume). It
never changes, reruns or selects a game result. An OUTSIDE row is a reason to
inspect inputs and code, not a reason to reroll canon.

Kernel 2014.6 plumbing (batch B1): band centres are keyed by cohort. A
cohort is graded against the calibration base of its own kernel version
(runtime.calibration_base.cohort_base; every kernel up to 2014.5 is the 2012
base), a cohort whose receipts map to two bases raises, and each receipt's
ledger coherence is checked with its own base's rules.
"""
from __future__ import annotations

import math

from .calibration_base import BASE_2012, cohort_base
from .usage import group

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


def expected(base=None):
    """The volume, share and top-share centres of one calibration base (the
    2012 base's when None)."""
    base = base or BASE_2012
    if not base.legacy_2012():
        return _expected_v3(base)
    usage = base.usage()["values"]
    cal = base.aggregate()
    tilt = base.top_share_centres()
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
        # Kernel 2014.4 (defect register item 19): the club's top-target and
        # top-carry (non-QB) player's share of the club's targets and carries
        # per team-game, centred on the 2012 per team-game means with their
        # SDs (library/data/2014_strength_calibration_v2.json,
        # team_game_top_shares_2012; 512 team-games).
        **{key: (tilt[key]["mean"], tilt[key]["sd"])
           for key in ("top_receiver_target_share", "top_rusher_carry_share")},
    }


def _pooled(entry):
    """events / denominator of a schema-3 [events, denominator] centre."""
    made, n = entry["pooled"]
    return made / n


def _moments(entry):
    """(n, mean, sd) of a schema-3 [n, sum, sum of squares] centre."""
    n, total, squares = entry["pooled"]
    mean = total / n
    return n, mean, math.sqrt(max(0.0, (squares - n * mean * mean) / (n - 1)))


def _expected_v3(base):
    """The volume, share and top-share centres of a schema-3 base (kernel
    2014.6, batch B5): the aggregate baseline's pooled volume pairs, the
    usage baseline's shares and its own per team-game top shares."""
    usage = base.usage()["values"]
    volume = base.aggregate()["volume"]
    tops = base.top_share_centres()
    rate = usage["assisted_tackle_play_rate"]
    return {
        "qb1_attempt_share": usage["passing"]["qb1_attempt_share"],
        "rush_share": usage["rush_share"],
        "target_share": usage["target_share"],
        "tackle_share": usage["tackle_share"],
        "assisted_credit_share": 2 * rate / (1 + rate),
        "plays_per_team_game": _pooled(volume["plays_per_team_game"]),
        "yards_per_team_game": _pooled(volume["net_yards_per_team_game"]),
        "points_per_team_game": _pooled(volume["points_per_team_game"]),
        "first_downs_per_team_game": _pooled(volume["first_downs_per_team_game"]),
        "third_down_attempts_per_team_game": _pooled(volume["third_down_attempts_per_team_game"]),
        "third_down_rate": _pooled(volume["third_down_rate"]),
        **{key: (tops[key]["mean"], tops[key]["sd"])
           for key in ("top_receiver_target_share", "top_rusher_carry_share")},
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
    top_target, top_carry = [], []
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
        targets = [line.get("targets", 0) for line in players.values()]
        if sum(targets):
            top_target.append(max(targets) / sum(targets))
        carries = [line.get("rushing_attempts", 0) for line in players.values()
                   if group(line.get("position")) != "QB"]
        if sum(carries):
            top_carry.append(max(carries) / sum(carries))
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
        # Net yards, as the 2012 centre (passing less sack yards, plus rushing:
        # 118,418 + 59,349 over 512 team-games). Receipts keep passing yards
        # gross and each passer's sack yards on his line.
        sack_yards = sum(line.get("sack_yards", 0) for line in players.values())
        totals["yards"] += game.get("passing_yards", 0) - sack_yards + game.get("rushing_yards", 0)
        totals["points"] += game.get("points", 0)
        totals["first_downs"] += game.get("first_downs", 0)
        totals["third_att"] += game.get("third_down_attempts", 0)
        totals["third_conv"] += game.get("third_down_conversions", 0)
    per = (lambda v: v / team_games) if team_games else (lambda v: None)
    return {
        "team_games": team_games,
        "qb1_attempt_share": sum(qb1) / len(qb1) if qb1 else None,
        "top_receiver_target_share": sum(top_target) / len(top_target) if top_target else None,
        "top_rusher_carry_share": sum(top_carry) / len(top_carry) if top_carry else None,
        "top_share_team_games": {"target": len(top_target), "carry": len(top_carry)},
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


def audit(receipts, cohort=None):
    """Return (team_games, rows); each row is (metric, observed, band, tolerance, status).
    Centres are the cohort's own base's (runtime.calibration_base.cohort_base)."""
    base = cohort_base(receipts, cohort)
    obs = observe(receipts)
    exp = expected(base)
    enough = obs["team_games"] >= MIN_TEAM_GAMES
    rows = []

    def add(metric, observed, band, tolerance):
        if observed is None or not enough:
            status = "INSUFFICIENT SAMPLE"
        else:
            status = "WITHIN" if abs(observed - band) <= tolerance else "OUTSIDE"
        rows.append((metric, observed, band, tolerance, status))

    add("QB1 share of team pass attempts", obs["qb1_attempt_share"], exp["qb1_attempt_share"], SHARE_TOLERANCE)
    # Item 19 rows: per team-game top shares against the 2012 per team-game
    # centres; tolerance three 2012 SDs over the root of the team-game count.
    for key, label, n in (("top_receiver_target_share", "top receiver share of team targets (team-game)",
                           obs["top_share_team_games"]["target"]),
                          ("top_rusher_carry_share", "top rusher share of non-QB carries (team-game)",
                           obs["top_share_team_games"]["carry"])):
        centre, sd_2012 = exp[key]
        add(label, obs[key], centre, 3 * sd_2012 / math.sqrt(n) if n else None)
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
# - kernel 2013.6 (Weeks 4-8): drive-model rows and the 15 original ledger
#   classes; known field-position, label and late-game defects (Entries 40-45
#   and the 2013.7 adoption entry). Detection only, never grounds to rerun.
# - current (kernel 2013.7 onward, from the first slate after Week 8): every
#   row, including the field-position rows and the 17 spot and label classes.
#   The current cohort is split again by exact kernel version
#   (current_cohorts): kernel 2013.7 receipts (Weeks 9-10, including the
#   Week 10 overtime defect) stay their own cohort; kernel 2013.8 (the 2013
#   overtime correction) starts a new one. Regulation is unchanged, so the
#   2013.7 known detections carry over to 2013.8 by the same registry.
# Tolerances are three standard errors at the observed sample, not constants:
# 3*sqrt(p(1-p)/n) for rates, 3*sqrt(lambda/n) for per-team-game counts and
# 3*sd/sqrt(n) for means, with the 2012 sd from the artifact.

from .statbook import DRIVE_MODEL_FROM_KERNEL, FIELD_POSITION_FROM_KERNEL, kernel_at_least

LEGACY_LABEL = (
    "legacy kernel, known snap-record defects (see the "
    "[September 8, 2013 Kansas City game report]"
    "(../../2013/regular_season/week_01_kansas_city_at_jacksonville/output.md) and "
    "[September 22, 2013 Seattle game report]"
    "(../../2013/regular_season/week_03_jacksonville_at_seattle/output.md)), detection only; "
    "never grounds to rerun"
)
KERNEL_2013_6_LABEL = (
    "known field-position, label and late-game defects (see the "
    "[documented 2013.6 limitations and 2013.7 adoption](../../../runtime/README.md)); "
    "detection only; never grounds to rerun"
)
MIN_BIN_ATTEMPTS = 30

# Known detections: graded drive-model rows whose documented, diagnosed design
# cause is accepted rather than tuned. The row stays graded and its status is
# never rewritten; the audit labels it, and the test sample tolerates it up to
# KNOWN_DETECTION_BOUND times its tolerance (any other graded row OUTSIDE
# fails). No centre, tolerance, coefficient or pool is changed by listing one.
# Both causes are the first-half half-final redirect: a drawn interior drive
# that would overrun the window is replaced by a half-final drive.
KNOWN_DETECTION_BOUND = 2
_PUNT_BIAS = (
    "the half-final redirect skews surviving interior drives "
    "short and punt-heavy (runtime/README.md, kernel 2013.6 limitations)"
)
_H1_FINAL = (
    "adopted as documented by the user's decision of "
    "September 27, 2026: the first-half half-final redirect starts first-half "
    "final possessions early, field-goal-heavy and clock-light "
    "(library/2012_field_position_model_calibration.md, acceptance)"
)
KNOWN_DETECTIONS = {
    "2013.6": {
        "punts per team game (drive-ending)": _PUNT_BIAS,
    },
    "2013.7": {
        "punts per team game (drive-ending)": _PUNT_BIAS,
        "FGM per team game": _H1_FINAL,
        "drive share: clock": _H1_FINAL,
        "clock-expired drives per team game": _H1_FINAL,
    },
}
# Kernel 2013.8 changes overtime only; the first-half redirect and its
# detections are unchanged.
KNOWN_DETECTIONS["2013.8"] = dict(KNOWN_DETECTIONS["2013.7"])
# Kernel 2013.9 changes only where a spike sits in a drive's snap order.
KNOWN_DETECTIONS["2013.9"] = dict(KNOWN_DETECTIONS["2013.8"])
# Kernel 2013.10 changes only which call label a snap carries.
KNOWN_DETECTIONS["2013.10"] = dict(KNOWN_DETECTIONS["2013.9"])
# Kernel 2013.11 changes only the home term at a neutral venue.
KNOWN_DETECTIONS["2013.11"] = dict(KNOWN_DETECTIONS["2013.10"])
# Kernel 2014.1 (timeouts, kneel zones, end-of-half fit fallback, goal to go): the
# registry carries over until its own acceptance run says otherwise.
KNOWN_DETECTIONS["2014.1"] = dict(KNOWN_DETECTIONS["2013.11"])
# Kernel 2014.2 (late-game recalibration) carries the registry over and adds
# two rows, registered by Claude on September 28, 2026 while carrying out the
# user's recalibration request (reversible; runtime/README.md, kernel 2014.2).
_FGA_2014_2 = (
    "field-goal attempts rise with FGM from the first-half half-final redirect; "
    "kernel 2014.2 also stops masking late field goals, whose expected share by "
    "need now tracks 2012 (runtime/README.md, kernel 2014.2 acceptance)"
)
_LATE_PUNT_2014_2 = (
    "about 70 events per 250 games; the 2014.2 expected late mix by need tracks "
    "2012 (trailing 4-8 punts 0.173 against 0.179), a 750-game fresh sample reads "
    "0.087 inside its tolerance, and the rest is the timing mix of possessions "
    "that end in the last 5:00 (runtime/README.md, kernel 2014.2 acceptance)"
)
KNOWN_DETECTIONS["2014.2"] = dict(KNOWN_DETECTIONS["2014.1"])
KNOWN_DETECTIONS["2014.2"]["FGA per team game"] = _FGA_2014_2
KNOWN_DETECTIONS["2014.2"]["punt share of possessions ending in Q4's last 5:00 or OT, offense trailing 1-8"] = _LATE_PUNT_2014_2
# Kernel 2014.3 changes credit only (runtime/README.md, kernel 2014.3): every
# result is identical to 2014.2, so the registry carries over unchanged.
KNOWN_DETECTIONS["2014.3"] = dict(KNOWN_DETECTIONS["2014.2"])
# Kernel 2014.4 (candidate; the version flips only at the user's release
# decision) carries the registry over: every known-detection row read WITHIN
# on its 250-game acceptance sample (runtime/README.md, kernel 2014.4
# candidate acceptance) and none was added or removed.
KNOWN_DETECTIONS["2014.4"] = dict(KNOWN_DETECTIONS["2014.3"])
# Kernel 2014.5 changes call labels only (runtime/README.md, kernel 2014.5):
# every result is identical to 2014.4, so the registry carries over unchanged.
KNOWN_DETECTIONS["2014.5"] = dict(KNOWN_DETECTIONS["2014.4"])
# Kernel 2014.6 (in build; the version flips only at its release): the
# 2014.5 registry is carried over with its metric strings unchanged. Each row
# is re-diagnosed against its new 2010-2014 centre at the batch that moves
# it; a row that is no longer OUTSIDE leaves the registry there, and a new
# OUTSIDE row is never registered here without the user (U8).
KNOWN_DETECTIONS["2014.6"] = dict(KNOWN_DETECTIONS["2014.5"])


def known_detections(cohort):
    """{metric: note} for a kernel cohort ("2013.6" through "2014.5", and the
    2014.6 cohort being built); empty otherwise."""
    return dict(KNOWN_DETECTIONS.get(cohort, {}))


def known_status(row, cohort):
    """A row's rendered status: unchanged unless the metric is a known
    detection of that cohort, which is labelled and, when OUTSIDE, checked
    against KNOWN_DETECTION_BOUND times its tolerance."""
    metric, observed, centre, tolerance, status = row
    if metric not in KNOWN_DETECTIONS.get(cohort, {}) or status not in ("WITHIN", "OUTSIDE"):
        return status
    if status == "WITHIN":
        return "WITHIN (known detection)"
    if abs(observed - centre) <= KNOWN_DETECTION_BOUND * tolerance:
        return "OUTSIDE (known detection, within %dx tolerance)" % KNOWN_DETECTION_BOUND
    return "OUTSIDE (known detection, beyond %dx tolerance: investigate)" % KNOWN_DETECTION_BOUND
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


def current_cohorts(current):
    """[(kernel version, receipts)] for the current cohort, split by exact
    kernel version in version order; audits never mix two versions."""
    by_version = {}
    for receipt in current:
        by_version.setdefault(str(receipt.get("kernel_version")), []).append(receipt)
    def key(version):
        try:
            return tuple(int(v) for v in version.split("."))
        except ValueError:
            return (float("inf"),)
    return [(version, by_version[version]) for version in sorted(by_version, key=key)]


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


def _drive_model_expected_v3(base):
    """Schema-3 drive-model centres (kernel 2014.6, batch B5): the
    field-position artifact's band centres (unweighted, equal weight per
    event, the 2010-2011 overtime drives excluded as the builder states).
    The kickoff and kick-return per team-game rows have no schema-3 centre
    and are not graded for this cohort."""
    centres = base.field_position().load()["band_centres"]
    edges = base.drive_model().load()["rates"]["fg_bin_edges"]
    share = {}
    for label, cats in SHARE_GROUPS:
        made = sum(centres["drive_share:" + c]["pooled"][0] for c in cats)
        share[label] = made / centres["drive_share:" + cats[0]]["pooled"][1]
    return {
        "fg_accuracy": _pooled(centres["fg_accuracy"]),
        "fg_by_distance": {label: _pooled(centres["fg_accuracy:" + label]) for label, _, _ in edges},
        "xp_accuracy": _pooled(centres["extra_point"]),
        "fga_per_team_game": _pooled(centres["fga_per_team_game"]),
        "fgm_per_team_game": _pooled(centres["fgm_per_team_game"]),
        "drives_per_team_game": _pooled(centres["drives_per_team_game"]),
        "punts_per_team_game": _pooled(centres["drive_ending_punts_per_team_game"]),
        "drive_share": share,
        "clock_expired_drives_per_team_game": _pooled(centres["clock_expired_drives_per_team_game"]),
        "offensive_drive_turnovers_per_team_game": _pooled(centres["offensive_drive_turnovers_per_team_game"]),
        "interception_share_of_turnovers": _pooled(centres["interception_share_of_turnovers"]),
        "kickoffs_per_team_game": None,
        "kick_returns_per_team_game": None,
    }


def drive_model_expected(base=None):
    base = base or BASE_2012
    if not base.legacy_2012():
        return _drive_model_expected_v3(base)
    data = base.drive_model().load()
    cal = base.aggregate()
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


def drive_model_observe(receipts, base=None):
    team_games = 0
    sums = {k: 0 for k in ("field_goal_attempts", "field_goals", "extra_point_attempts",
                           "extra_points_made", "drives", "punts", "clock_expired_drives",
                           "turnovers", "kickoffs", "kick_returns")}
    categories = {}
    bins = {}
    interceptions = 0
    edges = (base or BASE_2012).drive_model().load()["rates"]["fg_bin_edges"]
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


def audit_drive_model(receipts, cohort=None):
    """Rows (metric, observed, centre, tolerance, status) for one kernel cohort
    (2013.6 or 2013.7); never mixed across cohorts, and graded against the
    cohort's own base."""
    base = cohort_base(receipts, cohort)
    obs = drive_model_observe(receipts, base)
    exp = drive_model_expected(base)
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
    if exp["kickoffs_per_team_game"] is not None:
        count_row("kickoffs per team game (informational; centre includes kicks not modelled: "
                  "after non-offensive TDs, onside, re-kicks, after half-final scores)", sums["kickoffs"],
                  exp["kickoffs_per_team_game"], graded=False)
    if exp["kick_returns_per_team_game"] is not None:
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


def audit_field_position(receipts, cohort=None):
    """Rows (metric, observed, centre, tolerance, status) for the kernel 2013.7
    cohort: kick and punt transitions, late-game punts, real chains, sacks per
    dropback, and informational field-position shapes. Centres come from the
    cohort base's field-position artifact's band_centres (2012 through
    kernel 2014.5)."""
    from .usage import group

    base = cohort_base(receipts, cohort)
    if not base.legacy_2012():
        return _audit_field_position_v3(receipts, base)
    fp = base.field_position()
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

    # Kernel 2014.4 phase 2: return averages from the player lines (kick
    # returns are every non-touchback kickoff, punt returns the returned
    # punts), against the 2012 pools' own records.
    kr = pr = kr_yards = pr_yards = 0
    for receipt in receipts:
        for game in receipt.get("team_stats", {}).values():
            for line in game.get("players", {}).values():
                kr += line.get("kick_returns", 0) or 0
                kr_yards += line.get("kick_return_yards", 0) or 0
                pr += line.get("punt_returns", 0) or 0
                pr_yards += line.get("punt_return_yards", 0) or 0
    for label, c, made, n in (("mean kickoff return yards (non-touchback kickoffs)", return_centres(base)["kickoff"], kr_yards, kr),
                              ("mean punt return yards (returned punts)", return_centres(base)["punt"], pr_yards, pr)):
        add(label, made / n if n else None, c["mean"], 3 * c["sd"] / math.sqrt(n) if n else None, events=n)

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
    for grp, share in sorted((base.usage()["values"]["sack_share"] or {}).items()):
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


def _label_bounds(label):
    """(low, high) yardline_100 of a schema-3 punt-net label ('own 1-10',
    'opp 49-40') or a plain 'low-high' start-bin label."""
    side, _, span = label.rpartition(" ")
    a, b = (int(v) for v in span.split("-"))
    if side == "own":
        return 100 - max(a, b), 100 - min(a, b)
    return min(a, b), max(a, b)


def _first_half(d):
    return d.get("half") == 1


def _h1_window(d):
    """Seconds left in the first half at a first-half possession's start."""
    return d["start_clock"] - 1800


def _kick_clock(d):
    """The game clock at a drive's terminal snap (its own end): end clock
    plus the clock-expiry leg."""
    return d["end_clock"] + (d.get("expiry_seconds") or 0)


def _audit_field_position_v3(receipts, base):
    """Schema-3 field-position rows (kernel 2014.6, batch B5): the graded
    and informational rows of the pre-build specification (section 5, B5),
    each centre an artifact value (band_centres, unweighted, equal weight per
    event; the drawn pools for the return means), tolerances by the
    module's formulas. New rows exist only for this cohort."""
    from .usage import group

    fp = base.field_position()
    centres = fp.load()["band_centres"]
    team_games = sum(len(r.get("team_stats", {})) for r in receipts)
    rows, add = _grader(team_games >= MIN_TEAM_GAMES)
    drives = [d for r in receipts for d in _drives(r)]
    spotted = [d for d in drives if d.get("start_spot") is not None]

    def rate_row(metric, made, n, centre, *, graded=True):
        observed, tolerance = _rate(made, n, centre)
        add(metric, observed, centre, tolerance, events=n, graded=graded)

    def mean_row(metric, values, entry, *, graded=True):
        _, mean, sd = _moments(entry)
        add(metric, sum(values) / len(values) if values else None, mean,
            3 * sd / math.sqrt(len(values)) if values else None, events=len(values), graded=graded)

    def count_row(metric, total, n, centre, *, graded=True, dispersion=1.0):
        observed = total / n if n else None
        tolerance = 3 * math.sqrt(dispersion * centre / n) if n and centre else None
        add(metric, observed, centre, tolerance, graded=graded)

    # Kickoffs: every non-onside kickoff is followed by the receiving club's drive.
    kick_starts = [d for d in spotted if d.get("start_kind") in ("kickoff", "kickoff_touchback")]
    rate_row("kickoff touchback share", sum(d["start_kind"] == "kickoff_touchback" for d in kick_starts),
             len(kick_starts), _pooled(centres["kickoff_touchback_share"]))
    mean_row("mean start after a non-touchback kickoff (yardline_100)",
             [d["start_spot"] for d in kick_starts if d["start_kind"] == "kickoff"],
             centres["kickoff_nontouchback_start"])
    # Realized punt net by line of scrimmage.
    punts = [d for d in spotted if d["category"] == "punt" and d.get("next_start") is not None]
    for key in sorted(k for k in centres if k.startswith("punt_net:")):
        label = key.split(":", 1)[1]
        low, high = _label_bounds(label)
        mean_row("mean realized punt net, LOS %s" % label,
                 [d["end_spot"] - (100 - d["next_start"]) for d in punts if low <= d["end_spot"] <= high],
                 centres[key])
    # Return means from the player lines against the drawn pools' records.
    kr = pr = kr_yards = pr_yards = 0
    for receipt in receipts:
        for game in receipt.get("team_stats", {}).values():
            for line in game.get("players", {}).values():
                kr += line.get("kick_returns", 0) or 0
                kr_yards += line.get("kick_return_yards", 0) or 0
                pr += line.get("punt_returns", 0) or 0
                pr_yards += line.get("punt_return_yards", 0) or 0
    for label, c, made, n in (("mean kickoff return yards (non-touchback kickoffs)", return_centres(base)["kickoff"],
                               kr_yards, kr),
                              ("mean punt return yards (returned punts)", return_centres(base)["punt"], pr_yards, pr)):
        add(label, made / n if n else None, c["mean"], 3 * c["sd"] / math.sqrt(n) if n else None, events=n)
    # Late trailing punts.
    for key, seconds, text in (("late_punt_share_last5_trail1_8", 300, "last 5:00"),
                               ("late_punt_share_le120_trail1_8", 120, "last 2:00")):
        cell = [d for d in spotted if isinstance(d.get("score_diff"), int) and -8 <= d["score_diff"] <= -1
                and (d["half"] == "OT" or (d["half"] == 2 and d["end_clock"] <= seconds))]
        rate_row("punt share of possessions ending in Q4's %s or OT, offense trailing 1-8" % text,
                 sum(d["category"] == "punt" for d in cell), len(cell), _pooled(centres[key]))
    mean_row("third-down attempts per punt drive", [d["chains"][2] for d in punts if d.get("chains")],
             centres["third_down_attempts_per_punt_drive"])
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
    rate_row("sacks per dropback", sacks, dropbacks, _pooled(centres["sacks_per_dropback"]))
    total_credit = sum(credit.values())
    for grp, share in sorted((base.usage()["values"]["sack_share"] or {}).items()):
        rate_row("%s share of sack credits" % grp, credit.get(grp, 0), total_credit, share)

    # End of half and late game (R17, R7, R10, R14, W5b).
    h1 = [d for d in spotted if _first_half(d)]
    finals = [d for d in h1 if d.get("half_final")]
    rate_row("first-half final possessions: field-goal-attempt share",
             sum(d["category"] == "field_goal_attempt" for d in finals), len(finals),
             _pooled(centres["h1_final_fg_share"]))
    rate_row("first-half final possessions: clock share",
             sum(str(d["category"]).startswith("end_of_") for d in finals), len(finals),
             _pooled(centres["h1_final_clock_share"]))
    for low, high in ((61, 120), (121, 240)):
        starts = [d for d in h1 if low <= _h1_window(d) <= high]
        rate_row("P(final | first-half possession starting with %d-%d s left)" % (low, high),
                 sum(bool(d.get("half_final")) for d in starts), len(starts),
                 _pooled(centres["h1_p_final:%d-%d" % (low, high)]))
    for key in sorted((k for k in centres if k.startswith("h1_final_start_window:")),
                      key=lambda k: int(k.split(":")[1].split("-")[0])):
        low, high = (int(v) for v in key.split(":")[1].split("-"))
        rate_row("first-half final possessions starting with %d-%d s left (share)" % (low, high),
                 sum(low <= _h1_window(d) <= high for d in finals), len(finals), _pooled(centres[key]))
    expired = [d for d in finals if str(d["category"]).startswith("end_of_")]
    rate_row("clock-expired first halves ending inside the opponent 30", sum(d["end_spot"] <= 30 for d in expired),
             len(expired), _pooled(centres["h1_clock_expired_inside_30"]))
    for tag, low, high, graded in (("trail12p", -999, -12, True), ("trail9_11", -11, -9, False)):
        late_fg = sum(1 for d in spotted if d["half"] == 2 and d["category"] == "field_goal_attempt"
                      and _kick_clock(d) <= 120 and isinstance(d.get("score_diff"), int)
                      and low <= d["score_diff"] <= high)
        text = "12 or more" if tag == "trail12p" else "9-11"
        count_row("field-goal attempts inside 2:00 of Q4, offense trailing by %s (per team-game)" % text, late_fg,
                  team_games, _pooled(centres["q4_inside_2_min_fga_per_team_game:" + tag]), graded=graded)
    h2_open = [d for d in spotted if d["half"] == 2 and d["start_clock"] > 600 and d.get("timeouts")]
    count_row("defensive timeouts per second-half possession starting over 10:00",
              sum(d["timeouts"][3] for d in h2_open), len(h2_open),
              _pooled(centres["def_timeouts_per_h2_possession_over_600"]))
    # Timeouts per team-game, with the dispersion of the observed team-game counts.
    per_team_game = []
    for receipt in receipts:
        used = {team: 0 for team in receipt.get("team_stats", {})}
        for d in _drives(receipt):
            if d.get("timeouts"):
                used[d["team"]] = used.get(d["team"], 0) + d["timeouts"][2]
                other = next((t for t in used if t != d["team"]), None)
                if other is not None:
                    used[other] += d["timeouts"][3]
        per_team_game += list(used.values())
    mean = sum(per_team_game) / len(per_team_game) if per_team_game else 0
    dispersion = (sum((x - mean) ** 2 for x in per_team_game) / (len(per_team_game) - 1) / mean
                  if len(per_team_game) > 1 and mean else 1.0)
    count_row("timeouts per team-game", sum(per_team_game), len(per_team_game),
              _pooled(centres["timeouts_per_team_game"]), dispersion=dispersion)
    # Zero-tolerance rows (R14): overtime spikes outside the spike window and
    # trailing overtime punts. The spike row reads the possession field the
    # kernel records (results; a receipt's drives summary does not carry it).
    window = fp.SPIKE_WINDOW
    overtime = [d for d in spotted if d["half"] == "OT"]
    with_field = [d for r in receipts for d in r.get("possessions", ()) if d.get("half") == "OT"
                  and "category" in d]
    spikes = sum(1 for d in with_field if (d.get("last_spike_seconds_left") or 0) > window)
    rows.append(("overtime spikes with more than %d s left (zero tolerance)" % window,
                 spikes if with_field else None, 0, 0,
                 ("OUTSIDE" if spikes else "WITHIN") if with_field else "INSUFFICIENT SAMPLE"))
    trailing = [d for d in overtime if isinstance(d.get("score_diff"), int) and d["score_diff"] < 0]
    punts_ot = sum(d["category"] == "punt" for d in trailing)
    rows.append(("trailing overtime punts (zero tolerance)", punts_ot, 0, 0,
                 "OUTSIDE" if punts_ot else "WITHIN"))

    # Informational shapes.
    starts = [d["start_spot"] for d in spotted]
    _, mean_start, _ = _moments(centres["start_all"])
    add("mean drive start, all drives (all-drive centre)", sum(starts) / len(starts) if starts else None,
        mean_start, None, graded=False)
    bins = fp.load()["preregistration"]["start_bins"]
    counts = [sum(season[i] for season in centres["start_bin_counts"].values()) for i in range(len(bins))]
    for (low, high), n_bin in zip(bins, counts):
        mine = sum(low <= s <= high for s in starts)
        add("start-bin share %d-%d" % (low, high), mine / len(starts) if starts else None, n_bin / sum(counts),
            None, graded=False)
    for label, entry in centres["points_per_drive_by_start_bin"].items():
        low, high = (int(v) for v in label.split("-"))
        mine = [d.get("points", 0) for d in spotted if low <= d["start_spot"] <= high]
        add("points per drive, start %s" % label, sum(mine) / len(mine) if mine else None, _pooled(entry), None,
            graded=False)
    qb_carries = scrambles = 0
    for receipt in receipts:
        for row in receipt.get("play_ledger", ()):
            if row.get("play_type") == "run" and row.get("carrier_group") == "QB" and not row.get("kneel"):
                qb_carries += 1
                scrambles += bool(row.get("scramble"))
    add("QB scramble share of QB carries (label stream)", scrambles / qb_carries if qb_carries else None,
        _pooled(centres["scramble_share_of_qb_rushes"]), None, graded=False)
    fourth = [d["chains"] for d in spotted if d.get("chains")]
    attempts, games = centres["fourth_down_per_team_game"]["pooled"]
    conversions = centres["fourth_down_conversion"]["pooled"][0]
    add("fourth-down attempts per team game (drive chains)",
        sum(ch[4] for ch in fourth) / team_games if team_games else None, attempts / games, None, graded=False)
    add("fourth-down conversions per team game (drive chains)",
        sum(ch[5] for ch in fourth) / team_games if team_games else None, conversions / games, None, graded=False)
    add("kneels per team game", sum(d.get("kneels") or 0 for d in spotted) / team_games if team_games else None,
        _pooled(centres["kneels_per_team_game"]), None, graded=False)
    return team_games, rows


INJURY_ROWS = (
    ("game_onsets_per_team_game", "injury onsets per team-game"),
    ("rest_of_game_removals_per_team_game", "rest-of-game removals per team-game"),
    ("head_neck_share_game_onsets", "head/neck share of onsets"),
    ("head_neck_game_onsets_per_team_game", "head/neck onsets per team-game"),
    ("lower_extremity_share_game_onsets", "lower-extremity share of onsets"),
    ("time_loss_share_(short+)", "time-loss share of onsets (short or longer)"),
    ("long_term_share", "long-term share of onsets"),
)


def audit_injuries(receipts, cohort=None):
    """Injury rows by the kernel 2014.4 method (the calibration's acceptance
    bands, WITHIN when low <= observed <= high), for a cohort graded on a
    schema-3 base (kernel 2014.6 onward; batch B5); a 2012-base cohort has no
    injury rows (its bands were a candidate acceptance, never an audit)."""
    from .injury_model import acceptance_bands

    base = cohort_base(receipts, cohort)
    if base.legacy_2012():
        return 0, []
    bands = acceptance_bands(base.raw("injury"))
    team_games = sum(len(r.get("team_stats", {})) for r in receipts)
    injuries = [i for r in receipts for i in r.get("injuries", ())]
    n = len(injuries)
    enough = team_games >= MIN_TEAM_GAMES

    def share(pred):
        return sum(1 for i in injuries if pred(i)) / n if n else None
    observed = {
        "game_onsets_per_team_game": n / team_games if team_games else None,
        "rest_of_game_removals_per_team_game":
            sum(bool(i.get("removed")) for i in injuries) / team_games if team_games else None,
        "head_neck_share_game_onsets": share(lambda i: i.get("injury_class") == "head_neck"),
        "head_neck_game_onsets_per_team_game":
            sum(i.get("injury_class") == "head_neck" for i in injuries) / team_games if team_games else None,
        "lower_extremity_share_game_onsets": share(lambda i: i.get("injury_class") == "lower_extremity"),
        "time_loss_share_(short+)": share(lambda i: i.get("severity") != "minor"),
        "long_term_share": share(lambda i: i.get("severity") == "long_term"),
    }
    rows = []
    for key, label in INJURY_ROWS:
        low, high = bands[key]
        value = observed[key]
        if value is None or not enough:
            status = "INSUFFICIENT SAMPLE"
        else:
            status = "WITHIN" if low <= value <= high else "OUTSIDE"
        rows.append((label, value, (low + high) / 2, (high - low) / 2, status))
    return team_games, rows


def return_centres(base=None):
    """Kernel 2014.4 phase 2: the base's kickoff pool's non-touchback records
    and the punt pool's returned records (return yards mean and SD);
    memoised per base (the 2012 base when None). Schema 3 (batch B5): the
    records the kernel draws (receiving-club records; the retained
    kicking-team recoveries, onside kicks and return touchdowns are not in
    them), so the centre is the drawn pool's own, as for 2012."""
    base = base or BASE_2012

    def build():
        fp = base.field_position()
        data, KICK, PUNT = fp.load(), fp.KICK, fp.PUNT
        kick_pool = getattr(fp, "_kick_pools", {}).get("kickoff_pool", data["kickoff_pool"])
        punt_pool = getattr(fp, "_punt_pool", data["punt_pool"])
        kicks = [r[KICK["return_yards"]] for r in kick_pool if not r[KICK["touchback"]]]
        punts = [r[PUNT["return_yards"]] for r in punt_pool if r[PUNT["outcome"]] == "returned"]

        def moments(xs):
            m = sum(xs) / len(xs)
            return {"n": len(xs), "mean": m, "sd": math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))}
        return {"kickoff": moments(kicks), "punt": moments(punts)}
    return base.memo(("return_centres",), build)


def coherence(receipts, cohort=None):
    """Zero-tolerance ledger-coherence counts over the given receipts.

    Returns (receipts checked, [(class, count, measurable receipts)]) for the
    classes the cohort's table lists (runtime.play_detail.classes_for_cohort).
    A class with no measurable receipt reads 'not measurable' in the
    renderers. Each receipt is checked with its own base's rules; a cohort
    mixing two bases raises."""
    from .play_detail import check_ledger, classes_for_cohort, coherence_counts, measurable_classes

    cohort_base(receipts, cohort)
    listed = classes_for_cohort(cohort)
    errors = []
    checked = 0
    measurable = {cls: 0 for cls in listed}
    for receipt in receipts:
        if not receipt.get("drives"):
            continue
        checked += 1
        for cls in measurable_classes(receipt):
            if cls in measurable:
                measurable[cls] += 1
        errors += check_ledger(receipt)
    counts = coherence_counts(errors)
    return checked, [(cls, counts.get(cls, 0), measurable[cls]) for cls in listed]
