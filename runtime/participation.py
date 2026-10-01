"""Kernel 2014.4 participation model: who was on the field, and for how many snaps.

The kernel has no per-snap list of the 22 players on the field. This module
defines one explicit, deterministic convention for it, applied identically to
every club, and records the result as per-player snap counts
(``offensive_snaps``, ``defensive_snaps``, ``special_teams_snaps``). Those
counts are the injury exposure (runtime/injury_model.py) and are meant to be
the "actual participants" that E1 composes later.

Scrimmage snaps (every pass or run row of a drive: runs, dropbacks, sacks,
kneels and spikes), per drive:

* Offense: the drive's passer and the five linemen of
  ``usage.protection_front`` take every snap. The remaining skill slots
  follow the 2012 on-field slot mix that the injury calibration uses as its
  per-slot denominator (library/2012_nfl_injury_calibration.md, "Relative
  risk per on-field scrimmage slot": QB 1, OL 5, RB 1.25, WR 2.45, TE 1.3 of
  11; that mix is labelled Unverified there because 2012 has no public
  participation data). By club depth order: RB1 every snap and a 0.25 second
  back (the first fullback when one is dressed, else RB2); WR1 and WR2 every
  snap and WR3 0.45; TE1 every snap and TE2 0.30.
* Defense: the same mix's DL 3.7, LB 2.5, DB 4.8: DL1-3 every snap and DL4
  0.7; LB1-2 every snap and LB3 0.5; DB1-4 every snap and DB5 0.8.
* A fractional slot is credited through a per-club, per-slot integer
  accumulator in hundredths of a snap across the game, so its long-run share
  is exact and no random number is used: a slot of share s credits
  ``floor((c + s*n)/100) - floor(c/100)`` snaps on an n-snap drive.
* Any player the attribution layer names on a snap (passer, runner, target,
  blocker, tackler, assist tackler) is on the field for at least the number of
  that drive's snaps that name him (capped at the drive's snaps). This can put
  slightly more than eleven on a snap; the exposure normalization is per
  recorded player-snap, so the excess is small and counted, never hidden.

Kicking plays (one special-teams snap for each participant):

* Kickoff or free kick: the kicker and the kickoff coverage unit
  (``usage.coverage_unit``); the receiving club's kick returner and ten more
  drawn by the same bench make-up (the return unit).
* Punt: the punter, the long snapper and the punt coverage unit; the
  receiving club's punt returner and the same make-up (ten in all).
* Field goal or try: the kicker, the holder (the club's punter when he is not
  the kicker), the long snapper, the protection front and the first two tight
  ends, filled to eleven with the next linemen by depth; the defending club's
  DL1-4, LB1-3 and DB1-4.
* Anyone the kick row names (kicker, punter, snapper, returner, coverage
  tackler) is always a participant.

Removed players are not in the lists this module receives, so they can take
no later snap. Every choice reads only the club's own depth order, roles and
the kernel's already-resolved rows.
"""
from __future__ import annotations

from dataclasses import replace

from . import usage

SNAP_FIELDS = {"offense": "offensive_snaps", "defense": "defensive_snaps",
               "special_teams": "special_teams_snaps"}

# Hundredths of a snap per slot, by depth rank inside the group.
OFFENSE_SLOTS = (("WR", (100, 100, 45)), ("TE", (100, 30)))
BACK_SLOTS = (100, 25)
DEFENSE_SLOTS = (("DL", (100, 100, 100, 70)), ("LB", (100, 100, 50)),
                 ("DB", (100, 100, 100, 100, 80)))
# The on-field slot mix these constants encode (per 11 players a side).
SCRIMMAGE_SLOT_MIX = {"QB": 1.0, "OL": 5.0, "RB": 1.25, "WR": 2.45, "TE": 1.3,
                      "DL": 3.7, "LB": 2.5, "DB": 4.8}
FG_BLOCK_SLOTS = (("DL", 4), ("LB", 3), ("DB", 4))
SCRIMMAGE_TYPES = ("pass", "run")
KICK_TYPES = ("kickoff", "free_kick", "punt", "field_goal", "extra_point")
OFFENSE_FIELDS = ("passer", "runner", "target", "blocker")
DEFENSE_FIELDS = ("tackler", "assist_tackler")

