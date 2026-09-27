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
