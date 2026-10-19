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


def leaders(team):
    """[(category, player, season line)] for passing, rushing, receiving and tackling: the club's
    leader in each by yards (tackles), ties going to the later name."""
    stats = team.get("players") or {}
    out = []
    for label, field, unit in (("Passing", "passing_yards", "pass yds"), ("Rushing", "rushing_yards", "rush yds"),
                               ("Receiving", "receiving_yards", "rec yds"), ("Tackling", "tackles", "tackles")):
        ranked = [(name, row) for name, row in stats.items() if row.get(field, 0)]
        if not ranked:
            continue
        name, row = max(ranked, key=lambda pair: (pair[1].get(field, 0), pair[0]))
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
        out.append((label, name, value + (" · " + ", ".join(extra) if extra else "")))
    return out


# ------------------------------------------------------------------ medical
STATUS = re.compile(r"^(?P<kind>[A-Z][^,:;]*?),\s*(?P<severity>[^:;]+?):\s*(?P<injury>[^,;(]+)")
DATE = r"([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)"
REVIEW = re.compile(r"\breassessment " + DATE)
PROJECTED = re.compile(r"\bprojected return " + DATE)


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
    match = STATUS.match(row.get("availability") or "")
    if not match:
        return "Under medical instruction"
    kind = "Independent hold" if match["kind"] == "Independent medical hold" else match["kind"]
    return "%s · %s (%s)" % (kind, match["injury"].strip(), match["severity"].strip())


def _on(text, as_of):
    """The date ``text`` names ("October 6" or "October 6, 2014"), the year taken as the nearer one
    to ``as_of`` when the text gives none."""
    if "," in text:
        return datetime.strptime(text, "%B %d, %Y").date()
    month_day = datetime.strptime(text + " 2000", "%B %d %Y").date()
    options = [month_day.replace(year=y) for y in (as_of.year - 1, as_of.year, as_of.year + 1)]
    return min(options, key=lambda d: abs((d - as_of).days))


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

