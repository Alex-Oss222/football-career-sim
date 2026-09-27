"""Which ball carriers and targets a named offensive call family can describe.

Kernel 2013.7 labels each generated snap only after its ball carrier or
target is fixed (runtime.play_detail, label stream). A call label is eligible
for a snap only when the call's family names that player's position group.
The groups below are read from the active 2013 offensive iteration
(`career/playbook/alex_stone_2013_offensive_playbook_iteration_i.md`); each
entry cites its section. A later iteration is never read.

A weekly call sheet may override a family with explicit per-call fields:
``carrier`` for a run call, ``target`` for a pass call (both for a call typed
``any`` or ``mixed``). A value is a list of groups, ``"any"`` (pass targets
only) or ``"unspecified"``; an unspecified call is never eligible and the snap
gets a generic label. A family neither declared on the call nor listed here
fails closed at build time (``sheet_errors``), before any event is closed.

These declarations are descriptive only. They never enter the outcome packet
(``play_detail.canonical_call_sheet`` excludes them), never select a carrier
and never change a score, clock, possession, team counter or player line.
"""
from __future__ import annotations

import re

RUN_GROUPS = ("QB", "RB", "FB", "WR", "TE")
TARGET_GROUPS = ("RB", "FB", "WR", "TE")
BACKS = ("RB", "FB")
ANY = "any"
UNSPECIFIED = "unspecified"
PLAYBOOK = "career/playbook/alex_stone_2013_offensive_playbook_iteration_i.md"

