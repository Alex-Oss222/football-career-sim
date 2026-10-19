"""Kernel 2014.6 W1a: the defensive call record (records only).

Stone's structured defensive sheet (``call_sheet.json`` ``defensive_call_sheet``)
is transcribed from his weekly packet, row by row, each row with its packet
path, line and verbatim text. After a game has resolved, every defensive snap
of the club carrying a sheet is labelled with the applicable row of that sheet,
deterministically and with no random number: the snap's published down and
distance, line of scrimmage, period clock and the score at its possession's
start give an ordered list of defensive situation menus, and the first menu
with a labelling row names the row. Nothing here reaches a draw: the sheet
stays out of the journaled game packet and the kernel's outcome packet, the
labels are written after the last event of the game, and no coverage, pressure
or package changes any play (no admissible public evidence measures such an
effect, so it stays at zero; ``library/raw/DATA_REQUEST.md`` item 4).

Encoding rules (kernel 2014.6 plan, B14 W1a):

- only rows triggered by down and distance, field zone or clock get a menu key
  (``kind: situation``); presentation rows (the offense's personnel, formation
  or motion, which no ledger records) never label; counters and conditional
  calls get no labelling menu; one labelling row per menu key, so the
  applicable row is unique;
- nothing off the practiced menu is encoded: every package, front, coverage,
  pressure and tag a row names is on the sheet's ``practiced`` lists, and those
  lists hold only words of the active defensive book (read through the
  playbook lock: ``docs/repository_map.json`` ``active_playbooks``); each
  front, strength, coverage and tag a row names occurs on its own cited
  packet line, and each practiced front, coverage and tag on one of the
  practiced menu's cited lines (``source_errors``);
- pressure families are the active book's section 8 six; the interior mug is
  encoded as ``replace`` with the ``mug`` tag;
- lead-late is recorded as a convention naming both candidate windows
  (``LEAD_LATE_CONVENTION``): the applied window is the second half's last
  2:00 with the defense leading;
- the sheet's rush rule is "four unless Stone calls the five-man counter".

Published (append-only, only for a club with a sheet): each labelled snap row
carries ``def_row`` (the row id, or None), ``def_rush_rule``, ``def_situation``
(the snap's most specific defensive menu) and ``def_label_source``
(``sheet:<menu>``, ``none``, ``kneel`` or ``spike``); the result carries
``defensive_calls`` (the record: each club's sheet sha256, its offensive
menus' hash, its rows' menus and verbatim text) and ``defensive_call_stats``
(snaps by row only, no outcome column). No package is published as personnel
and there is no presentation field. Preseason and the Pro Bowl are out of
scope.
"""
from __future__ import annotations

import copy
import hashlib
import json
import posixpath
import re
from pathlib import Path

from . import call_situations as cs
from .packets import canonical

ROOT = Path(__file__).resolve().parents[1]

MODEL = "defensive-call-record-v1"
SITUATIONS = "defensive-situations-v1"
SCHEMA_VERSION = 1
SHEET_KEY = "defensive_call_sheet"
RUSH_RULE = "four unless Stone calls the five-man counter"
FIELDS = ("def_row", "def_rush_rule", "def_situation", "def_label_source")
SNAP_TYPES = ("run", "pass", "two_point")

SITUATION, PRESENTATION, COUNTER, CONDITIONAL = "situation", "presentation", "counter", "conditional"
KINDS = (SITUATION, PRESENTATION, COUNTER, CONDITIONAL)

# The defensive situation menus and what triggers each (only these three).
RED_ZONE = "red-zone"
LEAD_LATE = "lead-late"
MENU_TRIGGERS = {
    cs.NORMAL: "down-and-distance", cs.SECOND_LONG: "down-and-distance", cs.THIRD_SHORT: "down-and-distance",
    cs.THIRD_MEDIUM: "down-and-distance", cs.THIRD_LONG: "down-and-distance", cs.TWO_POINT: "down-and-distance",
    cs.GOAL_LINE: "zone", cs.LOW_RED: "zone", cs.HIGH_RED: "zone", RED_ZONE: "zone", cs.BACKED_UP: "zone",
    cs.TWO_MINUTE: "clock", cs.FOUR_MINUTE: "clock", LEAD_LATE: "clock",
}
MENUS = tuple(MENU_TRIGGERS)
LEAD_LATE_SECONDS = cs.TWO_MINUTE_SECONDS
LEAD_LATE_CONVENTION = {
    "menu": LEAD_LATE,
    "applied_window": "two-minute",
    "candidate_windows": {
        "two-minute": {"half": 2, "seconds_left_at_most": cs.TWO_MINUTE_SECONDS, "defense": "leading"},
        "four-minute": {"half": 2, "seconds_left_at_most": cs.FOUR_MINUTE_SECONDS, "defense": "leading"},
    },
    "note": "The packets' 'lead late' names no clock. The record applies the second half's last 2:00 with the "
            "defense leading (the offense's two-minute window); the second half's last 4:00 is the other "
            "candidate. A labelling convention, never Stone's definition.",
}

