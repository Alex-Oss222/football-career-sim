"""In-season roster rails for the 31 background clubs (2014 onward).

The other clubs' real in-season roster moves are committed, append-only, in
`library/data/YEAR_inseason_rails/` (manifest, base, one shard per effective
week; `library/YEAR_inseason_rails.md` documents the sources and the two
passes). This module replays them over the Week 1 depth-chart library and
returns each background club's state at a cutoff date. It is pure: it reads
only the committed rails data, the Week 1 library and the branch inputs the
caller passes (Jacksonville control by gsis, branch injuries already reduced
to projected returns). It never reads the schedule inside `league_state`, an
opponent, a score or a real injury, and the kernel, the game runner and the
packets never import it.

Rules (user-approved "hold, never invent", library/2014_inseason_rails.md):

- C1 every background club is held to 53 on the active list and 10 on the
  practice squad (the practice-squad count only where that club's base is
  verified); reserve lists do not count.
- C2 replay order: league-wide, by (replay date, gate date, phase, kind,
  move id). Phase 0 departures, retirements and branch reserve placements;
  phase 1 additions (own practice-squad promotion, claim, signing, poach,
  practice-squad signing); phase 2 fills of held places until nothing
  changes, active queues before practice-squad queues, oldest first. No club
  code is in any sort key.
- C3 a real addition with no open place is held: the player stays where the
  branch has him (on the practice squad he was on, or, if he was a free
  agent, signed by his real club and awaiting a place; never a free agent).
- C4 a freed place goes to the oldest held addition whose precondition still
  holds; a hold lapses when the player's own later applied move overtakes it.
- C5 a real injury, suspension or exempt placement never touches membership:
  the player stays at his branch slot, available unless a branch injury says
  otherwise; injury-driven releases are not applied.
- C6 a background player whose branch injury, in a game before the season's
  last regular-season date, projects a return after that date goes on his
  club's branch reserve list the day after the game; Jacksonville's reserve
  moves stay its own.
- C7 a club above 53 at the base keeps its players and holds additions until
  real departures bring it below 53. Nobody is released to correct it.

Newcomers enter at the bottom of their kernel group (group's highest depth
plus one; same-date newcomers by move id); departures leave gaps and no
incumbent is re-ranked. Only the Week 1 chart rides the rails as depth.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

from .usage import group, lineup_errors, MINIMUM_GAME_DAY

ROOT = Path(__file__).resolve().parents[1]
PROTAGONIST = "Jacksonville Jaguars"
PROTAGONIST_CODE = "JAX"
SCHEMA_VERSION = 1
LIMITS = {"active": 53, "practice_squad": 10}
LAYERS = ("active", "practice_squad", "reserve", "held")

# The fixed move-kind list. Effect: (action, layer).
KINDS = {
    "waived": ("depart", "active"),
    "released": ("depart", "active"),
    "trade_out": ("depart", "active"),
    "ps_release": ("depart", "practice_squad"),
    "released_unspecified": ("depart", "any"),
    "retirement": ("retire", None),
    "ps_promotion": ("add", "active"),
    "waiver_claim": ("add", "active"),
    "trade_in": ("add", "active"),
    "fa_signing": ("add", "active"),
    "re_signing": ("add", "active"),
    "activation_return": ("add", "active"),
    "ps_poach": ("add", "active"),
    "ps_signing": ("add", "practice_squad"),
    # Inert kinds: never touch membership (rails rule 2, C5).
    "injury_reserve": ("inert", None),
    "injury_release": ("inert", None),
    "injury_activation": ("inert", None),
    "suspension": ("inert", None),
    "availability": ("inert", None),
    "contract": ("inert", None),
    "administrative": ("inert", None),
}
ADD_RANK = {"ps_promotion": 0, "waiver_claim": 1, "trade_in": 1, "fa_signing": 2, "re_signing": 2,
            "activation_return": 2, "ps_poach": 3, "ps_signing": 4}
OUTCOMES = {
    "APPLY", "NOT_APPLIED_INJURY", "NOT_APPLIED_SUSPENSION", "NOT_APPLIED_AVAILABILITY",
    "NOT_APPLIED_JAX_CONTROL", "NOT_APPLIED_REAL_JAGUARS", "NOT_APPLIED_PRECONDITION",
    "NO_ROSTER_EFFECT", "REVIEW_UNPLACED", "REVIEW_SOURCE_CONFLICT", "REVIEW_IDENTITY",
    "EXCLUDED_SOURCE_ERROR", "EXCLUDED_SOURCE_CONFLICT",
}
# Rows committed without player identity or entry text (rules review C6):
# real injuries, suspensions and availability, and every Jacksonville or
# real-Jaguars row. They are inert by construction.
STRIPPED_OUTCOMES = {"NOT_APPLIED_INJURY", "NOT_APPLIED_SUSPENSION", "NOT_APPLIED_AVAILABILITY",
                     "NOT_APPLIED_JAX_CONTROL", "NOT_APPLIED_REAL_JAGUARS"}
STRIPPED_FIELDS = ("id", "gate_date", "club", "outcome", "effective_from_week", "source_pages")
# The closed list of reasons a departure may find nothing to remove.
NOOP_REASONS = {
    "excluded_from_base": "on the real Week 1 roster but excluded from the branch base (Jacksonville control, unplaced, or placed elsewhere by the branch)",
    "earlier_addition_not_applied": "his earlier addition to this club was held, not applied or failed its precondition",
    "ps_base_unverified": "the club's practice-squad base is not verified, so its practice-squad layer is incomplete",
    "already_departed": "already off this layer in the branch",
    "branch_placed_elsewhere": "the branch has him on another club",
    "never_in_branch": "a real departure of a player the branch base never carried (listed in the base evidence)",
}
ROLE_SECOND = {"kick_return": "KR2", "punt_return": "PR2", "placekicker": "K2", "punt": "P2"}
ROLE_OF_SPECIALIST = {"K": "placekicker", "P": "punt"}


def _d(value):
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def data_dir(season, root=ROOT):
    from .seasons import SeasonPaths
    return SeasonPaths(int(season), root).inseason_rails


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clubs_block_sha256(library):
    """sha256 of the Week 1 library's clubs block (canonical JSON)."""
    return hashlib.sha256(json.dumps(library["clubs"], sort_keys=True, separators=(",", ":"))
                          .encode("utf-8")).hexdigest()


# ---- data --------------------------------------------------------------------

@dataclass
class Rails:
    season: int
    manifest: dict
    base: dict
    rows: list
    library: dict
    codes: dict  # club name -> code
    root: Path = ROOT
    labels: dict = field(default_factory=dict)  # club -> builder-labelled no-op departures (closed list)

    @property
    def effective_from_week(self):
        return int(self.manifest["effective_from_week"])

    @property
    def as_of(self):
        return _d(self.manifest["as_of"])

    def name_of(self, code):
        for name, c in self.codes.items():
            if c == code:
                return name
        raise KeyError(code)


