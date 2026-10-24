#!/usr/bin/env python3
"""Issue the bye week's pages (rebuild step 5, C3; docs/bye_week.md; foundation/templates/bye_week/).

  python scripts/render_bye_week.py [--check] [--frame] [--root PATH]

While the bye is the open period (runtime/bye_week.active_bye: from the close
of Jacksonville's game before it until the bye's own close), this writes, in
the bye week's folder:

- the Bye Week Review (the template's layout), the staff's brief, built from
  stored facts only, as of its own issue: the club entering the bye (the
  record and the division and conference order from the closed games and the
  standings owner, the last game's result, the next game), health and pending
  examinations from the roster record's medical entries, the players' break
  (runtime/practices.bye_break_windows) and the padded practices left (pads
  only when one is known to be left of the eleven, runtime/practices.
  padded_status); the self-scouts, the staff's recommendations and the staff
  assessment as the staff stored them, with their authors and dates, in the
  bye week's data folder (``staff_bye_review.json``), "To come." where none is
  stored; and the notices at the top (runtime/event_inserts.render). Its
  issue record is the bye week's ``briefings.json``: each issue's date,
  revision, file, digest, time, reason and notices. It is issued again only
  under the one reissue rule (runtime/event_inserts.reissue_reason), the
  earlier copy kept beside it as he saw it;
- a blank My Adjustments with the template's fixed headings and lines (the
  fill-in guide left out), written once;
- the bye's index (its pages, My Responses when an event needs his answer,
  the practice and rest table once the week is recorded, the other business
  of the bye, the dates), replacing the placeholder.

It opens the bye's one ``bye_adjustments`` item first
(scripts/open_game_week.py), holding only the bye's own close. It runs no
league week and makes no Jacksonville input, score or box score. With
``--check`` it writes nothing and reports the bye's pages against their
records: the issue record and the reviews it holds, the index, a review the
situation has overtaken, an unclean page. ``--frame`` prints the Bye Week
Report's fixed parts (its header, the practice table and the applied
adjustments' rows) for the staff, who write the report after the work.
Opening or building a page never moves time or creates an event.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import bye_week, current_job, decisions, event_inserts, open_events, practices  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402

JAX = "Jacksonville Jaguars"
ISSUES = "briefings.json"
ISSUES_ABOUT = ("Every Bye Week Review issued for the bye, oldest first: the day it went out, its revision (the n-th "
                "issue of that day), its file in the week folder (the latest is the current review, each earlier one "
                "kept as he saw it), the sha256 of its bytes as issued, the time it went out (at, ET), why it was "
                "issued again under the one reissue rule (reason; null for the first issue) and the notices it carried "
                "at the top (inserts). Written only by scripts/render_bye_week.py; validation holds each review to its "
                "entry.")
STAFF_ABOUT = ("The coaching staff's authored parts of the Bye Week Review, each with its author and date: the "
               "offensive, defensive and special-teams self-scouts (rows and notes), the players for a football role "
               "review, the coaching decisions recommended to Stone and the staff assessment. A part not stored is "
               "shown \"To come.\"; nothing here is written by code.")
TO_COME = "To come."
# The staff's parts and their shapes (staff_bye_review.json ``texts``).
PARTS = {"offense": ("rows", ("pattern", "evidence", "known", "recommendation"), ("film_questions", "keep", "input")),
         "defense": ("rows", ("pattern", "evidence", "known", "recommendation"), ("held_up", "tests")),
         "special_teams": ("rows", ("unit", "performance", "question"), ("unchanged",)),
         "role_review": ("text", (), ()),
         "recommendations": ("rows", ("choice", "alternatives", "tradeoff", "deadline"), ()),
         "assessment": ("entries", (), ())}


def day(value, year=True):
    value = value if isinstance(value, date) else date.fromisoformat(value)
    return "%s %d, %d" % (value.strftime("%B"), value.day, value.year) if year else \
        "%s %d" % (value.strftime("%B"), value.day)


def long_day(value):
    return bye_week.long_day(value)


def link(page_rel, target_rel, label, anchor=""):
    rel = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, rel, "#" + anchor if anchor else "")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in row) + " |" for row in rows]
    return out


class Bye:
    """Everything the bye's pages read, loaded once: the open bye (or ``week``)."""

    def __init__(self, root=ROOT, week=None):
        from scripts import render_career_views as views
        self.root = Path(root).resolve()
        self.views = views
        self.cv = views.context(self.root)
        self.season, self.paths, self.master, self.job = self.cv.season, self.cv.paths, self.cv.master, self.cv.job
        self.week = week if week is not None else bye_week.active_bye(self.paths, self.root)
        if self.week is None:
            return
        self.period = {"bye": int(self.week)}
        self.pages = decisions.bye_pages(self.season, self.week, self.root)
        self.before, self.after = bye_week.around(self.season, self.week, self.root)
        self.first, self.last = bye_week.dates(self.season, self.week, self.root)
        self.closed = bye_week.bye_closed(self.paths, self.root, self.week)

    def rel(self, path):
        return Path(path).resolve().relative_to(self.root).as_posix()

    def place(self, club):
        return self.cv.places.get(club, club.rsplit(" ", 1)[0])

    def next_week(self, issued):
        """The next game's Week, built as of ``issued``: the closed games dated on or before it."""
        from scripts.render_game_week import Week
        wk = Week(self.root, int(self.after["week"]))
        games = {(int(g["week"]), g["away"], g["home"]): g for g in self.paths.regular_games()}
        wk.receipts = [r for r in wk.receipts if (games.get((int(r["week"]), r["away"], r["home"])) or {})
                       .get("date", "9999") <= issued.isoformat()]
        wk.as_of = issued
        return wk

    def game_short(self, game):
        """"Week 10 against Dallas, Sunday, November 9"."""
        return "Week %d %s %s, %s" % (int(game["week"]), "at" if game["away"] == JAX else "against",
                                      self.place(game["home"] if game["away"] == JAX else game["away"]),
                                      long_day(game["date"]))

    def game_words(self, game):
        return "%s, %s, %s" % (self.game_short(game), self.views.kickoff(game["kickoff_et"]), game.get("stadium"))

    def league_week(self):
        """(first, last) date of the league's other games in the bye week."""
        days = sorted(g["date"] for g in self.paths.regular_games() if int(g["week"]) == self.week)
        return (days[0], days[-1]) if days else (None, None)


