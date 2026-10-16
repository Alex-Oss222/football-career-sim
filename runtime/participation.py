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


# ---- Kernel 2014.6 batch B15 (W2b): position-true defensive-back seats ------
# Under the profile flag db_slots the kernel seats a club's defensive backs by
# position family before any consumer reads the DB depth order (the slot
# model's DB1-5, the field-goal block's DB1-4, the strength units' base four,
# tackle and coverage credit, the coverage units and the returner): DB1 and
# DB2 the two outside corners, DB3 and DB4 the two safeties, DB5 the nickel,
# then the reserves in the same family-balanced units. The family is the
# position label (a corner CB; a safety S, SS, FS or SAF; any other DB label,
# such as an emergency filler's, has none and fills a short seat). The
# labels are the inputs' own: from 2014 Week 5 the background clubs' come
# from their Week 1 chart slots, then their 2014 weekly-roster label
# (runtime.depth_library.relabel_defensive_backs), Jacksonville's from Stone's
# chart. Two slot-defining roles are read from the inputs: ``nickel`` (the
# player who takes DB5 whenever he is available, settled before the base) and
# ``outside_reserve`` (the first corner to replace an outside starter, the
# nickel staying inside). Without them the move-up convention applies (the
# third corner is the nickel; a removed outside corner is replaced by the
# nickel moving outside and the next corner entering at nickel), labelled as
# a convention: real practice splits it about evenly (design W2b, honest
# limit 4). A removed corner is replaced from the corners and a removed safety
# from the safeties; another family fills a seat only when its own family is
# exhausted. One deterministic rule for every club; no draw is used, the slot
# shares (SCRIMMAGE_SLOT_MIX) are unchanged and only the order inside the DB
# group moves.
SLOT_ROLES = ("nickel", "outside_reserve")
CORNER_LABELS = frozenset({"CB"})
SAFETY_LABELS = frozenset({"S", "SS", "FS", "SAF"})
DB_UNIT = ("corner", "corner", "safety", "safety", "nickel")


def db_family(position):
    """'corner', 'safety' or None (a generic DB label) for a position label."""
    label = str(position or "").upper()
    if label in CORNER_LABELS:
        return "corner"
    if label in SAFETY_LABELS:
        return "safety"
    return None


def _holds(player, role):
    return role in player.roles or role in player.responsibilities


def db_starters(players):
    """The ids of a dressed unit's two outside starters (W2b): its first two
    corners by depth that hold neither slot role. The kernel settles them
    once at kickoff from the game-day unit, so an outside reserve, not the
    next corner by depth, replaces a removed starter; a coach's replacement
    inherits the seat (kernel apply_decision)."""
    dbs = usage.depth_order(players, "DB")
    nickel = next((p for p in dbs if _holds(p, "nickel")), None)
    corners = [p for p in dbs if db_family(p.position) == "corner" and p is not nickel]
    reserve = next((p for p in corners if _holds(p, "outside_reserve")), None)
    return tuple(p.player_id for p in corners if p is not reserve)[:2]


