"""Depth-chart-aware player attribution shapes (kernels 2013.4-2013.7).

The possession kernel decides team outcomes. This module only decides which
available player receives an already-resolved carry, target, tackle or
defensive credit. Group shares and usage-rank shapes come from the sourced
2012 play-by-play baseline; the order inside a group comes from the club's own
depth chart, roles and rotation status. Nothing here rates a player, changes a
depth chart or imposes a Jacksonville touch quota.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data/2012_nfl_position_usage_baseline.json"

GROUP_OF = {
    "QB": "QB",
    "RB": "RB", "HB": "RB", "TB": "RB",
    "FB": "FB",
    "WR": "WR",
    "TE": "TE",
    "OT": "OL", "OG": "OL", "C": "OL", "T": "OL", "G": "OL", "OL": "OL",
    "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL",
    "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
    "CB": "DB", "S": "DB", "SS": "DB", "FS": "DB", "DB": "DB", "SAF": "DB",
    "K": "K", "PK": "K", "P": "P", "LS": "LS",
}

STATUS_ORDER = {"core": 0, "competition": 1, "bubble": 2, "reduced": 3}

# A legal NFL game-day unit: the minimum available players per group that the
# production runner requires before any event is closed.
MINIMUM_GAME_DAY = {
    "QB": 1, "RB": 1, "WR": 3, "TE": 1, "OL": 5,
    "DL": 3, "LB": 2, "DB": 4, "K": 1, "P": 1,
}

# Groups without their own sourced usage-rank shape borrow the closest
# sourced shape. This is a documented mapping, not an extra measurement.
SHAPE_FOR = {
    ("rush", "RB"): "rush_RB",
    ("rush", "FB"): "rush_RB",
    ("rush", "WR"): "target_WR",
    ("rush", "TE"): "target_TE",
    ("target", "WR"): "target_WR",
    ("target", "TE"): "target_TE",
    ("target", "RB"): "target_RB",
    ("target", "FB"): "target_RB",
    ("defense", "DL"): "tackle_DL",
    ("defense", "LB"): "tackle_LB",
    ("defense", "DB"): "tackle_DB",
}


def group(position):
    return GROUP_OF.get(str(position or "").upper())


@lru_cache(maxsize=1)
def load():
    """Parsed baseline; treat as read-only."""
    return json.loads(DATA.read_text())


def validate(data=None):
    data = data or load()
    errors = []
    values = data.get("values", {})
    for name in ("rush_share", "target_share", "tackle_share", "tfl_share",
                 "sack_share", "interception_share", "pass_defensed_share"):
        shares = values.get(name) or {}
        if not shares or any(not 0 <= v <= 1 for v in shares.values()):
            errors.append(f"{name} missing or outside [0, 1]")
        elif not 0.95 <= sum(shares.values()) <= 1.0001:
            errors.append(f"{name} does not cover the position groups")
    for name, shape in values.get("rank_shares", {}).items():
        if not shape or any(v < 0 for v in shape) or sum(shape) > 1.0001:
            errors.append(f"rank shape {name} invalid")
    for key in ("assisted_tackle_play_rate", "negative_run_rate"):
        if not 0 < values.get(key, -1) < 1:
            errors.append(f"{key} invalid")
    losses = values.get("negative_run_loss_distribution", {})
    if abs(sum(losses.values()) - 1) > 0.001:
        errors.append("negative-run loss distribution does not sum to one")
    model = data.get("drive_model", {})
    for outcome in ("touchdown", "field_goal", "punt", "turnover", "other"):
        row = model.get(outcome, {})
        if row.get("plays_mean", 0) <= 0 or row.get("seconds_per_play", 0) <= 0:
            errors.append(f"drive model missing {outcome}")
    return errors


def drive_scales(calibration, data=None):
    """Return (plays_scale, clock_scale) reconciling pbp drive shapes to the
    verified team-game totals in the aggregate baseline.

    Kernel 2013.5 only. Kernel 2013.6 takes plays and clock unscaled from the
    resampled 2012 drive tuples (runtime/drive_model.py); this is kept so the
    2013.5 draws remain reproducible from history."""
    data = data or load()
    model = data["drive_model"]
    outcomes = calibration["model"]["drive_outcomes"]
    drives = calibration["model"]["drives_per_team_game"]
    plays = calibration["model"]["plays_per_team_game"]
    expected_plays = sum(p * model[o]["plays_mean"] for o, p in outcomes.items())
    plays_scale = (plays / drives) / expected_plays
    expected_seconds = sum(
        p * model[o]["plays_mean"] * plays_scale * model[o]["seconds_per_play"]
        for o, p in outcomes.items()
    )
    clock_scale = (1800.0 / drives) / expected_seconds
    return plays_scale, clock_scale


def depth_order(players, grp, role=""):
    """Order one position group by the club's own depth inputs.

    Explicit depth first, then a matching role/responsibility, then rotation
    status, then roster order. Stable and deterministic.
    """
    members = [(i, p) for i, p in enumerate(players) if group(p.position) == grp]

    def key(item):
        index, player = item
        depth = getattr(player, "depth", None)
        has_role = bool(role) and (role in player.roles or role in player.responsibilities)
        return (
            depth if isinstance(depth, int) else 99,
            0 if has_role else 1,
            STATUS_ORDER.get(player.rotation_status, 1),
            index,
        )

    return [player for _, player in sorted(members, key=key)]


def rank_weights(shape, count):
    shape = list(shape or ())
    weights = shape[:count]
    if count > len(weights):
        floor = min((v for v in shape if v > 0), default=1.0) / 4
        weights += [floor] * (count - len(weights))
    return [max(w, 1e-4) for w in weights]


def game_passer(players):
    ordered = depth_order(players, "QB", "passer")
    return ordered[0] if ordered else None


def specialist(players, grp, role):
    ordered = depth_order(players, grp, role)
    return ordered[0] if ordered else None


def pick(rng, players, shares, kind, *, role="", exclude=(), only=None):
    """Pick one player: group by sourced share, then by usage rank on the
    club depth order. Falls back to every candidate only when no sourced
    group is present (legacy synthetic inputs)."""
    rank_shapes = load()["values"]["rank_shares"]
    blocked = {getattr(p, "player_id", p) for p in exclude}
    pool = [p for p in players if p.player_id not in blocked]
    if only is not None:
        pool = [p for p in pool if only(p)]
    groups = []
    for grp, share in shares.items():
        ordered = depth_order(pool, grp, role)
        if ordered and share > 0:
            groups.append((grp, share, ordered))
    if not groups:
        if not pool:
            raise ValueError("available participants required")
        return rng.choice(pool)
    grp, _, ordered = rng.choices(groups, weights=[g[1] for g in groups], k=1)[0]
    shape = rank_shapes.get(SHAPE_FOR.get((kind, grp), ""), [1.0])
    return rng.choices(ordered, weights=rank_weights(shape, len(ordered)), k=1)[0]


def draw_loss(rng):
    dist = load()["values"]["negative_run_loss_distribution"]
    keys = sorted(dist, key=lambda k: int(k.rstrip("+")))
    chosen = rng.choices(keys, weights=[dist[k] for k in keys], k=1)[0]
    # "6+" is recorded at its lower bound; the pooled tail is not expanded.
    return int(chosen.rstrip("+"))


# A club without an available kicker has its punter kick, and without an
# available punter its kicker punts, as NFL clubs do in an emergency.
EMERGENCY_SPECIALIST = {"K": "P", "P": "K"}


def lineup_errors(players):
    counts = {}
    for p in players:
        grp = group(p.position)
        if grp:
            counts[grp] = counts.get(grp, 0) + 1
    return [
        f"{grp}: {counts.get(grp, 0)} available, {need} required"
        for grp, need in MINIMUM_GAME_DAY.items()
        if counts.get(grp, 0) < need
        and not counts.get(EMERGENCY_SPECIALIST.get(grp, ""), 0)
    ]


def kicking_specialist(players, grp, role):
    """The club's own specialist, else its emergency one (punter kicks, kicker punts)."""
    return specialist(players, grp, role) or specialist(players, EMERGENCY_SPECIALIST[grp], role)


