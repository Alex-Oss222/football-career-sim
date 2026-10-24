#!/usr/bin/env python3
"""Rebuild every built page of a season, in order, from the stored facts (rebuild steps 4 and 5).

  python scripts/rebuild_pages.py [--season YEAR] [--check] [--root PATH]

One command for every page a builder owns (docs/rebuild_plan.md, stored-facts
rule 4: built pages are never the source). Each page has exactly one builder,
and this script only calls those builders, in an order in which no page is
built before a page or file it links to or reads:

 1. standings            scripts/render_standings.py      (the game records)
 2. statistics           scripts/render_season_stats.py   (the views, the statistics
                                                           index and the records index)
 3. team tracker         scripts/render_team_tracker.py
 4. award pages          scripts/render_award_pages.py    (the recorded award results;
                                                           nothing is drawn)
 5. contract pages       scripts/render_contract_pages.py (the contract and cap pages
                                                           from the permanent contract
                                                           records)
 6. player pages         scripts/render_player_pages.py   (reads the award results and
                                                           the contract records)
 7. player ages          scripts/render_player_ages.py
 8. club pages           scripts/render_club_pages.py     (team, roster, depth chart
                                                           and its change history)
 9. coach pages          scripts/render_coach_pages.py    (Coach page, Contract and
                                                           jobs, Staff page)
10. cap views            scripts/render_jaguars_cap_tracker.py
11. event results        scripts/resolve_event.py         (each resolved event's result
                                                           page built from its record;
                                                           an adopted Transaction or
                                                           head-coach change page is its
                                                           own builder's)
12. roster moves         runtime/transactions.py          (each applied move's
                                                           Transaction page and signing
                                                           records)
13. box scores           scripts/render_box_score.py      (each game page's marked
                                                           block, only where stale; a
                                                           Game Report's last, its
                                                           markers named once its
                                                           game has closed)
14. game-week pages      scripts/render_game_week.py      (each played week's index,
                                                           with its other business and
                                                           a recorded week's practice
                                                           table; the open week's
                                                           decision items, briefing,
                                                           Game Plan and index)
15. bye pages            scripts/render_bye_week.py       (while the bye is open: its
                                                           item, the Bye Week Review,
                                                           My Adjustments and its index)
16. week pages           scripts/render_week_pages.py     (Games and league-results
                                                           indexes, week pages, the
                                                           injury report, the medical
                                                           history's game entries)
17. in-season rails      scripts/render_inseason_rails.py (pages from Week 6 and any
                                                           missing week; earlier pages
                                                           are history)
18. trade pages          scripts/render_trade_pages.py    (the folder navigation and the
                                                           offer log's index of calls)
19. head-coach changes   scripts/render_coaching_changes.py (the league's index and change
                                                           pages; a new change page comes
                                                           only from coaching_check.py)
20. desk and career views scripts/render_career_views.py  (the desk with its season
                                                           summary, the calendar, the
                                                           Document 5 blocks)
21. preseason statistics scripts/render_preseason_stats.py
22. annual record        scripts/render_annual_record.py  (Record.md, last: it reads
                                                           the event lines the others
                                                           add)

Write mode writes only a page that differs from its build. It never plays a
game, draws an award, moves the clock, resolves a decision or creates an event:
an issued Game Week Briefing the situation has overtaken is re-issued (the old
one kept beside it, as render_game_week.py always does), and a Game Plan, a
Game Report, an incident record or a medical history entry already written is
never rewritten. A page a builder refuses to write (one that would break the
clean-page rule, or the career views while a game is paused) is reported and
the command exits 1. ``--check`` writes nothing: it runs each builder's own
check and lists every page that is missing, stale, hand-edited or unclean,
exiting 1 when there is any. Run it after every closed game and after any
change to a stored fact a page shows (docs/run_week.md, docs/update_workflow.md).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.seasons import CLEAN_SEASON, SeasonPaths, active_season  # noqa: E402

JAX = "Jacksonville Jaguars"
FIRST_SEASON = CLEAN_SEASON     # earlier seasons are closed history; their pages are never rebuilt


class Run:
    """The season being rebuilt and what each step wrote or found."""

    def __init__(self, root, year, check):
        self.root, self.year, self.check = Path(root).resolve(), year, check
        self.paths = SeasonPaths(year, self.root)
        self.written, self.problems = [], []

    def receipts(self):
        from scripts.render_season_stats import load_receipts
        return load_receipts(self.paths.receipts) if self.paths.receipts.is_dir() else []

    def put(self, path, text):
        """Write ``text`` at ``path`` when it differs (check mode: report it instead)."""
        path = Path(path)
        path = path if path.is_absolute() else self.root / path
        data = text.encode("utf-8")
        if path.is_file() and path.read_bytes() == data:
            return
        rel = path.relative_to(self.root).as_posix()
        if self.check:
            self.problems.append("Page missing or stale: %s" % rel)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.written.append(rel)

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()


# ------------------------------------------------------------------ the steps
def standings(run):
    from scripts import render_standings
    receipts = run.receipts()
    if receipts:
        run.put(run.paths.record("standings.md"), render_standings.render(run.year, receipts))


def statistics(run):
    from scripts import render_season_stats
    receipts = run.receipts()
    if receipts:
        for name, text in render_season_stats.render_views(run.year, JAX, receipts, run.root).items():
            run.put(render_season_stats.view_path(run.paths, name), text)


def team_tracker(run):
    from scripts import render_team_tracker
    if not run.receipts():
        return
    base = render_team_tracker.tracker_dir(run.root, run.year)
    for rel, text in render_team_tracker.render(run.root, run.year, JAX).items():
        run.put(base / rel, text)
    if run.check:
        run.problems += [e for e in render_team_tracker.check(run.root, run.year)
                         if e.startswith("Team tracker has an unexpected page")]


def award_pages(run):
    from runtime.events import preserve_event_comments
    from scripts.render_award_pages import render_pages
    folder, data = run.paths.awards, run.paths.awards_data
    results_path, method_path = data / "results.json", data / "methodology.json"
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.is_file() else {}
    if not results and not (folder / "week_01" / "README.md").is_file():
        return
    method = json.loads(method_path.read_text(encoding="utf-8")) if method_path.is_file() else None
    for relative, text in render_pages(run.year, results, method, root=run.root).items():
        path = folder / relative
        previous = path.read_text(encoding="utf-8") if path.is_file() else ""
        run.put(path, preserve_event_comments(text, previous))


def contract_pages(run):
    from scripts import render_contract_pages
    if run.check:
        run.problems += render_contract_pages.check(run.root, run.year)
        return
    run.written += render_contract_pages.write(run.root, run.year)


def player_pages(run):
    from runtime import player_pages as builder
    if run.check:
        run.problems += builder.check(run.root)
        return
    created, written, removed = builder.write(run.root)
    if created or written or removed:
        run.written.append("player pages: %d records created, %d pages written, %d files removed"
                           % (created, written, removed))


def player_ages(run):
    from scripts import render_player_ages
    for rel, text in render_player_ages.render_views(run.root).items():
        run.put(rel, text)


def club_pages(run):
    from scripts import render_club_pages
    if run.check:
        run.problems += render_club_pages.check(run.root)
        return
    for rel, text in render_club_pages.build(run.root).items():
        run.put(rel, text)


def coach_pages(run):
    from scripts import render_coach_pages
    if run.check:
        run.problems += render_coach_pages.check(run.root)
        return
    run.written += render_coach_pages.write(run.root)


def cap_views(run):
    from scripts import render_jaguars_cap_tracker as cap
    data = json.loads((run.root / cap.INPUT).read_text(encoding="utf-8"))
    for path, text in cap.render(data, run.root).items():
        run.put(path, text)


def event_results(run):
    """Each result page scripts/resolve_event.py built, from its event's record."""
    from scripts import resolve_event
    for path, text in resolve_event.built_pages(run.root, run.year):
        run.put(path, text)