# ------------------------------------------------------------------ the staff's stored parts
def staff_texts(bye):
    """{part: entry} of the staff's stored parts ({} before any); ValueError when one is malformed (an
    unknown part, no author or date, a date after today, or a part not in its shape)."""
    path = bye.pages.staff_review
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data.get("texts") if isinstance(data, dict) else None
    where = bye.rel(path)
    if not isinstance(texts, dict) or set(data) - {"about", "texts"}:
        raise ValueError("%s holds an optional about and the texts by part" % where)
    nonempty = lambda v: isinstance(v, str) and v.strip()
    for part, entry in texts.items():
        if part not in PARTS:
            raise ValueError("%s: %r is not a part of the review (%s)" % (where, part, ", ".join(PARTS)))
        shape, columns, notes = PARTS[part]
        if shape == "entries":
            if not isinstance(entry, list) or not entry or not all(
                    isinstance(e, dict) and set(e) == {"author", "date", "text"} and all(nonempty(v) for v in e.values())
                    for e in entry):
                raise ValueError("%s: assessment is a list of {author, date, text}" % where)
            dates = [e["date"] for e in entry]
        else:
            if not isinstance(entry, dict) or not nonempty(entry.get("author")) or not nonempty(entry.get("date")):
                raise ValueError("%s: %s needs its author and date" % (where, part))
            allowed = {"author", "date"} | ({"text"} if shape == "text" else {"rows"}) | set(notes)
            if set(entry) - allowed:
                raise ValueError("%s: %s holds only %s" % (where, part, ", ".join(sorted(allowed))))
            if shape == "text" and not nonempty(entry.get("text")):
                raise ValueError("%s: %s needs its text" % (where, part))
            if shape == "rows" and (not isinstance(entry.get("rows"), list) or not entry["rows"] or not all(
                    isinstance(r, dict) and set(r) == set(columns) and all(nonempty(v) for v in r.values())
                    for r in entry["rows"])):
                raise ValueError("%s: %s's rows each hold %s" % (where, part, ", ".join(columns)))
            if any(not nonempty(entry[n]) for n in notes if n in entry):
                raise ValueError("%s: %s has an empty note" % (where, part))
            dates = [entry["date"]]
        for when in dates:
            if date.fromisoformat(when) > bye.master:
                raise ValueError("%s: %s is dated %s, after today (%s)" % (where, part, when, bye.master))
    return texts


def text_strings(texts):
    out = []
    for part, entry in texts.items():
        if isinstance(entry, list):
            out += [e["text"] for e in entry]
            continue
        out += [entry[k] for k in entry if k not in ("author", "date", "rows")]
        for row in entry.get("rows") or ():
            out += list(row.values())
    return out


def by(entry):
    return " (%s, %s)" % (entry["author"], day(entry["date"], False))