# The active defensive book's words (2013 Iteration I, effective 2013-2015;
# tests/test_defensive_calls.py holds each list to the book read through the
# playbook lock). Pressure families: section 8's six, keyed.
PRESSURE_FAMILIES = {
    "base-4": "Base 4",
    "sam-will-edge": "Sam/Will Edge",
    "a-gap-dog": "A-gap Dog",
    "fire-zone": "Fire Zone",
    "corner-slot-pressure": "Corner/Slot Pressure",
    "replace": "Replace change-up",
}
FRONTS = ("Under", "Over", "Nickel Even", "Odd", "Bear")                      # section 5
STRENGTHS = ("Y", "Field", "Boundary", "Back", "Passing")                     # section 2.2
COVERAGES = ("0", "1", "1 Robber", "1 Rat", "1 Double", "2", "Palms", "Tampa", "3", "3 Match", "3 Buzz",
             "3 Cloud", "Quarters", "6", "8", "Cone", "Box", "Fire 3")         # section 10.1, appendix B
COVERAGE_FAMILIES = ("Post", "Man", "Split", "Bracket", "Pressure zone")      # section 10.1
# Package names and the defensive backs each names (a definition, never
# personnel: no snap publishes a package). Base 4-3, Nickel and Big Nickel
# (section 3), Dime (sections 4.1 and 15.4).
PACKAGES = {"Base": 4, "Nickel": 5, "Big Nickel": 5, "Dime": 6}
TAGS = ("mug", "field", "boundary")
REPLACE_TAGS = frozenset(TAGS)
PRACTICED_LISTS = {"packages": tuple(PACKAGES), "fronts": FRONTS, "coverages": COVERAGES + COVERAGE_FAMILIES,
                   "pressures": tuple(PRESSURE_FAMILIES), "tags": TAGS}
CALL_FIELDS = ("package", "front", "strength", "coverage", "pressure", "tags")
SHEET_FIELDS = ("schema_version", "team", "caller", "book", "packet", "rush_rule", "practiced", "rows", "notes")
# Schema version 1 holds the words of this iteration; a sheet on a later
# defensive iteration needs a new schema version with that book's words.
VOCABULARY_BOOK = "career/playbook/alex_stone_2013_defensive_playbook_iteration_i.md"
ROW_FIELDS = ("id", "kind", "menu", "call", "source")


def _db_range():
    """(floor, ceiling) of the defensive backs the participation convention
    seats (runtime.participation.DEFENSE_SLOTS: DB1-4 every snap, DB5 on a
    share): a package naming more or fewer is a reported conflict."""
    from .participation import DEFENSE_SLOTS
    shares = dict(DEFENSE_SLOTS)["DB"]
    return sum(1 for s in shares if s >= 100), len(shares)


# ---- the sheet: schema and validator --------------------------------------

def _source_errors_shape(source, where):
    if not isinstance(source, dict) or set(source) - {"path", "line", "text"}:
        return ["%s: source must be an object of path, line and text" % where]
    errors = []
    if not isinstance(source.get("path"), str) or not source["path"].strip():
        errors.append("%s: source needs the packet path" % where)
    line = source.get("line")
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
        errors.append("%s: source needs its packet line (a positive integer)" % where)
    if not isinstance(source.get("text"), str) or not source["text"].strip():
        errors.append("%s: source needs its verbatim text" % where)
    return errors


