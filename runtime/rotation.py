"""Preseason unit rotation (kernel 2014.4, preseason games only).

A preseason game rotates whole units: the first offense plays its two
possessions or its snap ceiling, the second unit follows, the reserves
finish. The kernel builds each possession's lineup from the club's live
depth order; this module tells it which players form the unit at the front
of that order for the current possession, and nothing more. It never changes
a draw, a score, a clock or a spot, and it is consulted only when
``game_type == "preseason"``: a regular-season, postseason or Pro Bowl game
never reads it, so every such result is byte-identical with or without it.

Plan schema (entries of ``TeamInput.rotation_plan``, in order; the existing
``{"player_id": ..., "featured": true}`` entries are unaffected)::

    {"side": "offense" | "defense" | "special_teams",
     "unit": "first offense",                      # a label for the receipt
     "until": {"possessions": 2, "snaps": 12},     # whichever comes first
     "players": {"QB": ["..."], "RB": [...], "WR": [...], "TE": [...],
                 "OL": ["LT", "LG", "C", "RG", "RT", ...spares],   # or the
                 "LT": "...", "LG": "...", "C": "...", "RG": "...", "RT": "..."
                 }}

``until`` ends the block (checked at each possession boundary, the kernel's
lineup granularity, so a unit may exceed a snap ceiling by the snaps of its
last possession): ``possessions`` played by the block on its side, ``snaps``
(scrimmage snaps the block has played), ``quarter`` (the block ends with the
last possession starting in that quarter; ``possessions_after`` extends it by
that many later possessions). Several keys end it at whichever comes first.
The last block of a side has no ``until`` and plays out the game; a block
that is not last must have one. Offense blocks advance by the club's own
offensive possessions, defense blocks by its defensive possessions,
special-teams blocks by its kicking plays. A side with no block keeps the
depth order. Groups are the kernel's: QB, RB, FB, WR, TE, OL (an ordered
list, first five LT, LG, C, RG, RT) or the five slot keys together, DL, LB,
DB, and the specialists K, P, LS. An unspecified group keeps the depth
order. Within a specified group, the named players who are still available
lead in the block's order, and the group's other available players follow
in depth order, so a removed starter's slot promotes by depth within the
block (E2) and the consequential-substitution pause is unchanged. The
specialists named by a special-teams block kick, punt and snap for the
offense too.

Default (no block on a side, preseason only): the club's depth order split
into three units of the starting counts in ``STARTERS``: the first through
the first quarter and the first possession of the second, the second through
the third quarter, the reserves after. A short slice is padded with the
deepest players above it. The same default applies to every club, Jacksonville
included; which club is ``controlled_team`` changes nothing here.
"""
from __future__ import annotations

from dataclasses import replace

from . import usage
from .usage import LINE_SLOTS

SIDES = ("offense", "defense", "special_teams")
GROUPS = ("QB", "RB", "FB", "WR", "TE", "OL", "DL", "LB", "DB", "K", "P", "LS")
SPECIALISTS = ("K", "P", "LS")
SIDE_GROUPS = {
    "offense": ("QB", "RB", "FB", "WR", "TE", "OL"),
    "defense": ("DL", "LB", "DB"),
    "special_teams": GROUPS,
}
UNTIL_KEYS = ("possessions", "snaps", "quarter", "possessions_after")
# Starting counts per group: the participation slot model's on-field slots
# (runtime/participation.py; two backs, five linemen, four down linemen,
# three linebackers, five defensive backs).
STARTERS = {"QB": 1, "RB": 2, "FB": 1, "WR": 3, "TE": 2, "OL": 5, "DL": 4, "LB": 3, "DB": 5,
            "K": 1, "P": 1, "LS": 1}
DEFAULT_UNTIL = ({"quarter": 1, "possessions_after": 1}, {"quarter": 3}, None)
DEFAULT_UNITS = ("first unit", "second unit", "reserves")
OVERTIME_QUARTER = 5


def is_block(entry):
    return isinstance(entry, dict) and "side" in entry and "featured" not in entry


def _ids(value, label, errors):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)) or not all(isinstance(v, str) and v for v in value):
        errors.append("%s must list player ids" % label)
        return []
    return list(value)