def db_seats(players, starters=None):
    """[(seat, player)] for the defensive backs of ``players`` in seat order
    (W2b): unit after unit of two outside corners, two safeties and a nickel
    (seat labels CB, S and NB with the unit number), the designated nickel
    settled first in the first unit. ``starters`` are the outside starters'
    ids (db_starters of the game-day unit; of ``players`` when None). The
    outside order is the starters, then the outside reserve, then the other
    corners by depth; the undesignated nickel is the next corner of that
    order other than the outside reserve (the reserve only when no other
    corner is left). A seat whose family is exhausted takes a generic DB,
    then the other family (a corner seat the next safety, a safety seat the
    next corner of the outside order, the outside reserve last); a seat
    nobody can fill stays empty."""
    dbs = usage.depth_order(players, "DB")
    if not dbs:
        return []
    starters = db_starters(players) if starters is None else tuple(starters)
    order = {p.player_id: i for i, p in enumerate(dbs)}
    nickel = next((p for p in dbs if _holds(p, "nickel")), None)
    corners = [p for p in dbs if db_family(p.position) == "corner" and p is not nickel]
    reserve = next((p for p in corners if _holds(p, "outside_reserve")), None)
    outside = sorted(corners, key=lambda p: (0 if p.player_id in starters else 1 if p is reserve else 2,
                                            order[p.player_id]))
    safeties = [p for p in dbs if db_family(p.position) == "safety" and p is not nickel]
    generic = [p for p in dbs if db_family(p.position) is None and p is not nickel]
    taken = set()

    def take(*pools):
        for pool in pools:
            for p in pool:
                if p.player_id not in taken:
                    taken.add(p.player_id)
                    return p
        return None

    seats, unit = [], 0
    while len(taken) < len(dbs):
        unit += 1
        chosen = {}
        if unit == 1 and nickel is not None:
            chosen[4] = nickel
            taken.add(nickel.player_id)
        # Own families first: the outside corners, the safeties, then the
        # undesignated nickel (the reserve kept outside while another corner
        # is left).
        for index, kind in enumerate(DB_UNIT[:4]):
            pick = take(outside if kind == "corner" else safeties)
            if pick is not None:
                chosen[index] = pick
        inside = [p for p in outside if p is not reserve]
        if 4 not in chosen:
            pick = take(inside, outside)
            if pick is not None:
                chosen[4] = pick
        # Then the short seats in seat order, from a generic DB, then the
        # other family (the outside reserve last among the corners).
        for index, kind in enumerate(DB_UNIT):
            if index in chosen:
                continue
            pools = ((generic, safeties) if kind == "corner" else (generic, inside, outside) if kind == "safety"
                     else (generic, inside, outside, safeties))
            pick = take(*pools)
            if pick is not None:
                chosen[index] = pick
        if not chosen:
            break
        for index in sorted(chosen):
            label = ("CB%d" % (2 * unit - 1 + index) if index < 2 else "S%d" % (2 * unit - 3 + index)
                     if index < 4 else "NB%d" % unit)
            seats.append((label, chosen[index]))
    return seats


def seat_defensive_backs(players, starters=None):
    """``players`` with each defensive back's depth renumbered by his seat
    (db_seats: DB1 and DB2 the outside corners, DB3 and DB4 the safeties, DB5
    the nickel, then the reserves), so usage.depth_order(view, "DB") reads
    the seat order; every other player and every other field is unchanged,
    and the tuple keeps its order. Idempotent for a fixed ``starters``."""
    players = tuple(players)
    seats = db_seats(players, starters)
    if not seats:
        return players
    rank = {p.player_id: i for i, (_, p) in enumerate(seats, 1)}
    return tuple(replace(p, depth=rank[p.player_id]) if p.player_id in rank else p for p in players)


# ---- scrimmage ---------------------------------------------------------------

def _credit(accumulator, key, share, snaps):
    before = accumulator.get(key, 0)
    after = before + share * snaps
    accumulator[key] = after
    return after // 100 - before // 100


def slot_lineup(offense_view, defense_view, passer, front):
    """Kernel 2014.6 batch B6 (W2a): the single on-field source. {side:
    [slot]} for one drive's scrimmage snaps, each slot a dict with its
    label, group, accumulator key (None for a full-share slot that is never
    accumulated: the passer and the five linemen), rank inside that key and
    share in hundredths. Order and keys are exactly those scrimmage()
    credited before this record existed, so crediting is byte for byte the
    same: passer, the protection front by slot, the back slots (RB1, then
    the first fullback or RB2), WR1-3, TE1-2; DL1-4, LB1-3, DB1-5."""
    offense = []
    if passer is not None:
        offense.append({"slot": "QB", "group": "QB", "key": None, "rank": None, "player": passer, "share": 100})
    for label, lineman in front.items():
        offense.append({"slot": label, "group": "OL", "key": None, "rank": None, "player": lineman, "share": 100})
    backs = usage.depth_order(offense_view, "RB")
    fullbacks = usage.depth_order(offense_view, "FB")
    back_slots = backs[:1] + (fullbacks[:1] or backs[1:2])
    for rank, (player, share) in enumerate(zip(back_slots, BACK_SLOTS)):
        label = "FB1" if rank == 1 and fullbacks[:1] and player is fullbacks[0] else "RB%d" % (rank + 1)
        offense.append({"slot": label, "group": "RB", "key": ("O", "RB"), "rank": rank, "player": player,
                        "share": share})
    for grp, shares in OFFENSE_SLOTS:
        for rank, (player, share) in enumerate(zip(usage.depth_order(offense_view, grp), shares)):
            offense.append({"slot": "%s%d" % (grp, rank + 1), "group": grp, "key": ("O", grp), "rank": rank,
                            "player": player, "share": share})
    defense = []
    for grp, shares in DEFENSE_SLOTS:
        for rank, (player, share) in enumerate(zip(usage.depth_order(defense_view, grp), shares)):
            defense.append({"slot": "%s%d" % (grp, rank + 1), "group": grp, "key": ("D", grp), "rank": rank,
                            "player": player, "share": share})
    return {"offense": offense, "defense": defense}


