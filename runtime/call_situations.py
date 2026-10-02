"""Kernel 2014.5: which of a frozen call sheet's situational menus a resolved
snap belongs to, and the opening sequence in script order.

Through kernel 2014.4 a snap's descriptive call label was drawn uniformly
from every sheet call whose family could describe the ball carrier or target,
with no regard to down, distance, field zone or clock. The frozen weekly
sheet carries each call's situational menus (``menus``), its opener position
(``opener``) and its planned returns (``opener_returns``), copied from the
head coach's packet; from 2014.5 the label stream reads them.

This module decides nothing about the football. The possession kernel has
already fixed every snap's kind, yards, carrier, target, down and distance
when a label is chosen (runtime.play_detail, label stream, its own keyed RNG
substream). A menu is a label source for narration and call statistics, never
a mechanism that changes who plays, which package is used or what succeeds
(AGENTS.md, no percentage-driven resolution).

**Situation conventions.** Zones and distance bins follow the active 2013
offensive iteration's situational table (section 15: Backed Up own 1-10,
High Red Zone 20-11, Low Red Zone 10-5, Goal Line 4-in; 2nd & 7+ long; 3rd &
1-2, 3-5, 6+) and the weekly packets' third-down scripts, which group the
sheet's calls the same way. Clock menus read the half clock and the score:
two-minute inside 2:00 of a half when the offense is not leading (any score
in the first half), four-minute inside 4:00 of the second half when it leads.
Sudden change is the first two snaps of a possession that began with a
takeaway. Fourth down takes the third-down menu of its distance. The zones
nest outward (goal line, low red zone, high red zone) so a snap the inner
menu cannot describe takes the nearest menu's call; ``normal down`` always
closes the list. The final-play-of-half and two-point menus
are not classified: the ledger has no two-point snap and no shot-decision
mark, so those calls label only through their other menus.
"""
from __future__ import annotations

import re

NORMAL = "normal-down"
SECOND_LONG = "second-and-long"
THIRD_SHORT = "third-and-short"
THIRD_MEDIUM = "third-and-medium"
THIRD_LONG = "third-and-long"
BACKED_UP = "backed-up"
HIGH_RED = "high-red-zone"
LOW_RED = "low-red-zone"
GOAL_LINE = "goal-line"
TWO_MINUTE = "two-minute"
PRESS = "press-sequence"
FOUR_MINUTE = "four-minute"
SUDDEN_CHANGE = "sudden-change"
OPENING = "opening-sequence"

_ALIASES = {
    "2nd-and-long": SECOND_LONG, "second-and-long": SECOND_LONG, "2nd-long": SECOND_LONG,
    "3rd-and-short": THIRD_SHORT, "3rd-short": THIRD_SHORT, "third-short": THIRD_SHORT,
    "3rd-and-medium": THIRD_MEDIUM, "3rd-medium": THIRD_MEDIUM, "third-medium": THIRD_MEDIUM,
    "3rd-and-long": THIRD_LONG, "3rd-long": THIRD_LONG, "third-long": THIRD_LONG,
    "normal-downs": NORMAL, "normal": NORMAL,
    "high-rz": HIGH_RED, "low-rz": LOW_RED, "red-zone-high": HIGH_RED, "red-zone-low": LOW_RED,
    "two-minute-drill": TWO_MINUTE, "press": PRESS, "four-minute-offense": FOUR_MINUTE,
    "opening-sequence": OPENING, "opener": OPENING,
}

# Section 15 of the active 2013 iteration and the weekly packets.
THIRD_SHORT_MAX = 2
THIRD_MEDIUM_MAX = 5
SECOND_LONG_MIN = 7
BACKED_UP_LINE = 90      # yardline_100 >= 90: own 1-10
HIGH_RED_LINE = 20       # 20-11
LOW_RED_LINE = 10        # 10-5
GOAL_LINE_LINE = 4       # 4-in
TWO_MINUTE_SECONDS = 120
FOUR_MINUTE_SECONDS = 240
SUDDEN_CHANGE_SNAPS = 2
TAKEAWAY_STARTS = ("interception", "fumble_lost")


def menu_key(name):
    """One canonical key for a menu name as the sheets spell it
    (``'2nd-and-long'``, ``'four minute'``, ``'PRESS sequence'``)."""
    key = re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")
    return _ALIASES.get(key, key)