# family -> {"carrier": groups for a run call, "target": groups for a pass
# call, "source": section of the active 2013 iteration}
FAMILIES = {
    # 9. Run game: "Back" / "Tailback" carries unless the page names another player.
    "Power": {"carrier": BACKS, "source": "9.1 Power: back presses downhill, reads the puller"},
    "Counter": {"carrier": BACKS, "source": "9.2 Counter / Trey: back takes controlled counter step"},
    "Duo": {"carrier": BACKS, "source": "9.3 Duo: back presses frontside A/B track"},
    "Lead": {"carrier": ("RB",), "source": "9.4 Lead / Iso: tailback follows the lead path"},
    "Iso": {"carrier": ("RB",), "source": "9.4 Lead / Iso: tailback follows the lead path"},
    "Inside Zone": {"carrier": BACKS, "source": "9.5 Inside Zone: back presses play-side A/B landmark"},
    "Split Zone": {"carrier": BACKS, "source": "9.6 Split Zone: back keeps normal inside-zone track"},
    "Outside Zone": {"carrier": BACKS, "source": "9.7 Outside Zone: back presses outside leg of TE/tackle"},
    "Pin-Pull": {"carrier": BACKS, "source": "9.8 Pin-Pull: back tracks the pullers"},
    "Trap": {"carrier": BACKS, "source": "9.9 Trap: back path is tight and immediate"},
    "Wham": {"carrier": BACKS, "source": "9.10 Wham: back hits directly off the wham"},
    "Toss": {"carrier": BACKS, "source": "9.11 Toss / Crack: back gains width with depth"},
    "Jet Sweep": {"carrier": ("WR",), "source": "9.12 Jet Sweep: motion player at full speed from 10/11/12 Trips, Trey, Wing, Doubles; 3.4 receivers are taught motion alignments"},
    "Draw": {"carrier": BACKS, "source": "9.13 Draw: back delays, then hits vertical"},
    "QB Sneak": {"carrier": ("QB",), "source": "9.14 QB Sneak / Follow: QB follows predetermined crease"},
    # 13. Access packages: the called run, or the attached immediate throw.
    "Inside + Bubble": {"carrier": BACKS, "target": ("WR",), "source": "13 Access: Inside Zone run; bubble is a receiver screen (12 Bubble)"},
    "Inside + Stick": {"carrier": BACKS, "target": ("WR", "TE"), "source": "13 Access: Inside Zone run; immediate stick to the slot/Y"},
    "Power + Smoke": {"carrier": BACKS, "target": ("WR",), "source": "13 Access: Power run; smoke to the receiver (12 Smoke / Now)"},
    "Zone + Slant": {"carrier": BACKS, "target": ("WR",), "source": "13 Access: Inside/Split Zone run; receiver slant"},
    # A weekly pairing of two taught pieces under the 13 Access rules (one read,
    # the line runs the called run, the throw is immediate): the Inside Zone run
    # and the attached Smoke / Now receiver throw, as in Power + Smoke.
    "Inside + Smoke": {"carrier": BACKS, "target": ("WR",), "source": "13 Access: Inside Zone run (9.5); smoke to the receiver (12 Smoke / Now), attached as in Power + Smoke"},
    # 10. Core pass game: job structures; exact player ownership changes with personnel.
    "Stick": {"target": ANY, "source": "10.1 Stick"},
    "Spacing": {"target": ANY, "source": "10.2 Spacing"},
    "Slant-Flat": {"target": ANY, "source": "10.3 Slant-Flat"},
    "Snag": {"target": ANY, "source": "10.4 Snag"},
    "Smash": {"target": ANY, "source": "10.5 Smash"},
    "Curl-Flat": {"target": ANY, "source": "10.6 Curl-Flat"},
    "Mesh": {"target": ANY, "source": "10.7 Mesh"},
    "Drive": {"target": ANY, "source": "10.8 Drive"},
    "Shallow": {"target": ANY, "source": "10.9 Shallow"},
    "Y-Cross": {"target": ANY, "source": "10.10 Y-Cross"},
    "Levels": {"target": ANY, "source": "10.11 Levels"},
    "Dagger": {"target": ANY, "source": "10.12 Dagger"},
    "Sail": {"target": ANY, "source": "10.13 Sail / Flood"},
    "Flood": {"target": ANY, "source": "10.13 Sail / Flood"},
    "Texas": {"target": ANY, "source": "10.14 Texas / Angle"},
    "Mills": {"target": ANY, "source": "10.15 Mills (Post-Dig)"},
    "Four Verticals": {"target": ANY, "source": "10.16 Four Verticals"},
    "Post-Cross": {"target": ANY, "source": "10.17 Post-Cross"},
    "Choice": {"target": ANY, "source": "10.18 Choice"},
    "Whip": {"target": ANY, "source": "10.19 Whip / Pivot"},
    "Scissors": {"target": ANY, "source": "10.20 Scissors"},
    # 11. Play-action and movement passes.
    "Power Pass": {"target": ANY, "source": "11 Power Pass: Post-Cross or deep corner + flat"},
    "Counter Boot": {"target": ANY, "source": "11 Counter Boot: cross / intermediate sail / flat"},
    "Outside Boot Flood": {"target": ANY, "source": "11 Outside Boot: deep sail / crosser / flat (10.13 Boot Flood)"},
    "Boot Flood": {"target": ANY, "source": "10.13 Sail / Flood (Wing Boot Flood); 11 Outside Boot"},
    "Lead Post": {"target": ANY, "source": "11 Lead Post: post / dig or cross / flat"},
    "Split Leak": {"target": ANY, "source": "11 Split Leak: cross with delayed TE/H leak"},
    "Play-Action Dagger": {"target": ANY, "source": "11 Play-Action Dagger: seam clear + dig"},
    "Sprint Flood": {"target": ANY, "source": "11 Sprint Flood: three-level sideline flood"},
    "Naked Keep": {"carrier": ("QB",), "target": ANY, "source": "11 Naked Keep: QB carries the fake and attacks the edge"},
    # 12. Screen game.
    "RB Slow Screen": {"target": BACKS, "source": "12 RB Slow: back delays then works behind convoy"},
    "RB Slip": {"target": BACKS, "source": "12 RB Slip: back slips through edge/interior"},
    "WR Tunnel": {"target": ("WR",), "source": "12 WR Tunnel / Jail: receiver steps inside behind blockers"},
    "Bubble": {"target": ("WR",), "source": "12 Bubble: immediate perimeter receiver screen"},
    "Smoke/Now": {"target": ("WR",), "source": "12 Smoke / Now: immediate throw to uncovered/off receiver"},
    "TE Delay": {"target": ("TE",), "source": "12 TE Delay: TE shows block, delays, then releases"},
    "Middle Screen": {"target": BACKS, "source": "12 Middle: back works underneath interior rush"},
}

