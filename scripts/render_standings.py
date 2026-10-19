#!/usr/bin/env python3
"""Rebuild career/YEAR/standings.md from closed-game stat receipts.

`--through-week N` prints the standings as they stood after week N instead
of writing the current file; `--check` writes nothing and exits 1 when the
page differs from its render.

From 2014 the page is written clean (docs/rebuild_plan.md, rule 4): football
words only, the streak as "Won 3", with no file, script or rulebook names.
Every figure, order and seed is the same computation as before; 2013 keeps
its page byte for byte.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.league import CONFERENCES, DIVISION_OF, DIVISIONS, TEAMS, conference_of
from runtime.standings import compute, pct_text
from runtime.seasons import CLEAN_SEASON
from scripts.render_season_stats import load_receipts

PROTAGONIST = "Jacksonville Jaguars"
# The first season whose standings page is written clean (the 2013 page is history).
CLEAN_FROM = CLEAN_SEASON
STREAK_WORDS = {"W": "Won", "L": "Lost", "T": "Tied"}


def club(team):
    return "**%s**" % team if team == PROTAGONIST else team


def diff(value):
    return "%+d" % value if value else "0"


def streak_text(streak, clean):
    """The streak cell: the stored "W3" form, or "Won 3" on a clean page."""
    if clean and streak[:1] in STREAK_WORDS and streak[1:].isdigit():
        return "%s %s" % (STREAK_WORDS[streak[0]], streak[1:])
    return streak


def division_tables(result, clean=False):
    lines = ["## Division standings", "",
             "Clubs are ordered by winning percentage, ties broken by the division procedure.", ""]
    for division in DIVISIONS:
        lines += ["### " + division, "",
                  "| Team | W | L | T | Pct | PF | PA | Diff | Home | Away | Div | Conf | Strk |",
                  "|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|---|---|"]
        for team in result["division_ranks"][division]:
            line = result["lines"][team]
            o = line.overall
            lines.append("| %s | %d | %d | %d | %s | %d | %d | %s | %s | %s | %s | %s | %s |" % (
                club(team), o.wins, o.losses, o.ties, pct_text(o.pct), line.points_for,
                line.points_against, diff(line.points_for - line.points_against),
                line.home.text(), line.away.text(), line.division.text(), line.conference.text(),
                streak_text(line.streak, clean)))
        lines.append("")
    return lines


def conference_tables(result):
    lines = ["## Conference standings and playoff seeding", ""]
    if not result["played"]:
        lines += ["No game has been played, so no club is seeded. Six clubs per conference "
                  "qualify: the four division winners (seeds 1-4) and two wild cards (seeds 5-6).", ""]
    else:
        lines += ["If the season ended today. Seeds 1-4 are the division leaders ordered by record; "
                  "seeds 5-6 are the two best remaining clubs. Every other club follows in wild-card order.", ""]
    for conference in CONFERENCES:
        entry = result["conferences"][conference]
        order = entry["division_winners"] + entry["others"]
        lines += ["### " + conference, "",
                  "| Rank | Team | Division | W | L | T | Pct | Div | Conf | SOV | SOS | Status |",
                  "|--:|---|---|--:|--:|--:|--:|---|---|--:|--:|---|"]
        for index, team in enumerate(order, 1):
            line = result["lines"][team]
            o = line.overall
            if not result["played"]:
                status = "-"
            elif index <= 4:
                status = "Seed %d, division leader" % index
            elif index <= 4 + result["wild_cards"]:
                status = "Seed %d, wild card" % index
            else:
                status = "Out of the field"
            rank = str(index) if result["played"] else "-"
            lines.append("| %s | %s | %s | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
                rank, club(team), DIVISION_OF[team].split()[1], o.wins, o.losses, o.ties,
                pct_text(o.pct), line.division.text(), line.conference.text(),
                pct_text(result["sov"][team]), pct_text(result["sos"][team]), status))
        lines.append("")
    return lines


def league_table(result):
    lines = ["## League", "",
             "All 32 clubs by winning percentage. Clubs with the same percentage share a place; "
             "league-wide order is not tiebroken across conferences here.", "",
             "| Place | Team | Conf | W | L | T | Pct | PF | PA | Diff |",
             "|--:|---|---|--:|--:|--:|--:|--:|--:|--:|"]
    rows = sorted(TEAMS, key=lambda t: (-result["lines"][t].overall.pct, t))
    place = 0
    for index, team in enumerate(rows, 1):
        line = result["lines"][team]
        o = line.overall
        if index == 1 or o.pct != result["lines"][rows[index - 2]].overall.pct:
            place = index
        lines.append("| %s | %s | %s | %d | %d | %d | %s | %d | %d | %s |" % (
            place if result["played"] else "-", club(team), conference_of(team), o.wins, o.losses,
            o.ties, pct_text(o.pct), line.points_for, line.points_against,
            diff(line.points_for - line.points_against)))
    lines.append("")
    return lines


def tiebreak_notes(result):
    lines = ["## Tiebreakers applied", ""]
    if not result["notes"]:
        return lines + ["None. No two clubs have yet needed a tiebreaker.", ""]
    for note in result["notes"]:
        others = ", ".join(note["others"])
        if note["step"]:
            lines.append("- %s: %s over %s on %s." % (note["context"], note["winner"], others, note["step"]))
        else:
            lines.append("- %s: %s and %s remain tied after every step before the coin toss; "
                         "listed alphabetically as an unbroken tie." % (note["context"], note["winner"], others))
    lines.append("")
    return lines


def render(year, receipts, through_week=None):
    from runtime.seasons import require_receipt_season
    require_receipt_season(receipts, year)
    if through_week is not None:
        receipts = [r for r in receipts if int(r["week"]) <= through_week]
    result = compute(receipts)
    week = result["through_week"]
    through = ("Week %d" % week) if result["played"] else "no regular-season game has been played"
    if year >= CLEAN_FROM:
        lines = [
            "# %d NFL standings" % year, "",
            "**Through:** %s. All 32 clubs, regular-season games only." % through, "",
            "Pct counts a tie as half a win. SOV is strength of victory, the combined winning "
            "percentage of the clubs a team has beaten; SOS is strength of schedule, the combined "
            "winning percentage of all its opponents. Ties in the standings are broken by the NFL "
            "tiebreaking procedure; a tie that survives to the coin toss is reported, never tossed.", "",
        ]
        return "\n".join(lines + division_tables(result, clean=True) + conference_tables(result)
                         + league_table(result) + tiebreak_notes(result))
    lines = [
        "# %d NFL standings" % year, "",
        "**Through:** %s." % through,
        "**Scope:** all 32 clubs; regular-season games only.",
        "**Source:** generated from the closed-game receipts in `stats/game_receipts/` by "
        "`python scripts/render_standings.py %d`. Past weeks: add `--through-week N`." % year, "",
        "Pct counts a tie as half a win. SOV is strength of victory, the combined winning "
        "percentage of the clubs a team has beaten; SOS is strength of schedule, the combined "
        "winning percentage of all its opponents. Tiebreakers follow the 2013 NFL procedure in "
        "Document 2 section 5.3; a tie that survives to the coin toss is reported, never tossed.", "",
    ]
    lines += division_tables(result) + conference_tables(result) + league_table(result) + tiebreak_notes(result)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("year", type=int)
    parser.add_argument("--through-week", type=int)
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when the page is stale")
    args = parser.parse_args()
    from runtime.seasons import SeasonPaths
    paths = SeasonPaths(args.year, ROOT)
    receipts = load_receipts(paths.receipts)
    text = render(args.year, receipts, args.through_week)
    if args.through_week is not None:
        print(text)
        return
    if args.check:
        page = paths.record('standings.md')
        current = page.is_file() and page.read_text(encoding="utf-8") == text
        print("STANDINGS CURRENT" if current else "Standings stale: %s" % page.relative_to(ROOT))
        return 0 if current else 1
    paths.record('standings.md').write_text(text, encoding="utf-8")
    print("rendered standings from %d receipts" % len(receipts))


if __name__ == "__main__":
    sys.exit(main())
