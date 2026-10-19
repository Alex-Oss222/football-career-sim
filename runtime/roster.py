"""Jacksonville's roster record (rebuild step 3b): the one owner of who the club controls.

From 2014 the season's roster is a JSON record in the data area
(``SeasonPaths(year).roster``, placed by the folder map). Each player row
holds his name, roster position, list (``active``, ``reserve`` or
``practice_squad``), his position group on the roster page, his status as the
club recorded it ("Active 53 (re-signed April 4, 2014)": the status and at most
one dated parenthetical) and the club's current medical communication on his
availability (the practice squad carries none), each with its source. The
``departures`` rows hold every player who left the club's control in a dated
table of the season: how control ended, in the year of its heading, and the
historical-rails disposition or the outstanding Jacksonville position.

Every reader of club control reads this record: the weekly build
(runtime/week_inputs.controlled_active), the exclusivity gate
(scripts/check_week_input_exclusivity), the preseason build, the in-season
rails' Jacksonville control, the progression roster, the player pages, the
cap tracker, the age views and repository validation. The roster page
(``SeasonPaths(year).roster_page``) is built from it by scripts/render_club_pages.py.

2013 keeps its historical layout: its roster page stays its own owner, and a
reader given a Markdown roster reads it as it always did.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

LISTS = ("active", "reserve", "practice_squad")
KEYS = ("team", "season", "as_of", "practice_squad_places", "active_limit", "about", "field_sources", "players",
        "departures")
PLAYER_KEYS = ("name", "position", "list", "group", "status", "availability", "sources")
# A value reworded for the page keeps the exact words it was first written in, under "as_written"
# ({field: original text}); it is never rendered.
PLAYER_OPTIONAL = ("as_written",)
DEPARTURE_KEYS = ("name", "position", "heading", "year", "how_control_ended", "source")
DEPARTURE_OPTIONAL = ("disposition", "outstanding", "control_began", "as_written")
# The status a list's rows carry (the status before any dated parenthetical).
# The active list is the 53 in season and the offseason roster before the cut; the reserve lists
# are every reserve status the league uses (injured, PUP, NFI, suspended, exempt).
LIST_STATUS = {"active": re.compile(r"^(?:Active 53|Offseason roster)(?:\s*\(|$)"),
               "reserve": re.compile(r"^(?:Reserve/|Injured reserve|IR\b|PUP|NFI|Suspended|Commissioner)"),
               "practice_squad": re.compile(r"^Practice squad(?:\s*\(|$)")}


LINKED_NAME = re.compile(r"^\[[^\]]*\]\(")


def refuse_built_page(path, names):
    """Fail on a Markdown roster without plain player rows. From 2014 the roster page is built from
    the record (its player cells are links to the player pages), so a reader of the 2013 page layout
    handed it would misread the club; read the record (``SeasonPaths(year).roster``) instead."""
    names = list(names)
    if not names or any(LINKED_NAME.match(name) for name in names):
        raise ValueError("%s holds no plain player rows: from 2014 read the roster record "
                         "(SeasonPaths(year).roster), not the built roster page" % path)


def list_for(status):
    """The list a status belongs to, or None."""
    return next((name for name, pattern in LIST_STATUS.items() if pattern.match(status or "")), None)


def is_record(path):
    """Whether a roster path is the JSON record (2014 onward) rather than a Markdown page."""
    return Path(path).suffix == ".json"


def load(path):
    """The roster record at ``path``, checked; a broken record fails closed."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = errors(data)
    if problems:
        raise ValueError("Invalid roster record %s: %s" % (path, "; ".join(problems)))
    return data


def errors(data):
    """Schema problems of a roster record."""
    out = []
    if not isinstance(data, dict) or set(data) != set(KEYS):
        return ["the record must hold exactly %s" % ", ".join(KEYS)]
    try:
        date.fromisoformat(data["as_of"]["date"])
    except (TypeError, KeyError, ValueError):
        out.append("as_of needs an ISO date")
    if not isinstance(data["as_of"], dict) or not isinstance(data["as_of"].get("event"), str):
        out.append("as_of needs the event it follows")
    seen = set()
    for row in data["players"]:
        if (not isinstance(row, dict) or not set(PLAYER_KEYS) <= set(row)
                or not set(row) <= set(PLAYER_KEYS) | set(PLAYER_OPTIONAL)):
            out.append("player row keys must be %s (optionally %s): %r"
                       % (", ".join(PLAYER_KEYS), ", ".join(PLAYER_OPTIONAL), row))
            continue
        if "as_written" in row and not _as_written_ok(row):
            out.append("%s: as_written must hold the original text of fields the row has" % row["name"])
        name = row["name"]
        if name in seen:
            out.append("%s is listed twice" % name)
        seen.add(name)
        if row["list"] not in LISTS:
            out.append("%s: unknown list %r" % (name, row["list"]))
        elif not LIST_STATUS[row["list"]].match(row["status"] or ""):
            out.append("%s: status %r does not belong to the %s list" % (name, row["status"], row["list"]))
        if row["list"] == "active" and not row["group"]:
            out.append("%s: an active player needs a position group" % name)
        if row["list"] != "practice_squad" and not isinstance(row["availability"], str):
            out.append("%s: availability needs the club's current communication" % name)
        sources = row["sources"] if isinstance(row["sources"], dict) else {}
        if not sources.get("status") or (row["availability"] is not None and not sources.get("availability")):
            out.append("%s: every value needs its source" % name)
    for row in data["departures"]:
        if (not isinstance(row, dict) or not set(DEPARTURE_KEYS) <= set(row)
                or not set(row) <= set(DEPARTURE_KEYS) | set(DEPARTURE_OPTIONAL)):
            out.append("departure row keys must be %s (optionally %s): %r"
                       % (", ".join(DEPARTURE_KEYS), ", ".join(DEPARTURE_OPTIONAL), row))
        elif type(row["year"]) is not int:
            out.append("%s's departure needs the year of its heading" % row["name"])
        elif "as_written" in row and not _as_written_ok(row):
            out.append("%s's departure: as_written must hold the original text of fields the row has" % row["name"])
    return out


def _as_written_ok(row):
    kept = row["as_written"]
    return (isinstance(kept, dict) and bool(kept) and all(k in row and k != "as_written" for k in kept)
            and all(isinstance(v, str) and v != row[k] for k, v in kept.items()))


def players(data, lists=LISTS):
    """The player rows on the given lists, in the record's order."""
    return [row for row in data["players"] if row["list"] in lists]


def controlled(data):
    """The controlled players the roster counts: the active roster and the reserve lists (the
    practice squad is under contract but counted apart)."""
    return players(data, ("active", "reserve"))


def as_of_label(data):
    """"October 5, 2014, after the Week 5 game against Pittsburgh"."""
    day = date.fromisoformat(data["as_of"]["date"])
    return "%s %d, %d, %s" % (day.strftime("%B"), day.day, day.year, data["as_of"]["event"])


def status_name(status):
    """A status without its dated parenthetical: "Active 53 (re-signed April 4, 2014)" is "Active 53"."""
    return re.sub(r"\s*\(.*\)$", "", status).strip()


def counts(data):
    """{active, reserve, practice_squad, controlled, open active places, open practice-squad places}."""
    n = {name: len(players(data, (name,))) for name in LISTS}
    n["controlled"] = n["active"] + n["reserve"]
    n["open_active"] = data["active_limit"] - n["active"]
    n["open_practice_squad"] = data["practice_squad_places"] - n["practice_squad"]
    return n