# ---- Kernel 2014.3: who is on the field for protection and the kicking game.
# Credit only. Every rule below is deterministic, reads only the club's own
# depth order and roles, and applies to every club alike. None of it can
# change a score, clock, spot or team counter.

LINE_SLOTS = ("LT", "LG", "C", "RG", "RT")
_LINE_FILL = (("C", "C"), ("LT", "T"), ("RT", "T"), ("LG", "G"), ("RG", "G"))
_LINE_POSITION = {"T": "T", "OT": "T", "G": "G", "OG": "G", "C": "C"}
# A rusher off the edge beats a tackle; an interior rusher beats a guard or
# the center (by the rusher's own position label). A generic LB or DL label
# says neither, so that rusher may have beaten any of the five.
EDGE_RUSHERS = frozenset({"DE", "OLB", "CB", "S", "SS", "FS", "DB", "SAF"})
INTERIOR_RUSHERS = frozenset({"DT", "NT", "ILB", "MLB"})
EDGE_SLOTS = ("LT", "RT")
INTERIOR_SLOTS = ("LG", "C", "RG")
# Base-personnel starters skipped when a club has not designated its coverage
# units or returners: one back, three receivers, one tight end (11
# personnel), three linebackers and four defensive backs (4-3 base). A
# mechanical convention, labelled as such in runtime/README.md (kernel 2014.3).
# Four linebackers are skipped for every club, so a 3-4 club's starters stay
# out of coverage too.
BASE_STARTERS = {"RB": 1, "WR": 3, "TE": 1, "FB": 0, "LB": 4, "DB": 4}
COVERAGE_GROUPS = ("LB", "DB", "TE", "FB", "RB", "WR")
RETURN_GROUPS = ("WR", "RB", "DB")
COVERAGE_SIZE = {"kickoff_coverage": 10, "punt_coverage": 9}
# The unit's make-up when the club has designated none (a mechanical
# convention: backup linebackers and defensive backs, a tight end, a
# fullback or back, a receiver).
COVERAGE_MIX = {
    "kickoff_coverage": ((("LB",), 3), (("DB",), 4), (("TE",), 1), (("FB", "RB"), 1), (("WR",), 1)),
    "punt_coverage": ((("LB",), 3), (("DB",), 3), (("TE",), 1), (("FB", "RB"), 1), (("WR",), 1)),
}


