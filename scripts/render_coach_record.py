#!/usr/bin/env python3
"""Stone's head-coaching record table for the weekly turn's Coach info block.

Every count comes from the closed-game receipts (regular-season receipts and
the sibling postseason receipts of every season from his first, 2013, through
the requested season); nothing is typed. The career start is the accepted
Jacksonville hire, January 15, 2013 (the 2013 season ledger header and
Document 3 section 3.1), so `--date` prints the day count since it.

    python scripts/render_coach_record.py 2014 --opponent "Philadelphia Eagles" --date 2014-09-07

The table follows the template's omission rules: no postseason column until a
postseason game has been coached, and no "This season" row in the first
season with the team, when it would repeat the row below it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.standings import pct_text

TEAM = "Jacksonville Jaguars"
FIRST_SEASON = 2013
CAREER_START = dt.date(2013, 1, 15)


def nickname(club):
    return club.split()[-1]


def load_games(year, root=ROOT):
    """[(postseason?, receipt)] for every Jacksonville game closed in that season."""
    from runtime.seasons import SeasonPaths
    paths = SeasonPaths(year, root)
    games = []
    for postseason, folder in ((False, paths.receipts), (True, paths.postseason_receipts)):
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.json")):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            if TEAM in (receipt.get("home"), receipt.get("away")):
                games.append((postseason, receipt))
    return games


def outcome(receipt):
    """'W', 'L' or 'T' for Jacksonville."""
    score = receipt["final_score"]
    other = receipt["home"] if receipt["away"] == TEAM else receipt["away"]
    mine, theirs = score[TEAM], score[other]
    return "W" if mine > theirs else "L" if mine < theirs else "T"


def opponent_of(receipt):
    return receipt["home"] if receipt["away"] == TEAM else receipt["away"]


class Tally:
    def __init__(self):
        self.regular = {"W": 0, "L": 0, "T": 0}
        self.postseason = {"W": 0, "L": 0, "T": 0}

    def add(self, postseason, result):
        (self.postseason if postseason else self.regular)[result] += 1

    @staticmethod
    def _text(counts, with_ties=True):
        base = "%d-%d" % (counts["W"], counts["L"])
        return base + ("-%d" % counts["T"] if with_ties else "")

    @staticmethod
    def _pct(counts):
        games = counts["W"] + counts["L"] + counts["T"]
        return pct_text((counts["W"] + 0.5 * counts["T"]) / games) if games else ".000"

    def overall(self):
        return {k: self.regular[k] + self.postseason[k] for k in self.regular}

    def cells(self, with_pct, show_postseason):
        regular, overall = self._text(self.regular), self._text(self.overall())
        if with_pct:
            regular += " (%s)" % self._pct(self.regular)
            overall += " (%s)" % self._pct(self.overall())
        cells = [regular]
        if show_postseason:
            cells.append(self._text(self.postseason, with_ties=False))
        return cells + [overall]


def compute(year, opponent=None, root=ROOT):
    """Rows of the record table, in template order."""
    games = {season: load_games(season, root) for season in range(FIRST_SEASON, year + 1)}
    season, team, career, versus = Tally(), Tally(), Tally(), Tally()
    for s, played in games.items():
        for postseason, receipt in played:
            result = outcome(receipt)
            career.add(postseason, result)
            team.add(postseason, result)  # one club so far: career and club tallies agree
            if s == year:
                season.add(postseason, result)
            if opponent and opponent in (opponent_of(receipt), nickname(opponent_of(receipt))):
                versus.add(postseason, result)
    show_postseason = sum(career.postseason.values()) > 0
    rows = []
    if year > FIRST_SEASON:
        rows.append(("This season", season.cells(False, show_postseason)))
    rows.append(("With %s" % nickname(TEAM), team.cells(True, show_postseason)))
    rows.append(("NFL head coach, career", career.cells(True, show_postseason)))
    if opponent:
        rows.append(("Against %s" % opponent, versus.cells(False, show_postseason)))
    return rows, show_postseason


def render(year, opponent=None, root=ROOT):
    rows, show_postseason = compute(year, opponent, root)
    headers = ["Record", "Regular season"] + (["Postseason"] if show_postseason else []) + ["Overall"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for label, cells in rows:
        lines.append("| " + " | ".join([label] + cells) + " |")
    return "\n".join(lines)


def days_since_start(on):
    return (on - CAREER_START).days


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("year", type=int, help="The season the turn belongs to")
    parser.add_argument("--opponent", help="Club name for the 'Against' row")
    parser.add_argument("--date", type=dt.date.fromisoformat, help="The turn's date, for the day count")
    args = parser.parse_args()
    if args.date:
        print("Day %d since career start (%s)" % (days_since_start(args.date), CAREER_START.isoformat()))
        print()
    print(render(args.year, args.opponent))


if __name__ == "__main__":
    main()
