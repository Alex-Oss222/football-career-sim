"""The active offensive book's words, for checking Stone's Game Plan (rebuild step 4).

The playbook lock (AGENTS.md, "Playbook: active-iteration lock") lets a call
name only what the iteration in force has: in 2014 the 2013 Iteration I
offensive book (``PLAYBOOK``, read through ``docs/repository_map.json``
``active_playbooks``). Every list below is that book's, each with its section;
tests/test_game_plan.py holds each word to the book and no later iteration is
read. The defense has its own lists (runtime/defensive_calls.py).

A call on the Game Plan is checked word by word:

- its concept: a family of the call-family map (runtime/call_families.py,
  read from the same book), or one of the plays the book names that the map
  does not carry (``BOOK_PLAYS``, which need an explicit target or carrier);
- its personnel: one of the book's groupings;
- its formation: an optional grouping, then at least one formation family,
  with the book's modifiers, directions, shift words and position labels;
- its motion: at least one of the book's motion calls, with the same words;
- its protection: one of the book's protections;
- its name: every word one of the book's words above, a concept word of the
  family map, a route tag, a position label, or a part of the name of a
  player on the club's roster;
- its tags: every word one the name may use, a number, or one of the plain
  staff words a tag describes a call with (``TAG_WORDS``: what the call is
  for, never a play), so no later book's term reaches the sheet as a tag.

Lowercase connecting words (``CONNECTIVES``) may join the words of a
formation or a motion ("SHIFT to Empty"). Nothing here is read by the game
path; it only refuses a page before anything is frozen.
"""
from __future__ import annotations

import re

from . import call_families

PLAYBOOK = "career/playbook/alex_stone_2013_offensive_playbook_iteration_i.md"

# 3 Personnel Architecture; 14 Six-Offensive-Lineman Package.
PERSONNEL = ("10", "11", "12", "13", "20", "21", "22", "6OL")
# 5 Formation Architecture (the families); 14.1 6OL Families; 2.1 and 9 (Gun Trips, Gun Strong,
# 20 Spread); 5 Ace (an under-center or pistol set).
FAMILIES = ("Doubles", "Ace", "Trips", "Trey", "Bunch", "Wing", "Pro", "I", "Empty", "Heavy", "Unbalanced",
            "Over", "Nub", "Leak", "Gun", "Pistol", "Spread")
# 5.3 Formation Modifiers and the family table's modifiers column.
MODIFIERS = ("Tight", "Wide", "Open", "Closed", "Y-Off", "Stack", "Plus", "Minus", "Slot", "Strong", "Weak",
             "Trade", "Offset", "Quads", "Y-Iso", "Split", "Tackle-Over")
# 2.1 and 2.4 (Trey Right, Power L), 5.4 Ball Location and Formation.
DIRECTIONS = ("Right", "Left", "R", "L", "Field", "Boundary", "Either")
# 6 Shift and Motion System; 17.3 (Motion F across, Flex F, SHIFT F to wing).
MOTIONS = ("Zip", "Jet", "Return", "Orbit", "Trade", "Shift", "Motion", "Flex")
# 2.5 Position Labels and Eligibility Language.
LABELS = ("X", "Z", "H", "Y", "R", "F")
# 8 Protection System; 11 (Sprint Flood: sprint protection).
PROTECTIONS = ("SCAT", "HALF", "SOLID", "BOB", "MAX", "TURNBACK", "NAKED", "Sprint")
# 8.4 Back Protection Rules.
BACK_PROTECTION = ("Check-release", "Scan", "Insert", "Chip-release")
# 10.24 Route Tags; 10.25 Special Pass Calls.
ROUTE_TAGS = ("Alert Post", "Go", "Wheel", "Choice", "Bender", "Sit", "Return", "Out-and-Up", "Sluggo",
              "Double Post", "Fade Stop")
# 12.4 Special Plays and Gadgets; 12.3 Fake Screens and Complements. The call-family map carries
# none of them, so a call naming one declares its target or carrier.
BOOK_PLAYS = ("Flea Flicker", "Halfback Pass", "Throwback Screen", "WR Reverse", "WR Pass", "Bubble Pump Go",
              "RB Screen Fake Cross", "Tunnel Fake Draw")
# 13 Access and Packaged Plays; 2.2 Vocabulary Rules (Cross, Vert).
CALL_WORDS = ("Access", "Cross", "Vert")
# The staff's plain words for what a call is for (its situation, its purpose, its package), which
# a tag may use besides the book's words: none names a concept, a route or a protection.
TAG_WORDS = ("answer", "backed", "change", "conditional", "down", "downs", "end", "ends", "folder",
             "four-minute", "gate", "goal", "install", "line", "movement", "opener", "package", "pass",
             "play", "pressure", "protection", "receiving", "red", "relief", "run", "short", "shot",
             "special", "sudden", "third", "tight", "two-minute", "two-point", "up", "week", "yardage",
             "zone")