def _call_errors(call, practiced, where):
    if not isinstance(call, dict) or not call:
        return ["%s: call must be a nonempty object" % where]
    errors = ["%s: unknown call field %r" % (where, key) for key in call if key not in CALL_FIELDS]
    if not any(call.get(k) for k in ("package", "front", "coverage", "pressure")):
        errors.append("%s: call names no package, front, coverage or pressure" % where)

    def on_menu(kind, value, vocabulary):
        if value not in vocabulary:
            errors.append("%s: %s %r is not a word of the active defensive book" % (where, kind, value))
        elif value not in practiced.get(kind + "s", ()):
            errors.append("%s: %s %r is not on the practiced menu" % (where, kind, value))

    if call.get("package") is not None:
        on_menu("package", call["package"], PACKAGES)
    if call.get("front") is not None:
        on_menu("front", call["front"], FRONTS)
    if call.get("strength") is not None and call["strength"] not in STRENGTHS:
        errors.append("%s: strength %r is not a word of the active defensive book" % (where, call["strength"]))
    if call.get("strength") is not None and call.get("front") is None:
        errors.append("%s: a strength declaration needs its front" % where)
    coverage = call.get("coverage")
    if coverage is not None:
        if not isinstance(coverage, list) or not coverage:
            errors.append("%s: coverage must be a nonempty list (the row's alternatives)" % where)
        else:
            for item in coverage:
                on_menu("coverage", item, COVERAGES + COVERAGE_FAMILIES)
    if call.get("pressure") is not None:
        on_menu("pressure", call["pressure"], PRESSURE_FAMILIES)
    tags = call.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errors.append("%s: tags must be a list" % where)
        else:
            for tag in tags:
                on_menu("tag", tag, TAGS)
            if REPLACE_TAGS & set(tags) and call.get("pressure") != "replace":
                errors.append("%s: the %s tag belongs to the replace family" % (where, "/".join(sorted(
                    REPLACE_TAGS & set(tags)))))
    return errors


def sheet_errors(sheet):
    """Problems with a structured defensive sheet ([] when it is valid). The
    structural rules only; source_errors checks the packet lines and the book
    against the repository."""
    if not isinstance(sheet, dict):
        return ["defensive_call_sheet must be an object"]
    errors = ["unknown sheet field %r" % key for key in sheet if key not in SHEET_FIELDS]
    if sheet.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be %d" % SCHEMA_VERSION)
    for key in ("team", "caller", "book", "packet"):
        if not isinstance(sheet.get(key), str) or not sheet[key].strip():
            errors.append("%s must be a nonempty string" % key)
    if isinstance(sheet.get("book"), str) and sheet["book"] != VOCABULARY_BOOK:
        errors.append("book must be %s: schema version %d holds that defensive iteration's words"
                      % (VOCABULARY_BOOK, SCHEMA_VERSION))
    notes = sheet.get("notes")
    if notes is not None and (not isinstance(notes, list) or not all(isinstance(n, str) for n in notes)):
        errors.append("notes must be a list of strings (never read)")
    rush = sheet.get("rush_rule")
    if not isinstance(rush, dict) or set(rush) - {"rule", "source"}:
        errors.append("rush_rule must be an object of rule and source")
    else:
        if rush.get("rule") != RUSH_RULE:
            errors.append("rush_rule.rule must read %r" % RUSH_RULE)
        errors += _source_errors_shape(rush.get("source"), "rush_rule")
    practiced = sheet.get("practiced")
    if not isinstance(practiced, dict):
        errors.append("practiced must be an object of the practiced menu's lists and sources")
        practiced = {}
    else:
        for key in practiced:
            if key not in tuple(PRACTICED_LISTS) + ("sources",):
                errors.append("practiced: unknown list %r" % key)
        for key, vocabulary in PRACTICED_LISTS.items():
            items = practiced.get(key, [])
            if not isinstance(items, list):
                errors.append("practiced.%s must be a list" % key)
                continue
            for item in items:
                if item not in vocabulary:
                    errors.append("practiced.%s: %r is not a word of the active defensive book" % (key, item))
        sources = practiced.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append("practiced.sources must list the packet lines of the practiced menu")
        else:
            for i, source in enumerate(sources):
                errors += _source_errors_shape(source, "practiced.sources[%d]" % i)
    rows = sheet.get("rows")
    if not isinstance(rows, list) or not rows:
        return errors + ["rows must be a nonempty list"]
    seen, menus = set(), {}
    for i, row in enumerate(rows):
        where = "rows[%d]" % i
        if not isinstance(row, dict):
            errors.append("%s must be an object" % where)
            continue
        errors += ["%s: unknown row field %r" % (where, key) for key in row if key not in ROW_FIELDS]
        rid = row.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append("%s: id must be a nonempty string" % where)
        elif rid in seen:
            errors.append("%s: duplicate row id %r" % (where, rid))
        else:
            seen.add(rid)
            where = "row %s" % rid
        kind = row.get("kind")
        if kind not in KINDS:
            errors.append("%s: kind must be one of %s" % (where, ", ".join(KINDS)))
        menu = row.get("menu")
        if kind == SITUATION:
            if menu not in MENUS:
                errors.append("%s: a situation row needs a menu key triggered by down and distance, zone or "
                              "clock (%s)" % (where, ", ".join(MENUS)))
            elif menu in menus:
                errors.append("%s: menu %s already labels row %s (one labelling row per menu)"
                              % (where, menu, menus[menu]))
            else:
                menus[menu] = rid
            if "call" not in row:
                errors.append("%s: a situation row needs its call" % where)
        elif kind in KINDS and menu is not None:
            errors.append("%s: a %s row never labels and takes no menu" % (where, kind))
        if "call" in row:
            errors += _call_errors(row["call"], practiced, where)
        errors += _source_errors_shape(row.get("source"), where)
        source = row.get("source") if isinstance(row.get("source"), dict) else {}
        call = row.get("call") if isinstance(row.get("call"), dict) else None
        if call is not None and "mug" in str(source.get("text", "")).lower():
            # The interior mug is encoded as the replace family with the mug tag.
            if call.get("pressure") != "replace" or "mug" not in (call.get("tags") or ()):
                errors.append("%s: an interior mug is encoded as pressure replace with the mug tag" % where)
    return errors