# ---- emergency personnel (exhausted depth) ---------------------------------
# When removals take a position group below the smaller of its legal game-day
# minimum (usage.MINIMUM_GAME_DAY) and the number the club dressed, the next
# spare from these groups (beyond that group's own minimum, by depth) plays
# the vacated position for that side only. A mechanical convention, applied
# to every club alike; it never reuses a removed player.
SIDE_GROUPS = {"offense": ("QB", "OL", "RB", "WR", "TE"), "defense": ("DL", "LB", "DB")}
EMERGENCY_FROM = {
    "QB": ("RB", "WR", "TE"), "RB": ("FB", "WR", "TE"), "WR": ("TE", "RB", "DB"),
    "TE": ("OL", "FB", "WR"), "OL": ("TE", "DL"), "DL": ("LB", "OL"),
    "LB": ("DL", "DB"), "DB": ("LB", "WR"),
}
MINIMUM_PER_SIDE = 11


class NoLegalPersonnel(RuntimeError):
    """E2 step 3: no legal personnel solution exists; the game must stop."""


def group_counts(players):
    counts = {}
    for p in players:
        grp = usage.group(p.position)
        if grp:
            counts[grp] = counts.get(grp, 0) + 1
    return counts


def emergency_view(players, baseline, side, prefer=None):
    """(players as they line up on this side, [emergency notes]).

    ``baseline`` is the club's group counts at kickoff: a group the club
    never dressed to the minimum is not filled (legacy synthetic inputs).
    ``prefer`` maps a group to the player who filled it on the club's last
    drive (October 1, 2026): he keeps the job while he is available, even
    when a later removal reorders his own group, so an emergency passer
    does not change without a removal (kernel validate_result)."""
    prefer = prefer or {}
    players = tuple(players)
    if len(players) < MINIMUM_PER_SIDE:
        raise NoLegalPersonnel("%d available players: no legal eleven" % len(players))
    view = list(players)
    notes = []
    for grp in SIDE_GROUPS[side]:
        need = min(usage.MINIMUM_GAME_DAY.get(grp, 0), baseline.get(grp, 0))
        have = sum(usage.group(p.position) == grp for p in view)
        while have < need:
            candidate = None
            kept = prefer.get(grp)
            if kept is not None:
                candidate = next((p for p in view if p.player_id == kept
                                  and usage.group(p.position) in EMERGENCY_FROM[grp]), None)
            for source in EMERGENCY_FROM[grp] if candidate is None else ():
                ordered = usage.depth_order(view, source)
                spare = ordered[usage.MINIMUM_GAME_DAY.get(source, 0):] or []
                if spare:
                    candidate = spare[0]
                    break
            if candidate is None:
                notes.append({"group": grp, "available": have, "required": need, "filled_by": None})
                break
            index = next(i for i, p in enumerate(view) if p.player_id == candidate.player_id)
            view[index] = replace(candidate, position=grp, depth=100 + have)
            notes.append({"group": grp, "available": have, "required": need,
                          "filled_by": candidate.player_id, "from": usage.group(candidate.position)})
            have += 1
    return tuple(view), notes


# ---- scrimmage ---------------------------------------------------------------

def _credit(accumulator, key, share, snaps):
    before = accumulator.get(key, 0)
    after = before + share * snaps
    accumulator[key] = after
    return after // 100 - before // 100


def _slot_snaps(accumulator, prefix, ordered, shares, snaps, out):
    for rank, share in enumerate(shares):
        if rank >= len(ordered):
            break
        credited = _credit(accumulator, (prefix, rank), share, snaps)
        if credited:
            pid = ordered[rank].player_id
            out[pid] = out.get(pid, 0) + credited