CONNECTIVES = ("to", "toward", "across", "from", "after", "the", "and", "with", "into", "back", "both", "one",
               "of", "or")
# The lists every word of which tests/test_game_plan.py holds to the book.
BOOK_LISTS = {"personnel": PERSONNEL, "formation families": FAMILIES, "modifiers": MODIFIERS,
              "directions": DIRECTIONS, "motions": MOTIONS, "labels": LABELS, "protections": PROTECTIONS,
              "back protection": BACK_PROTECTION, "route tags": ROUTE_TAGS, "plays": BOOK_PLAYS,
              "call words": CALL_WORDS}


def _low(words):
    return {w.lower() for w in words}


def _tokens(words):
    return {t.lower() for w in words for t in re.split(r"[\s/+]+", w) if t}


_FAMILY = _low(FAMILIES)
_SHAPE = _FAMILY | _low(MODIFIERS) | _low(DIRECTIONS) | _low(MOTIONS) | _low(LABELS)
_MOTION = _low(MOTIONS)
_PROTECTION = _low(PROTECTIONS)
_PLAYS = {re.sub(r"[^a-z0-9+]", "", p.lower()): p for p in BOOK_PLAYS}
_NAME = (_SHAPE | _PROTECTION | _tokens(BACK_PROTECTION) | _tokens(ROUTE_TAGS) | _tokens(BOOK_PLAYS)
         | _tokens(CALL_WORDS) | _tokens(call_families.FAMILIES) | _tokens(call_families.ALIASES))


_TAG = _NAME | _low(TAG_WORDS)


def concept(family):
    """The book's name for a call's concept: its call-family map entry, or a play the book names
    that the map lacks; None when the active book has no such concept."""
    name, _ = call_families.family_entry(family)
    if name is not None:
        return name
    return _PLAYS.get(re.sub(r"[^a-z0-9+]", "", str(family or "").lower()))


def _word_ok(word, allowed):
    low = word.lower()
    if low in allowed or low in CONNECTIVES:
        return True
    parts = [p for p in low.split("-") if p]
    return len(parts) > 1 and all(p in allowed or p in CONNECTIVES for p in parts)


def _words(text):
    return [w for w in re.split(r"[\s,/+()]+", str(text or "")) if w]


def shape_errors(field, text):
    """Problems with a formation or a motion: each word the book's (``CONNECTIVES`` may join
    them), a grouping only as a formation's first word, and the formation family or motion call
    the field must name."""
    words = _words(text)
    out = []
    if field == "formation" and words and words[0].upper() in PERSONNEL:
        words = words[1:]
    for word in words:
        if word.upper() in PERSONNEL and field == "formation":
            out.append("the grouping %r belongs at the front of the formation" % word)
        elif not _word_ok(word, _SHAPE):
            out.append("%r is not a %s word of the active playbook" % (word, field))
    need = _FAMILY if field == "formation" else _MOTION
    if not out and not any(w.lower() in need for w in words):
        out.append("%r names no %s of the active playbook (%s)" % (
            text, "formation" if field == "formation" else "motion",
            ", ".join(FAMILIES if field == "formation" else MOTIONS)))
    return out


def call_errors(call, player_names=()):
    """Every word of one Game Plan call that is not the active book's, in football words
    ([] when every word is). ``player_names`` are the club's players, whose names a call may
    carry ("Thielen Whip")."""
    out = []
    family = call.get("family")
    if family and concept(family) is None:
        out.append("the concept %r is not in the active playbook" % family)
    personnel = call.get("personnel")
    if personnel and str(personnel).upper() not in PERSONNEL:
        out.append("personnel %r is not a grouping of the active playbook (%s)" % (personnel, ", ".join(PERSONNEL)))
    for field in ("formation", "motion"):
        if call.get(field):
            out += shape_errors(field, call[field])
    protection = call.get("protection")
    if protection and str(protection).lower() not in _PROTECTION:
        out.append("the protection %r is not one of the active playbook's (%s)" % (protection, ", ".join(PROTECTIONS)))
    players = {p.lower() for name in player_names for p in re.split(r"[\s.]+", name) if p}
    for word in _words(call.get("name")):
        if word.upper() in PERSONNEL or word.lower() in players or _word_ok(word, _NAME):
            continue
        out.append("the call's name has %r, which is not a word of the active playbook" % word)
    for tag in call.get("tags") or ():
        for word in _words(tag):
            if word.isdigit() or word.upper() in PERSONNEL or word.lower() in players or _word_ok(word, _TAG):
                continue
            out.append("the tag %r has %r, which is not a word of the active playbook" % (tag, word))
    return out
