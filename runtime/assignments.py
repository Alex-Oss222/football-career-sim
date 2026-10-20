"""Seats and role wording: the one place the depth chart page and the player pages read them.

A player's current assignment is one plain, confirmed role. For a Jaguar it comes from the game
depth chart (``depth``, ``positions``, ``roles``) and Stone's dated role decisions on the working
chart (``stone_role_decisions``), the owners the depth chart page renders
(scripts/render_club_pages.depth_chart_page), so the two pages can never disagree. For another
club's player it comes from his slot on the season's Week 1 depth chart (the library entry's
``slots``), when nothing since has moved him (runtime/player_pages.current_assignment decides
that). Injuries do not change an assignment until the chart changes.

This module only reads the dicts it is given and imports nothing from the career layer.
"""
from __future__ import annotations

import re

# The game chart's role names in football words (the depth chart page's Role column).
ROLE_NAMES = {"passer": "Starter", "placekicker": "Kicker", "punt": "Punter", "kick_return": "Kick returner",
              "punt_return": "Punt returner", "nickel": "Nickel", "outside_reserve": "Outside reserve corner"}

# The first-unit offense, in the depth chart page's order: (group, index in the group's depth
# order, the page's seat label, the player page's words).
OFFENSE_SEATS = (
    ("QB", 0, "QB", "Starting quarterback"),
    ("RB", 0, "RB", "Starting running back"),
    ("FB", 0, "FB", "Fullback"),
    ("WR", 0, "X", "Starting X receiver"),
    ("WR", 1, "H", "Starting H receiver"),
    ("WR", 2, "Z", "Starting Z receiver"),
    ("TE", 0, "TE", "Starting tight end"),
    ("OL", 0, "LT", "Starting left tackle"),
    ("OL", 1, "LG", "Starting left guard"),
    ("OL", 2, "C", "Starting center"),
    ("OL", 3, "RG", "Starting right guard"),
    ("OL", 4, "RT", "Starting right tackle"),
)
# The base defense's first groups: (group, the page's unit name, how many start). A starter
# there reads "Starting" and his chart position's words.
DEFENSE_FIRST = (("DL", "Defensive line", 4), ("LB", "Linebackers", 3), ("DB", "Defensive backs", 4))
# The dime seat: the sixth defensive back in the order.
DIME = ("DB", 5)
# The specialists: (group, the job). The first in each group's order holds the job.
SPECIALISTS = (("K", "Kicker"), ("P", "Punter"), ("LS", "Long snapper"))
SEATS = {"offense": OFFENSE_SEATS, "defense": DEFENSE_FIRST, "dime": DIME, "specialists": SPECIALISTS}

POSITION_WORDS = {
    "QB": "quarterback", "RB": "running back", "HB": "running back", "FB": "fullback", "WR": "wide receiver",
    "TE": "tight end", "OT": "tackle", "T": "tackle", "G": "guard", "OG": "guard", "C": "center",
    "DE": "defensive end", "DT": "defensive tackle", "NT": "nose tackle", "DL": "defensive lineman",
    "LB": "linebacker", "OLB": "outside linebacker", "ILB": "inside linebacker", "MLB": "middle linebacker",
    "CB": "cornerback", "S": "safety", "FS": "free safety", "SS": "strong safety", "DB": "defensive back",
    "K": "kicker", "PK": "kicker", "P": "punter", "LS": "long snapper",
}

# Stone's working-chart labels in page words. A label not named here fails the check
# (label_errors), so a new label is worded before any page shows it.
LABEL_WORDS = {
    "X (WR1)": "Starting X receiver",
    "H": "Starting H receiver",
    "Z": "Starting Z receiver",
    "Z (WR3)": "Starting Z receiver",
    "Left guard": "Starting left guard",
    "Right guard": "Starting right guard",
    "Edge 1": "Starting defensive end",
    "Long snapper": "Long snapper",
    "Kick returner and punt returner": "Kick returner and punt returner",
    "First general receiver relief": "First relief receiver",
    "X relief (fifth receiver)": "Fifth receiver and X relief",
    "Sixth receiver": "Sixth receiver",
    "Nickel (DB5)": "Nickel cornerback",
    "Sixth defensive back (Dime)": "Dime defensive back",
    "Outside reserve": "Reserve outside cornerback",
}