def menu_keys(value):
    """The canonical menu keys declared on one sheet call (a tuple; empty
    when the call declares none)."""
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    out = []
    for item in value:
        key = menu_key(item)
        if key and key not in out:
            out.append(key)
    return tuple(out)


def half_clock(start_clock, remaining, overtime):
    """(half, seconds left in that half) for a snap at ``remaining`` seconds
    of the regulation clock (2700 at kickoff) or of an overtime window."""
    if overtime:
        return "OT", int(remaining)
    if int(start_clock) > 1800:
        return 1, int(remaining) - 1800
    return 2, int(remaining)


def classify(*, down, ydstogo, yardline, goal_to_go, half, half_remaining, score_diff,
             start_kind=None, snap_index=0):
    """The applicable menus for one scrimmage snap, most specific first and
    always ending with ``normal-down``. ``yardline`` is the line of scrimmage
    as yardline_100 (distance to the opponent's goal line); ``score_diff`` is
    offense minus defense before the snap; ``snap_index`` is the snap's
    0-based index in its drive."""
    menus = []
    down = int(down or 1)
    ydstogo = int(ydstogo if ydstogo is not None else 10)
    yardline = int(yardline)
    if down >= 3:
        if ydstogo <= THIRD_SHORT_MAX:
            menus.append(THIRD_SHORT)
        elif ydstogo <= THIRD_MEDIUM_MAX:
            menus.append(THIRD_MEDIUM)
        else:
            menus.append(THIRD_LONG)
    # The zones nest outward: the goal line falls back to the low red zone
    # (the sheet's own rule when the surface cannot block it), the low red
    # zone to the high red zone, before the normal-down menu.
    if yardline <= GOAL_LINE_LINE:
        menus += [GOAL_LINE, LOW_RED, HIGH_RED]
    elif yardline <= LOW_RED_LINE:
        menus += [LOW_RED, HIGH_RED]
    elif yardline <= HIGH_RED_LINE:
        menus.append(HIGH_RED)
    elif yardline >= BACKED_UP_LINE:
        menus.append(BACKED_UP)
    if half_remaining is not None:
        if half_remaining <= TWO_MINUTE_SECONDS and (half == 1 or score_diff <= 0):
            menus += [TWO_MINUTE, PRESS]
        elif half == 2 and half_remaining <= FOUR_MINUTE_SECONDS and score_diff > 0:
            menus.append(FOUR_MINUTE)
    if start_kind in TAKEAWAY_STARTS and snap_index < SUDDEN_CHANGE_SNAPS and down <= 2:
        menus.append(SUDDEN_CHANGE)
    if down == 2 and ydstogo >= SECOND_LONG_MIN:
        menus.append(SECOND_LONG)
    menus.append(NORMAL)
    return menus


def restricted(call):
    """Whether a sheet call may label only inside its declared menus: it
    declares menus and ``normal down`` is not one of them (Snag on the low
    red zone only; a shot kept to one menu). An undeclared call is never
    restricted, so a sheet without menus labels exactly as before 2014.5."""
    menus = call.get("menus") or ()
    return bool(menus) and NORMAL not in menus


def script_positions(sheet):
    """{position: call} for the sheet's opening sequence: each call's
    ``opener`` position and every ``opener_returns`` position (a return is
    the same call sent again). Positions are the packet's numbering."""
    positions = {}
    for call in sheet:
        slots = []
        if call.get("opener") is not None:
            slots.append(call["opener"])
        slots += list(call.get("opener_returns") or ())
        for slot in slots:
            try:
                slot = int(slot)
            except (TypeError, ValueError):
                continue
            positions.setdefault(slot, call)
    return positions


def script_state(rows, offense):
    """(scrimmage snaps already taken, positions already sent) for an offense
    from the game's ledger so far; kneels and spikes are not script snaps."""
    snaps, sent = 0, set()
    for row in rows:
        if row.get("offense") != offense or row.get("play_type") not in ("run", "pass"):
            continue
        if row.get("kneel") or row.get("spike"):
            continue
        snaps += 1
        if row.get("script_position") is not None:
            sent.add(int(row["script_position"]))
    return snaps, sent


def next_script_call(positions, sent, fits):
    """The lowest unsent opener position whose call can describe the snap
    (the carrier/target and personnel test ``fits``), or None. Order is the
    packet's; a position whose call cannot describe this snap waits for one
    it can, so the script is sent as a subsequence in its own order."""
    for slot in sorted(positions):
        if slot in sent:
            continue
        if fits(positions[slot]):
            return slot, positions[slot]
    return None, None
