"""Short football summaries several built pages share (rebuild step 4).

The desk, the statistics index, the injury report and the depth chart each show
a few of the same facts in the same words: the club's record and place, its
points and third-down rates, its leaders, and each player's medical status and
next medical date. They are worked out here once, from the closed games and the
roster record, so the pages cannot disagree. Nothing here owns a page, decides
anything or reads a built page back.
"""
from __future__ import annotations

import re
from datetime import datetime

from .league import DIVISION_OF

NO_RESTRICTION = "No communicated restriction"
ORDINALS = {1: "1st", 2: "2nd", 3: "3rd"}


def ordinal(n):
    return ORDINALS.get(n, "%dth" % n)


# ------------------------------------------------------------------ the club's season
def club_games(receipts, club):
    """The club's closed regular-season games, in week order."""
    return sorted((r for r in receipts if club in (r["home"], r["away"])), key=lambda r: int(r["week"]))


def opponent(receipt, club):
    return receipt["away"] if receipt["home"] == club else receipt["home"]


def record_text(games, club):
    """"3-2", with ties when there are any."""
    won = lost = tied = 0
    for r in games:
        ours, theirs = r["final_score"][club], r["final_score"][opponent(r, club)]
        won, lost, tied = won + (ours > theirs), lost + (ours < theirs), tied + (ours == theirs)
    return "%d-%d" % (won, lost) + ("-%d" % tied if tied else "")


def glance(team, games, standings, club):
    """(record and place, points, efficiency): the three cells of the season line."""
    own, against = team.get("team_stats") or {}, team.get("opponent_stats") or {}
    played = len(games)
    if not played:
        return ("No games played", "Not established", "Not established")
    division = DIVISION_OF[club]
    conference = division.split()[0]
    place = standings["division_ranks"][division].index(club) + 1
    order = standings["conferences"][conference]["division_winners"] + standings["conferences"][conference]["others"]
    first = "%s · %s %s · %s position %d" % (record_text(games, club), ordinal(place), division, conference,
                                              order.index(club) + 1)
    scored, allowed = own.get("points", 0), against.get("points", 0)
    points = "%d scored · %d allowed · %+d differential" % (scored, allowed, scored - allowed)
    made, tries = own.get("third_down_conversions", 0), own.get("third_down_attempts", 0)
    given, faced = against.get("third_down_conversions", 0), against.get("third_down_attempts", 0)
    efficiency = "%0.1f points per game · %0.1f%% on third down · %0.1f%% allowed" % (
        scored / played, 100 * made / tries if tries else 0, 100 * given / faced if faced else 0)
    return first, points, efficiency


def _sacks(value):
    shown = ("%g" % value) if isinstance(value, float) else str(value)
    return "%s sack%s" % (shown, "" if value == 1 else "s")


def tied_leaders(players, field):
    """[(name, line)] of every player sharing the club's highest nonzero ``field``, in name order:
    a tie is shown as a tie, never settled by the order of the names."""
    ranked = [(name, row) for name, row in (players or {}).items() if row.get(field, 0)]
    if not ranked:
        return []
    top = max(row.get(field, 0) for _, row in ranked)
    return sorted((pair for pair in ranked if pair[1].get(field, 0) == top), key=lambda pair: pair[0])


def leaders(team):
    """[(category, player, season line)] for passing, rushing, receiving and tackling: the club's
    leader in each by yards (tackles). Players tied for the lead each have a row, the category
    reading "Tackling, tied"."""
    stats = team.get("players") or {}
    out = []
    for label, field, unit in (("Passing", "passing_yards", "pass yds"), ("Rushing", "rushing_yards", "rush yds"),
                               ("Receiving", "receiving_yards", "rec yds"), ("Tackling", "tackles", "tackles")):
        top = tied_leaders(stats, field)
        for name, row in top:
            value = "%s %s" % (format(row.get(field, 0), ","), unit)
            extra = []
            if field == "passing_yards":
                extra = ["%d TD" % row.get("passing_touchdowns", 0), "%d INT" % row.get("interceptions_thrown", 0)]
            elif field == "rushing_yards":
                extra = ["%d TD" % row.get("rushing_touchdowns", 0)]
            elif field == "receiving_yards":
                extra = ["%d catches" % row.get("receptions", 0), "%d TD" % row.get("receiving_touchdowns", 0)]
            elif row.get("sacks"):
                extra = [_sacks(row["sacks"])]
            out.append((label + (", tied" if len(top) > 1 else ""), name,
                        value + (" · " + ", ".join(extra) if extra else "")))
    return out


# ------------------------------------------------------------------ medical
# The roster record's medical communication for a player (its ``availability`` field) has one
# format, which the injury report, the desk, the depth chart and the Game Week Briefing all read
# here, and which runtime/week_pages.availability_entry writes from a game's record:
#
#   <Instruction>, <severity>: <injury>[, <how and when it happened>][; projected return
#   <Month D, YYYY>][; reassessment <Month D>][; no practice before <Month D>, no return before
#   <Month D>][; <later findings>] ([medical record](<incident record>))
#
# <Instruction> is "Out", "Limited" or "Independent medical hold"; <severity> is the game's
# severity in words ("minor", "short", "multi-week", "long term"). A reassessment's year is the
# one nearer the date the page is built for, so an exam across the new year keeps its year.
STATUS = re.compile(r"^(?P<kind>[A-Z][^,:;]*?),\s*(?P<severity>[^:;]+?):\s*(?P<injury>[^,;(]+)")
DATE = r"([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)"
REVIEW = re.compile(r"\breassessment " + DATE)
PROJECTED = re.compile(r"\bprojected return " + DATE)
LIMIT = re.compile(r"\bno (?:practice|return) before [A-Z][a-z]+ \d{1,2}(?:, \d{4})?")
RECORD = re.compile(r"\[(medical record|medical history)\]\(([^)]+)\)")
KINDS = {"Independent medical hold": "Independent hold"}