def staff_table(texts, part, head):
    entry = texts.get(part)
    if entry is None:
        return [TO_COME, ""]
    columns = PARTS[part][1]
    return table(head, [[r[c] for c in columns] for r in entry["rows"]]) + [
        "", "Prepared by %s, %s." % (entry["author"], day(entry["date"], False)), ""]


def note(texts, part, key, label):
    entry = texts.get(part)
    if entry is None or key not in entry:
        return "**%s:** %s" % (label, TO_COME)
    return "**%s:** %s%s" % (label, entry[key].rstrip(), by(entry))


# ------------------------------------------------------------------ the review's facts
def coordinators(bye, on):
    holder = bye.job.get("holder")
    out = []
    for phase, label in (("offense", "Offense"), ("defense", "Defense"), ("special_teams", "Special Teams")):
        interval = current_job.interval_on(bye.job, phase, on)
        if not interval:
            continue
        who = interval.get("prepares") if interval.get("caller") == holder else interval.get("caller")
        if who and who != holder:
            out.append("%s, %s" % (current_job.party_name(bye.job, who), label))
    return out


def caller_words(bye, phase, on):
    interval = current_job.interval_on(bye.job, phase, on)
    if not interval:
        return "Not recorded"
    caller = current_job.party_name(bye.job, interval["caller"])
    prepares = interval.get("prepares")
    if prepares and prepares != interval["caller"]:
        return "%s calls it; %s prepares it" % (caller, current_job.party_name(bye.job, prepares))
    return "%s calls it" % caller


def result_words(bye, receipt):
    """"Jacksonville 24, Dallas 17" (the winner first)."""
    scores = sorted(receipt["final_score"].items(), key=lambda kv: (-kv[1], kv[0] != JAX))
    return ", ".join("%s %d" % (bye.place(club), points) for club, points in scores)


def last_receipt(bye):
    from runtime.week_inputs import receipt_name
    path = bye.paths.receipts / receipt_name(bye.before)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def break_words(bye):
    windows = practices.bye_break_windows(bye.season, bye.week, bye.root)
    if not windows:
        return "No four-day window fits this bye week; the staff raises it with you"
    words = " or ".join("%s to %s" % (long_day(a), long_day(b)) for a, b in windows)
    rule = ("including Saturday and Sunday" if windows[0][1].weekday() == 6
            else "Wednesday to Saturday, before the Thursday game")
    return "Four consecutive days, %s: %s%s; earlier days off may lengthen it, and an injured player's treatment " \
           "is as the medical staff directs" % (rule, words, " is the only window this week allows"
                                                if len(windows) == 1 else "")


def padded_words(bye):
    status = practices.padded_status(bye.season, bye.week - 1, bye.root,
                                     {w: r for w, r in practices.records(bye.season, bye.root).items() if w < bye.week})
    period = status["first" if bye.week <= practices.FIRST_WEEKS else "last"]
    if not period["known"]:
        return ("Padded practices: the count is not known (%s not recorded), so no padded practice can be held in "
                "the bye; helmets-only work, meetings and film within the medical instructions"
                % practices.weeks_words(period["unknown_weeks"]))
    if period["left"] == 0:
        return ("Padded practices: all %d of the first eleven weeks are used; no padded practice in the bye. "
                "Helmets-only work, meetings and film within the medical instructions" % period["limit"])
    return ("Padded practices: %d of the %d for the first eleven weeks used, %d left; any field work within the "
            "medical instructions" % (period["used"], period["limit"], period["left"]))


def club_rows(bye, wk, page_rel):
    from scripts.render_game_week import medical_rows, stakes_text
    record = wk.record(JAX)
    stakes = re.sub(r"^A division game\. ", "", stakes_text(wk))
    receipt = last_receipt(bye)
    report = bye.paths.game_report(int(bye.before["week"]))
    last = "%s: %s" % (bye.game_short(bye.before), result_words(bye, receipt) if receipt else "not recorded")
    if report.is_file():
        last += " (%s)" % link(page_rel, bye.rel(report), "Game Report")
    medical = medical_rows(wk, page_rel, {})
    health = ("%d player%s under a medical restriction or waiting on an examination (Players and medical instructions "
              "below)" % (len(medical), "" if len(medical) == 1 else "s")) if medical else \
        "No player on the active roster is under a medical restriction or waiting on an examination"
    history = bye.paths.record("medical/medical_history.md")
    if history.is_file():
        health += "; %s" % link(page_rel, bye.rel(history), "medical history")
    return [["Current record, division position", "%s. %s" % (record, stakes)],
            ["Last game", last],
            ["Next game", "%s; its Game Week Briefing opens when the bye closes" % bye.game_words(bye.after)],
            ["Health / availability", health],
            ["Mandatory player time off", break_words(bye)],
            ["Lawful field work remaining", padded_words(bye)]]


