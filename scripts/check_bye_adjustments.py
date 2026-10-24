#!/usr/bin/env python3
"""Check Stone's My Adjustments for the bye (rebuild step 5, C3; docs/bye_week.md, sections 3, 5 and 6).

  python scripts/check_bye_adjustments.py WEEK --season YEAR [--file PAGE] [--root PATH]

The page is his: the template's fixed headings and lines in ordinary football
language. The check holds it to the rules before anything is applied, in the
messages of docs/bye_week.md section 6: the exact headings and lines, each
answered ("No change" is a full answer); each direction's parts as keep,
correct, reduce, remove, test or defer, kept distinct; the players named on
the roster or coach records; the calls named in quotation marks in the active
playbooks (the playbook lock: no later book's term); the immediate role or
depth changes in the Game Plan's forms, each player on the active roster and
medically available; no medical clearance assumed and no install claimed; a
recommendation to the general manager written as a recommendation, never a
transaction; the players' days off and the bye's work of section 6 inside the
bye, with a legal four-day break and within the padded-practice budget the
earlier records leave; "Briefing answered" naming an issue of the Bye Week
Review (a later issue whose own sections differ needs it updated); and "I have
finished the bye-week decisions: Yes" before it is applied. The same decisions
in other words compile to the same record (runtime/bye_week.
compile_adjustments). With --file an uploaded .md or .txt page is checked and,
only when it passes, placed as the bye's My Adjustments; nothing else is
written. An applied page stays as written. Nothing here moves the clock or
creates an event.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import bye_week, decisions, event_inserts  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402


def briefing_problems(bye, compiled):
    """(problems, notes): "Briefing answered" against the review's issue record."""
    from scripts import render_bye_week as rbw
    entries = rbw.issues(bye)
    if not entries:
        return ["Briefing answered: no Bye Week Review has been issued"], []
    labels = [rbw.label_of(rbw.issue_of(e)) for e in entries]
    answered = compiled["briefing"]
    if answered not in labels:
        return ["Briefing answered: %r is not an issue of the Bye Week Review (%s)" % (answered, "; ".join(labels))], []
    n = labels.index(answered)
    if n == len(labels) - 1:
        return [], []
    old = (bye.pages.folder / entries[n]["file"]).read_text(encoding="utf-8")
    new = bye.pages.review.read_text(encoding="utf-8")
    if event_inserts.own_sections(old) == event_inserts.own_sections(new):
        return [], ["the Bye Week Review has been issued again with new notices at the top; your answers stand"]
    return ["Briefing answered: the Bye Week Review has been issued again since %s (now %s); read it and write its date"
            % (answered, labels[-1])], []


def check(root, season, week, text=None):
    """(problems, notes, compiled): the page (or ``text``) against the rules; compiled is None with any
    problem."""
    from scripts import render_bye_week as rbw
    root = Path(root).resolve()
    bye = rbw.Bye(root, week)
    if bye.week is None or bye_week.active_bye(bye.paths, root) != week:
        return ["The Week %d bye is not open; My Adjustments is answered while it is" % week], [], None
    pages = bye.pages
    applied = bye_week.applied_record(season, week, root)
    if text is None:
        if not pages.adjustments.is_file():
            return ["My Adjustments is not written for the Week %d bye" % week], [], None
        text = pages.adjustments.read_text(encoding="utf-8")
    if applied is not None:
        if bye_week.page_sha256(text) != applied["page_sha256"]:
            return ["My Adjustments was applied on %s and stays as written" % rbw.day(applied["date"])], [], None
        return [], ["My Adjustments was applied on %s" % rbw.day(applied["date"])], applied["choices"]
    rel = pages.adjustments.relative_to(root).as_posix()
    problems = [e.split(": ", 1)[-1] for e in page_errors(rel, text, root=root)]
    compiled, found = bye_week.compile_adjustments(text, season, week, root)
    problems += found
    notes = []
    if compiled is not None:
        more, notes = briefing_problems(bye, compiled)
        problems += more
        if not compiled["finished"]:
            problems.append("I have finished the bye-week decisions: No; the adjustments are applied once every "
                            "decision is explicit and you write Yes")
        if compiled.get("recommendation") is not None:
            notes.append("your recommendation to the general manager is recorded as your recommendation; he decides")
    return problems, notes, (compiled if not problems else None)


def place_upload(root, season, week, source):
    """An uploaded .md or .txt My Adjustments, placed only when it passes the check; (problems, notes)."""
    source = Path(source)
    if source.suffix.lower() not in (".md", ".txt"):
        return ["An uploaded My Adjustments is a .md or .txt file"], []
    text = source.read_text(encoding="utf-8")
    text = text if text.endswith("\n") else text + "\n"
    problems, notes, _ = check(root, season, week, text)
    if problems:
        return problems, notes
    page = decisions.bye_pages(season, week, root).adjustments
    page.write_text(text, encoding="utf-8")
    return [], notes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.file is not None:
        problems, notes = place_upload(args.root, args.season, args.week, args.file)
    else:
        problems, notes, _ = check(args.root, args.season, args.week)
    print("BYE ADJUSTMENTS: %s  Week %d, %d" % ("NOT READY" if problems else "READY", args.week, args.season))
    for problem in problems:
        print("- " + problem)
    for note in notes:
        print("  note: " + note)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