def protection_front(players):
    """{slot: player} for the five linemen on the field.

    A unit-wide chart (every lineman a distinct depth, as the library and
    Jacksonville's depth chart build it) lists the first string LT, LG, C,
    RG, RT at depths 1-5: each available first-stringer plays his depth's
    slot whatever his label, and a vacant slot takes the next available
    lineman by depth whose label fits it (a tackle at LT/RT, a guard at
    LG/RG, a center at C), else the next by depth. A per-position chart
    (tied depths) seats its five lowest-depth linemen by label: the center,
    tackles left then right, guards left then right."""
    line = depth_order(players, "OL", "pass_protection")
    depths = [p.depth for p in line]
    front, used = {}, set()
    if line and all(isinstance(d, int) for d in depths) and len(set(depths)) == len(depths):
        for player in line:
            if 1 <= player.depth <= len(LINE_SLOTS):
                front[LINE_SLOTS[player.depth - 1]] = player
                used.add(player.player_id)
        wanted = {slot: label for slot, label in _LINE_FILL}
        for slot in LINE_SLOTS:
            if slot in front:
                continue
            rest = [p for p in line if p.player_id not in used]
            pick = next((p for p in rest if _LINE_POSITION.get(str(p.position).upper()) == wanted[slot]),
                        rest[0] if rest else None)
            if pick is not None:
                front[slot] = pick
                used.add(pick.player_id)
        return {slot: front[slot] for slot in LINE_SLOTS if slot in front}
    starters = line[:len(LINE_SLOTS)]
    for slot, label in _LINE_FILL:
        for player in starters:
            if player.player_id not in used and _LINE_POSITION.get(str(player.position).upper()) == label:
                front[slot] = player
                used.add(player.player_id)
                break
    spares = [p for p in starters if p.player_id not in used]
    for slot in LINE_SLOTS:
        if slot not in front and spares:
            front[slot] = spares.pop(0)
    return {slot: front[slot] for slot in LINE_SLOTS if slot in front}


