"""Kernel 2014.6 batch B11: per-play penalty records (R11).

Before 2014.6 a penalty was a counter only: one Bernoulli per scrimmage play
at an unsourced factor, every flag charged to the offence, one randint(5, 10)
yardage per drive, while the replayed real drive's own penalty yardage stayed
folded into its gross passing and rushing yards (defect register item 11). The
2010-2014 drive tuples of the bound calibration base carry each real drive's
penalty clauses (library/data/2010_2014w4_nfl_field_position_model.json, field
``pen``: the hosting row's order, the type's index into ``penalty_types``, the
side relative to the drive's offence, the signed accepted yards, the status
accepted/declined/offsetting, the enforcement on a no-play row (N), after a
counted scrimmage snap (S) or on the drive's kick row (K), the real
first-down-by-penalty flag, the hosting row's kind and the type's nominal
yards); every kick record carries its kick row's clauses (``pen``: type,
kicking or receiving side, yards signed for the receiving club, status). Under
the profile flag ``penalty_records`` those records are replayed, never
decided:

- **Classification (classify).** A no-play row before the drive's last
  scrimmage snap is a movable event (the layout search seats it); a no-play
  row after it is a tail event before the kick (a punt, field goal or clock
  drive: "pre-kick", classified by its position in the drive, plan B11); one
  after the terminal snap of a touchdown, turnover, safety or downs drive, and
  every clause on that terminal snap itself, is enforced after the possession
  (on the kickoff, the try or the next possession, whose start comes from the
  kernel's own transition pools) and is not replayed (counted,
  ``penalty_post_terminal_excluded``). Clauses on a counted scrimmage snap
  ride on a laid-out host snap of their kind; clauses on the drive's own punt
  or field-goal row are not the drive's (the punt row carries the punt
  record's own clauses; a field-goal row's are not modelled, counted
  ``penalty_kick_row_excluded``).
- **Yardage.** The drive's scrimmage free total is its net less its fixed
  snaps less the accepted yards of its replayed records (the 1.6% of real
  drives whose own identity does not hold keep the remainder in the
  scrimmage split, as before). Records keep their real yards: a record is
  placed only where its yards are legal (legal): a defensive foul moves the
  ball at most half the distance to the goal (2 x yards <= spot), a spot
  foul (a type with no nominal yards: defensive pass interference,
  intentional grounding) only needs the new spot in the field,
  an offensive foul at most half the distance to its own goal, and a
  half-distance record (an accepted record the artifact's margin or more
  yards below its type's nominal yards) only where half the distance to the
  goal it moves toward, floor or ceiling in whole yards, equals its yards.
- **First downs.** A defensive foul gives a first down when it is automatic
  for its type (the artifact's two-pass automatic-first-down table; a type
  the table leaves to the record replays the record's own real flag) or its
  yards reach the line to gain; an offensive foul never does. The walk is
  runtime.chains.walk_steps (CHAIN_MODEL ledger-walk-v2).
- **Credit.** Each record's fouler is a group draw on the keyed stream
  public-penalty-detail-v1 (no team id): the group by the artifact's sourced
  type and side shares, then evenly among that side's on-field players of the
  group (runtime.participation.slot_lineup), else evenly among the side's
  on-field players (``fouler_basis`` group_draw or group_fallback); the
  source's unnamed share of a type (its feed named no player) is a club foul
  naming no one (``team``); a kick play's fouler evenly from the play's unit
  (unit_draw). A foul is never
  player evidence. Team counters go to the fouling club (accepted only, the
  NFL convention); declined and offsetting records and the offence's
  first downs by penalty have their own counters. Accept or decline is the
  real record's own (``decision_source`` "replayed"), never a coaching
  choice.

Protagonist-blind by construction: no function here reads a club identity or
which side is the protagonist; the records are anonymous real-drive content
replayed for any club; the credit stream's sub-keys carry no team id.
Individual and club penalty tendencies are slope 0 ("not studied", no
admissible persistence evidence was studied).
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import namedtuple

TAG = "public-penalty-detail-v1"
SCHEMA = "2010-2014w4-nfl-penalties-v1"
MODEL = "penalty-records-v1"
DECISION_SOURCE = "replayed"
GROUP_DRAW = "group_draw"          # evenly from the drawn sourced group's on-field players
GROUP_FALLBACK = "group_fallback"  # the drawn group is not on the field (or the type has no sourced share)
UNIT_DRAW = "unit_draw"            # a kick play's fouler, evenly from that side's unit on the play
TEAM_FOUL = "team"                 # the drawn group is the source's unnamed fouler: charged to the club alone
UNNAMED_GROUP = "unknown"          # the artifact's group for a record whose feed names no fouler

STATUS = {"A": "accepted", "D": "declined", "X": "offsetting"}
STATUS_CODE = {name: code for code, name in STATUS.items()}
NO_PLAY = "no_play"        # a no-play row (the down is replayed)
AFTER_SNAP = "after_snap"  # enforced after a counted scrimmage snap (the host row's list)
PRE_KICK = "pre_kick"      # a no-play row after the drive's last scrimmage snap, before its kick or end
ON_KICK = "on_kick"        # a kick play's clause (already in the kick record's next start)
PENALTY_ROW = "penalty"    # the ledger play_type of a no-play or pre-kick row

# Kernel categories whose last scrimmage snap is the drive's terminal play.
TERMINAL_SNAP_CATEGORIES = ("touchdown", "interception", "fumble_lost", "safety", "downs")
# A record's hosting row kind and the laid-out snap kinds it may ride on.
HOST_KINDS = {"run": ("run",), "complete": ("att", "catch"), "incomplete": ("att",), "sack": ("sack",),
              "interception": ("int",), "qb_kneel": ("kneel",), "qb_spike": ("spike",)}
SNAP_KINDS = ("run", "att", "catch", "int", "sack", "kneel", "spike")
PEN_FIELDS = ("order", "type_code", "side", "signed_yards", "status", "enforce", "first_down", "host",
              "half_distance", "nominal_yards")
KICK_PEN_FIELDS = ("type_code", "side", "signed_yards", "status")

# Named slope-0 terms (no admissible persistence evidence was studied; E1).
TERMS = {"player_penalty_propensity": 0.0, "club_penalty_propensity": 0.0}
TERM_STATUS = "not studied (no admissible persistence evidence)"


class PenaltyError(ValueError):
    """A penalty artifact or record the runtime cannot read."""


# One replayed clause of a drive. `rid` is its index in the tuple's list;
# `yards` its accepted signed yards (0 unless accepted); `auto` whether an
# accepted defensive record is a first down by rule (resolved); `half` a
# half-distance record; `spot_foul` a spot foul (a type with no nominal yards).
Rec = namedtuple("Rec", "rid order type_code type side yards status enforce real_fd host nominal auto half spot_foul")
# A no-play or pre-kick row of one replayed drive: its records (in row
# order), `before` its real order among the drive's scrimmage snaps.
Event = namedtuple("Event", "eid order records tail before")
# Clauses on one counted scrimmage snap: the host kind and its records.
Attach = namedtuple("Attach", "aid order host records before")


def stream(seed, event_id, *subkey):
    """The keyed public-penalty-detail-v1 stream of one drive's records
    ("drive", n), one kick ("kick", k) or one punt ("punt", n): credit only,
    never the possession, chain-layout, snap-detail, label or ball-security
    stream. No team id."""
    payload = json.dumps([TAG, event_id, *subkey], separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(seed + payload).digest(), "big"))


class PenaltyModel:
    """The base's penalty artifact (library/data/2010_2014w4_penalties.json,
    scripts/research/build_2010_2014_penalties.py --check): the
    automatic-first-down classes, the half-distance types, the sourced fouler
    group shares and the band centres. Every value is read, never typed."""

    def __init__(self, data, penalty_types):
        if data.get("schema") != SCHEMA:
            raise PenaltyError("penalty artifact schema %r" % data.get("schema"))
        if list(data.get("penalty_types") or ()) != list(penalty_types or ()):
            raise PenaltyError("the penalty artifact's type vocabulary differs from the field-position artifact's")
        self.data = data
        self.types = list(penalty_types)
        classes = data["auto_first_down"]["types"]
        self.auto_class = {}
        for name, entry in classes.items():
            cls = entry["class"]
            if cls not in ("automatic", "yardage", "replay"):
                raise PenaltyError("automatic-first-down class %r for %s" % (cls, name))
            self.auto_class[name] = cls
        # A record this many yards or more below its type's nominal yards is a
        # half-distance enforcement (the artifact's measured rule).
        self.reduced_below = int(data["half_distance"]["reduced_below_nominal"])
        if self.reduced_below < 1:
            raise PenaltyError("half-distance rule %r" % self.reduced_below)
        self.groups = {}
        for key, counts in data["fouler_groups"]["shares"].items():
            side, name = key.split("|", 1)
            self.groups[(side, name)] = {g: int(n) for g, n in counts.items() if int(n) > 0}
        self.centres = data["band_centres"]

    def type_name(self, code):
        try:
            return self.types[int(code)]
        except (IndexError, TypeError, ValueError):
            raise PenaltyError("penalty type code %r" % (code,)) from None

    def auto(self, name, real_fd):
        """Whether an accepted defensive record of this type is a first down
        by rule: automatic, yardage only, or (a type the table leaves to the
        record, or a type absent from it) the record's own real flag."""
        cls = self.auto_class.get(name, "replay")
        if cls == "automatic":
            return True
        if cls == "yardage":
            return False
        return bool(real_fd)

    def record(self, rid, raw):
        """A tuple's raw clause as a Rec."""
        if len(raw) < 8:
            raise PenaltyError("penalty record %r" % (raw,))
        entry = dict(zip(PEN_FIELDS, raw))
        name = self.type_name(entry["type_code"])
        side, status = entry["side"], entry["status"]
        if side not in ("O", "D") or status not in STATUS or entry["enforce"] not in ("N", "S", "K"):
            raise PenaltyError("penalty record %r" % (raw,))
        yards = int(entry["signed_yards"] or 0) if status == "A" else 0
        if status == "A" and ((side == "D" and yards < 0) or (side == "O" and yards > 0)):
            raise PenaltyError("penalty record %r: yards against the fouling side's sign" % (raw,))
        nominal = entry.get("nominal_yards")
        auto = status == "A" and side == "D" and self.auto(name, entry["first_down"])
        half = status == "A" and nominal is not None and int(nominal) - abs(yards) >= self.reduced_below
        # A type with no dominant accepted yardage (no nominal yards: the
        # artifact's own annotation rule) is a spot foul: defensive pass
        # interference, intentional grounding and the rare personal fouls
        # without a nominal; it only needs a new spot in the field.
        return Rec(rid, int(entry["order"]), int(entry["type_code"]), name, side, yards, status, entry["enforce"],
                   bool(entry["first_down"]), entry["host"], nominal, bool(auto), bool(half),
                   status == "A" and nominal is None)

    def fouler_group(self, side, name, u):
        """The fouler's position group by the sourced shares of this type and
        side (u a uniform), or None when the artifact holds no share for it."""
        counts = self.groups.get((side, name))
        if not counts:
            return None
        total = sum(counts.values())
        acc = 0.0
        for group in sorted(counts):
            acc += counts[group] / total
            if u < acc:
                return group
        return sorted(counts)[-1]