def header(bye, issued, previous, revision):
    status = ("Superseding issue: it replaces the review of %s, which is kept as it went out" % label_of(previous)
              if previous else "Initial issue")
    staff = coordinators(bye, issued)
    lines = ["**To:** %s, Head Coach" % current_job.party_name(bye.job, bye.job.get("holder")),
             "**From:** %s, with the position coaches and the medical staff" % ("; ".join(staff) or "The coaching staff"),
             "**Issued:** %s" % label_of((issued, revision)),
             "**Evidence through:** %s, the last closed game" % bye.game_short(bye.before),
             "**Bye:** %s to %s; no Jacksonville game" % (long_day(bye.first), long_day(bye.last)),
             "**Next game:** %s" % bye.game_words(bye.after),
             "**Status:** %s." % status]
    return [l + "  " for l in lines[:-1]] + lines[-1:] + [""]


def label_of(issue):
    when, revision = issue
    return day(when) + (", revision %d" % revision if revision and revision > 1 else "")


def review(bye, issued=None, previous=None, revision=1, route=None):
    """The Bye Week Review as of ``issued`` (by default today), the day's ``revision``-th issue."""
    issued = issued or bye.master
    page_rel = bye.rel(bye.pages.review)
    route = route if route is not None else issue_route(bye, issued, revision)
    texts = staff_texts(bye)
    wk = bye.next_week(issued)
    out = ["# Week %d Bye Week Review" % bye.week, ""]
    out += header(bye, issued, previous, revision)
    out += event_inserts.render(route, page_rel, issued)
    out += _sections(bye, wk, texts, page_rel, issued)
    return "\n".join(out).rstrip("\n") + "\n"


def _sections(bye, wk, texts, page_rel, issued):
    from scripts.render_game_week import medical_rows
    adjustments = link(page_rel, bye.rel(bye.pages.adjustments), "My Adjustments")
    out = ["## The club entering the bye", ""]
    out += table(["Item", "Verified position on issue date"], club_rows(bye, wk, page_rel)) + [""]
    out += ["## Offensive self-scout", ""]
    out += staff_table(texts, "offense", ["Observed pattern or incident", "Supporting games, calls or cut-ups",
                                          "What we know / what remains unknown", "Football recommendation"])
    out += [note(texts, "offense", "film_questions", "Film questions worth answering") + "  ",
            note(texts, "offense", "keep", "What we should not discard") + "  ",
            note(texts, "offense", "input", "Quarterback and position-coach input recorded"), ""]
    out += ["## Defensive self-scout", ""]
    out += staff_table(texts, "defense", ["Observed pattern or incident", "Supporting games, situations or cut-ups",
                                          "Known cause or unresolved football question", "Football recommendation"])
    out += [note(texts, "defense", "held_up", "Calls and personnel that held up") + "  ",
            note(texts, "defense", "tests", "Situations worth testing after the break") + "  ",
            "**Who makes the defensive call:** %s." % caller_words(bye, "defense", issued), ""]
    out += ["## Special-teams self-scout", ""]
    out += staff_table(texts, "special_teams", ["Unit / situation", "Verified performance or event",
                                                "Coaching question / proposed work"])
    out += ["**Caller:** %s." % caller_words(bye, "special_teams", issued) + "  ",
            note(texts, "special_teams", "unchanged", "Unchanged units"), ""]
    out += ["## Players and medical instructions", ""]
    rows = medical_rows(wk, page_rel, {})
    who = "The medical staff for diagnosis and clearance; %s for an eligible assignment" % current_job.party_name(
        bye.job, bye.job.get("holder"))
    if rows:
        out += table(["Player", "Communicated status / limitation as of issue date", "Next examination / decision date",
                      "Football implication", "Who decides"], [r + [who] for r in rows])
    else:
        out += ["No player on the active roster is under a medical restriction or waiting on an examination. A player "
                "not listed is not thereby medically cleared."]
    role = texts.get("role_review")
    out += ["", "**Players for a football role review, not a medical decision:** %s" % (
        role["text"].rstrip() + by(role) if role else TO_COME), ""]
    out += ["## Calendar and available coaching work", ""]
    out += table(["Window", "Permitted activity", "Relevant limit or verified appointment"], calendar_rows(bye)) + [""]
    out += ["## Coaching decisions recommended to Stone", ""]
    out += staff_table(texts, "recommendations", ["Football choice", "Staff's supported alternative(s)",
                                                  "Consequence / tradeoff", "Your deadline"])
    instruction = current_job.practice_instruction(bye.job, bye.season)
    out += ["**Already governed by standing instructions:** %s" % (
        "Your standing practice instruction sets the game weeks; the bye's work and the players' break are yours to "
        "set on %s." % adjustments if instruction else "None sets the bye's work; you set it on %s." % adjustments),
        "",
        "**Who has authority:** %s sets coaching priorities, permitted practice and eligible player roles. The medical "
        "staff controls medical clearance. %s controls transactions. The current calling arrangement stands until it "
        "is changed." % (current_job.party_name(bye.job, bye.job.get("holder")),
                         current_job.party_name(bye.job, "caldwell")), "",
        "**Precisely what is due from you:** Complete %s for the decisions that need your answer before they are put "
        "into the week's work. \"Same as current\" and \"No change\" are legitimate answers. Silence is not an answer."
        % adjustments, "",
        "**The brief becomes stale if:** a new matter needs your answer, a recorded finding changes a choice still "
        "open (a medical determination, a transaction, a corrected finding), or an answer falls due before the next "
        "scheduled brief; a new dated issue is then written and this one kept as you saw it.", ""]
    out += ["## Staff assessment", ""]
    entries = texts.get("assessment")
    if entries:
        for e in entries:
            out += ["**%s, %s:** %s" % (e["author"], day(e["date"], False), e["text"].rstrip()), ""]
    else:
        out += [TO_COME, ""]
    out += [links_line(bye, page_rel), ""]
    return out