def active_defensive_book(root=ROOT):
    """The active defensive iteration's path, read through the playbook lock
    (docs/repository_map.json ``active_playbooks``), or None."""
    mapping = json.loads((Path(root) / "docs/repository_map.json").read_text(encoding="utf-8"))
    books = [p for p in mapping.get("active_playbooks", ()) if "defensive" in Path(p).name]
    return books[0] if len(books) == 1 else None


def defensive_iterations(root=ROOT):
    """{book path: (first season, last season)} from the defensive table of
    career/playbook/README.md (the playbook lock's index; no book is read)."""
    text = (Path(root) / "career/playbook/README.md").read_text(encoding="utf-8")
    table = text.split("## Defensive iterations", 1)[1]
    out = {}
    for line in table.splitlines():
        match = re.match(r"\|[^|]+\|\s*(\d{4})-(\d{4})\s*\|\s*`([^`]+)`", line)
        if match:
            out["career/playbook/" + match[3]] = (int(match[1]), int(match[2]))
    return out


def _effective_seasons(text):
    match = re.search(r'^effective_seasons:\s*"?(\d{4})-(\d{4})"?\s*$', text, re.M)
    return (int(match[1]), int(match[2])) if match else None


def _normalized(text):
    return " ".join(str(text).split())


LOCKED_PREFIXES = ("career/playbook/", "archive/")


def packet_path(rel, root=ROOT):
    """The packet file a sheet's ``packet`` or a source's ``path`` names, or
    None when it is not a packet in the repository. Overnight review fix
    (October 17, 2026): decided on the resolved path, never the raw string,
    so it must be a Markdown file inside the repository, spelled as its own
    normalized repository-relative path (no './', '..', absolute or symlink
    spelling), and never a playbook page (the playbook lock) or an archive
    page (the hindsight archive)."""
    if not isinstance(rel, str) or not rel:
        return None
    base = Path(root).resolve()
    try:
        if posixpath.normpath(rel) == rel and not (base / rel).exists():
            # A frozen sheet keeps its packet's path as written. A page that a
            # later layout change moved (rebuild step 2b: the season folders
            # lost their numbers) resolves through the season layout's
            # translation, and the translated spelling passes the same checks.
            from .season_layout import repository_relative
            rel = repository_relative(rel)
        path = (base / rel).resolve()
        if not path.is_relative_to(base):
            return None
        norm = path.relative_to(base).as_posix()
        if rel != norm or norm.startswith(LOCKED_PREFIXES) or path.suffix != ".md" or not path.is_file():
            return None
    except (OSError, ValueError):  # an unreadable spelling (a NUL byte, an overlong name) is no packet
        return None
    return path