DrivePlan = namedtuple("DrivePlan", "events attached post kick_row records yards")


def classify(model, pen, category, plays):
    """Split one tuple's clauses into the replayed drive's events (module
    docstring). `category` is the tuple's own category (clock for every
    window-ending drive), `plays` its scrimmage snaps."""
    recs = [model.record(i, raw) for i, raw in enumerate(pen or ())]
    rows = {}
    for r in recs:
        rows.setdefault(r.order, []).append(r)
    no_play = sorted(o for o, rs in rows.items() if rs[0].enforce == "N")
    events, attached, post, kick_row = [], [], [], []
    terminal_snap = category in TERMINAL_SNAP_CATEGORIES
    for order in sorted(rows):
        rs = tuple(rows[order])
        enforce = rs[0].enforce
        if any(r.enforce != enforce for r in rs):
            raise PenaltyError("one row holds clauses of two enforcements")
        before = order - sum(1 for o in no_play if o < order)
        if enforce == "K":
            kick_row.extend(rs)
        elif enforce == "N":
            if before >= plays:
                if terminal_snap:
                    post.extend(rs)
                else:
                    events.append(Event(len(events), order, rs, True, before))
            else:
                events.append(Event(len(events), order, rs, False, before))
        else:
            if terminal_snap and before >= plays - 1:
                post.extend(rs)
            else:
                attached.append(Attach(len(attached), order, rs[0].host, rs, before))
    replayed = [r for e in events for r in e.records] + [r for a in attached for r in a.records]
    return DrivePlan(tuple(events), tuple(attached), tuple(post), tuple(kick_row),
                     tuple(sorted(replayed, key=lambda r: r.rid)), sum(r.yards for r in replayed))


