"""The 2014 draft's selection order, from closed branch receipts only.

Rules (library/2014_league_calendar_and_financial_rules.md, section D):
- the 20 non-playoff clubs select 1-20 in order of regular-season winning
  percentage, lowest first;
- the 12 playoff clubs select 21-32 by round of elimination: Wild Card losers
  21-24, Divisional losers 25-28, conference-championship losers 29-30, the
  Super Bowl loser 31 and the winner 32; within a group, lowest winning
  percentage first;
- ties in winning percentage go to the club with the lower strength of
  schedule. A tie that survives strength of schedule needs the division or
  conference tiebreakers and then a coin flip; that step is never simulated
  here. Such clubs are reported as an unresolved tie in alphabetical order.

This module orders slots by club. Pick ownership (trades) is a separate
record: see career/2014/draft/draft_order.md.
"""
import json
from pathlib import Path

from .league import TEAMS
from .standings import Season, games_from_receipts
from . import postseason

ROOT = Path(__file__).resolve().parents[1]
GROUPS = (("non-playoff", 1), ("wild_card", 21), ("divisional", 25),
          ("conference", 29), ("super_bowl_loser", 31), ("champion", 32))


def _load(directory):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]


def elimination(post_receipts):
    """{club: group} for the 12 playoff clubs, from the closed postseason receipts."""
    loser_group = {18: "wild_card", 19: "divisional", 20: "conference", 21: "super_bowl_loser"}
    out = {}
    for receipt in post_receipts:
        week = int(receipt["week"])
        won = postseason.winner(receipt)
        lost = next(t for t in receipt["final_score"] if t != won)
        out[lost] = loser_group[week]
        if week == 21:
            out[won] = "champion"
    return out


def _break(season, tied, division_ranks):
    """[(club, how)] earliest pick first for clubs tied on percentage and SOS.

    Same division or same conference: the club that would win the standings
    tiebreaker picks later. Clubs in different conferences, or clubs still
    level, await a coin flip that is never simulated here.
    """
    if len(tied) == 1:
        return [(tied[0], None)]
    from .league import DIVISION_OF, conference_of
    if len({conference_of(c) for c in tied}) > 1:
        return [(c, "coin flip pending: " + ", ".join(o for o in tied if o != c)) for c in tied]
    step = "division" if len({DIVISION_OF[c] for c in tied}) == 1 else "conference"
    remaining, later = list(tied), []
    while len(remaining) > 1:
        winner = season.best_of(remaining, "2014 draft order", division_ranks)
        later.insert(0, winner)
        remaining.remove(winner)
    earliest_first = remaining + later
    return [(c, step + " tiebreaker with " + ", ".join(o for o in tied if o != c)) for c in earliest_first]


def order(regular_receipts=None, post_receipts=None):
    """[{slot, club, group, record, pct, sos, tie}] for slots 1-32."""
    regular = _load(postseason.REGULAR_RECEIPTS) if regular_receipts is None else regular_receipts
    post = _load(postseason.POSTSEASON_RECEIPTS) if post_receipts is None else post_receipts
    if sum(1 for r in post if int(r["week"]) == 21) != 1:
        raise ValueError("the Super Bowl has not closed; the draft order is not final")
    season = Season(games_from_receipts(regular))
    sos = season.strength_of_schedule(list(TEAMS))
    group_of = elimination(post)
    for club in TEAMS:
        group_of.setdefault(club, "non-playoff")
    division_ranks = season.division_ranks()
    season.recording = False
    rows = []
    for group, first in GROUPS:
        clubs = [c for c in TEAMS if group_of[c] == group]
        key = lambda c: (season.pct(c), round(sos[c], 6))
        ordered = []
        for value in sorted({key(c) for c in clubs}):
            tied = sorted(c for c in clubs if key(c) == value)
            ordered.extend((club, how) for club, how in _break(season, tied, division_ranks))
        for i, (club, how) in enumerate(ordered):
            line = season.lines[club].overall
            rows.append({"slot": first + i, "club": club, "group": group,
                         "record": line.text(), "pct": season.pct(club), "sos": sos[club],
                         "tie": how})
    assert [r["slot"] for r in rows] == list(range(1, 33))
    return rows