def _occurs(word, text):
    """Whether a book word occurs in a packet line: case-insensitive, on
    token boundaries (no letter or digit either side), its parts separated
    by whitespace or hyphens, singular or with a plural 's'."""
    parts = r"[\s-]+".join(re.escape(part) for part in str(word).split())
    return re.search(r"(?<![0-9A-Za-z])%ss?(?![0-9A-Za-z])" % parts, str(text), re.I) is not None


def _call_words(call):
    """(kind, word) of a call's front, strength, coverage alternatives and
    tags: the words its cited packet line must hold. Packages and pressure
    keys stay on the declared lists ('base-4' has no fixed wording)."""
    words = [(kind, call[kind]) for kind in ("front", "strength") if call.get(kind) is not None]
    words += [("coverage", item) for item in call.get("coverage") or ()]
    words += [("tag", tag) for tag in call.get("tags") or ()]
    return words


def source_errors(sheet, root=ROOT, season=None):
    """The repository checks of a sheet that passes sheet_errors: its book
    is the active defensive iteration (the playbook lock), or, for a sheet of
    ``season``, the iteration whose effective seasons cover it in the
    playbook index, never one beginning after the active season; its packet
    and every source name a packet of the repository (``packet_path``); every
    source names an existing packet line whose text holds the row's text
    verbatim (whitespace runs compared as one space); every front, strength,
    coverage and tag a row's call names occurs on that row's cited packet
    line; and every practiced front, coverage and tag occurs on one of the
    practiced menu's cited lines (``_occurs``)."""
    root = Path(root)
    errors = []
    book = sheet.get("book")
    if season is None:
        if book != active_defensive_book(root):
            errors.append("book %r is not the active defensive playbook (%s)" % (book, active_defensive_book(root)))
    else:
        # A committed sheet of an earlier season keeps the iteration in force
        # then (career/playbook/README.md); never one whose range begins after
        # the active season.
        active = json.loads((root / "docs/repository_map.json").read_text(encoding="utf-8")).get("active_season")
        span = defensive_iterations(root).get(book)
        if span is None or not span[0] <= int(season) <= span[1] or (active is not None and span[0] > int(active)):
            errors.append("book %r is not the defensive iteration in force for %s" % (book, season))
    packet = sheet.get("packet")
    if packet_path(packet, root) is None:
        errors.append("packet %r is not a packet in the repository" % packet)
    practiced = sheet.get("practiced") or {}
    rows = [r for r in sheet.get("rows") or () if isinstance(r, dict)]
    sources = [("rush_rule", (sheet.get("rush_rule") or {}).get("source"), None)]
    sources += [("practiced.sources[%d]" % i, s, None) for i, s in enumerate(practiced.get("sources") or ())]
    sources += [("row %s" % r.get("id"), r.get("source"), r) for r in rows]
    cache, practiced_lines = {}, []
    for where, source, row in sources:
        if not isinstance(source, dict):
            continue
        rel = source.get("path")
        path = packet_path(rel, root)
        if path is None:
            errors.append("%s: source path %r is not a packet in the repository" % (where, rel))
            continue
        lines = cache.setdefault(rel, path.read_text(encoding="utf-8").splitlines())
        line = source.get("line")
        if not isinstance(line, int) or not 1 <= line <= len(lines):
            errors.append("%s: line %s is outside %s" % (where, line, rel))
            continue
        full = lines[line - 1]
        if _normalized(source.get("text", "")) not in _normalized(full):
            errors.append("%s: text is not verbatim on %s line %d" % (where, rel, line))
            continue
        if where.startswith("practiced."):
            practiced_lines.append(full)
        call = row.get("call") if row is not None else None
        if isinstance(call, dict):
            # Overnight review fix (October 17, 2026): a row's encoded call
            # is held to its own cited line, not only to the declared lists.
            for kind, word in _call_words(call):
                if not _occurs(word, full):
                    errors.append("%s: %s %r is not on its cited line (%s line %d)" % (where, kind, word, rel, line))
    # Each practiced front, coverage and tag on one of the menu's install lines.
    for key in ("fronts", "coverages", "tags"):
        for word in practiced.get(key) or ():
            if not any(_occurs(word, full) for full in practiced_lines):
                errors.append("practiced.%s: %r is on none of the practiced menu's cited lines" % (key, word))
    return errors