def compiled(records):
    """(accepted signed yards, automatic first down, the record a first down
    credits: the automatic record, else the accepted defensive record with the
    most yards) of one row's records, the walk's view
    (runtime.chains.walk_steps)."""
    yards = sum(r.yards for r in records)
    auto = next((i for i, r in enumerate(records) if r.status == "A" and r.side == "D" and r.auto), None)
    best = None
    for i, r in enumerate(records):
        if r.status == "A" and r.side == "D" and (best is None or r.yards > records[best].yards):
            best = i
    return yards, auto is not None, auto if auto is not None else best


def _legal(clauses, spot):
    """The enforcement rule over (accepted signed yards, side O/D, half
    distance, spot foul) clauses in row order (legal, legal_entries)."""
    s = int(spot)
    for y, side, half, spot_foul in clauses:
        if half:
            distance = s if side == "D" else 100 - s
            if abs(y) not in (distance // 2, (distance + 1) // 2):
                return False
        elif spot_foul:
            pass  # only the new spot in the field (below)
        elif y > 0:
            if 2 * y > s:
                return False
        elif y < 0 and 2 * -y > 100 - s:
            return False
        s -= y
        if not 1 <= s <= 99:
            return False
    return True


def legal(records, spot):
    """Whether one row's records may be enforced from `spot` (module
    docstring): each accepted record with yards, in row order, from the spot
    the earlier ones leave; the new spot stays in the field."""
    return _legal(((r.yards, r.side, r.half, r.spot_foul) for r in records if r.status == "A"), spot)


def legal_entries(entries, spot):
    """legal over one ledger row's published entries (the audit's view)."""
    return _legal(((int(e.get("penalty_yards") or 0), "O" if e.get("penalty_side") == "offense" else "D",
                    bool(e.get("half_distance")), bool(e.get("spot_foul")))
                   for e in entries if e.get("status") == "accepted"), spot)


def static_summary(plan):
    """What the static gates read from a plan (runtime.chains.chain_feasible's
    penalty branch and relocation_ok): the accepted records' net yards; the
    pre-kick (tail) rows' accepted yards; the offensive yards and defensive
    yards of the rows the search may seat anywhere (movable rows and clauses
    on snaps); how many of those can give a first down without a snap, how
    many by rule; and every accepted record's (yards, half, spot foul, side)."""
    tail = [r for e in plan.events if e.tail for r in e.records if r.status == "A"]
    movable = ([r for e in plan.events if not e.tail for r in e.records if r.status == "A"]
               + [r for a in plan.attached for r in a.records if r.status == "A"])
    records = tuple((r.yards, r.half, r.spot_foul, r.side) for r in plan.records if r.status == "A")
    # A movable defensive record that can be a first down before the first
    # snap (automatic, or at least the opening ten): the largest such yards.
    openers = [r.yards for r in movable if r.side == "D" and (r.auto or r.yards >= 10)]
    return {"yards": plan.yards, "tail_yards": sum(r.yards for r in tail),
            "off_movable": sum(-r.yards for r in movable if r.yards < 0),
            "def_movable": sum(r.yards for r in movable if r.yards > 0),
            "def_nonauto": sum(r.yards for r in movable if r.yards > 0 and not r.auto),
            "def_tail": sum(r.yards for r in tail if r.yards > 0),
            "opener": max(openers) if openers else None,
            "resetters": sum(1 for r in movable if r.side == "D" and (r.yards > 0 or r.auto)),
            "auto_movable": sum(1 for r in movable if r.auto),
            "records": records, "events": len(plan.events), "tail": sum(1 for e in plan.events if e.tail)}


def relocation_ok(summary, *, spot, end, sacks, runs, run_loss):
    """The static relocation gate (a necessary condition under the kernel's
    value model): every accepted record needs a legal spot inside the band
    the replay can reach. The band runs from the nearer of its start and end
    less every backward step the drive can take, to the deeper of them plus
    those steps (its offensive penalty yards, ten yards per sack, the
    kernel's sack-loss bound, and `run_loss` per run, the base's largest
    sourced run loss), inside the 1 to the 99."""
    back = (sum(-y for y, _, _, side in summary["records"] if y < 0) + 10 * int(sacks)
            + int(run_loss) * int(runs))
    low, high = sorted((int(spot), int(end)))
    nearest, deepest = max(1, low - back), min(99, high + back)
    for record in summary["records"]:
        lo, hi = _window(*record)
        if max(lo, nearest) > min(hi, deepest):
            return False
    return True


def _window(y, half, spot_foul, side):
    """The spots (yards from the goal line) from which one accepted record is
    legal (legal), as a closed interval."""
    if y > 0 or side == "D":
        if spot_foul:
            return y + 1, 99
        if half:
            return max(1, 2 * y - 1), 2 * y + 1
        return 2 * y, 99
    a = -y
    if spot_foul:
        return 1, 99 - a
    if half:
        return 100 - 2 * a - 1, 100 - 2 * a + 1
    return 1, 100 - 2 * a


def needs_excursion(summary, *, spot, end):
    """Whether some accepted record is legal only outside the drive's own
    path (its start to its end): the replay must first carry the ball there
    and back (the tuple gate's excursion rule, FieldPositionModelV3
    .static_feasible)."""
    low, high = sorted((int(spot), int(end)))
    for record in summary["records"]:
        lo, hi = _window(*record)
        if hi < low or lo > high:
            return True
    return False


# ---- publication ------------------------------------------------------------------------

def side_name(side):
    return "offense" if side == "O" else "defense"


def published(rec, *, offense, defense, enforcement, first_down=False):
    """A record as a ledger entry (its fouler is named by name_fouler)."""
    entry = {"penalty_type": rec.type, "penalty_side": side_name(rec.side),
             "team": offense if rec.side == "O" else defense, "status": STATUS[rec.status],
             "penalty_yards": int(rec.yards), "enforcement": enforcement, "first_down": bool(first_down),
             "decision_source": DECISION_SOURCE, "fouler": None, "fouler_basis": None}
    if rec.side == "D" and rec.status == "A":
        entry["auto_first_down"] = bool(rec.auto)
    if rec.half:
        entry["half_distance"] = True
    if rec.spot_foul:
        entry["spot_foul"] = True
    return entry


def kick_records(model, pen, *, kicking, receiving):
    """A kick record's clauses as ledger entries: side kicking or receiving,
    yards signed for the receiving club as the record stores them (already
    in its next start), the fouling club charged."""
    out = []
    for raw in pen or ():
        entry = dict(zip(KICK_PEN_FIELDS, raw))
        side, status = entry["side"], entry["status"]
        if side not in ("K", "R") or status not in STATUS:
            raise PenaltyError("kick penalty record %r" % (raw,))
        yards = int(entry["signed_yards"] or 0) if status == "A" else 0
        out.append({"penalty_type": model.type_name(entry["type_code"]),
                    "penalty_side": "kicking" if side == "K" else "receiving",
                    "team": kicking if side == "K" else receiving, "status": STATUS[status],
                    "penalty_yards": yards, "enforcement": ON_KICK, "first_down": False,
                    "decision_source": DECISION_SOURCE, "fouler": None, "fouler_basis": None})
    return out


def charged_yards(entry):
    """The yards a published accepted record charges its fouling club."""
    return abs(int(entry.get("penalty_yards") or 0)) if entry.get("status") == "accepted" else 0


def name_fouler(rng, model, entry, side_players):
    """Name one scrimmage record's fouler: the group by the sourced shares
    (one uniform), then evenly among the side's on-field players of that
    group, else evenly among the side's on-field players. The source's
    unnamed share (a record whose feed names no player, the artifact's
    "unknown" group: a twelve-men or team delay foul, mostly) names no one:
    the foul is the club's alone (fouler_basis "team"). `side_players` is
    the fouling side's on-field list (unique players)."""
    side = "O" if entry["penalty_side"] == "offense" else "D"
    u = rng.random()
    group = model.fouler_group(side, entry["penalty_type"], u)
    if group == UNNAMED_GROUP:
        entry["fouler"], entry["fouler_basis"] = None, TEAM_FOUL
        return None
    from . import usage
    members = [p for p in side_players if usage.group(p.position) == group] if group else []
    if members:
        pick, basis = members[rng.randrange(len(members))], GROUP_DRAW
    elif side_players:
        pick, basis = side_players[rng.randrange(len(side_players))], GROUP_FALLBACK
    else:
        pick, basis = None, None
    entry["fouler"] = pick.player_id if pick is not None else None
    entry["fouler_basis"] = basis
    return pick


def name_kick_fouler(rng, entry, unit_ids):
    """Name one kick record's fouler evenly from the fouling side's unit on
    the play (player ids)."""
    ids = [pid for pid in unit_ids if pid]
    entry["fouler"] = ids[rng.randrange(len(ids))] if ids else None
    entry["fouler_basis"] = UNIT_DRAW if ids else None
    return entry["fouler"]


TEAM_FIELDS = ("penalties_declined", "penalties_offsetting", "penalty_first_downs")
PLAYER_FIELDS = ("penalties", "penalty_yards")


def charge(entry, stats):
    """Charge one published record to its fouling club (team counters) and
    its fouler (player counters): accepted records count and charge their
    yards; declined and offsetting records their own counters."""
    line = stats.get(entry.get("team"))
    if line is None:
        return
    status = entry.get("status")
    if status == "accepted":
        line["penalties"] += 1
        line["penalty_yards"] += charged_yards(entry)
        fouler = entry.get("fouler")
        if fouler and fouler in line["players"]:
            player = line["players"][fouler]
            player["penalties"] = player.get("penalties", 0) + 1
            player["penalty_yards"] = player.get("penalty_yards", 0) + charged_yards(entry)
    elif status == "declined":
        line["penalties_declined"] = line.get("penalties_declined", 0) + 1
    elif status == "offsetting":
        line["penalties_offsetting"] = line.get("penalties_offsetting", 0) + 1


ENTRY_KEYS = ("penalty_type", "penalty_side", "team", "status", "penalty_yards", "enforcement", "first_down",
              "decision_source", "fouler", "fouler_basis")
SCRIMMAGE_SIDES = ("offense", "defense")
KICK_SIDES = ("kicking", "receiving")
FOULER_BASES = (GROUP_DRAW, GROUP_FALLBACK, UNIT_DRAW)


def entry_errors(entry, *, offense, defense, kick=False):
    """What is malformed about one published entry (an empty list when
    nothing is): its keys, side, club, status, yards against the fouling
    side's sign, enforcement, first-down flag and fouler basis. On a kick
    row `offense` is the kicking club and `defense` the receiving one."""
    if not isinstance(entry, dict) or any(k not in entry for k in ENTRY_KEYS):
        return ["missing keys"]
    out = []
    sides = KICK_SIDES if kick else SCRIMMAGE_SIDES
    side, status, yards = entry["penalty_side"], entry["status"], entry["penalty_yards"]
    if side not in sides:
        out.append("side %r" % side)
    elif entry["team"] != (offense if side == sides[0] else defense):
        out.append("club %r for side %s" % (entry["team"], side))
    if status not in STATUS_CODE:
        out.append("status %r" % status)
    if not isinstance(yards, int) or isinstance(yards, bool):
        out.append("yards %r" % (yards,))
    elif status != "accepted" and yards:
        out.append("%s record with yards" % status)
    elif not kick and status == "accepted" and ((side == "defense" and yards < 0) or (side == "offense" and yards > 0)):
        out.append("yards against the fouling side")
    elif kick and status == "accepted" and ((side == "kicking" and yards < 0) or (side == "receiving" and yards > 0)):
        out.append("yards against the fouling side")
    allowed = (ON_KICK,) if kick else (NO_PLAY, AFTER_SNAP, PRE_KICK)
    if entry["enforcement"] not in allowed:
        out.append("enforcement %r" % entry["enforcement"])
    if entry["first_down"] and (kick or side != "defense" or status != "accepted"):
        out.append("first down on a record that cannot give one")
    if entry["decision_source"] != DECISION_SOURCE:
        out.append("decision source %r" % entry["decision_source"])
    basis = entry["fouler_basis"]
    if basis == TEAM_FOUL:
        if entry["fouler"] is not None or kick:
            out.append("a club foul naming a player")
    elif basis not in FOULER_BASES + (None,) or (entry["fouler"] is None) != (basis is None):
        out.append("fouler basis %r" % basis)
    return out


def summary_of(entries, offense):
    """A possession's or kick's compact penalty summary (ledger-free
    reconciliation): per fouling club [accepted, charged yards, declined,
    offsetting], the net accepted yards signed for the offense (a drive) and
    the first downs by penalty."""
    clubs = {}
    net = 0
    first_downs = 0
    for e in entries:
        row = clubs.setdefault(e["team"], [0, 0, 0, 0])
        status = e.get("status")
        if status == "accepted":
            row[0] += 1
            row[1] += charged_yards(e)
            if e.get("enforcement") != ON_KICK:
                net += int(e.get("penalty_yards") or 0)
        elif status == "declined":
            row[2] += 1
        elif status == "offsetting":
            row[3] += 1
        first_downs += bool(e.get("first_down"))
    return {"clubs": {k: clubs[k] for k in sorted(clubs)}, "net": net, "first_downs": first_downs,
            "offense": offense}