def _parse_block(entry, errors, where):
    side = entry.get("side")
    if side not in SIDES:
        errors.append("%s: unknown side %r" % (where, side))
        return None
    unit = entry.get("unit")
    if not isinstance(unit, str) or not unit.strip():
        errors.append("%s: a block needs a unit label" % where)
        return None
    until = entry.get("until")
    if until is not None:
        if not isinstance(until, dict) or not until or any(k not in UNTIL_KEYS for k in until):
            errors.append("%s: until must use %s" % (where, ", ".join(UNTIL_KEYS)))
            return None
        for key, value in until.items():
            floor = 0 if key == "possessions_after" else 1
            if not isinstance(value, int) or isinstance(value, bool) or value < floor:
                errors.append("%s: until.%s must be an integer >= %d" % (where, key, floor))
                return None
        if "possessions_after" in until and "quarter" not in until:
            errors.append("%s: possessions_after needs a quarter" % where)
            return None
    players = entry.get("players") or {}
    if not isinstance(players, dict):
        errors.append("%s: players must map a group to its players in order" % where)
        return None
    groups = {}
    slots = {}
    for key, value in players.items():
        if key in LINE_SLOTS:
            ids = _ids(value, "%s %s" % (where, key), errors)
            if len(ids) != 1:
                errors.append("%s: slot %s names one lineman" % (where, key))
            else:
                slots[key] = ids[0]
            continue
        if key not in SIDE_GROUPS[side]:
            errors.append("%s: unknown group %r for %s" % (where, key, side))
            continue
        groups[key] = _ids(value, "%s %s" % (where, key), errors)
    if slots:
        if "OL" in groups or set(slots) != set(LINE_SLOTS):
            errors.append("%s: name all five line slots (%s) or an ordered OL list" % (where, ", ".join(LINE_SLOTS)))
        else:
            groups["OL"] = [slots[s] for s in LINE_SLOTS]
    for grp, ids in groups.items():
        if len(set(ids)) != len(ids):
            errors.append("%s: %s names a player twice" % (where, grp))
    return {"side": side, "unit": unit.strip(), "until": dict(until) if until else None, "players": groups}


def parse(team, players=None):
    """({side: [block]}, errors) from a TeamInput's rotation_plan.

    ``players`` (the club's game-day unit, normalize_players) checks that
    every named player is dressed and in the named group."""
    blocks = {side: [] for side in SIDES}
    errors = []
    by_id = {p.player_id: p for p in players} if players is not None else None
    for index, entry in enumerate(getattr(team, "rotation_plan", ()) or ()):
        if not is_block(entry):
            continue
        where = "%s rotation block %d" % (team.team_id, index + 1)
        block = _parse_block(entry, errors, where)
        if block is None:
            continue
        if by_id is not None:
            for grp, ids in block["players"].items():
                for pid in ids:
                    player = by_id.get(pid)
                    if player is None:
                        errors.append("%s: %s is not on the game-day unit" % (where, pid))
                    elif usage.group(player.position) != grp:
                        errors.append("%s: %s is not a %s" % (where, pid, grp))
        blocks[block["side"]].append(block)
    for side, listed in blocks.items():
        for block in listed[:-1]:
            if block["until"] is None:
                errors.append("%s rotation: %s block %r needs an until rule (only the last block plays out)"
                              % (team.team_id, side, block["unit"]))
    return blocks, errors


def plan_errors(team, players, game_type):
    """Fail closed: a malformed plan, a player not on the unit, an unknown
    group, or a rotation block outside a preseason game."""
    has_blocks = any(is_block(e) for e in getattr(team, "rotation_plan", ()) or ())
    if game_type != "preseason":
        return ["%s: rotation blocks apply to preseason games only" % team.team_id] if has_blocks else []
    return parse(team, players)[1]


def default_blocks(players, sides=("offense", "defense")):
    """The documented quarter rotation from the club's depth order."""
    blocks = {side: [] for side in SIDES}
    for side in sides:
        for index, (unit, until) in enumerate(zip(DEFAULT_UNITS, DEFAULT_UNTIL)):
            named = {}
            for grp in SIDE_GROUPS[side]:
                ordered = [p.player_id for p in usage.depth_order(players, grp)]
                n = STARTERS[grp]
                chunk = ordered[index * n:(index + 1) * n]
                for pid in reversed(ordered[:index * n]):
                    if len(chunk) >= n:
                        break
                    if pid not in chunk:
                        chunk.append(pid)
                if chunk:
                    named[grp] = chunk
            blocks[side].append({"side": side, "unit": unit, "until": dict(until) if until else None,
                                 "players": named})
    return blocks


def apply(block, players):
    """(view, lineup) with the block's named players at the front of their
    groups: the view renumbers depth within each specified group so
    usage.depth_order, protection_front and the slot model read the unit.
    ``lineup`` is {group: [ids]} for the groups the block specifies."""
    renumber, lineup = {}, {}
    for grp, named in block["players"].items():
        members = usage.depth_order(players, grp)
        by_id = {p.player_id: p for p in members}
        chosen = set(named)
        ordered = [by_id[pid] for pid in named if pid in by_id] + [p for p in members if p.player_id not in chosen]
        for rank, player in enumerate(ordered, 1):
            renumber[player.player_id] = rank
        lineup[grp] = [p.player_id for p in ordered]
    if not renumber:
        return tuple(players), lineup
    return tuple(replace(p, depth=renumber[p.player_id]) if p.player_id in renumber else p
                 for p in players), lineup