def sheet_sha256(sheet):
    """sha256 of the sheet's canonical JSON (runtime.packets.canonical)."""
    return hashlib.sha256(canonical(sheet)).hexdigest()


def offensive_menus_sha256(call_sheet):
    """sha256 of the club's frozen offensive menus: each offensive call's name
    and canonical menu keys, in sheet order (play_detail._normalize_call), so
    the record binds the defensive labels to the same frozen weekly sheet."""
    from .play_detail import _normalize_call
    rows = [[c["name"], list(c["menus"])] for c in (_normalize_call(item, "any") for item in call_sheet or ())]
    return hashlib.sha256(canonical(rows)).hexdigest()


def labelling_rows(sheet):
    """{menu: row} of the sheet's labelling (situation) rows."""
    return {row["menu"]: row for row in sheet["rows"] if row.get("kind") == SITUATION}


def package_conflict(row):
    """Whether the row's package names more or fewer defensive backs than the
    participation convention seats (reported, never a violation)."""
    package = (row.get("call") or {}).get("package")
    if package is None:
        return False
    floor, ceiling = _db_range()
    return not floor <= PACKAGES[package] <= ceiling


# ---- the snap's defensive situation ---------------------------------------

def half_clock(row):
    """(half, seconds left in it) from a snap row's published period and
    clock: 1 or 2 in regulation, 'OT' in an overtime period (its own clock);
    (half, None) without a clock."""
    period = row.get("period")
    clock = row.get("game_clock")
    left = None
    if isinstance(clock, str) and ":" in clock:
        minutes, seconds = clock.split(":", 1)
        left = int(minutes) * 60 + int(seconds)
    if period in (1, 2, 3, 4):
        half = 1 if period <= 2 else 2
        if left is not None and period in (1, 3):
            left += 900
        return half, left
    return "OT", left


def snap_menus(row, score_diff):
    """The applicable defensive menus of one snap row, most specific first.
    ``score_diff`` is the offense's score minus the defense's at the start
    of the snap's possession. A two-point try takes the try menu and the
    goal-line zones. Otherwise: the third-down menu by distance (fourth down
    likewise), the zone (goal line, low red zone, high red zone, then
    red-zone; or backed up), the clock (lead-late, two-minute or
    four-minute), second-and-long, and normal-down on first and second down
    only (a third-down snap never takes the normal-down row)."""
    if row.get("play_type") == "two_point":
        return [cs.TWO_POINT, cs.GOAL_LINE, cs.LOW_RED, cs.HIGH_RED, RED_ZONE]
    down = int(row.get("down") or 1)
    ydstogo = int(row["ydstogo"]) if row.get("ydstogo") is not None else 10
    yardline = int(row["yardline"])
    menus = []
    if down >= 3:
        if ydstogo <= cs.THIRD_SHORT_MAX:
            menus.append(cs.THIRD_SHORT)
        elif ydstogo <= cs.THIRD_MEDIUM_MAX:
            menus.append(cs.THIRD_MEDIUM)
        else:
            menus.append(cs.THIRD_LONG)
    if yardline <= cs.GOAL_LINE_LINE:
        menus += [cs.GOAL_LINE, cs.LOW_RED, cs.HIGH_RED, RED_ZONE]
    elif yardline <= cs.LOW_RED_LINE:
        menus += [cs.LOW_RED, cs.HIGH_RED, RED_ZONE]
    elif yardline <= cs.HIGH_RED_LINE:
        menus += [cs.HIGH_RED, RED_ZONE]
    elif yardline >= cs.BACKED_UP_LINE:
        menus.append(cs.BACKED_UP)
    half, left = half_clock(row)
    if left is not None:
        if half == 2 and left <= LEAD_LATE_SECONDS and score_diff < 0:
            menus.append(LEAD_LATE)
        if left <= cs.TWO_MINUTE_SECONDS and (half == 1 or score_diff <= 0):
            menus.append(cs.TWO_MINUTE)
        elif half == 2 and left <= cs.FOUR_MINUTE_SECONDS and score_diff > 0:
            menus.append(cs.FOUR_MINUTE)
    if down == 2 and ydstogo >= cs.SECOND_LONG_MIN:
        menus.append(cs.SECOND_LONG)
    if down <= 2:
        menus.append(cs.NORMAL)
    return menus