def beaten_slots(rusher, front):
    """The front slots a sack by this rusher can be charged to."""
    label = str(rusher.position).upper()
    wanted = (EDGE_SLOTS if label in EDGE_RUSHERS else INTERIOR_SLOTS if label in INTERIOR_RUSHERS
              else LINE_SLOTS)
    slots = [s for s in wanted if s in front]
    return slots or [s for s in LINE_SLOTS if s in front]


def _designated(players, role):
    return [p for p in players if role in p.roles or role in p.responsibilities]


def _beyond_starters(players, groups):
    """(rank past the base starters, group order, player) for non-starters."""
    out = []
    for order, grp in enumerate(groups):
        ranked = depth_order(players, grp)
        for rank, player in enumerate(ranked[BASE_STARTERS.get(grp, 0):]):
            out.append((rank, order, player))
    return sorted(out, key=lambda item: (item[0], item[1]))


def club_returner(players, role):
    """The designated returner, else the club's first non-starter receiver,
    back or defensive back by depth (receivers before backs before DBs at
    the same rank). Deterministic: one club returner per game."""
    designated = _designated(players, role)
    if designated:
        return min(enumerate(designated),
                   key=lambda item: (item[1].depth if isinstance(item[1].depth, int) else 99, item[0]))[1]
    candidates = _beyond_starters(players, RETURN_GROUPS)
    if candidates:
        return candidates[0][2]
    pool = [p for p in players if group(p.position) in RETURN_GROUPS]
    return pool[0] if pool else None


def coverage_unit(players, role, exclude=()):
    """The club's kickoff or punt coverage players (kicker and punter aside).

    Designated players first (role or responsibility `kickoff_coverage` /
    `punt_coverage`), then a fixed make-up (COVERAGE_MIX) filled from each
    group's non-starters by depth; a short group is made up from the other
    non-starters in depth order, then from the lowest-ranked starters. The
    club's own returners are left out."""
    size = COVERAGE_SIZE[role]
    blocked = {getattr(p, "player_id", p) for p in exclude if p is not None}
    for returner_role in ("kick_return", "punt_return"):
        returner = club_returner(players, returner_role)
        if returner is not None:
            blocked.add(returner.player_id)
    unit = [p for p in _designated(players, role) if p.player_id not in blocked][:size]
    taken = {p.player_id for p in unit}
    bench = {grp: [p for p in depth_order(players, grp)[BASE_STARTERS.get(grp, 0):] if p.player_id not in blocked]
             for grp in COVERAGE_GROUPS}
    for groups, count in COVERAGE_MIX[role]:
        for grp in groups:
            for p in bench[grp]:
                if count and len(unit) < size and p.player_id not in taken:
                    unit.append(p)
                    taken.add(p.player_id)
                    count -= 1
    spares = [p for _, _, p in _beyond_starters(players, COVERAGE_GROUPS)
              if p.player_id not in blocked and p.player_id not in taken]
    unit += spares[:max(0, size - len(unit))]
    if len(unit) < size:
        taken = {p.player_id for p in unit}
        starters = []
        for grp in COVERAGE_GROUPS:
            starters += list(reversed(depth_order(players, grp)[:BASE_STARTERS.get(grp, 0)]))
        unit += [p for p in starters if p.player_id not in blocked and p.player_id not in taken][:size - len(unit)]
    return unit[:size]


def long_snapper(players, front=None):
    """The club's first long snapper, else the center on the field."""
    snapper = specialist(players, "LS", "long_snap")
    if snapper is None and front:
        snapper = front.get("C")
    return snapper