def under_instruction(row):
    """Whether the roster record carries a medical communication for the player."""
    return not (row.get("availability") or NO_RESTRICTION).startswith(NO_RESTRICTION)


def held(roster):
    """The players on the active roster under a medical instruction, in the record's order."""
    return [p for p in roster.get("players") or () if p.get("list") == "active" and under_instruction(p)]


def reserve(roster):
    return [p for p in roster.get("players") or () if p.get("list") == "reserve"]


def medical_status(row):
    """"Out · lower extremity (minor)", "Independent hold · head/neck (short)": the instruction,
    the injury and its severity as the roster record gives them."""
    if not under_instruction(row):
        return NO_RESTRICTION
    match = STATUS.match(row.get("availability") or "")
    if not match:
        return "Under medical instruction"
    kind = KINDS.get(match["kind"], match["kind"])
    return "%s · %s (%s)" % (kind, match["injury"].strip(), match["severity"].strip())


def medical_entry(row, as_of):
    """The player's medical communication read in its one format (above), as of ``as_of``:
    {"instruction", "injury", "severity", "projected" (a date or None), "reviews" (the
    reassessments on or after ``as_of``, in order), "limits" (the communicated limits, as
    written), "record" ((label, destination from the roster page) or None)}. None when the
    player carries no communicated restriction; ValueError when the text is not in the format."""
    text = row.get("availability") or ""
    if not under_instruction(row):
        return None
    match = STATUS.match(text)
    if not match:
        raise ValueError("%s's medical communication is not in the medical format: %r" % (row.get("name"), text))
    projected = PROJECTED.search(text)
    reviews = sorted({_on(m.group(1), as_of) for m in REVIEW.finditer(text)})
    record = RECORD.search(text)
    return {"instruction": KINDS.get(match["kind"], match["kind"]), "injury": match["injury"].strip(),
            "severity": match["severity"].strip(),
            "projected": _on(projected.group(1), as_of) if projected else None,
            "reviews": [d for d in reviews if d >= as_of],
            "limits": [m.group(0) for m in LIMIT.finditer(text)],
            "record": (record.group(1), record.group(2)) if record else None}


def format_errors(roster, as_of):
    """Every roster player's medical communication that is not in the medical format, or whose
    projected return gives no year."""
    errors = []
    for row in roster.get("players") or ():
        try:
            entry = medical_entry(row, as_of)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        found = PROJECTED.search(row.get("availability") or "") if entry else None
        if found and "," not in found.group(1):
            errors.append("%s's projected return (%s) gives no year" % (row.get("name"), found.group(1)))
    return errors


def _on(text, as_of):
    """The date ``text`` names ("October 6" or "October 6, 2014"), the year taken as the nearer one
    to ``as_of`` when the text gives none."""
    if "," in text:
        return datetime.strptime(text, "%B %d, %Y").date()
    month_day = datetime.strptime(text + " 2000", "%B %d %Y").date()
    options = [month_day.replace(year=y) for y in (as_of.year - 1, as_of.year, as_of.year + 1)]
    return min(options, key=lambda d: abs((d - as_of).days))


def date_on(text, as_of):
    """The date ``text`` names ("October 6" or "October 6, 2014"), a missing year taken as the one
    nearer ``as_of``."""
    return _on(text, as_of)


def _long(day):
    return "%s %d, %d" % (day.strftime("%B"), day.day, day.year)


def next_dates(row, as_of):
    """"Review October 6; projected return October 6, 2014": the next reassessment and the projected
    return the roster record gives, each only when it falls on or after ``as_of`` (a passed date is
    history, kept on the player's medical record)."""
    text = row.get("availability") or ""
    out = []
    for label, pattern in (("Review", REVIEW), ("Projected return", PROJECTED)):
        found = pattern.search(text)
        if found:
            day = _on(found.group(1), as_of)
            if day >= as_of:
                out.append("%s %s" % (label if not out else label.lower(), _long(day)))
    return "; ".join(out) or "None communicated"


# ------------------------------------------------------------------ the week's schedule
MONTH_DAY = re.compile(r"^((?:January|February|March|April|May|June|July|August|September|October|November|"
                       r"December) \d{1,2})\b")


def first_practice(scheduled, week, as_of):
    """The first day of Week ``week``'s practice week, from the scheduled events ((date, event)
    pairs: Document 5's next dated events, "October 7 to 11 | Week 6 practice week"), when it is
    still to come on ``as_of``; else None. A game plan's practice work is due before it."""
    pattern = re.compile(r"\bWeek %d practice week\b" % week)
    for when, what in scheduled:
        start = MONTH_DAY.match(when)
        if start and pattern.search(what):
            first = _on(start.group(1), as_of)
            return first if first >= as_of else None
    return None