def expected_label(row, score_diff, rows_by_menu, rush_rule=RUSH_RULE):
    """The four published fields of one snap of a sheet club's defense."""
    menus = snap_menus(row, score_diff)
    if row.get("kneel") or row.get("spike"):
        return {"def_row": None, "def_rush_rule": rush_rule, "def_situation": menus[0],
                "def_label_source": "kneel" if row.get("kneel") else "spike"}
    for menu in menus:
        if menu in rows_by_menu:
            return {"def_row": rows_by_menu[menu], "def_rush_rule": rush_rule, "def_situation": menus[0],
                    "def_label_source": "sheet:" + menu}
    return {"def_row": None, "def_rush_rule": rush_rule, "def_situation": menus[0], "def_label_source": "none"}


def _score_diffs(possessions):
    return {p.get("number"): int(p.get("score_diff") or 0) for p in possessions}


def team_record(sheet, offensive_call_sheet):
    """One club's entry of the result record."""
    return {"sheet_sha256": sheet_sha256(sheet), "offensive_menus_sha256": offensive_menus_sha256(offensive_call_sheet),
            "book": sheet["book"], "rush_rule": sheet["rush_rule"]["rule"],
            "rows": {row["id"]: {"menu": row["menu"], "text": row["source"]["text"],
                                 "package_conflict": package_conflict(row)}
                     for row in sheet["rows"] if row.get("kind") == SITUATION}}


def label_game(play_ledger, possessions, sheets):
    """Label every defensive snap of each club in ``sheets`` ({team_id:
    (sheet, offensive call sheet)}) in place, after the game has resolved.
    Returns (record, stats): the result's ``defensive_calls`` and
    ``defensive_call_stats``. Deterministic; no random number; reads only the
    published rows and the possessions' starting score."""
    diffs = _score_diffs(possessions)
    record = {"model": MODEL, "situations": SITUATIONS, "lead_late": copy.deepcopy(LEAD_LATE_CONVENTION),
              "snap_types": list(SNAP_TYPES), "teams": {}}
    stats = {}
    by_menu = {}
    for team_id, (sheet, offensive) in sorted(sheets.items()):
        record["teams"][team_id] = team_record(sheet, offensive)
        by_menu[team_id] = {menu: row["id"] for menu, row in labelling_rows(sheet).items()}
        stats[team_id] = {"rows": {rid: {"snaps": 0} for rid in by_menu[team_id].values()}, "unlabelled_snaps": 0}
    for row in play_ledger:
        team_id = row.get("defense")
        if row.get("play_type") not in SNAP_TYPES or team_id not in by_menu:
            continue
        label = expected_label(row, diffs.get(row.get("drive"), 0), by_menu[team_id],
                               record["teams"][team_id]["rush_rule"])
        row.update(label)
        if label["def_row"] is None:
            stats[team_id]["unlabelled_snaps"] += 1
        else:
            stats[team_id]["rows"][label["def_row"]]["snaps"] += 1
    return record, stats


# ---- coherence (runtime.play_detail.check_ledger, group w1a_defense) ------