def calendar_rows(bye):
    windows = practices.bye_break_windows(bye.season, bye.week, bye.root)
    start = min(a for a, _ in windows) if windows else bye.last + timedelta(days=1)
    rows = []
    if start > bye.first:
        rows.append(["%s to %s" % (long_day(bye.first), long_day(start - timedelta(days=1))),
                     "Player meetings, film or permitted field work, as you set them on My Adjustments; staff work",
                     padded_words(bye)])
    for a, b in windows:
        rows.append(["%s to %s" % (long_day(a), long_day(b)),
                     "The players' four consecutive days off; staff film and analysis may continue",
                     "No required player meeting, practice or remote assignment; an injured player's treatment as the "
                     "medical staff deems reasonably necessary"])
    nxt = bye.last + timedelta(days=1)
    rows.append([long_day(nxt), "Week %d preparation begins" % int(bye.after["week"]),
                 "The Week %d Game Week Briefing and Game Plan govern the opponent's calls and the game-day inactives"
                 % int(bye.after["week"])])
    return rows


def links_line(bye, page_rel):
    out = [link(page_rel, bye.rel(bye.pages.adjustments), "My Adjustments"),
           link(page_rel, bye.rel(bye.pages.readme), "Week %d" % bye.week),
           link(page_rel, bye.rel(bye.paths.roster_page), "Roster"),
           link(page_rel, bye.rel(bye.paths.record("depth_chart.md")), "Depth chart"),
           link(page_rel, bye.rel(bye.paths.record("medical/medical_history.md")), "Medical history")]
    report = bye.paths.game_report(int(bye.before["week"]))
    if report.is_file():
        out.append(link(page_rel, bye.rel(report), "Week %d report" % int(bye.before["week"])))
    return " · ".join(out)


# ------------------------------------------------------------------ the issue record
def issues(bye):
    path = bye.pages.briefings
    return [dict(e) for e in json.loads(path.read_text(encoding="utf-8")).get("issued") or ()] if path.is_file() else []


def save_issues(bye, entries):
    path = bye.pages.briefings
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"about": ISSUES_ABOUT, "issued": entries}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def issue_of(entry):
    return date.fromisoformat(entry["date"]), int(entry["revision"])


def issue_route(bye, issued, revision):
    entries = issues(bye)
    for n, entry in enumerate(entries, 1):
        if entry.get("date") == issued.isoformat() and int(entry.get("revision", 0)) == revision:
            return open_events.route(bye.season, open_events.issued_at(entry), bye.period, bye.root, issue=n)
    at = open_events.master_at(bye.root) if issued == bye.master else open_events.et(issued)
    return open_events.route(bye.season, at, bye.period, bye.root, issue=len(entries) + 1)


def previous_issue(bye, new=False):
    entries = issues(bye)
    if new:
        return issue_of(entries[-1]) if entries else None
    return issue_of(entries[-2]) if len(entries) > 1 else None


def items_open(bye):
    """Whether the bye's own decisions are open: its adjustments item, or an item of an event raised in
    the bye."""
    events = {r["id"] for r in open_events.load(bye.season, bye.root) if r.get("period") == bye.period}
    item = bye_week.bye_item(bye.cv.queue, bye.season, bye.week)
    return (item is not None and item.get("status") == "OPEN") or any(
        i.get("status") == "OPEN" and i.get("event") in events for i in bye.cv.queue["items"])