def load(season, root=ROOT):
    """The season's committed rails data, or None when the season has none."""
    folder = data_dir(season, root)
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        return None
    return _load(str(folder), str(root))


@lru_cache(maxsize=4)
def _load(folder, root):
    folder, root = Path(folder), Path(root)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported in-season rails schema")
    base = json.loads((folder / manifest["base"]["path"]).read_text(encoding="utf-8"))
    rows, labels = [], {}
    for shard in manifest["shards"]:
        data = json.loads((folder / shard["path"]).read_text(encoding="utf-8"))
        rows.extend(data["rows"])
        for code, entries in data.get("noop_labels", {}).items():
            labels.setdefault(code, []).extend(entries)
    library = json.loads((root / manifest["base"]["library"]).read_text(encoding="utf-8"))
    codes = {name: club["code"] for name, club in library["clubs"].items()}
    return Rails(int(manifest["season"]), manifest, base, rows, library, codes, root, labels)


def from_parts(manifest, base, rows, library, root=ROOT, labels=None):
    """A Rails object from in-memory parts (tests and the builder)."""
    codes = {name: club["code"] for name, club in library["clubs"].items()}
    return Rails(int(manifest["season"]), manifest, base, list(rows), library, codes, Path(root), dict(labels or {}))


def effective(season, week, root=ROOT):
    rails = load(season, root)
    return rails is not None and int(week) >= rails.effective_from_week


# ---- dates -------------------------------------------------------------------

def slate_cutoffs(games, protagonist=PROTAGONIST):
    """{event key: cutoff date} for one week's slate.

    The freeze date is the information gate's game day: Jacksonville's game,
    or the slate's first date on a bye. A game's cutoff is the day before the
    earlier of its own date and the freeze date, so a move dated on a club's
    game day applies from its next game (no time of day is established) and
    nothing after the clock at the build is read. The same rule for every
    club; on a Jacksonville Thursday game or a bye every later game's cutoff
    moves back to the day before the freeze date.
    """
    ours = [g for g in games if protagonist in (g["away"], g["home"])]
    freeze = _d((ours or sorted(games, key=lambda g: g["date"]))[0]["date"])
    out = {}
    for g in games:
        out[game_key(g)] = min(_d(g["date"]), freeze) - timedelta(days=1)
    return out


def game_key(game):
    return "%s|%s|%s" % (game["date"], game["away"], game["home"])


def replay_date(row, last_cutoffs):
    """max(gate date, last cutoff of the week before the row's effective
    week + 1 day): a row found late, an amendment or a branch event never
    changes a closed week's state (engineering review B5)."""
    gate = _d(row["gate_date"])
    efw = int(row["effective_from_week"])
    if efw <= 1:
        return gate
    prior = last_cutoffs.get(efw - 1)
    if prior is None:
        # A truncated map would replay a later week's row inside an earlier
        # week (engineering review, late-found rows): fail closed.
        raise ValueError("replay date of %s: no last cutoff for Week %d (pass every scheduled week's, "
                         "runtime.week_inputs.season_last_cutoffs)" % (row.get("id"), efw - 1))
    return max(gate, prior + timedelta(days=1))


# ---- identity ----------------------------------------------------------------

_NORM = re.compile(r"[^a-z]")


def norm(name):
    """The Week 1 builder's name normalization (letters only, lower case)."""
    return _NORM.sub("", str(name).split(" (")[0].lower())


# ---- Jacksonville control ----------------------------------------------------