def scrimmage(accumulator, offense_id, defense_id, offense_view, defense_view, passer, front, rows,
              hazard_out=None):
    """{team_id: {player_id: snaps}} for one drive's pass and run rows.

    `hazard_out`, when given a dict, receives {team_id: {player_id: snaps}}
    from the slot model alone (before the named-player uplift below): the
    injury exposure. It depends only on the lineups and the drive's snap
    count, so no attribution draw can move an injury hazard (kernel 2014.4,
    defect register item 19: the attribution tilt changes credit only)."""
    snaps_rows = [r for r in rows if r.get("play_type") in SCRIMMAGE_TYPES]
    n = len(snaps_rows)
    offense, defense = {}, {}
    if not n:
        if hazard_out is not None:
            hazard_out.update({offense_id: {}, defense_id: {}})
        return {offense_id: offense, defense_id: defense}
    if passer is not None:
        offense[passer.player_id] = n
    for lineman in front.values():
        offense[lineman.player_id] = n
    backs = usage.depth_order(offense_view, "RB")
    fullbacks = usage.depth_order(offense_view, "FB")
    back_slots = backs[:1] + (fullbacks[:1] or backs[1:2])
    _slot_snaps(accumulator, (offense_id, "O", "RB"), back_slots, BACK_SLOTS, n, offense)
    for grp, shares in OFFENSE_SLOTS:
        _slot_snaps(accumulator, (offense_id, "O", grp), usage.depth_order(offense_view, grp), shares, n, offense)
    for grp, shares in DEFENSE_SLOTS:
        _slot_snaps(accumulator, (defense_id, "D", grp), usage.depth_order(defense_view, grp), shares, n, defense)
    if hazard_out is not None:
        hazard_out.update({offense_id: dict(offense), defense_id: dict(defense)})
    for side, fields in ((offense, OFFENSE_FIELDS), (defense, DEFENSE_FIELDS)):
        named = {}
        for row in snaps_rows:
            for pid in {row.get(f) for f in fields} - {None}:
                named[pid] = named.get(pid, 0) + 1
        for pid, count in named.items():
            side[pid] = min(n, max(side.get(pid, 0), count))
    return {offense_id: offense, defense_id: defense}


# ---- kicking plays -------------------------------------------------------------

def _ids(players):
    return [p.player_id for p in players if p is not None]


def _unique(ids):
    seen, out = set(), []
    for pid in ids:
        if pid is not None and pid not in seen:
            seen.add(pid)
            out.append(pid)
    return out


def _by_id(players, pid):
    return next((p for p in players if p.player_id == pid), None)


def kick(row, kicking_id, receiving_id, kicking_players, receiving_players):
    """{team_id: [player_id]} for one kicking-play row."""
    kind = row.get("play_type")
    if kind in ("kickoff", "free_kick"):
        kicker = _by_id(kicking_players, row.get("kicker"))
        kicking = [row.get("kicker")] + _ids(usage.coverage_unit(kicking_players, "kickoff_coverage",
                                                                exclude=(kicker,) if kicker else ()))
        returner = usage.club_returner(receiving_players, "kick_return")
        receiving = _ids([returner]) + _ids(usage.coverage_unit(receiving_players, "kickoff_coverage"))
        kicking.append(row.get("cover_player"))
        receiving.append(row.get("returner"))
    elif kind == "punt":
        punter = _by_id(kicking_players, row.get("punter"))
        kicking = [row.get("punter"), row.get("long_snapper")] + _ids(
            usage.coverage_unit(kicking_players, "punt_coverage", exclude=(punter,) if punter else ()))
        returner = usage.club_returner(receiving_players, "punt_return")
        receiving = _ids([returner]) + _ids(usage.coverage_unit(receiving_players, "punt_coverage"))
        kicking.append(row.get("cover_player"))
        receiving.append(row.get("returner"))
    elif kind in ("field_goal", "extra_point"):
        holder = usage.kicking_specialist(kicking_players, "P", "punt")
        front = usage.protection_front(kicking_players)
        kicking = [row.get("kicker"), row.get("long_snapper")]
        if holder is not None and holder.player_id != row.get("kicker"):
            kicking.append(holder.player_id)
        kicking += _ids(front.values()) + _ids(usage.depth_order(kicking_players, "TE")[:2])
        spare_line = [p for p in usage.depth_order(kicking_players, "OL") if p.player_id not in kicking]
        kicking = _unique(kicking)
        kicking += _ids(spare_line[:max(0, 11 - len(kicking))])
        receiving = []
        for grp, count in FG_BLOCK_SLOTS:
            receiving += _ids(usage.depth_order(receiving_players, grp)[:count])
    else:
        return {kicking_id: [], receiving_id: []}
    return {kicking_id: _unique(kicking), receiving_id: _unique(receiving)}


def credit(stats, team_id, snaps, side):
    """Bump the append-only snap counters; returns the same mapping."""
    field = SNAP_FIELDS[side]
    players = stats[team_id]["players"]
    for pid, count in snaps.items():
        if count and pid in players:
            players[pid][field] += count
    return snaps