def reissue_reason(bye, old=None):
    """Why the review must be issued again now (event_inserts.reissue_reason, the one rule), or None.
    Its own sections are its rebuild for its own issue, compared without the notices."""
    entries = issues(bye)
    if not entries or not bye.pages.review.is_file():
        return None
    when, revision = issue_of(entries[-1])
    old = bye.pages.review.read_text(encoding="utf-8") if old is None else old
    changed = event_inserts.strip_inserts(old) != event_inserts.strip_inserts(
        review(bye, when, previous_issue(bye), revision))
    now = open_events.route(bye.season, open_events.master_at(bye.root), bye.period, bye.root, issue=len(entries) + 1)
    state = event_inserts.PeriodState(bye.season, bye.period, bye.root, own_changed=changed, items_open=items_open(bye),
                                      next_issue_at=open_events.et(bye.last + timedelta(days=1)))
    return event_inserts.reissue_reason(state, entries[-1], now)


def issue_errors(bye):
    """The bye's reviews against the issue record: each recorded review present with the bytes it went
    out with, the latest the current review, dates in order and not after today, and no review in the
    folder that no issue produced."""
    label = "Week %d bye" % bye.week
    entries = issues(bye)
    current = bye.pages.review
    if not entries:
        return ["%s: the Bye Week Review has no issue record" % label] if current.is_file() else []
    errors, previous, recorded = [], None, set()
    for n, entry in enumerate(entries):
        try:
            when, revision = issue_of(entry)
            name, digest = entry["file"], entry["sha256"]
        except (KeyError, TypeError, ValueError):
            errors.append("%s: issue record entry %d is malformed" % (label, n + 1))
            continue
        recorded.add(name)
        if previous is not None and when < previous:
            errors.append("%s: the review of %s is recorded after a later one" % (label, day(when)))
        if when > bye.master:
            errors.append("%s: a review is recorded as issued %s, after today" % (label, day(when)))
        previous = when
        if n == len(entries) - 1 and name != current.name:
            errors.append("%s: the latest issue (%s) is not the current Bye Week Review" % (label, name))
        path = bye.pages.folder / name
        if not path.is_file():
            errors.append("%s: the review issued %s is missing" % (label, day(when)))
        elif sha256(path) != digest:
            errors.append("%s: %s differs from the review issued %s; a review is never edited by hand"
                          % (label, bye.rel(path), day(when)))
    for path in sorted(bye.pages.folder.glob(current.stem + "_*.md")):
        if path.name not in recorded:
            errors.append("%s: %s is not a review the issue record holds" % (label, bye.rel(path)))
    return errors


# ------------------------------------------------------------------ My Adjustments and the index
def adjustments_page(bye):
    title = "Week %d My Adjustments" % bye.week
    values = {"head_coach": current_job.party_name(bye.job, bye.job.get("holder")),
              "bye": "%d, Week %d, %s to %s" % (bye.season, bye.week, long_day(bye.first), long_day(bye.last))}
    return bye_week.blank_page(title, values, bye.job, bye.master)


def other_business(bye, page_rel):
    """The bye's other business (results resolved in it and events still open), the same function as
    a game week's index (runtime/event_inserts.other_business)."""
    return event_inserts.other_business(bye.season, bye.period, page_rel, bye.root, open_now=not bye.closed,
                                        job=bye.job)