# The Week 1 library's slot codes in page words. None: the slot names no position (OFF, DEF,
# SPE). ROSTER: the slot is a scheme label read through the entry's roster position (the
# library's own rule 2).
ROSTER = "roster"
SLOT_WORDS = {
    "QB": "quarterback", "RB": "running back", "FB": "fullback", "WR": "wide receiver", "TE": "tight end",
    "LT": "left tackle", "LG": "left guard", "C": "center", "RG": "right guard", "RT": "right tackle",
    "T": "tackle",
    "DE": "defensive end", "LDE": "defensive end", "RDE": "defensive end", "LE": "defensive end",
    "RE": "defensive end", "END": "defensive end",
    "DT": "defensive tackle", "LDT": "defensive tackle", "RDT": "defensive tackle", "NT": "nose tackle",
    "OLB": "outside linebacker", "LOLB": "outside linebacker", "ROLB": "outside linebacker",
    "LLB": "outside linebacker", "RLB": "outside linebacker",
    "SAM": "strongside linebacker", "SLB": "strongside linebacker",
    "WILL": "weakside linebacker", "WLB": "weakside linebacker",
    "MLB": "middle linebacker", "MIKE": "middle linebacker",
    "ILB": "inside linebacker", "LILB": "inside linebacker", "RILB": "inside linebacker",
    "LB": "linebacker", "BLB": "linebacker", "JLB": "linebacker",
    "JACK": ROSTER, "RUSH": ROSTER, "LEO": ROSTER,
    "CB": "cornerback", "LCB": "cornerback", "RCB": "cornerback", "NKL": "nickel cornerback",
    "S": "safety", "DS": "safety", "SS": "strong safety", "FS": "free safety",
    "K": "kicker", "PK": "kicker", "FG": "kicker", "P": "punter", "LS": "long snapper",
    "KR": "kick returner", "KOR": "kick returner", "PR": "punt returner", "KO": "kickoff specialist",
    "H": "holder",
    "OFF": None, "DEF": None, "SPE": None,
}
# Special-teams slots, in the order they name a job when no scrimmage slot does.
SPECIAL_ORDER = (("K", "PK", "FG", "P", "LS"), ("KR", "KOR", "PR"), ("KO",))
SPECIAL_JOBS = {"K": "Kicker", "PK": "Kicker", "FG": "Kicker", "P": "Punter", "LS": "Long snapper",
                "KR": "Kick returner", "KOR": "Kick returner", "PR": "Punt returner", "KO": "Kickoff specialist"}
NOT_SCRIMMAGE = {c for group in SPECIAL_ORDER for c in group} | {"H", "OFF", "DEF", "SPE"}
SLOT = re.compile(r"^([A-Z]+)(\d+)$")


# ------------------------------------------------------------------ Jacksonville
def stone_labels(working):
    """{player: label}: Stone's latest dated role decision on the working chart; a later decision
    with no role clears the label."""
    labels = {}
    for decision in (working or {}).get("stone_role_decisions", ()):
        for row in decision.get("decisions", ()):
            if row.get("role") is None:
                labels.pop(row["player"], None)
            else:
                labels[row["player"]] = row["role"]
    return labels


def role_labels(chart, working):
    """{player: label}: Stone's latest dated role decision on the working chart, else his game role
    (the depth chart page's Role column)."""
    labels = stone_labels(working)
    for player, roles in (chart or {}).get("roles", {}).items():
        if player not in labels and roles:
            labels[player] = ", ".join(ROLE_NAMES.get(r, r) for r in roles)
    return labels


def label_errors(working):
    """Stone's role labels that have no page wording (fail closed, like the club page's DECISIONS)."""
    errors = []
    for decision in (working or {}).get("stone_role_decisions", ()):
        for row in decision.get("decisions", ()):
            role = row.get("role")
            if role is not None and role not in LABEL_WORDS:
                errors.append("Stone's role label %r for %s (%s) has no player-page wording in "
                              "runtime/assignments.LABEL_WORDS" % (role, row.get("player"), decision.get("date")))
    return errors


def position_words(position):
    if position not in POSITION_WORDS:
        raise ValueError("no page words for the position %r" % position)
    return POSITION_WORDS[position]