# Alternate spellings used in the book's sample calls and the weekly sheets.
ALIASES = {
    "Inside": "Inside Zone", "Outside": "Outside Zone", "Split": "Split Zone",
    "Trey": "Counter", "GT": "Counter", "Lead/Iso": "Lead", "Lead / Iso": "Lead",
    "Duo Lead": "Duo", "Toss Crack": "Toss", "Crack Toss": "Toss", "Jet": "Jet Sweep",
    "Sneak": "QB Sneak", "QB Follow": "QB Sneak", "Follow": "QB Sneak", "Sneak/Follow": "QB Sneak",
    "Sail/Flood": "Sail", "Texas/Angle": "Texas", "Angle": "Texas", "Post-Dig": "Mills",
    "Mills (Post-Dig)": "Mills", "Vert": "Four Verticals", "Verticals": "Four Verticals",
    "Whip/Pivot": "Whip", "Pivot": "Whip", "Outside Boot": "Outside Boot Flood",
    "RB Slow": "RB Slow Screen", "RB Screen": "RB Slow Screen", "Slow Screen": "RB Slow Screen",
    "Smoke": "Smoke/Now", "Now": "Smoke/Now", "Smoke Now": "Smoke/Now", "Tunnel": "WR Tunnel",
    "Jail": "WR Tunnel", "WR Tunnel/Jail": "WR Tunnel", "Middle": "Middle Screen",
    "Access Bubble": "Bubble", "Bubble Access": "Bubble", "PA Dagger": "Play-Action Dagger",
}


def _key(name):
    return re.sub(r"[^a-z0-9+]", "", str(name or "").lower())


_INDEX = {_key(name): name for name in FAMILIES}
_INDEX.update({_key(alias): target for alias, target in ALIASES.items()})


def family_entry(family):
    """The map entry for a family (aliases resolved), or None."""
    name = _INDEX.get(_key(family))
    return (name, FAMILIES[name]) if name else (None, None)


def _declared(value, allowed, allow_any):
    """Normalise one explicit declaration; raise ValueError when invalid."""
    if isinstance(value, str):
        if value == UNSPECIFIED or (allow_any and value == ANY):
            return value
        value = [value]
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("must be a non-empty list of groups%s or 'unspecified'" % (", 'any'" if allow_any else ""))
    groups = []
    for group in value:
        if group not in allowed:
            raise ValueError("unknown group %r (allowed: %s)" % (group, ", ".join(allowed)))
        if group not in groups:
            groups.append(group)
    return tuple(groups)


def resolve(raw):
    """(carrier, target) declarations for one call-sheet entry.

    Each is a tuple of groups, 'any' (target only), 'unspecified' or None
    when the call's type does not use it. Explicit fields override the
    family map. Raises ValueError naming the problem when neither exists."""
    if isinstance(raw, str):
        raw = {"name": raw, "family": raw}
    family = raw.get("family") or raw.get("concept") or raw.get("name")
    kind = str(raw.get("type") or "any").lower()
    _, entry = family_entry(family)
    out = {}
    for field, allowed, allow_any, needed in (
            ("carrier", RUN_GROUPS, False, kind in ("run", "any", "mixed")),
            ("target", TARGET_GROUPS, True, kind in ("pass", "any", "mixed"))):
        if raw.get(field) is not None:
            try:
                out[field] = _declared(raw[field], allowed, allow_any)
            except ValueError as exc:
                raise ValueError("call %r %s %s" % (raw.get("name") or family, field, exc))
        elif not needed:
            out[field] = None
        elif entry is not None and field in entry:
            value = entry[field]
            out[field] = value if isinstance(value, str) else tuple(value)
        else:
            raise ValueError(
                "call %r (family %r, type %s) has no %s declaration and its family is not in the "
                "2013 call-family map" % (raw.get("name") or family, family, kind, field))
    return out["carrier"], out["target"]


def sheet_errors(sheet):
    """Every fail-closed problem in one offensive call sheet (empty when valid)."""
    errors = []
    for index, raw in enumerate(sheet or ()):
        if not isinstance(raw, (str, dict)):
            errors.append("call %d is not a string or an object" % (index + 1))
            continue
        if isinstance(raw, dict):
            kind = str(raw.get("type") or "any").lower()
            if kind not in ("run", "pass", "any", "mixed"):
                errors.append("call %r has unsupported type %r" % (raw.get("name"), raw.get("type")))
                continue
        try:
            resolve(raw)
        except ValueError as exc:
            errors.append(str(exc))
    return errors