def roster_moves(run):
    """Each applied roster move's Transaction page and signing records, from their records."""
    from runtime import transactions
    for path, text in transactions.built_pages(run.year, run.root).items():
        run.put(path, text)


def box_scores(run):
    from runtime.seasons import GAME_OUTPUT, GAME_REPORT
    from scripts.render_box_score import fill, is_report, named, stale_blocks
    pages = sorted(p for name in (GAME_OUTPUT, GAME_REPORT) for folder in (run.paths.regular_season,
                                                                           run.paths.postseason)
                   if folder.is_dir() for p in folder.glob("*/" + name))
    for page in pages:
        try:
            # A Game Report's template markers name its game once the game has closed.
            text = named(page, run.year, run.root)
        except ValueError:
            continue        # the game is still to be played: its box score waits for it
        if text != page.read_text(encoding="utf-8") or stale_blocks(page, run.paths.receipts, season=run.year):
            run.put(page, fill(text, run.paths.receipts, run.year, report=is_report(page)))


def game_week_pages(run):
    from runtime import decisions
    from scripts import render_game_week
    if run.check:
        # Every week's index and issue record, played weeks included, and the open week's briefing.
        run.problems += render_game_week.check(run.root)
        return
    from runtime import game_weeks
    closed = run.receipts() + game_weeks.postseason_receipts(run.paths)     # a playoff game's week too
    played = sorted({int(r["week"]) for r in closed if JAX in (r["home"], r["away"])})
    for week in played:
        pages = decisions.week_pages(run.year, week, run.root)
        if not (pages.briefing.is_file() or pages.plan.is_file()):
            continue        # a week before the Game Week pages keeps its index as written
        run.written += [run.rel(p) for p in render_game_week.write_index(run.root, week)]
    run.written += [run.rel(p) for p in render_game_week.write(run.root)]


