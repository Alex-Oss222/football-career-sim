"""Kernel 2014.6 batch B10: ball security (W4 muffs; R12 layers A, B and C).

The fumbles themselves come from the replayed real drives and kick records of
the bound calibration base (library/data/2010_2014w4_nfl_field_position_model.json):
every drive tuple carries its own fumbles (snap order, kind, host play, outcome,
forced, the forcer's and recoverer's position groups, whether the recoverer was
the forcer or the fumbler) and every kick record its muff or return fumble
(kind, outcome, the muffer's role). This module supplies the rest from the
base's ball-security artifact (library/data/2010_2014w4_ball_security.json,
built by scripts/research/build_2010_2014_ball_security.py with a --check mode
and pinned as the base's ``ball_security`` role): the band centres and the
sourced shares the credit draws read.

Three layers, each under its own profile flag (runtime.profiles):

- **W4 and layer A (credit only, ``ball_security_credit``).** A muffed kick
  names its muffer by the record's role (the club's returner by the
  deterministic depth rule, a group draw from the return unit for "other");
  every kept or out-of-bounds scrimmage fumble of the replayed drive is
  seated on the laid-out snap of its kind nearest its stored order (never a
  terminal snap, a kneel or a spike); forcers and recoverers come from the
  side-aware on-field sets (runtime.participation.slot_lineup for scrimmage
  snaps, runtime.participation.kick for kick plays, so exposure is
  identical); a forced fumble's tackle is the forcer's. Every name carries an
  attribution and none is player evidence (E1).
- **Layer B (``fumble_terminal_kind``).** A lost fumble's terminal snap kind
  comes from the tuple's own lost entry (terminal_kind), not the snap-count
  draw; an aborted snap is carried by the quarterback or the centre.
- **Layer C (``retained_kicks``).** The kick and punt pools hold the kicking
  club's recoveries at their real frequency; the turnover is the receiving
  club's and the next possession the kicking club's (batch B8's sequencing).

Protagonist-blind by construction: no function here reads a club identity,
and the credit stream's literal sub-keys ("kick", k), ("scrim", drive) and
("punt", drive) carry no team id (an AST test checks the module reads no
team_id). The named slope-0 terms below are "not studied (admissible
2010-2012 evidence exists)": no player's history moves a fumble, a muff or a
forced fumble.
"""
from __future__ import annotations

import hashlib
import json
import random

TAG = "public-ball-security-v1"
SCHEMA = "2010-2014w4-nfl-ball-security-v1"
MODEL = "ball-security-v1"

# Attribution of every name a ball-security record carries (never player evidence).
CARRIER = "carrier"          # the snap's own ball carrier, target or passer (deterministic)
RUSHER = "rusher"            # the sack's own rusher (the sourced forcer of a forced sack fumble)
RETURNER = "returner"        # the club's returner by the deterministic depth rule (a recorded role)
CONVENTION = "convention"    # a labelled convention (an unrecorded muffer named the returner)
FUMBLER = "fumbler"          # recovered by the player who fumbled (the record's flag or the sourced share)
FORCER = "forcer"            # recovered by the forcer (the record's flag or the sourced share)
COVERAGE = "coverage_tackler"  # a kick fumble forced by the play's coverage tackler
GROUP_DRAW = "group_draw"    # evenly from the record's (or the sourced) position group on the field
GROUP_FALLBACK = "group_fallback"  # the group is not on the field: evenly from the side's on-field players
SOURCED_SHARE = "sourced_share"  # a forced/unforced or quarterback/centre choice drawn at a sourced share

# Named slope-0 terms (no admissible persistence evidence was studied; E1).
TERMS = {
    "carrier_ball_security": 0.0,   # the ball carrier's own fumbling
    "returner_muffs": 0.0,          # the returner's own muffing
    "defender_forcing": 0.0,        # the defender's own forcing
}
TERM_STATUS = "not studied (admissible 2010-2012 evidence exists)"

SCRIMMAGE_KINDS = ("run", "reception", "sack", "aborted")
DEFENSE_GROUPS = ("DL", "LB", "DB")
# Layer B: the layout kind of a lost entry's kind (an aborted snap by its host play).
LAYOUT_KIND = {"run": "run", "reception": "catch", "sack": "sack"}
ABORTED_HOST_KIND = {"sack": "sack", "complete": "catch"}
# The layout kinds a kept fumble of each kind may be seated on (attempt or catch
# snaps must be completed for a reception).
FUMBLE_FIELDS = ("snap_order", "kind", "host", "outcome", "forced", "forcer_group", "recoverer_group",
                 "recoverer_is_forcer", "recoverer_is_fumbler")