# One definition of a roster Status that shows club control, shared with the
# weekly exclusivity gate (scripts/check_week_input_exclusivity.py): the
# status alone or followed by one dated parenthetical, e.g.
# "Active 53 (signed August 31, 2014)".
CONTROLLED_STATUS = re.compile(
    r"^(?:Active 53|Offseason roster|Practice squad|Injured reserve|IR|Reserve(?:/[^|(]+?)?|"
    r"PUP|NFI|Suspended|Commissioner(?:/[^|(]+?)?)\s*(?:\([^|]*\))?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Control:
    """Jacksonville control by gsis id: uid -> ((start, end), ...), each a
    half-open interval with None for an open end. `departures` holds every
    in-season departure: uid -> ((end, disposition), ...), where the
    disposition is ("unplaced", ()), ("follows", (row id, ...)) or None when
    the roster records none yet (method section 3)."""
    intervals: dict
    retirement_names: frozenset = frozenset()
    names: dict = field(default_factory=dict)  # uid -> roster name
    departures: dict = field(default_factory=dict)

    def controlled(self, uid, on):
        on = _d(on)
        for start, end in self.intervals.get(uid, ()):
            if (start is None or on >= start) and (end is None or on < end):
                return True
        return False

    def controlled_ids(self, on):
        return {uid for uid in self.intervals if self.controlled(uid, on)}

    def acquisitions(self):
        """(date, uid) for every control interval that starts in the season."""
        return sorted((start, uid) for uid, spans in self.intervals.items()
                      for start, _ in spans if start is not None)

    def departure_before(self, uid, on):
        """(end, disposition) of the player's latest in-season departure on
        or before `on`, or None."""
        on = _d(on)
        found = [d for d in self.departures.get(uid, ()) if d[0] <= on]
        return max(found, key=lambda d: d[0]) if found else None


# A control start is the first acquisition in a Status parenthetical with the
# full date in the same clause; a promotion or a reserve placement happens
# inside Jacksonville control and starts nothing.
_ACQUIRED = re.compile(r"\b(?:signed|re-signed|claimed|acquired|traded)\b", re.IGNORECASE)
_LONG_DATE = re.compile(r"[A-Z][a-z]+ \d{1,2}, \d{4}")
_DEPARTED = re.compile(r"\b(?:Waived|Released|Traded|withdrawn|Contract expired|Not tendered|Retired)\b[^;]*?"
                       r"([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)")
_ROW_ID = re.compile(r"\bR\d{2}-\d{4}\b")


def _parse_long_date(text, year):
    text = text if "," in text else "%s, %d" % (text, year)
    return datetime.strptime(text, "%B %d, %Y").date()


def _status_start(status, season_start):
    """(start, error): the in-season start of control a Status shows (None
    when undated or before the season), or an error when it names an
    acquisition without a full date."""
    paren = status[status.find("("):] if "(" in status else ""
    m = _ACQUIRED.search(paren)
    if not m:
        return None, None
    clause = re.split(r"[;)]", paren[m.end():], maxsplit=1)[0]
    when = _LONG_DATE.search(clause)
    if not when:
        return None, "an acquisition with no full date"
    start = datetime.strptime(when.group(0), "%B %d, %Y").date()
    return (start if start >= season_start else None), None


def _disposition(text):
    """A Departures "Rails disposition" cell as data: ("follows", row ids)
    when it names the real rows the player follows (the same kind of move in
    the same window), ("unplaced", ()) when it starts "Unplaced", otherwise
    None (pending or missing)."""
    if not text:
        return None
    ids = tuple(_ROW_ID.findall(text))
    if ids:
        return ("follows", ids)
    if text.strip().lower().startswith("unplaced"):
        return ("unplaced", ())
    return None


def _tables(text):
    """Yield (row dict, heading year or None) for every table row with a
    Player column."""
    columns, year = None, None
    for line in text.splitlines():
        heading = re.match(r"^###\s+.*?(\d{4})", line)
        if heading:
            year = int(heading.group(1))
        if not line.startswith("|"):
            columns = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Player" in cells:
            columns = cells
            continue
        if columns is None or set(cells[0]) <= {"-", ":"} or len(cells) != len(columns):
            continue
        yield dict(zip(columns, cells)), year


def jacksonville_control(season, root=ROOT, registry=None):
    """Dated Jacksonville control intervals by gsis id (engineering review S4).

    Read from the season roster's dated history, which survives departures:
    - every current row with a Status column must show club control
      (CONTROLLED_STATUS, the exclusivity gate's definition), else the build
      fails; it is controlled from its dated acquisition in the season
      (signed, re-signed, claimed, acquired or traded, with a full date), or
      from before the season when undated, with no end;
    - every Departures row ends control on the first dated action in its
      "How control ended" cell. An in-season departure (ended on or after
      September 1) must carry a dated "Control began" cell, and its "Rails
      disposition" cell is kept for the same-kind, same-window rule;
    - a player with several rows keeps every interval (released and later
      re-signed); overlapping intervals, or a current row with no dated start
      after an in-season departure, fail closed.
    gsis ids come from `library/data/player_birth_dates.json`; an unresolved
    or duplicated id fails closed.
    """
    from .seasons import SeasonPaths
    from . import player_bios
    registry = player_bios.load(root) if registry is None else registry
    text = SeasonPaths(int(season), root).roster.read_text(encoding="utf-8")
    current, departed = text.split("\n## Departures", 1) if "\n## Departures" in text else (text, "")
    departed = re.split(r"^## ", departed, maxsplit=1, flags=re.M)[0]
    season_start = date(int(season), 9, 1)
    intervals, names, departures, errors = {}, {}, {}, []
    dated_current = {}

    def uid_for(name):
        row = registry.get(name)
        if not row or not row.get("gsis_id"):
            errors.append("Jacksonville control: no gsis id for %s" % name)
            return None
        return row["gsis_id"]

    for row, _ in _tables(current):
        if "Status" not in row:
            continue
        status = row["Status"]
        if not CONTROLLED_STATUS.match(status):
            errors.append("Jacksonville control: %s's Status %r shows no club control" % (row["Player"], status))
            continue
        uid = uid_for(row["Player"])
        if uid is None:
            continue
        start, problem = _status_start(status, season_start)
        if problem:
            errors.append("Jacksonville control: %s's Status names %s" % (row["Player"], problem))
            continue
        if uid in names and names[uid] != row["Player"]:
            errors.append("Jacksonville control: gsis %s is two roster names" % uid)
        names[uid] = row["Player"]
        dated_current[uid] = start
        intervals.setdefault(uid, []).append((start, None))
    for row, year in _tables(departed):
        how = row.get("How control ended", "")
        m = _DEPARTED.search(how)
        if not m:
            continue
        uid = uid_for(row["Player"])
        if uid is None:
            continue
        end = _parse_long_date(m.group(1), year or int(season))
        start = None
        began = row.get("Control began")
        if began is not None:
            when = _LONG_DATE.search(began)
            if when:
                start = datetime.strptime(when.group(0), "%B %d, %Y").date()
                start = start if start >= season_start else None
            elif end >= season_start:
                errors.append("Jacksonville control: %s's in-season departure has no dated 'Control began'"
                              % row["Player"])
        elif end >= season_start:
            errors.append("Jacksonville control: %s's in-season departure has no 'Control began' column"
                          % row["Player"])
        if end >= season_start:
            departures.setdefault(uid, []).append((end, _disposition(row.get("Rails disposition"))))
            if uid in dated_current and dated_current[uid] is None:
                errors.append("Jacksonville control: %s is back on the roster after an in-season departure "
                              "with no dated acquisition" % row["Player"])
        names.setdefault(uid, row["Player"])
        intervals.setdefault(uid, []).append((start, end))
    for uid, spans in intervals.items():
        ordered = sorted(spans, key=lambda s: (s[0] or date.min))
        for (s1, e1), (s2, e2) in zip(ordered, ordered[1:]):
            if e1 is None or (s2 or date.min) < e1:
                errors.append("Jacksonville control: %s has overlapping control intervals" % names.get(uid, uid))
                break
    if errors:
        raise ValueError("; ".join(sorted(set(errors))))
    retired = set()
    retire_path = SeasonPaths(int(season), root).record("league/personnel/retirements.md")
    if retire_path.is_file():
        for line in retire_path.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[3].lower().startswith("yes"):
                retired.add(re.sub(r",\s*[A-Z]+$", "", cells[1]).strip())
    return Control({k: tuple(v) for k, v in intervals.items()}, frozenset(retired), names,
                   {k: tuple(sorted(v, key=lambda d: d[0])) for k, v in departures.items()})


# ---- branch inputs ------------------------------------------------------------

@dataclass(frozen=True)
class Branch:
    control: Control
    events: tuple = ()  # branch events: C6 placements, emergency promotions


def c6_events(returns, last_regular_date, last_cutoffs, week_of_game, first_week=1, protagonist=PROTAGONIST):
    """Branch reserve placements (C6) from projected returns.

    `returns` is the shared projection (runtime.week_inputs.projected_returns):
    each row names the player, his club, the game date and the projected
    return date. A background player projected back after the season's last
    regular-season date goes on his club's branch reserve list the day after
    the game, effective from the week after the game (and never before the
    rails' first week, so a placement from a closed week joins the first
    batch in its date order). An injury in a game on or after the last
    regular-season date (the final Sunday or any postseason game) never
    places anyone: a return days later is not season-ending, and the
    projection already holds him out. Reads only branch injuries;
    Jacksonville is never touched.
    """
    out = []
    last = _d(last_regular_date)
    for r in returns:
        played = _d(r["played"])
        if r["team"] == protagonist or _d(r["back"]) <= last or played >= last:
            continue
        efw = max(int(week_of_game(r)) + 1, int(first_week))
        ev = {"id": "C6|%s|%s" % (played.isoformat(), r["player"]), "kind": "branch_reserve",
              "team": r["team"], "player_id": r["player"], "gate_date": (played + timedelta(days=1)).isoformat(),
              "effective_from_week": efw, "reason": "branch injury projected back %s, after %s" % (
                  _d(r["back"]).isoformat(), last.isoformat())}
        out.append(ev)
    return out


# ---- state -------------------------------------------------------------------

class State:
    """One league-wide replay result at a cutoff."""

    def __init__(self, cutoff):
        self.cutoff = cutoff
        self.clubs = {}        # code -> {"active": [...], "practice_squad": [...], "reserve": [...]}
        self.held = {}         # code -> {"active": [hold...], "practice_squad": [hold...]}
        self.where = {}        # uid -> (code, layer)
        self.held_by = {}      # uid -> (code, layer, hold)
        self.retired = set()
        self.carry = {}        # code -> active count above 53 at the base (C7)
        self.ps_verified = {}  # code -> bool
        self.log = []
        self.errors = []
        self.ids = {}          # uid -> player_id
        self.unplaced = frozenset()
        self.status = {}       # uid -> (available, return_week): Week 1 status travels with him

    # -- queries
    def layer(self, code, name):
        return self.clubs[code][name]

    def count(self, code, name):
        return len(self.clubs[code][name])

    def has_room(self, code, name):
        if name == "practice_squad" and not self.ps_verified.get(code):
            return True
        return self.count(code, name) < LIMITS[name]

    def find(self, uid):
        return self.where.get(uid)

    def record(self, uid):
        loc = self.where.get(uid)
        if not loc or loc[1] == "held":
            return None
        for p in self.clubs[loc[0]][loc[1]]:
            if p["uid"] == uid:
                return p
        return None

    def note(self, when, ref, code, action, uid, reason=""):
        self.log.append({"date": _d(when).isoformat(), "ref": ref, "club": code, "action": action,
                         "uid": uid, "player_id": self.ids.get(uid), "reason": reason})

    # -- views
    def club_entry(self, code):
        """The club's active layer in the Week 1 library's club schema."""
        players = []
        for p in self.clubs[code]["active"]:
            row = {"player_id": p["player_id"], "position": p["position"], "depth": p["depth"],
                   "gsis_id": p.get("gsis_id")}
            if p.get("roles"):
                row["roles"] = list(p["roles"])
            if p.get("available") is False:
                row["available"] = False
                if p.get("return_week"):
                    row["return_week"] = p["return_week"]
            players.append(row)
        return {"code": code, "players": players}

    def summary(self):
        return {code: {"active": [p["uid"] for p in c["active"]],
                       "depth": {p["uid"]: p["depth"] for p in c["active"]},
                       "practice_squad": sorted(p["uid"] for p in c["practice_squad"]),
                       "reserve": sorted(p["uid"] for p in c["reserve"]),
                       "held": [h["uid"] for h in self.held[code]["active"] + self.held[code]["practice_squad"]]}
                for code, c in sorted(self.clubs.items())}

    def digest(self):
        return hashlib.sha256(json.dumps(self.summary(), sort_keys=True, separators=(",", ":"))
                              .encode("utf-8")).hexdigest()


def _player(row, *, uid, depth, since, via, available=True, return_week=None, roles=(), slots=""):
    position = row["position"]
    return {"uid": uid, "gsis_id": uid if re.match(r"^\d{2}-\d{7}$", uid or "") else None,
            "player_id": row["player_id"], "position": position, "group": group(position),
            "depth": depth, "roles": list(roles), "available": available, "return_week": return_week,
            "slots": slots, "since": since, "via": via}


def _next_depth(players, grp):
    depths = [p["depth"] for p in players if p["group"] == grp and isinstance(p["depth"], int)]
    return (max(depths) + 1) if depths else 1


def base_state(rails, cutoff):
    """The base: the Week 1 library, the dated base corrections and
    restorations (all effective from the rails' first week), and the
    practice-squad base."""
    state = State(cutoff)
    state.unplaced = frozenset(rails.base.get("unplaced_former_jaguars", ()))
    base_clubs = rails.base["clubs"]
    for name, club in rails.library["clubs"].items():
        code = club["code"]
        state.clubs[code] = {"active": [], "practice_squad": [], "reserve": []}
        state.held[code] = {"active": [], "practice_squad": []}
        info = base_clubs.get(code, {})
        state.ps_verified[code] = bool(info.get("ps_base_verified"))
        for p in club["players"]:
            uid = p.get("gsis_id") or ("name:" + p["player_id"])
            rec = _player(p, uid=uid, depth=p["depth"], since=None, via="week1_library",
                          available=p.get("available", True), return_week=p.get("return_week"),
                          roles=p.get("roles", ()), slots=p.get("slots", ""))
            state.clubs[code]["active"].append(rec)
            if uid in state.where:
                state.errors.append("base: %s on two clubs" % uid)
            state.where[uid] = (code, "active")
            state.ids[uid] = p["player_id"]
    library_week1 = {uid: state.record(uid) for uid in state.where}
    # Dated corrections and restorations, in their committed order.
    for corr in rails.base.get("corrections", ()):
        code = corr["club"]
        uid = corr["uid"]
        if corr["action"] == "remove":
            rec = state.record(uid)
            if rec is None or state.where[uid][0] != code:
                state.errors.append("base correction %s: %s not on %s" % (corr["id"], uid, code))
                continue
            state.clubs[code]["active"].remove(rec)
            state.where.pop(uid)
            state.note(corr["date"], corr["id"], code, "base_remove", uid, corr.get("reason", ""))
        elif corr["action"] == "add":
            if uid in state.where:
                state.errors.append("base correction %s: %s already on %s" % (corr["id"], uid, state.where[uid][0]))
                continue
            players = state.clubs[code]["active"]
            prior = library_week1.get(uid)
            rec = _player(corr, uid=uid, depth=_next_depth(players, group(corr["position"])),
                          since=corr["date"], via=corr["id"],
                          available=prior["available"] if prior else corr.get("available", True),
                          return_week=prior["return_week"] if prior else corr.get("return_week"))
            players.append(rec)
            state.where[uid] = (code, "active")
            state.ids[uid] = corr["player_id"]
            state.note(corr["date"], corr["id"], code, "base_add", uid, corr.get("reason", ""))
        else:
            raise ValueError("unknown base correction action %r" % corr["action"])
    for code, info in base_clubs.items():
        for p in info.get("practice_squad", ()):
            uid = p["uid"]
            if uid in state.where:
                # The Week 1 chart (later than September 1) wins (engineering B3).
                state.note(p["since"], "ps_base", code, "ps_base_skipped_on_chart", uid)
                continue
            rec = _player(p, uid=uid, depth=None, since=p["since"], via="ps_base")
            state.clubs[code]["practice_squad"].append(rec)
            state.where[uid] = (code, "practice_squad")
            state.ids[uid] = p["player_id"]
    for code, c in state.clubs.items():
        state.carry[code] = max(0, len(c["active"]) - LIMITS["active"])
    return state


# ---- replay ------------------------------------------------------------------

def _events(rails, branch, cutoff, last_cutoffs):
    """Every applicable row and branch event with replay date <= cutoff."""
    out = []
    for row in rails.rows:
        if row.get("outcome") != "APPLY":
            continue
        kind = row["kind"]
        action = KINDS[kind][0]
        if action == "inert":
            continue
        when = replay_date(row, last_cutoffs)
        if when > cutoff:
            continue
        phase = 0 if action in ("depart", "retire") else 1
        out.append(((when, _d(row["gate_date"]), phase, ADD_RANK.get(kind, 0), row["id"]), "row", row))
    for ev in branch.events:
        when = replay_date(ev, last_cutoffs)
        if when > cutoff:
            continue
        phase = 0 if ev["kind"] in ("branch_reserve", "jax_acquired") else 1
        out.append(((when, _d(ev["gate_date"]), phase, 9, ev["id"]), "branch", ev))
    for start, uid in branch.control.acquisitions():
        if start <= cutoff:
            ev = {"id": "JAX|%s|%s" % (start.isoformat(), uid), "kind": "jax_acquired", "uid": uid,
                  "gate_date": start.isoformat(), "effective_from_week": 0}
            out.append(((start, start, 0, 0, ev["id"]), "branch", ev))
    out.sort(key=lambda item: item[0])
    return out


def league_state(rails, cutoff, branch, last_cutoffs):
    """The league-wide state at `cutoff` (a date): every background club's
    active list, practice squad, reserve list and held queue.

    `last_cutoffs` maps a week to its last cutoff date (the schedule only
    picks the dates; the replay never reads which club plays whom)."""
    cutoff = _d(cutoff)
    state = base_state(rails, cutoff)
    window = {code: _d(info["base_as_of"]["active"]) for code, info in rails.base["clubs"].items()}
    events = _events(rails, branch, cutoff, last_cutoffs)
    i = 0
    while i < len(events):
        group_key = events[i][0][:2]
        j = i
        while j < len(events) and events[j][0][:2] == group_key:
            j += 1
        for _, source, item in events[i:j]:
            if source == "row":
                _apply_row(state, rails, branch, item, group_key[0], window)
            else:
                _apply_branch(state, rails, branch, item, group_key[0])
        _fill(state, branch, group_key[0])
        i = j
    check_rails_state(state, branch)
    return state


def _remove(state, uid):
    loc = state.where.pop(uid, None)
    if loc is None:
        return None
    code, layer = loc
    if layer == "held":
        return None
    rec = None
    for p in list(state.clubs[code][layer]):
        if p["uid"] == uid:
            state.clubs[code][layer].remove(p)
            rec = p
            break
    if rec is not None:
        state.status[uid] = (rec.get("available", True), rec.get("return_week"))
    if rec is not None and layer == "active":
        _pass_roles(state, code, rec)
    if uid in state.held_by:
        # Off his old squad while another club holds him: signed by that
        # club, awaiting a place (rules review B3).
        state.where[uid] = (state.held_by[uid][0], "held")
    return rec


def _pass_roles(state, code, leaver):
    """A departing role-holder's role passes to the club's Week 1 second
    string for it (KR2, PR2, K2, P2) when he is still on the active list;
    otherwise nobody holds it and the kernel default applies."""
    for role in leaver.get("roles", ()):
        if any(role in p["roles"] for p in state.clubs[code]["active"]):
            continue
        slot = ROLE_SECOND.get(role)
        heir = next((p for p in state.clubs[code]["active"]
                     if slot and slot in str(p.get("slots", "")).split(",")), None)
        if heir is not None:
            heir["roles"].append(role)


def _cancel_hold(state, uid):
    held = state.held_by.pop(uid, None)
    if held is None:
        return None
    code, layer, hold = held
    state.held[code][layer].remove(hold)
    if state.where.get(uid) == (code, "held"):
        state.where.pop(uid)
    return held


def _carry_availability(state, uid):
    """A player's Week 1 availability (return_week) travels with his gsis id
    through every move, a spell as a free agent included (rules C12)."""
    rec = state.record(uid)
    if rec is None:
        return state.status.get(uid, (True, None))
    return rec.get("available", True), rec.get("return_week")


def _join(state, code, layer, uid, info, when, ref):
    """Move a player onto `layer` of `code` (taking him off every other
    layer of every club and out of any hold); he enters at the bottom of his
    group."""
    available, return_week = _carry_availability(state, uid)
    _cancel_hold(state, uid)
    _remove(state, uid)
    state.retired.discard(uid)  # un-retirement is the player's choice: his later real signing applies
    players = state.clubs[code][layer]
    grp = group(info["position"])
    depth = _next_depth(players, grp) if layer == "active" else None
    rec = _player(info, uid=uid, depth=depth, since=_d(when).isoformat(), via=ref,
                  available=available, return_week=return_week)
    if layer == "active":
        role = ROLE_OF_SPECIALIST.get(grp)
        if role and not any(role in p["roles"] for p in players):
            rec["roles"].append(role)
    players.append(rec)
    state.where[uid] = (code, layer)
    state.ids[uid] = info["player_id"]


def _hold(state, code, layer, uid, info, when, ref):
    _cancel_hold(state, uid)
    state.retired.discard(uid)  # a returning retiree's held signing stands until it fills
    hold = {"uid": uid, "info": info, "since": _d(when).isoformat(), "ref": ref, "layer": layer}
    state.held[code][layer].append(hold)
    state.held_by[uid] = (code, layer, hold)
    if uid not in state.where:
        # A held free agent is signed by his real club, awaiting a place
        # (rules review B3); a held practice-squad player stays on his squad.
        state.where[uid] = (code, "held")
    state.ids[uid] = info["player_id"]


def _info(row):
    return {"player_id": row["player_id"], "position": row["position"]}


def _effective_outcome(state, rails, branch, row, when):
    """Recompute the outcome at replay (engineering review S4).

    - A retirement applies league-wide, Jacksonville included, whoever filed
      it (rails rule 5, method section 5): it is checked first.
    - A real Jaguars move never happens (rails rule 4).
    - A move involving a player Jacksonville controls on the row's date or on
      its replay date does not apply.
    - A former Jaguar follows a later real move only when it is the same
      kind of move in the same window (rails rule 6, method section 3): the
      branch's pre-season departures are the base's frozen unplaced list; an
      in-season departure's roster disposition either names the real rows he
      follows or makes him unplaced. A later row with no recorded disposition
      fails the build."""
    uid = row["uid"]
    if row["kind"] == "retirement":
        return "APPLY"
    if row["club"] == PROTAGONIST_CODE or row.get("counterparty") == PROTAGONIST_CODE:
        return "NOT_APPLIED_REAL_JAGUARS"
    if branch.control.controlled(uid, row["gate_date"]) or branch.control.controlled(uid, when):
        return "NOT_APPLIED_JAX_CONTROL"
    if uid in state.unplaced:
        return "REVIEW_UNPLACED"
    departure = branch.control.departure_before(uid, row["gate_date"])
    if departure is not None:
        end, disposition = departure
        if disposition is None:
            state.errors.append("%s: %s left Jacksonville control on %s and the roster records no rails "
                                "disposition for his later real moves (method section 3)"
                                % (row["id"], row.get("player_id") or uid, end.isoformat()))
            return "REVIEW_UNPLACED"
        if disposition[0] == "unplaced":
            return "REVIEW_UNPLACED"
        named = disposition[1]
        if row["id"] in named:
            return "APPLY"
        if any(e["uid"] == uid and e["ref"] in named for e in state.log):
            return "APPLY"  # back on the rails once he has followed his real move
        return "REVIEW_UNPLACED"
    return "APPLY"


def _apply_row(state, rails, branch, row, when, window):
    uid, code, kind = row["uid"], row["club"], row["kind"]
    action, layer = KINDS[kind]
    outcome = _effective_outcome(state, rails, branch, row, when)
    if outcome != "APPLY":
        state.note(when, row["id"], code, "not_applied", uid, outcome)
        return
    state.ids.setdefault(uid, row["player_id"])
    # The club's base window: the Week 1 library reflects its active list as
    # of base_as_of, and every contradiction is an explicit dated base
    # correction (engineering B3), so a row inside the window touches only
    # the other layers (rules B1: no stored per-row membership flag).
    in_window = code in window and _d(row["gate_date"]) <= window[code]
    if action == "retire":
        if branch.control.controlled(uid, row["gate_date"]) or branch.control.controlled(uid, when):
            # Jacksonville's player: the retirement record owns its date and
            # its contract effects; without it the build fails closed.
            name = branch.control.names.get(uid, row["player_id"])
            if name not in branch.control.retirement_names:
                state.errors.append("retirement %s: Jacksonville-controlled %s has no retirements.md row"
                                    % (row["id"], name))
                return
            _cancel_hold(state, uid)
            state.retired.add(uid)
            state.note(when, row["id"], code, "retired_jacksonville", uid, "recorded in retirements.md")
            return
        loc = state.where.get(uid)
        _cancel_hold(state, uid)
        _remove(state, uid)
        state.retired.add(uid)
        state.note(when, row["id"], loc[0] if loc else code, "retired", uid)
        return
    if action == "depart":
        _depart(state, rails, row, when, layer, in_window)
        return
    cur = state.where.get(uid)
    if in_window and layer == "active":
        if cur and cur[1] == "practice_squad":
            _remove(state, uid)
        state.note(when, row["id"], code, "in_base", uid)
        return
    if cur == (code, layer):
        state.note(when, row["id"], code, "already_there", uid)
        return
    if cur and cur[1] in ("active", "reserve"):
        # On a 53 or a reserve list (his own club's or another's): a real
        # move the branch's divergence makes impossible.
        state.note(when, row["id"], code, "not_applied", uid,
                   "NOT_APPLIED_PRECONDITION: on %s %s" % cur)
        return
    if cur and cur[1] == "practice_squad" and row.get("after_real_jaguars") and \
            (layer == "practice_squad" or kind == "ps_poach"):
        # In reality he left that squad only through a real Jaguars move the
        # branch never made (rails rule 4): no release by his branch club
        # happened, so none is implied.
        state.note(when, row["id"], code, "not_applied", uid,
                   "NOT_APPLIED_PRECONDITION: on %s %s; he left it in reality only through a real Jaguars move" % cur)
        return
    if cur and cur[1] == "practice_squad" and layer == "practice_squad":
        # A real practice-squad signing of a player the branch has on another
        # club's squad: that club released him (the wire omits practice-squad
        # terminations, a recorded coverage gap), so the release is implied by
        # the real signing, never invented.
        _remove(state, uid)
        state.note(when, row["id"], cur[0], "implied_ps_release", uid, "released before his %s signing" % code)
    if state.has_room(code, layer):
        _join(state, code, layer, uid, _info(row), when, row["id"])
        state.note(when, row["id"], code, "added_" + layer, uid)
    else:
        _hold(state, code, layer, uid, _info(row), when, row["id"])
        state.note(when, row["id"], code, "held_" + layer, uid)


def _depart(state, rails, row, when, layer, in_window):
    """An applied real departure: the player leaves his club (whichever of
    its layers the branch has him on; a practice-squad release only the
    practice squad) and any hold that club has on him. A departure that finds
    nothing is a no-op only with a reason from the closed list (engineering
    B4)."""
    uid, code = row["uid"], row["club"]
    layers = ("practice_squad",) if layer == "practice_squad" else ("active", "practice_squad")
    done = False
    held = state.held_by.get(uid)
    if held and held[0] == code:
        _cancel_hold(state, uid)
        state.note(when, row["id"], code, "hold_lapsed", uid)
        done = True
    loc = state.where.get(uid)
    if loc and loc[0] == code and loc[1] in layers + ("reserve",):
        if in_window and loc[1] == "active":
            state.note(when, row["id"], code, "in_base", uid)
            return
        _remove(state, uid)
        state.note(when, row["id"], code, "removed_" + loc[1], uid)
        return
    if done:
        return
    if in_window and layer != "practice_squad":
        state.note(when, row["id"], code, "in_base", uid)
        return
    reason = _noop_reason(state, rails, row, layers)
    if reason is None:
        state.errors.append("unexplained no-op: %s %s %s %s" % (row["id"], code, row["kind"], row["player_id"]))
        reason = "unexplained"
    state.note(when, row["id"], code, "noop", uid, reason)


def _noop_reason(state, rails, row, layers):
    uid, code = row["uid"], row["club"]
    info = rails.base["clubs"].get(code, {})
    if uid in {p["uid"] for p in info.get("fill_excluded", ())}:
        return "excluded_from_base"
    if uid in {e["uid"] for e in rails.labels.get(code, ())}:
        return "never_in_branch"
    loc = state.where.get(uid)
    if loc and loc[0] != code:
        return "branch_placed_elsewhere"
    earlier = [e for e in state.log if e["uid"] == uid and e["club"] == code]
    if any(e["action"] in ("not_applied", "held_active", "held_practice_squad", "hold_lapsed") for e in earlier):
        return "earlier_addition_not_applied"
    if any(e["action"].startswith("removed_") or e["action"] in ("base_remove",) for e in earlier):
        return "already_departed"
    if (row["kind"] in ("ps_release", "released_unspecified")) and not state.ps_verified.get(code):
        return "ps_base_unverified"
    return None


def _apply_branch(state, rails, branch, ev, when):
    kind = ev["kind"]
    if kind == "jax_acquired":
        uid = ev["uid"]
        held = _cancel_hold(state, uid)
        loc = state.where.get(uid)
        if loc:
            _remove(state, uid)
            state.note(when, ev["id"], loc[0], "to_jacksonville", uid)
        elif held:
            state.note(when, ev["id"], held[0], "to_jacksonville", uid)
        return
    code = ev.get("club") or rails.codes.get(ev.get("team"), ev.get("team"))
    if code not in state.clubs:
        return
    if kind == "branch_reserve":
        rec = next((p for p in state.clubs[code]["active"] if p["player_id"] == ev["player_id"]), None)
        if rec is None:
            state.note(when, ev["id"], code, "noop", None, "branch reserve: not on the active list")
            return
        _remove(state, rec["uid"])
        rec["depth"] = None
        state.clubs[code]["reserve"].append(rec)
        state.where[rec["uid"]] = (code, "reserve")
        state.note(when, ev["id"], code, "branch_reserve", rec["uid"], ev.get("reason", ""))
        return
    if kind == "emergency_promotion":
        uid = ev["uid"]
        if ev.get("reserve_uid"):
            rec = state.record(ev["reserve_uid"])
            if rec is not None and state.where[ev["reserve_uid"]] == (code, "active"):
                _remove(state, ev["reserve_uid"])
                rec["depth"] = None
                state.clubs[code]["reserve"].append(rec)
                state.where[ev["reserve_uid"]] = (code, "reserve")
                state.note(when, ev["id"], code, "branch_reserve", ev["reserve_uid"], "emergency room")
        swap = bool(ev.get("reserve_uid")) and state.where.get(ev["reserve_uid"]) == (code, "reserve")
        ceiling = LIMITS["active"] + state.carry.get(code, 0)
        if not state.has_room(code, "active") and not (swap and state.count(code, "active") < ceiling):
            # A carry-over club (C7) swaps one for one, staying at or below
            # its own base count; nobody is released to make room.
            state.errors.append("emergency promotion %s: %s has no open place" % (ev["id"], code))
            return
        info = {"player_id": ev["player_id"], "position": ev["position"]}
        _join(state, code, "active", uid, info, when, ev["id"])
        state.note(when, ev["id"], code, "emergency_promotion", uid, ev.get("reason", ""))
        return
    raise ValueError("unknown branch event %r" % kind)


def _fill(state, branch, when):
    """Fill freed places from held additions, oldest first, until nothing
    changes (active queues before practice-squad queues)."""
    changed = True
    while changed:
        changed = False
        for layer in ("active", "practice_squad"):
            holds = sorted((h for code in state.held for h in state.held[code][layer]),
                           key=lambda h: (h["since"], h["ref"]))
            for hold in holds:
                code = next(c for c in state.held if hold in state.held[c][layer])
                if not state.has_room(code, layer):
                    continue
                uid = hold["uid"]
                loc = state.where.get(uid)
                if branch.control.controlled(uid, when) or uid in state.retired:
                    _cancel_hold(state, uid)
                    state.note(when, hold["ref"], code, "hold_lapsed", uid, "precondition no longer holds")
                    changed = True
                    break
                if loc and loc[1] in ("active", "reserve"):
                    _cancel_hold(state, uid)
                    state.note(when, hold["ref"], code, "hold_lapsed", uid, "on %s %s" % loc)
                    changed = True
                    break
                _join(state, code, layer, uid, hold["info"], when, hold["ref"])
                state.note(when, hold["ref"], code, "filled_" + layer, uid)
                changed = True
                break
            if changed:
                break


def check_rails_state(state, branch):
    """League-wide invariants (engineering review (d) check_rails_state)."""
    seen = {}
    for code, layers in state.clubs.items():
        for layer, players in layers.items():
            for p in players:
                if p["uid"] in seen:
                    state.errors.append("%s on two layers: %s and %s %s" % (p["uid"], seen[p["uid"]], code, layer))
                seen[p["uid"]] = "%s %s" % (code, layer)
        if len(layers["active"]) > LIMITS["active"] + state.carry.get(code, 0):
            state.errors.append("%s: %d on the active list, above its limit" % (code, len(layers["active"])))
        if state.ps_verified.get(code) and len(layers["practice_squad"]) > LIMITS["practice_squad"]:
            state.errors.append("%s: practice squad above 10" % code)
    for uid, (code, layer, hold) in state.held_by.items():
        if state.where.get(uid) == (code, "held") and uid in seen:
            state.errors.append("%s held by %s and on %s" % (uid, code, seen[uid]))
    for uid in branch.control.controlled_ids(state.cutoff):
        if uid in seen:
            state.errors.append("Jacksonville-controlled %s on %s" % (uid, seen[uid]))
        if uid in state.held_by:
            state.errors.append("Jacksonville-controlled %s held by %s" % (uid, state.held_by[uid][0]))
    by_pid = {}
    for uid in seen:
        pid = state.ids.get(uid)
        if pid in by_pid and by_pid[pid] != uid:
            state.errors.append("player id %s names two players (%s, %s)" % (pid, by_pid[pid], uid))
        by_pid[pid] = uid


# ---- emergency path (engineering review S5) -----------------------------------

def emergency_events(state, code, week, out_ids, cutoff, available_fn, excluded=()):
    """Branch events that give `code` a legal game-day unit, or [] when it
    already has one. Fires only when the available players fail
    `lineup_errors`. Source order: the club's own practice squad at the short
    group (earliest signing, then id), then its held additions at that group;
    with the club at its limit (or above it under C7), room comes only from
    putting its longest-projected injured player at that group on branch
    reserve. `excluded` names players already in an earlier game's TeamInput
    this week (the slate deferral): they cannot play for this club this week
    and cannot be promoted, but are not injured."""
    from types import SimpleNamespace
    excluded = set(excluded)
    active = state.clubs[code]["active"]
    avail = [p for p in active if available_fn(p, week) and p["player_id"] not in out_ids
             and p["player_id"] not in excluded]
    if not lineup_errors([SimpleNamespace(position=p["position"]) for p in avail]):
        return []
    counts = {}
    for p in avail:
        counts[p["group"]] = counts.get(p["group"], 0) + 1
    events, room = [], LIMITS["active"] - len(active)
    for grp, need in MINIMUM_GAME_DAY.items():
        short = need - counts.get(grp, 0)
        if short <= 0:
            continue
        pool = sorted((p for p in state.clubs[code]["practice_squad"] if p["group"] == grp),
                      key=lambda p: (p["since"] or "", p["uid"]))
        pool = [{"uid": p["uid"], "player_id": p["player_id"], "position": p["position"]} for p in pool]
        pool += [{"uid": h["uid"], **h["info"]} for h in state.held[code]["active"]
                 if group(h["info"]["position"]) == grp]
        pool = [c for c in pool if c["player_id"] not in excluded]
        injured = sorted((p for p in active if p["group"] == grp and p["player_id"] in out_ids),
                         key=lambda p: (-out_ids[p["player_id"]].toordinal()
                                        if isinstance(out_ids[p["player_id"]], date) else 0, p["uid"]))
        for cand in pool[:short]:
            ev = {"id": "EMERGENCY|%s|%s" % (_d(cutoff).isoformat(), cand["uid"]), "kind": "emergency_promotion",
                  "team": None, "club": code, "uid": cand["uid"], "player_id": cand["player_id"],
                  "position": cand["position"], "gate_date": _d(cutoff).isoformat(),
                  "effective_from_week": int(week),
                  "reason": "no legal game-day unit at %s (%s)" % (grp, ", ".join(lineup_errors(
                      [SimpleNamespace(position=p["position"]) for p in avail])))}
            if room <= 0:
                if not injured:
                    break
                ev["reserve_uid"] = injured.pop(0)["uid"]
            else:
                room -= 1
            events.append(ev)
    return events


# ---- identities and checks ------------------------------------------------------

def identities(rails):
    """{player_id: {gsis_id, birth_date, sources}} for the rails' newcomers
    (rows and base entries with a real gsis id): public identity data from
    nflverse players, for player ages only (engineering review S7)."""
    out = {}
    entries = [r for r in rails.rows if r.get("player_id")] + list(rails.base.get("corrections", ()))
    for club in rails.base["clubs"].values():
        entries += club.get("practice_squad", ())
    for e in entries:
        gsis = e.get("gsis_id") or (e.get("uid") if re.match(r"^\d{2}-\d{7}$", e.get("uid") or "") else None)
        if not gsis or e["player_id"] in out:
            continue
        out[e["player_id"]] = {"gsis_id": gsis, "birth_date": e.get("birth_date"),
                               "evidence": "nflverse_players_inseason_rails", "sources": ["nflverse_players"]}
    return out


def week_cutoff_coverage_error(rails, last_cutoff, week):
    """The week-scoped coverage gate (engineering review S3): the committed
    moves must reach the slate's last cutoff before its inputs are built."""
    if rails.as_of < _d(last_cutoff):
        return ("In-season rails: the moves are committed through %s, before Week %d's last cutoff %s; "
                "append the moves through %s (two passes) before building Week %d"
                % (rails.as_of.isoformat(), week, _d(last_cutoff).isoformat(), _d(last_cutoff).isoformat(), week))
    return None


ROW_FIELDS = {"id", "research_ref", "real_date", "gate_date", "date_basis", "club", "kind", "kind_basis",
              "counterparty", "player", "uid", "identity_basis", "outcome", "reason", "verification", "sources",
              "source_pages", "effective_from_week", "player_id", "gsis_id", "position", "kernel_group",
              "birth_date", "after_real_jaguars"}


def data_errors(season, master, root=ROOT):
    """validate_repository's checks of the committed rails data: schema,
    the information gate (no gate date or as-of after the master date),
    recorded hashes, the stripped form of injury, suspension, availability
    and Jacksonville rows, append-only ids and the fixed kind list."""
    folder = data_dir(season, root)
    if not (folder / "manifest.json").is_file():
        return []
    errors = []
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    master = _d(master)
    if _d(manifest["as_of"]) > master:
        errors.append("in-season rails as_of %s is after the master date %s" % (manifest["as_of"], master))
    files = [(manifest["base"]["path"], manifest["base"].get("sha256"))] + [
        (s["path"], s.get("sha256")) for s in manifest["shards"]]
    for path, digest in files:
        target = folder / path
        if not target.is_file():
            errors.append("in-season rails file missing: " + path)
        elif digest != sha256_file(target):
            errors.append("in-season rails file changed after it was recorded: " + path)
    if errors:
        return errors
    library = json.loads((Path(root) / manifest["base"]["library"]).read_text(encoding="utf-8"))
    if clubs_block_sha256(library) != manifest["base"]["library_clubs_sha256"]:
        errors.append("the Week 1 library's clubs block differs from the rails base pin")
    seen = []
    for shard in manifest["shards"]:
        rows = json.loads((folder / shard["path"]).read_text(encoding="utf-8"))["rows"]
        for row in rows:
            seen.append(row["id"])
            if _d(row["gate_date"]) > master or _d(row["gate_date"]) > _d(manifest["as_of"]):
                errors.append("in-season rails row %s is gated %s, after the clock" % (row["id"], row["gate_date"]))
            if row["outcome"] not in OUTCOMES:
                errors.append("in-season rails row %s: unknown outcome %s" % (row["id"], row["outcome"]))
            if not row.get("source_pages"):
                errors.append("in-season rails row %s has no source-page hash" % row["id"])
            if row["outcome"] in STRIPPED_OUTCOMES:
                if set(row) != set(STRIPPED_FIELDS):
                    errors.append("in-season rails row %s must carry only %s" % (row["id"], ", ".join(STRIPPED_FIELDS)))
                continue
            if set(row) - ROW_FIELDS:
                errors.append("in-season rails row %s: unknown fields %s" % (row["id"], sorted(set(row) - ROW_FIELDS)))
            if row.get("kind") not in KINDS:
                errors.append("in-season rails row %s: kind %s is not on the fixed list" % (row["id"], row.get("kind")))
            if _d(row["real_date"]) > _d(row["gate_date"]):
                errors.append("in-season rails row %s is gated before its real date" % row["id"])
            if row["outcome"] == "APPLY" and not row.get("uid"):
                errors.append("in-season rails row %s applies without an identity" % row["id"])
    if seen != ["R14-%04d" % i for i in range(1, len(seen) + 1)] and season == 2014:
        errors.append("in-season rails ids must run R14-0001 upward without gaps, in shard order")
    return errors


DEPARTURE_ACTIONS = {"removed_active", "removed_practice_squad", "removed_reserve", "retired", "to_jacksonville",
                     "implied_ps_release", "retired_jacksonville"}


def receipt_departure_errors(state, receipts, game_dates, codes, effective_from_week, protagonist=PROTAGONIST):
    """The closed-week invariant (engineering review B5): a background player
    in a closed receipt from the effective week on who is no longer with that
    club in `state` must have a departure from it dated on or after that
    game. Anything else would drop a player who has played, with no move."""
    errors = []
    by_pid = {}
    for uid, pid in state.ids.items():
        by_pid.setdefault(pid, set()).add(uid)
    for receipt in receipts:
        if int(receipt["week"]) < int(effective_from_week):
            continue
        played = _d(game_dates[(int(receipt["week"]), receipt["away"], receipt["home"])])
        for team in (receipt["away"], receipt["home"]):
            if team == protagonist or team not in codes:
                continue
            code = codes[team]
            for pid in receipt["team_stats"][team].get("players", ()):
                uids = by_pid.get(pid, set())
                if any(state.where.get(u, (None,))[0] == code for u in uids):
                    continue
                if not any(e["uid"] in uids and e["club"] == code and e["action"] in DEPARTURE_ACTIONS
                           and _d(e["date"]) >= played for e in state.log):
                    errors.append("%s played for %s on %s and left with no dated departure" % (pid, team, played))
    return errors
