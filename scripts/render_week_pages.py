#!/usr/bin/env python3
"""Build the result-side pages a game week's close rewrites (rebuild step 4).

  python scripts/render_week_pages.py [--season YEAR] [--check] [--root PATH]

The pages and their owners are listed in runtime/week_pages.py: the Games
index, the league-results index and week pages (from the first Game Report
week), the current injury report, the medical history's entry for each
Jacksonville game's injuries (appended once, with its event-record line) and
one incident record per new injury (created once, then kept by hand).

Write mode rebuilds every page, appends a missing medical-history entry at the
end of the history and creates a missing incident record; it never rewrites
an existing incident record or an earlier history entry. A new incident
record is a new medical owner, so the write then refreshes the season
handoff's carry-forward inventory (scripts/season_handoff.prepare), as the
close of any week with a new injury does. Nothing is written
when a page would break the clean-page rule (runtime/clean_pages.py): the
problems are printed instead. ``--check`` writes nothing and reports a page
that is missing, stale, hand-edited or unclean, a game without its medical
history entry, a missing incident record (an entry and an incident record
are written once, as of the game, and later facts never rewrite them) and a
roster medical communication not in its one format (runtime/season_summary.py).
``--availability`` prints, and writes nothing, each player's medical
communication from the latest Jacksonville game's record, in that format, for
the close to record on his roster row. Run it after
every closed game and after any change to the roster record
(docs/update_workflow.md); repository validation runs the check.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import season_summary as summary, week_pages  # noqa: E402
from runtime.clean_pages import text_errors  # noqa: E402
from runtime.seasons import CLEAN_SEASON, active_season  # noqa: E402


def plan(root, year):
    """(season, {rel: text} to write in full, appended history text or None, {rel: text} new incidents)."""
    root = Path(root).resolve()
    season = week_pages.Season(root, year)
    history = week_pages.medical_path(season, "medical_history.md")
    current = history.read_text(encoding="utf-8") if history.is_file() else ""
    missing = [entry for event, entry in week_pages.history_entries(season) if '"id": "%s"' % event not in current]
    appended = None
    if missing:
        appended = current.rstrip("\n") + "\n\n" + "\n".join(missing)
    created = {rel: text for rel, text in week_pages.incidents(season).items() if not (root / rel).is_file()}
    # The pages link the incident records this write creates, so one write is final.
    season.pending = set(created)
    pages = week_pages.built(season)
    return season, pages, appended, created


def check(root=ROOT, year=None):
    root = Path(root).resolve()
    year = active_season(root) if year is None else year
    if year < CLEAN_SEASON:
        return []
    season = week_pages.Season(root, year)
    errors = []
    for rel, text in week_pages.built(season).items():
        path = root / rel
        if not path.is_file():
            errors.append("Week page missing: %s; run scripts/render_week_pages.py" % rel)
        elif path.read_bytes() != text.encode("utf-8"):
            errors.append("Week page stale or hand-edited: %s; run scripts/render_week_pages.py" % rel)
        errors += text_errors(rel, text, root)
    history = week_pages.medical_path(season, "medical_history.md")
    current = history.read_text(encoding="utf-8") if history.is_file() else ""
    for event, _ in week_pages.history_entries(season):
        if '"id": "%s"' % event not in current:
            errors.append("Medical history lacks the entry for %s; run scripts/render_week_pages.py" % event)
    for rel in week_pages.incidents(season):
        if not (root / rel).is_file():
            errors.append("Incident record missing: %s; run scripts/render_week_pages.py" % rel)
    # The pages read each player's medical communication in its one format (runtime/season_summary.py).
    errors += ["Roster record: %s" % e for e in summary.format_errors(season.roster, season.as_of)]
    return errors


def availability(root=ROOT, year=None):
    """[(player, text, source)]: the roster record's medical communication for each Jacksonville
    player injured in the latest closed Jacksonville game, written from the game's record
    (runtime/week_pages.availability_entry), for the close to record on his roster row."""
    root = Path(root).resolve()
    season = week_pages.Season(root, active_season(root) if year is None else year)
    ours = [r for r in season.receipts.values() if week_pages.JAX in (r["away"], r["home"])]
    if not ours:
        return []
    last = max(ours, key=lambda r: int(r["week"]))
    return [(i["player"],) + week_pages.availability_entry(season, last, i) for i in week_pages.ours_injured(last)]


def write(root=ROOT, year=None):
    """Write every page; returns (pages written, problems). Nothing is written when any page would
    break the clean-page rule."""
    root = Path(root).resolve()
    year = active_season(root) if year is None else year
    season, pages, appended, created = plan(root, year)
    history = season.rel(week_pages.medical_path(season, "medical_history.md"))
    outputs = dict(pages)
    outputs.update(created)
    if appended is not None:
        outputs[history] = appended + ("" if appended.endswith("\n") else "\n")
    problems = [p for rel, text in outputs.items() for p in text_errors(rel, text, root)]
    if problems:
        return 0, problems
    written = 0
    for rel, text in outputs.items():
        path = root / rel
        data = text.encode("utf-8")
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written += 1
    if created:
        # A new incident record is a new medical owner: the season handoff's carry-forward
        # inventory lists the medical owners, so it is refreshed (reopening the medical review).
        from scripts import season_handoff
        if season_handoff.manifest_path(root, year).is_file():
            season_handoff.prepare(root, year)
    return written, []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--availability", action="store_true",
                        help="print each player's medical communication from the latest Jacksonville game; writes nothing")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.availability:
        for player, text, source in availability(args.root, args.season):
            print("%s\n  availability: %s\n  source: %s" % (player, text, source))
        return 0
    if args.check:
        errors = check(args.root, args.season)
        print("\n".join(errors) if errors else "WEEK PAGES CURRENT")
        return 1 if errors else 0
    written, problems = write(args.root, args.season)
    if problems:
        print("Week pages not written: each would break the clean-page rule\n" + "\n".join(problems))
        return 1
    print("week pages: %d written" % written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