class BallSecurityError(ValueError):
    """A ball-security artifact the runtime cannot read."""


def stream(seed, event_id, *subkey):
    """The keyed public-ball-security-v1 stream of one kick ("kick", k), one
    drive's scrimmage fumbles ("scrim", drive) or one punt ("punt", drive):
    credit only, never the possession, chain-layout, snap-detail, label or
    kickoff stream. No team id."""
    payload = json.dumps([TAG, event_id, *subkey], separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))


def entries(fumbles):
    """The scrimmage entries of a tuple's fumble list as dicts (a kick-play
    entry, the drive's own punt or field-goal snap, belongs to its kick record
    or is not modelled, and is left out)."""
    out = []
    for raw in fumbles or ():
        entry = dict(zip(FUMBLE_FIELDS, raw))
        if entry["kind"] in SCRIMMAGE_KINDS:
            out.append(entry)
    return out


def lost_entry(fumbles):
    """The tuple's lost scrimmage fumble (the drive's terminal), or None."""
    lost = [e for e in entries(fumbles) if e["outcome"] == "lost"]
    return lost[-1] if lost else None


def terminal_kind(entry):
    """Layer B: the layout kind of a lost entry (run, catch or sack; an aborted
    snap by its host play: a sack host is a sack, a completed host a catch,
    otherwise a run carried by the quarterback or the centre), or None."""
    if entry is None:
        return None
    if entry["kind"] == "aborted":
        return ABORTED_HOST_KIND.get(entry.get("host"), "run")
    return LAYOUT_KIND.get(entry["kind"])


def scrimmage_index(entry, pen):
    """An entry's stored order among the real drive's scrimmage snaps: its
    order among the drive's rows less the no-play rows before it that the
    tuple records (its penalty records on no-play rows, by their own order).
    A no-play row without a penalty (a timeout or a two-minute warning in the
    feed) is not recorded, so the index can run past the drive's last snap;
    seat_kept bounds it there."""
    no_play = {p[0] for p in pen or () if len(p) > 7 and p[7] == "no_play"}
    order = int(entry["snap_order"])
    return order - sum(1 for o in no_play if o < order)


def candidate(kind, host, layout_kind, completed):
    """Whether a laid-out snap may hold a kept fumble of that kind."""
    if kind == "run":
        return layout_kind == "run"
    if kind == "reception":
        return layout_kind in ("att", "catch") and completed
    if kind == "sack":
        return layout_kind == "sack"
    # An aborted snap: its host play's kind first (seat_kept falls back).
    if host == "run":
        return layout_kind == "run"
    if host == "sack":
        return layout_kind == "sack"
    return layout_kind in ("att", "catch")


def seat_kept(sources, kinds, completed, terminal_index, diagnostics=None):
    """Seat every kept or out-of-bounds scrimmage fumble of a laid-out drive.

    `sources` lists the replayed real drives the snaps come from: (offset,
    kept snaps, the tuple's fumble list, its penalty records, its laid-out
    snaps), a single drive or batch B9F's segments (a four-item source keeps
    all its snaps). Each entry's stored order (scrimmage_index, bounded by
    the replayed drive's last snap) plus the segment's offset is its target;
    it goes to the laid-out snap of its kind (candidate) nearest the target
    (ties to the earlier snap), never the terminal snap, a kneel, a spike or
    a snap already holding one; an aborted snap with no host-kind snap takes
    the nearest scrimmage snap (counted kept_fumble_kind_fallback); an entry
    beyond a segment's kept snaps was cut at a fourth-down decision
    (kept_fumble_cut); one with no legal snap is left unseated
    (kept_fumble_unseated). Deterministic: no draw."""
    diagnostics = diagnostics if diagnostics is not None else {}
    used = set()
    out = []

    def bump(name):
        diagnostics[name] = diagnostics.get(name, 0) + 1

    def legal(i):
        return i != terminal_index and kinds[i] not in ("kneel", "spike") and i not in used

    for source in sources:
        offset, length, fumbles, pen = source[:4]
        full = source[4] if len(source) > 4 else length
        for entry in entries(fumbles):
            if entry["outcome"] == "lost":
                continue
            local = min(scrimmage_index(entry, pen), max(full - 1, 0))
            if local >= length:
                bump("kept_fumble_cut")
                continue
            target = offset + local
            span = range(offset, offset + length)
            pool = [i for i in span if legal(i) and candidate(entry["kind"], entry.get("host"), kinds[i], completed[i])]
            if not pool and entry["kind"] == "aborted":
                pool = [i for i in span if legal(i) and kinds[i] in ("run", "att", "catch", "sack")]
                if pool:
                    bump("kept_fumble_kind_fallback")
            if not pool:
                bump("kept_fumble_unseated")
                continue
            index = min(pool, key=lambda i: (abs(i - target), i))
            used.add(index)
            out.append((entry, index))
    return out