def check(result, possessions, ledger, err):
    """def_label_wrong_club, def_label_menu_mismatch and the reported
    def_package_participation_conflict, from the result or full receipt
    alone (its record, its rows and its possessions' starting score)."""
    record = result.get("defensive_calls") or {}
    teams = record.get("teams") or {}
    clubs = set(result.get("final_score") or result.get("score") or {})
    for team_id in teams:
        if team_id not in clubs:
            err("def_label_wrong_club", "the record names %s, which did not play" % team_id)
    diffs = _score_diffs(possessions)
    by_menu = {t: {entry["menu"]: rid for rid, entry in (e.get("rows") or {}).items()} for t, e in teams.items()}
    counts = {t: {"rows": {rid: 0 for rid in (e.get("rows") or {})}, "unlabelled_snaps": 0} for t, e in teams.items()}
    for row in ledger:
        labelled = [f for f in FIELDS if f in row]
        snap = row.get("play_type") in SNAP_TYPES
        where = "drive %s snap %s" % (row.get("drive"), row.get("snap_in_drive"))
        if labelled and (not snap or row.get("defense") not in teams):
            err("def_label_wrong_club", "%s (%s, defense %s) carries a defensive label" % (
                where, row.get("play_type"), row.get("defense")))
            continue
        if not snap or row.get("defense") not in teams:
            continue
        team_id = row["defense"]
        if len(labelled) != len(FIELDS):
            err("def_label_wrong_club", "%s of %s's defense lacks %s" % (
                where, team_id, ", ".join(f for f in FIELDS if f not in row)))
            continue
        expected = expected_label(row, diffs.get(row.get("drive"), 0), by_menu[team_id],
                                  teams[team_id].get("rush_rule"))
        got = {f: row[f] for f in FIELDS}
        if got != expected:
            err("def_label_menu_mismatch", "%s labelled %s, its situation gives %s" % (
                where, json.dumps(got, sort_keys=True), json.dumps(expected, sort_keys=True)))
            continue
        if expected["def_row"] is None:
            counts[team_id]["unlabelled_snaps"] += 1
        else:
            counts[team_id]["rows"][expected["def_row"]] += 1
            if (teams[team_id]["rows"][expected["def_row"]] or {}).get("package_conflict"):
                err("def_package_participation_conflict", "%s: row %s names a package the participation "
                    "convention does not seat" % (where, expected["def_row"]))
    stats = result.get("defensive_call_stats")
    if stats is not None:
        published = {t: {"rows": {rid: (line or {}).get("snaps") for rid, line in (s.get("rows") or {}).items()},
                         "unlabelled_snaps": s.get("unlabelled_snaps")} for t, s in stats.items()}
        if published != counts:
            err("def_label_menu_mismatch", "defensive_call_stats %s differ from the labelled snaps %s" % (
                json.dumps(published, sort_keys=True), json.dumps(counts, sort_keys=True)))


def has_record(result):
    """Kernel 2014.6 W1a: the result or full receipt carries the defensive
    call record and its snap ledger."""
    return bool(result.get("defensive_calls")) and bool(result.get("play_ledger"))


# ---- the committed record (scripts/validate_repository.py) ----------------

def committed_sheet_errors(data, root=ROOT, season=None):
    """Problems with a committed call_sheet.json's defensive_call_sheet ([]
    when absent or valid): the schema, the verbatim packet lines, the
    playbook lock and the sheet's club."""
    sheet = data.get(SHEET_KEY)
    if sheet is None:
        return []
    errors = sheet_errors(sheet)
    if errors:
        return errors
    errors = source_errors(sheet, root, season)
    if sheet.get("team") != data.get("team"):
        errors.append("the defensive sheet is %s's; the call sheet is %s's" % (sheet.get("team"), data.get("team")))
    return errors


def receipt_record_errors(receipt, call_sheet):
    """A receipt's defensive call record against the week's committed call
    sheet (the parsed call_sheet.json, or None): the record names only that
    sheet's club, and its sheet sha256 and offensive menus' hash are the
    committed sheet's."""
    record = receipt.get("defensive_calls")
    if not record:
        return []
    if call_sheet is None or call_sheet.get(SHEET_KEY) is None:
        return ["the receipt carries a defensive call record but the week's committed call sheet holds no "
                "defensive_call_sheet"]
    errors = []
    teams = record.get("teams") or {}
    if set(teams) != {call_sheet.get("team")}:
        errors.append("the defensive call record names %s; the committed sheet is %s's"
                      % (", ".join(sorted(teams)) or "no club", call_sheet.get("team")))
    for team_id, entry in teams.items():
        if entry.get("sheet_sha256") != sheet_sha256(call_sheet[SHEET_KEY]):
            errors.append("%s: the record's sheet sha256 is not the committed defensive sheet's" % team_id)
        if entry.get("offensive_menus_sha256") != offensive_menus_sha256(call_sheet.get("offensive_call_sheet")
                                                                          or ()):
            errors.append("%s: the record's offensive menus' hash is not the committed call sheet's" % team_id)
    return errors