def slot_map(lineup, side):
    """{player_id: slot label} of one side of a slot_lineup (a player in two
    slots keeps the first)."""
    out = {}
    for slot in lineup[side]:
        out.setdefault(slot["player"].player_id, slot["slot"])
    return out


def _credit_slots(accumulator, team_id, slots, n, out):
    for slot in slots:
        pid = slot["player"].player_id
        if slot["key"] is None:
            out[pid] = n
            continue
        credited = _credit(accumulator, ((team_id,) + slot["key"], slot["rank"]), slot["share"], n)
        if credited:
            out[pid] = out.get(pid, 0) + credited


def scrimmage(accumulator, offense_id, defense_id, offense_view, defense_view, passer, front, rows,
              hazard_out=None):
    """{team_id: {player_id: snaps}} for one drive's pass and run rows.

    `hazard_out`, when given a dict, receives {team_id: {player_id: snaps}}
    from the slot model alone (before the named-player uplift below): the
    injury exposure. It depends only on the lineups and the drive's snap
    count, so no attribution draw can move an injury hazard (kernel 2014.4,
    defect register item 19: the attribution tilt changes credit only).
    Batch B6 (W2a): the slots are slot_lineup's, the single on-field source."""
    snaps_rows = [r for r in rows if r.get("play_type") in SCRIMMAGE_TYPES]
    n = len(snaps_rows)
    offense, defense = {}, {}
    if not n:
        if hazard_out is not None:
            hazard_out.update({offense_id: {}, defense_id: {}})
        return {offense_id: offense, defense_id: defense}
    lineup = slot_lineup(offense_view, defense_view, passer, front)
    _credit_slots(accumulator, offense_id, lineup["offense"], n, offense)
    _credit_slots(accumulator, defense_id, lineup["defense"], n, defense)
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


def try_snap(accumulator, offense_id, defense_id, offense_view, defense_view, passer, front, row,
             hazard_out=None):
    """Kernel 2014.6 batch B9 (R8): {team_id: {player_id: snaps}} for one
    two-point try snap: one offensive snap for the scoring club's slot
    lineup and one defensive snap for the other club's (slot_lineup, the
    single on-field source; fractional slots through the same per-club
    accumulator, n = 1), and the try's named passer, runner and target on
    the field. A labelled convention: the 2013 snap counts give 1.06
    recorded snaps per try snap (library/data/2010_2014w4_scoring_decisions.json
    try_snap_participation). The try is not a scrimmage row
    (SCRIMMAGE_TYPES): it never counts toward a drive's snaps or a
    preseason block's limits. `hazard_out` receives the slot credits alone
    (the injury exposure), as for scrimmage()."""
    lineup = slot_lineup(offense_view, defense_view, passer, front)
    offense, defense = {}, {}
    _credit_slots(accumulator, offense_id, lineup["offense"], 1, offense)
    _credit_slots(accumulator, defense_id, lineup["defense"], 1, defense)
    if hazard_out is not None:
        hazard_out.update({offense_id: dict(offense), defense_id: dict(defense)})
    for field in OFFENSE_FIELDS:
        pid = row.get(field)
        if pid is not None:
            offense[pid] = max(offense.get(pid, 0), 1)
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