def index_page(bye):
    page_rel = bye.rel(bye.pages.readme)
    entries = issues(bye)
    rows = []
    if bye.pages.review.is_file():
        rows.append([link(page_rel, bye.rel(bye.pages.review), "Bye Week Review"),
                     "The coaching staff's self-scout through the last game, health, the players' break, the field work "
                     "left and the decisions for you", "Issued %s" % label_of(issue_of(entries[-1])) if entries
                     else "Issued"])
    else:
        rows.append(["Bye Week Review", "The coaching staff's self-scout", "To come"])
    applied = bye_week.applied_record(bye.season, bye.week, bye.root)
    rows.append([link(page_rel, bye.rel(bye.pages.adjustments), "My Adjustments") if bye.pages.adjustments.is_file()
                 else "My Adjustments",
                 "Your decisions for the bye: what to keep, correct, test, remove or defer, the eligible roles, the "
                 "bye's work and the players' days off",
                 "Applied %s" % day(applied["date"]) if applied else
                 "Waiting on you" if bye.pages.adjustments.is_file() else "To come"])
    if bye.pages.responses.is_file():
        rows.append([link(page_rel, bye.rel(bye.pages.responses), "My Responses"),
                     "Your answers to the notices at the top of the review", "Open"])
    report = bye.pages.report
    rows.append([link(page_rel, bye.rel(report), "Bye Week Report") if report.is_file() else "Bye Week Report",
                 "What the staff did in the bye: the work held, the players' time off and what changed",
                 ("Closed" if bye.closed else "Written") if report.is_file() else "After the work"])
    first, last = bye.league_week()
    out = ["# Week %d: Bye" % bye.week, "",
           "%s to %s, %d. No Jacksonville game; the club's record stands through the bye.%s" % (
               long_day(bye.first), long_day(bye.last), bye.last.year,
               " The league's other Week %d games run %s to %s." % (bye.week, long_day(first), long_day(last))
               if first else ""), ""]
    out += table(["Page", "What it holds", "Status"], rows) + [""]
    earlier = [(bye.pages.folder / e["file"], issue_of(e)) for e in entries[:-1]]
    if earlier:
        out += ["Earlier reviews, as they went out: " + "; ".join(
            link(page_rel, bye.rel(p), label_of(i)) for p, i in earlier) + ".", ""]
    practice = practices.render_table(practices.load(bye.season, bye.week, bye.root))
    if practice:
        out += ["## Practice and rest", "", practice.rstrip("\n"), ""]
    out += other_business(bye, page_rel)
    out += [" · ".join([link(page_rel, bye.rel(bye.pages.folder.parent / "README.md"), "All weeks"),
                        link(page_rel, bye.rel(bye.paths.record("statbook.md")), "Regular-season statistics"),
                        link(page_rel, bye.rel(bye.paths.awards / ("week_%02d" % bye.week) / "README.md"),
                             "Week %d awards" % bye.week)]), ""]
    return "\n".join(out)


# ------------------------------------------------------------------ write and check
def write(root=ROOT):
    """Issue the open bye's pages; returns the paths written ([] when no bye is open)."""
    bye = Bye(root)
    if bye.week is None:
        return []
    written = []
    from scripts import open_game_week
    had_page = bye.pages.adjustments.is_file()
    if open_game_week.open_items(root):
        written.append(Path(root).resolve() / open_game_week.QUEUE)
        if not had_page and bye.pages.adjustments.is_file():
            written.append(bye.pages.adjustments)
        bye = Bye(root)
    bye.pages.folder.mkdir(parents=True, exist_ok=True)
    if not bye.pages.adjustments.is_file():
        bye.pages.adjustments.write_text(adjustments_page(bye), encoding="utf-8")
        written.append(bye.pages.adjustments)
    entries = issues(bye)
    problems = issue_errors(bye)
    if problems:
        raise ValueError("; ".join(problems))
    reason = reissue_reason(bye) if entries else None
    if not entries or reason is not None:
        if entries:
            when, revision = issue_of(entries[-1])
            label = day(when, False) + (" %d" % revision if revision > 1 else "")
            target, n = bye.pages.earlier_review(label), 2
            while target.exists():
                target, n = bye.pages.earlier_review("%s %d" % (label, n)), n + 1
            target.write_bytes(bye.pages.review.read_bytes())
            entries[-1]["file"] = target.name
            written.append(target)
        revision = 1 + sum(1 for e in entries if e["date"] == bye.master.isoformat())
        at = open_events.master_at(bye.root)
        route = open_events.route(bye.season, at, bye.period, bye.root, issue=len(entries) + 1)
        from runtime import responses
        if responses.ensure_blocks(route, bye.root):
            written += [bye.pages.responses, bye.pages.responses_record]
        bye.pages.review.write_text(review(bye, previous=previous_issue(bye, new=True), revision=revision,
                                           route=route), encoding="utf-8")
        entries.append({"date": bye.master.isoformat(), "revision": revision, "file": bye.pages.review.name,
                        "sha256": sha256(bye.pages.review), "at": open_events.iso(at), "reason": reason,
                        "inserts": event_inserts.issue_inserts(route, bye.rel(bye.pages.review))})
        written += [bye.pages.review, save_issues(bye, entries)]
    written += write_index(root, bye)
    return written


def write_index(root=ROOT, bye=None):
    """Rebuild the bye's index (after its adjustments are applied, its week recorded or it closes)."""
    bye = bye or Bye(root, _pages_week(root))
    if bye.week is None or not (bye.pages.review.is_file() or bye.pages.adjustments.is_file()):
        return []
    index = index_page(bye)
    if not bye.pages.readme.is_file() or bye.pages.readme.read_text(encoding="utf-8") != index:
        bye.pages.readme.write_text(index, encoding="utf-8")
        return [bye.pages.readme]
    return []