def bye_pages(run):
    from scripts import render_bye_week
    if run.check:
        run.problems += render_bye_week.check(run.root)
        return
    run.written += [run.rel(p) for p in render_bye_week.write(run.root)]
    run.written += [run.rel(p) for p in render_bye_week.write_index(run.root)]


def week_pages(run):
    from scripts import render_week_pages
    if run.check:
        run.problems += render_week_pages.check(run.root, run.year)
        return
    written, problems = render_week_pages.write(run.root, run.year)
    run.problems += problems
    if written:
        run.written.append("week pages: %d written" % written)


def rails_pages(run):
    from runtime import rails
    from scripts import render_inseason_rails as builder
    if run.check:
        run.problems += builder.check(run.year, run.root)
        return
    data = rails.load(run.year, run.root)
    if data is None:
        return
    receipts = run.receipts()
    for week in sorted({int(r["week"]) for r in receipts}):
        if week < data.effective_from_week:
            continue
        path = builder.page_path(run.year, week, run.root)
        before = [r for r in receipts if int(r["week"]) < week]
        if path.is_file():
            current = path.read_bytes()
            if builder._history_page(run.rel(path), current, run.root):
                continue        # written before Week 6: kept as written, its record checked by the check
            meta = builder.meta_path(run.year, week, run.root)
            fresh = builder._without_events(builder.render(run.year, week, run.root, before))
            if builder._without_events(current.decode("utf-8")) == fresh and meta.is_file() and \
                    json.loads(meta.read_text(encoding="utf-8")) == builder.week_meta(run.year, week, run.root, before):
                continue
        builder.write(run.year, week, run.root, before)
        run.written.append(run.rel(path))


def career_views(run):
    from scripts import render_career_views
    if run.check:
        run.problems += render_career_views.check(run.root)
        return
    try:
        run.written += [run.rel(p) for p in render_career_views.write(run.root)]
    except (render_career_views.Paused, ValueError) as exc:
        run.problems.append("Desk and career views not written: %s" % exc)


def trade_pages(run):
    from scripts import render_trade_pages
    for path, text in render_trade_pages.pages(run.root, run.year).items():
        run.put(path, text)


def coaching_pages(run):
    from scripts import render_coaching_changes
    if run.check:
        run.problems += render_coaching_changes.check(run.root, run.year)
        return
    try:
        run.written += [run.rel(p) for p in render_coaching_changes.write(run.root, run.year)]
    except ValueError as exc:
        run.problems.append("Head-coach pages not written: %s" % exc)


def preseason_statistics(run):
    from scripts import render_preseason_stats
    stale = render_preseason_stats.stale_views(run.paths)
    if stale and run.check:
        run.problems += ["Preseason statistics stale: %s" % name for name in stale]
    elif stale:
        render_preseason_stats.write_views(run.paths)
        run.written += ["preseason statistics: %s" % name for name in stale]


def annual_record(run):
    from runtime.events import annual_record_path, load_events, render_record
    from scripts.render_annual_record import problems
    text = render_record(run.year, load_events(run.root), run.root)
    unclean = problems(run.root, run.year, text)
    if unclean:
        run.problems += ["Record.md not written: " + p for p in unclean]
        return
    run.put(annual_record_path(run.root, run.year), text)


STEPS = (("standings", standings), ("statistics", statistics), ("team tracker", team_tracker),
         ("award pages", award_pages), ("contract pages", contract_pages), ("player pages", player_pages),
         ("player ages", player_ages), ("club pages", club_pages), ("coach pages", coach_pages),
         ("cap views", cap_views), ("event results", event_results), ("roster moves", roster_moves),
         ("box scores", box_scores), ("game-week pages", game_week_pages), ("bye pages", bye_pages),
         ("week pages", week_pages), ("in-season rails", rails_pages), ("trade pages", trade_pages),
         ("head-coach changes", coaching_pages), ("desk and career views", career_views),
         ("preseason statistics", preseason_statistics), ("annual record", annual_record))


def rebuild(root=ROOT, year=None, check=False):
    """Run every step; returns (written, problems). ``check`` writes nothing."""
    root = Path(root).resolve()
    year = active_season(root) if year is None else year
    if year < FIRST_SEASON:
        raise ValueError("%d is a closed season; its pages are history and are not rebuilt" % year)
    run = Run(root, year, check)
    for name, step in STEPS:
        before = len(run.problems)
        try:
            step(run)
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            run.problems.append("cannot be built: %s" % exc)
        run.problems[before:] = ["%s: %s" % (name, p) for p in run.problems[before:]]
    return run.written, run.problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int)
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a page is stale")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    written, problems = rebuild(args.root, args.season, args.check)
    if args.check:
        print("\n".join(problems) if problems else "BUILT PAGES CURRENT")
        return 1 if problems else 0
    for line in written:
        print("wrote %s" % line)
    if not written:
        print("built pages: nothing to write")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