def _pair(value):
    k, n = int(value[0]), int(value[1])
    if n < 0 or not 0 <= k <= max(n, 0):
        raise BallSecurityError("invalid count pair %r" % (value,))
    return k, n


def _p(pair):
    k, n = pair
    return k / n if n else 0.0


class BallSecurityModel:
    """The base's ball-security artifact: band centres and the sourced
    credit shares (every value read, never typed)."""

    def __init__(self, data):
        if data.get("schema") != SCHEMA:
            raise BallSecurityError("ball-security artifact schema %r" % data.get("schema"))
        self.data = data
        self.centres = data["band_centres"]
        credit = data["credit_shares"]
        aborted = credit["aborted_fumbler"]
        qb, line = int(aborted["QB"]), int(aborted["OL"])
        if qb + line <= 0:
            raise BallSecurityError("no aborted-snap fumbler counts")
        # An aborted snap is the quarterback's or the centre's (the other
        # groups' few are left with the quarterback, labelled).
        self.p_centre_aborted = line / (qb + line + int(aborted.get("other", 0)))
        self.kick = {kind: {name: _pair(v[name]) for name in ("forced", "kept_self", "lost_forcer_recovers")}
                     for kind, v in credit["kick"].items()}
        self.scrimmage = {}
        for kind, v in credit["scrimmage"].items():
            self.scrimmage[kind] = {
                "lost_forced": _pair(v["lost_forced"]), "forcer_recovers": _pair(v["forcer_recovers"]),
                "forcer_group": {g: int(n) for g, n in v["forcer_group"].items()},
                "lost_recoverer_group": {g: int(n) for g, n in v["lost_recoverer_group"].items()},
            }

    # -- shares ------------------------------------------------------------------------------

    def p_kick(self, kind, name):
        """A kick fumble's sourced share: kind "muff" or "return"; name
        forced, kept_self or lost_forcer_recovers."""
        return _p(self.kick[kind][name])

    def synthetic_entry(self, kind, rng):
        """A lost scrimmage entry for a fumble the replayed drive does not
        describe (a fourth-down attempt's fumble, batch B9F): forced at the
        kind's sourced share, the forcer's and the recoverer's groups drawn by
        the sourced group counts, the forcer recovering at its share. Four
        uniforms are always drawn."""
        shares = self.scrimmage[kind]
        u_forced, u_group, u_recovers, u_recoverer = rng.random(), rng.random(), rng.random(), rng.random()
        forced = u_forced < _p(shares["lost_forced"])
        recovers = forced and u_recovers < _p(shares["forcer_recovers"])
        return {"snap_order": None, "kind": kind, "host": None, "outcome": "lost", "forced": int(forced),
                "forcer_group": _weighted(shares["forcer_group"], u_group) if forced else None,
                "recoverer_group": _weighted(shares["lost_recoverer_group"], u_recoverer),
                "recoverer_is_forcer": int(recovers), "recoverer_is_fumbler": 0, "synthetic": True}


def _weighted(counts, u):
    total = sum(counts.values())
    if total <= 0:
        return None
    acc = 0.0
    for group in sorted(counts):
        acc += counts[group] / total
        if u < acc:
            return group
    return sorted(counts)[-1]


def even(rng, players):
    """One player of a non-empty list, evenly (a labelled convention: no
    sourced within-group share exists)."""
    return players[rng.randrange(len(players))]