def _pages_week(root):
    """The open bye, else the season's bye whose pages are written, else None."""
    root = Path(root).resolve()
    from runtime.seasons import SeasonPaths, active_season
    season = active_season(root)
    paths = SeasonPaths(season, root)
    week = bye_week.active_bye(paths, root)
    if week is not None:
        return week
    return next((w for w in bye_week.byes(season, root) if decisions.bye_pages(season, w, root).briefings.is_file()),
                None)


def read_errors(bye):
    try:
        texts = staff_texts(bye)
    except (OSError, ValueError) as exc:
        return ["Staff texts: %s" % exc]
    errors = []
    for value in text_strings(texts):
        errors += ["Staff texts: %s" % e for e in page_errors(bye.rel(bye.pages.staff_review), value, root=bye.root)]
    return errors


def check(root=ROOT):
    """The bye's pages against their records, writing nothing; [] when they hold or no bye has pages."""
    try:
        week = _pages_week(root)
        if week is None:
            return []
        bye = Bye(root, week)
        label = "Week %d bye" % week
        errors = issue_errors(bye) + read_errors(bye)
        if bye.pages.review.is_file() or bye.pages.adjustments.is_file():
            index = index_page(bye)
            if not bye.pages.readme.is_file() or bye.pages.readme.read_text(encoding="utf-8") != index:
                errors.append("%s: the index is missing or stale (%s)" % (label, bye.rel(bye.pages.readme)))
        errors += bye_week.validation_errors(bye.root)
        if bye.closed:
            return errors
        if bye_week.active_bye(bye.paths, bye.root) != week:
            return errors
        if not bye.pages.review.is_file():
            return errors + ["%s: no Bye Week Review has been issued" % label]
        if not bye.pages.adjustments.is_file():
            errors.append("%s: My Adjustments is missing beside the review" % label)
        if not errors and reissue_reason(bye) is not None:
            errors.append("%s: the situation has changed since the review of %s; a new review is due"
                          % (label, label_of(issue_of(issues(bye)[-1]))))
        when, revision = issue_of(issues(bye)[-1])
        errors += page_errors(bye.rel(bye.pages.review), review(bye, when, previous_issue(bye), revision), root=bye.root)
        return errors
    except ValueError as exc:
        return ["bye pages: cannot be built: %s" % exc]


# ------------------------------------------------------------------ the report's fixed parts
def report_frame(bye):
    """The Bye Week Report's fixed parts for the staff to write around: its header, the practice and rest
    table of section 2 (once recorded) and section 3's rows of the applied adjustments; every staff
    part is left "To come." and must be written before the report is checked."""
    applied = bye_week.applied_record(bye.season, bye.week, bye.root)
    record = bye_week.record_words(bye.season, bye.week, bye.root)
    out = ["# Week %d Bye Week Report" % bye.week, "",
           "**Jacksonville Jaguars | %s to %s | No Jacksonville game**  " % (long_day(bye.first), long_day(bye.last)),
           "**Head coach:** %s  " % current_job.party_name(bye.job, bye.job.get("holder")),
           "%s %s through Week %d; no game this week  " % (bye_week.RECORD_LINE, record, int(bye.before["week"])),
           "**Next:** %s  " % bye.game_words(bye.after),
           "**Coach's approved instructions:** %s" % ("My Adjustments, applied %s" % day(applied["date"]) if applied
                                                      else TO_COME), ""]
    for n, heading in enumerate(bye_week.REPORT_HEADINGS, 1):
        out += ["## %s" % heading, ""]
        if n == 2:
            table_text = practices.render_table(practices.load(bye.season, bye.week, bye.root))
            out += [table_text.rstrip("\n") if table_text else TO_COME, ""]
        elif n == 3 and applied:
            out += [bye_week.ADJUSTMENT_HEAD, "|---|---|---|---|"]
            out += ["| %s | %s | %s | %s |" % (a, b, TO_COME, TO_COME) for a, b in bye_week.adjustment_rows(applied, bye.root)]
            out += [""]
        else:
            out += [TO_COME, ""]
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--frame", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        print("\n".join(errors) if errors else "BYE WEEK PAGES CURRENT")
        return 1 if errors else 0
    if args.frame:
        week = _pages_week(args.root)
        if week is None:
            print("bye pages: no bye is open")
            return 1
        print(report_frame(Bye(args.root, week)))
        return 0
    try:
        written = write(args.root)
    except ValueError as exc:
        print("bye pages: cannot be built: %s" % exc)
        return 1
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(Path(args.root).resolve()).as_posix())
    if not written:
        print("bye pages: nothing to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