def on_field(players, side):
    """{group: [ids]} the side's starting counts from a view's depth order."""
    out = {}
    for grp in SIDE_GROUPS[side] if side != "special_teams" else SPECIALISTS:
        ids = [p.player_id for p in usage.depth_order(players, grp)][:STARTERS[grp]]
        if ids:
            out[grp] = ids
    return out


def quarter_of(half, window, quarter=None):
    """The quarter a possession starts in: from the Pro Bowl's own quarter,
    else the half and the seconds left in it; overtime counts as 5."""
    if quarter:
        return quarter
    if half == "OT":
        return OVERTIME_QUARTER
    late = window <= 900
    return (2 if late else 1) if half == 1 else (4 if late else 3)


def quarter_of_remaining(remaining, overtime=False):
    """The quarter of a kick from the seconds left in regulation."""
    if overtime:
        return OVERTIME_QUARTER
    for quarter, floor in ((1, 2700), (2, 1800), (3, 900)):
        if remaining > floor:
            return quarter
    return 4


class Tracker:
    """One club's rotation through a preseason game.

    ``blocks`` from parse(); a side with none takes the default. The
    tracker counts possessions and scrimmage snaps per block, reads the
    quarter the kernel passes, and records each application for the receipt."""

    def __init__(self, team_id, blocks, players):
        self.team_id = team_id
        self.blocks = {side: list(blocks.get(side) or ()) for side in SIDES}
        self.basis = {}
        defaults = default_blocks(players)
        for side in SIDES:
            if not self.blocks[side]:
                self.blocks[side] = defaults[side]
                self.basis[side] = "default" if defaults[side] else "depth_order"
            else:
                self.basis[side] = "plan"
        self.index = {side: 0 for side in SIDES}
        self.counts = {side: [{"possessions": 0, "snaps": 0, "after": 0} for _ in self.blocks[side]]
                       for side in SIDES}
        self.applied = {side: [] for side in SIDES}

    def _done(self, side, index, quarter):
        block = self.blocks[side][index]
        until = block["until"]
        if until is None:
            return False
        count = self.counts[side][index]
        if "possessions" in until and count["possessions"] >= until["possessions"]:
            return True
        if "snaps" in until and count["snaps"] >= until["snaps"]:
            return True
        if "quarter" in until and quarter > until["quarter"] and count["after"] >= until.get("possessions_after", 0):
            return True
        return False

    def select(self, side, quarter):
        """(block index, block) active for a possession starting in ``quarter``; None without blocks."""
        blocks = self.blocks[side]
        if not blocks:
            return None, None
        while self.index[side] < len(blocks) - 1 and self._done(side, self.index[side], quarter):
            self.index[side] += 1
        return self.index[side], blocks[self.index[side]]

    def view(self, side, players, quarter, number, record=True):
        """The side's rotated view for possession/kick ``number``."""
        index, block = self.select(side, quarter)
        if block is None:
            view, lineup = tuple(players), {}
        else:
            view, lineup = apply(block, players)
        if side != "special_teams" and self.blocks["special_teams"]:
            st_index, st_block = self.select("special_teams", quarter)
            specialists = {g: ids for g, ids in st_block["players"].items() if g in SPECIALISTS}
            if specialists:
                view, _ = apply({"players": specialists}, view)
        if record and block is not None:
            entry = {"possession" if side != "special_teams" else "kick": number, "quarter": quarter,
                     "block": index, "unit": block["unit"] if block else None,
                     "lineup": on_field(view, side)}
            self.applied[side].append(entry)
        return view, index

    def played(self, side, index, quarter, snaps=0):
        """Count a possession (or kick) the block played."""
        if index is None:
            return
        count = self.counts[side][index]
        count["possessions"] += 1
        count["snaps"] += snaps
        until = self.blocks[side][index]["until"] or {}
        if "quarter" in until and quarter > until["quarter"]:
            count["after"] += 1

    def receipt(self):
        """The plan as applied, for the result's ``rotation`` field."""
        return {
            "basis": dict(self.basis),
            "blocks": {side: [{"unit": b["unit"], "until": b["until"], "players": b["players"]}
                              for b in self.blocks[side]] for side in SIDES},
            "applied": {side: list(self.applied[side]) for side in SIDES},
        }

    def kicked(self, quarter):
        """Count one kicking play against the active special-teams block."""
        if self.blocks["special_teams"]:
            self.played("special_teams", self.select("special_teams", quarter)[0], quarter)