def jacksonville_assignment(name, chart, working):
    """The one plain role the club's records confirm for a Jaguar on the game depth chart, or None
    when he is not on it. A seat first, then Stone's dated label, then his game role, then the
    dime seat and the second quarterback, else a reserve at his chart position."""
    depth = (chart or {}).get("depth") or {}
    positions = (chart or {}).get("positions") or {}
    if not any(name in (names or ()) for names in depth.values()):
        return None
    for group, index, _label, words in OFFENSE_SEATS:
        names = depth.get(group) or []
        if index < len(names) and names[index] == name:
            return words
    for group, _unit, count in DEFENSE_FIRST:
        if name in (depth.get(group) or [])[:count]:
            return "Starting " + position_words(positions.get(name))
    for group, job in SPECIALISTS:
        if (depth.get(group) or [])[:1] == [name]:
            return job
    labels = stone_labels(working)
    if name in labels:
        if labels[name] not in LABEL_WORDS:
            raise ValueError("Stone's role label %r for %s has no page wording" % (labels[name], name))
        return LABEL_WORDS[labels[name]]
    roles = set((chart.get("roles") or {}).get(name) or ())
    if "nickel" in roles:
        return "Nickel cornerback"
    if "outside_reserve" in roles:
        return "Reserve outside cornerback"
    if {"kick_return", "punt_return"} <= roles:
        return "Kick returner and punt returner"
    if "kick_return" in roles:
        return "Kick returner"
    if "punt_return" in roles:
        return "Punt returner"
    group, index = DIME
    names = depth.get(group) or []
    if index < len(names) and names[index] == name:
        return "Dime defensive back"
    quarterbacks = depth.get("QB") or []
    if len(quarterbacks) > 1 and quarterbacks[1] == name:
        return "Backup quarterback"
    return "Reserve " + position_words(positions.get(name))


# ------------------------------------------------------------------ other clubs
def slot_codes(entry):
    """[(code, string)] of a Week 1 library entry's slots, in their written order."""
    out = []
    for token in (entry.get("slots") or "").split(","):
        token = token.strip()
        if not token:
            continue
        m = SLOT.match(token)
        if not m:
            raise ValueError("unreadable Week 1 slot %r for %s" % (token, entry.get("player_id")))
        out.append((m.group(1), int(m.group(2))))
    return out


def slot_errors(library):
    """Week 1 slot codes the player pages have no words for."""
    errors = set()
    for club, data in (library or {}).get("clubs", {}).items():
        for entry in data.get("players", ()):
            try:
                codes = slot_codes(entry)
            except ValueError as exc:
                errors.add(str(exc))
                continue
            for code, _ in codes:
                if code not in SLOT_WORDS:
                    errors.add("Week 1 slot code %s (%s, %s) has no player-page words in "
                               "runtime/assignments.SLOT_WORDS" % (code, entry.get("player_id"), club))
                elif SLOT_WORDS[code] == ROSTER and entry_words(entry) is None:
                    errors.add("Week 1 slot %s of %s (%s) reads through a roster position with no words"
                               % (code, entry.get("player_id"), club))
    return sorted(errors)


def entry_words(entry):
    """The entry's roster position in words: its roster label when the library keeps one, else its
    stored position."""
    return POSITION_WORDS.get(entry.get("listed_position") or entry.get("position"))


def week1_assignment(entry, words=None):
    """One plain role from a Week 1 library entry's slots, or None. A scrimmage slot with the
    lowest string first (ties to the first written), then the kicker, punter or long snapper,
    then a returner, then the kickoff specialist; a holder slot alone names nothing, and a
    special-teams slot names his job only as the first at it."""
    words = words if words is not None else entry_words(entry)
    codes = slot_codes(entry)
    scrimmage = [(string, i, code) for i, (code, string) in enumerate(codes)
                 if code not in NOT_SCRIMMAGE and SLOT_WORDS.get(code) is not None]
    if scrimmage:
        string, _, code = min(scrimmage)
        named = words if SLOT_WORDS[code] == ROSTER else SLOT_WORDS[code]
        if named is None:
            return None
        if string == 1:
            return "Starting " + named
        if code == "QB":
            return "Backup quarterback"
        return "Reserve " + named
    for group in SPECIAL_ORDER:
        for code, string in codes:
            if code in group and string == 1:
                return SPECIAL_JOBS[code]
    return None
