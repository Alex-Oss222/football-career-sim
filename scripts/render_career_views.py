#!/usr/bin/env python3
"""Render the career views from the current-job record and the decision queue.

  python scripts/render_career_views.py [--check]

state/current_job.json and state/decision_queue.json own the facts; these
views only show them (docs/career_layer.md). Document 5 holds two blocks
between NAME:begin and NAME:end comment markers, current-job and
decision-queue, and docs/career_layer.md the decision-classes block. The desk
is the whole of the active season's README, a clean page built with no
markers: today and the last result, the job, what is waiting on the head
coach, the next event, then everything else. Document 5's manifest also names
both files' git blobs, which binds them into its digest and so into the
private snapshot. The views read only those two files, Stone's coach record
(the contract), Document 5's master-date cell and section 9, the active
season's fixtures, the closed events, docs/repository_map.json, whether the
next game's week README and call sheet and the last game's output exist, and
the employer club's own closed-game receipts for the desk's last result and
record; never another club's receipt, the standings, awards or the wall clock.
The staff register's phase-control table is no longer written: the Staff page
(scripts/render_coach_pages.py) shows who calls what. Writing is refused while
a Jacksonville game is paused; --check is read-only and exits 1 on a stale,
malformed, unclean or unrenderable view.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import current_job, decision_queue  # noqa: E402
from runtime.events import load_events, repository_map, resolve_path  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.season_layout import NUMBERED_FOLDERS  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts.render_coach_pages import (COACH_PAGE, CONTRACT_PAGE, club_record, football_anchor,  # noqa: E402
                                        heading, last_game)
from scripts import render_season_hub  # noqa: E402
from scripts.validate_repository import anchors, git_blob, without_code  # noqa: E402

STATE = Path("state/05_Current_Season_State.md")
DOC = Path("docs/career_layer.md")
# (Document 5 manifest label, file, link text); the rows follow Document 4's.
MANIFEST_ROWS = (("Current job record", current_job.JOB.as_posix(), "Job, authority and delegation"),
                 ("Decision queue", decision_queue.QUEUE.as_posix(), "Open and resolved decisions"))
BANNED = re.compile(r"\b(branch|simulation|receipt|kernel|engine|ledger|snapshot|checkpoint)s?\b", re.I)
VOICED = frozenset({"desk", "calendar", "medical", "statbook"})   # reader prose; the Document 5 blocks are a state file
LINK = re.compile(r"\]\(@([^)#]*)(?:#([^)]*))?\)")   # a view's repository-relative link before localizing
PHASE_LABEL = {"offense": "Offense", "defense": "Defense", "special_teams": "Special teams"}
DECISION_LABEL = {"fourth_down": "fourth downs", "two_point": "two-point tries", "kickoff": "onside kicks",
                  "timeouts_and_clock": "timeouts and clock management", "replay_challenge": "replay challenges"}
SUBJECT_LABEL = {"play_calling": "Calling arrangement", "inactives": "Inactives", "two_point": "Two-point tries",
                 "kickoff": "Kickoffs", "fourth_down": "Fourth downs"}
STATUS_LABEL = {"IN_FORCE": "in force", "RECORDED": "recorded, not in force", "SUPERSEDED": "superseded",
                "WITHDRAWN": "withdrawn"}
REPORTING_LABEL = (("direct_supervisor", "direct supervisor"), ("evaluator", "evaluator"),
                   ("cadence", "review cadence"), ("escalation", "escalation"))
HISTORY_LABEL = {"accepted": "hire", "retained": "retention"}
# The holder's part in a row, in Document 5's final-authority sentence.
AUTHORITY_NOTE = {"recommends": " on {who}'s recommendation", "consulted": " after consulting {who}",
                  "unset": " ({who}'s role not recorded)", "responds": " ({who} responds)",
                  "informs": " ({who} supplies information)", "decides_part": " ({who} decides {scope})",
                  "none": ""}
# The desk is football only: an open decision, a dated event or a standing instruction shows
# only its clauses free of these process words (rebuild plan, "The desk").
DESK_WORDS = re.compile(r"\b(frozen|freez\w*|inputs?|holds?|held|gates?|call sheets?|draws?|queue|blocks?|"
                        r"releases? the hold)\b", re.I)
# Logical season records (SeasonPaths.record), so the next season's desk works.
DESK_LINKS = (("Team", "team/README.md"), ("Roster", "roster.md"), ("Depth chart", "depth_chart.md"),
              ("Injury report", "medical/current_injury_report.md"))
# The label of a desk link to one of these season records (any other page is labelled by its
# week or its own heading, never "Record").
PAGE_LABELS = DESK_LINKS + (("Film queue", "offseason/film/player_queue.md"),
                            ("Roster decisions", "offseason/training_camp/roster_decisions.md"))
# The calling arrangement links to the Staff page's section on it.
CALLING_SECTION = "who-calls-what"
FOLDER_NOTES = {
    "Team_Operations": "Year-round roster, staff, medical, development, film, trades, free agency and finances",
    "Early_Offseason": "Staffing, scouting, preparation and offseason decisions",
    "Offseason_Training": "Phase One, Phase Two, rookie minicamp, OTA and mandatory-minicamp plans and reports",
    "Draft": "Board, pick ownership, selections, undrafted signings and rookie agreements",
    "Training_Camp_and_Preseason": "Camp reports, position battles, preseason games and roster decisions",
    "Regular_Season": "Weekly games and preparation, statistics, standings and awards",
    "Postseason": "Playoff games, postseason statistics, honours and the Pro Bowl",
    "Season_Review": "Player exit interviews, coach reviews, final assessments and the next-season handoff",
}


class Paused(ValueError):
    """A Jacksonville game is paused: Document 5 and both files are frozen."""


@dataclass
class Context:
    root: Path
    mapping: dict
    season: int
    paths: SeasonPaths
    job: dict
    queue: dict
    master: date
    clock: str                       # Document 5's master-date cell
    scheduled: list                  # (date cell, event cell) of the section 9 rows still scheduled
    games: list                      # the employer club's fixtures, amendments applied, by date
    places: dict                     # club -> the place name the views use
    events: dict = field(default_factory=dict)   # closed events by id (the owner page of each)
    fields: list = field(default_factory=list)   # (source field, value) shown in the block being built
    headings: dict = field(default_factory=dict)

    def show(self, source, value):
        """Record a shown source value so a banned word names its field."""
        self.fields.append((source, str(value)))
        return value


# ---- small text helpers -----------------------------------------------------

def day(value, year=True):
    when = value if isinstance(value, date) else date.fromisoformat(value)
    return f"{when:%B} {when.day}, {when.year}" if year else f"{when:%B} {when.day}"


def span(start, end, start_label=None):
    """'from X until Y', the year once when both dates share it."""
    if start is None:
        return "from %s until %s" % (start_label or "the start", day(end))
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return "from %s until %s" % (day(first, first.year != last.year), day(last))


def join(items, word="and"):
    items = [str(i) for i in items]
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " " + word + " " + items[-1]


def first_clause(text):
    text = str(text).split(";")[0].strip()
    return text[:1].lower() + text[1:]


def kickoff(clock):
    hour, minute = (int(part) for part in clock.split(":"))
    if (hour, minute) == (12, 0):
        return "noon ET"
    hand = hour % 12 or 12
    return ("%d" % hand if minute == 0 else "%d:%02d" % (hand, minute)) + (" a.m." if hour < 12 else " p.m.") + " ET"


def name(ctx, pid, lower=False):
    text = ctx.show("parties.%s.name" % pid, current_job.party_name(ctx.job, pid))
    party = (ctx.job.get("parties") or {}).get(pid) or {}
    return text[:1].lower() + text[1:] if lower and party.get("kind") == "group" else text


def short(ctx, pid):
    party = (ctx.job.get("parties") or {}).get(pid) or {}
    return (party.get("aliases") or [current_job.party_name(ctx.job, pid)])[0]


def verb(ctx, pids, singular="decides", plural="decide"):
    parties = ctx.job.get("parties") or {}
    one = len(pids) == 1 and (parties.get(pids[0]) or {}).get("kind") != "group"
    return singular if one else plural


def rows_text(rows):
    """Document 3 row numbers, runs of three or more as a range."""
    order = current_job.AUTHORITY_ROWS
    runs = []
    for i in sorted(order.index(r) for r in rows):
        if runs and i == runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    parts = []
    for run in runs:
        parts.extend(["%s-%s" % (order[run[0]], order[run[-1]])] if len(run) >= 3 else [order[i] for i in run])
    return ("row " if len(rows) == 1 else "rows ") + join(parts)


def link(ctx, label, record):
    """A link to a {path, anchor?} record written with the repository path
    (localized per file later); the target and its heading must exist."""
    record = {"path": record} if isinstance(record, str) else record
    target = resolve_path(ctx.root, record["path"], ctx.mapping)
    if not target.is_file():
        raise ValueError("career view link target missing: %s" % record["path"])
    anchor = record.get("anchor")
    if anchor:
        if target not in ctx.headings:
            ctx.headings[target] = anchors(without_code(target.read_text(encoding="utf-8")))
        if target.suffix != ".md" or anchor not in ctx.headings[target]:
            raise ValueError("career view link heading missing: %s#%s" % (record["path"], anchor))
    rel = target.relative_to(ctx.root).as_posix()
    return "[%s](@%s%s)" % (label, rel, "#" + anchor if anchor else "")


def season_link(ctx, label, logical):
    return link(ctx, label, ctx.paths.record(logical).relative_to(ctx.root).as_posix())


def localize(text, rel):
    """Each @-link relative to the file at ``rel``, encoded as
    runtime.season_layout.rebase_markdown encodes it (spaces as %20)."""
    def one(match):
        path = posixpath.relpath(match[1], posixpath.dirname(rel) or ".")
        return "](" + quote(path, safe="/._-") + ("#" + match[2] if match[2] else "") + ")"
    return LINK.sub(one, text)


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    return "\n".join(lines + ["| " + " | ".join(str(c).replace("|", "/") for c in row) + " |" for row in rows])


# ---- inputs -----------------------------------------------------------------

def context(root):
    root = Path(root).resolve()
    mapping = repository_map(root)
    season = int(mapping["active_season"])
    paths = SeasonPaths(season, root)
    job = current_job.load(root)
    queue = decision_queue.load(root)
    state = (root / STATE).read_text(encoding="utf-8")
    cell = re.search(r"^\| Master date/time \| (.+?) \|\s*$", state, re.M)
    if not cell:
        raise ValueError("Document 5 has no master date/time row")
    master = master_date(root)
    club = ((current_job.appointment(job) or {}).get("employer") or {}).get("club")
    data = json.loads(paths.schedule.read_text(encoding="utf-8"))
    every = paths.regular_games()
    changes = {}
    for amendment in data.get("amendments") or ():
        if amendment.get("effective") and date.fromisoformat(amendment["effective"]) <= master:
            changes.setdefault(amendment["game_id"], []).append(amendment["change"])
    games = []
    for game in every:
        if club in (game["away"], game["home"]):
            game = dict(game)
            for change in changes.get(game["game_id"], ()):
                game.update({k: change[k] for k in ("date", "weekday", "kickoff_et", "stadium") if k in change})
            games.append(game)
    clubs = {g[side] for g in every for side in ("away", "home")}
    place = {c: c.rsplit(" ", 1)[0] for c in clubs}
    places = {c: p if list(place.values()).count(p) == 1 else c for c, p in place.items()}
    return Context(root, mapping, season, paths, job, queue, master, cell[1].strip(), scheduled_events(state),
                   sorted(games, key=lambda g: (g["date"], g["week"])), places, load_events(root, mapping))


def scheduled_events(state):
    """(date, event) for each section 9 row whose position starts
    Scheduled, parentheticals removed from the event."""
    found = re.search(r"^## 9\. Next dated events\s*$", state, re.M)
    if not found:
        raise ValueError("Document 5 has no section 9 (Next dated events)")
    section = re.split(r"^## ", state[found.end():], maxsplit=1, flags=re.M)[0]
    rows = []
    for line in section.splitlines():
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip()[1:-1].split("|")]
            if len(cells) >= 3 and cells[2].startswith("Scheduled"):
                rows.append((cells[0], re.sub(r"\s*\([^()]*\)", "", cells[1])))
    return rows


def last_and_next(ctx):
    """The latest employer-club fixture already played by the clock (on the
    master date only when the clock says after that week's game) and the
    first one after it."""
    after = re.search(r"after the Week (\d+) game", ctx.clock)
    played = [g for g in ctx.games if date.fromisoformat(g["date"]) < ctx.master
              or (date.fromisoformat(g["date"]) == ctx.master and after and int(after[1]) == g["week"])]
    rest = [g for g in ctx.games if g not in played]
    return (played[-1] if played else None), (rest[0] if rest else None)


# ---- the job record ---------------------------------------------------------

def _interval_notes(ctx, interval):
    notes = []
    start = date.fromisoformat(interval["from"]) if interval.get("from") else None
    if start is None and interval.get("from_label"):
        notes.append("since " + ctx.show("from_label", interval["from_label"]))
    elif interval.get("from_label"):
        notes.append(ctx.show("from_label", interval["from_label"]))
    year = start.year if start else None
    if interval.get("instructed"):
        when = date.fromisoformat(interval["instructed"])
        notes.append("instructed " + day(when, when.year != year))
    if interval.get("end_rule"):
        notes.append(first_clause(ctx.show("end_rule", interval["end_rule"])))
    for later in interval.get("continued") or ():
        when = date.fromisoformat(later["date"])
        notes.append("continued " + day(when, when.year != year))
    return notes


def _previous(ctx, phase, current):
    earlier = [r for r in current_job._intervals(ctx.job, phase) if r is not current and r.get("to")]
    return ["%s%s (%s)" % (name(ctx, r["caller"]), ", interim" if r.get("interim") else "",
                           span(r.get("from"), r["to"], r.get("from_label"))) for r in reversed(earlier)]


def _current_interval(ctx, phase):
    rows = current_job._intervals(ctx.job, phase)
    return next((r for r in rows if r.get("to") is None), rows[-1] if rows else None)


def _interval_link(ctx, interval):
    return link(ctx, "instruction" if interval.get("instructed") else "record", interval["record"])


def phase_value(ctx, phase):
    """Document 5's row for a phase: who calls it now, who prepares and
    transmits, and who called it before."""
    interval = _current_interval(ctx, phase)
    if interval is None:
        return "not recorded"
    who = "%s%s calls" % (name(ctx, interval["caller"]), ", interim" if interval.get("interim") else "")
    if interval.get("from"):
        who += " from " + day(interval["from"])
    notes = _interval_notes(ctx, interval)
    parts = [who + (" (%s)" % "; ".join(notes) if notes else "")]
    parts += _staff_parts(ctx, interval, with_prepares=True)
    text = "; ".join(parts) + " (%s)" % _interval_link(ctx, interval)
    before = _previous(ctx, phase, interval)
    return text + (". Before: " + "; ".join(before) if before else "")


def _staff_parts(ctx, interval, with_prepares):
    parts = []
    prepares, transmits = interval.get("prepares"), interval.get("transmits")
    what = ctx.show("transmits_what", interval.get("transmits_what") or "the call")
    if with_prepares and prepares and prepares != interval["caller"]:
        both = transmits == prepares
        parts.append("%s prepares%s" % (name(ctx, prepares), " and transmits " + what if both else ""))
    if transmits and not (with_prepares and transmits == prepares and prepares != interval["caller"]):
        parts.append("%s transmits %s" % (name(ctx, transmits), what))
    if interval.get("front_declaration"):
        parts.append("%s declares the front" % name(ctx, interval["front_declaration"]))
    return parts


def management_value(ctx):
    management = ((current_job.appointment(ctx.job) or {}).get("delegation") or {}).get("game_management") or {}
    decisions = management.get("decisions") or []
    labels = [DECISION_LABEL.get(d["id"], d["id"].replace("_", " ")) for d in decisions]
    who = short(ctx, ctx.job["holder"])
    text = "%s %s %s" % (name(ctx, management["decides"]), verb(ctx, [management["decides"]]), join(labels))
    if management.get("with"):
        text += ", with " + ctx.show("game_management.with", management["with"])
    if management.get("record"):
        text += " (%s)" % link(ctx, "Document 3", management["record"])
    groups = (("%s's live calls" % who, ("live",)), ("From the week's frozen call sheet", ("sheet_rule",)),
              ("Not %s's live calls" % who, ("not_live", "not_modelled")))
    sentences = [text]
    for heading, mechanisms in groups:
        entries = []
        for decision in decisions:
            if decision.get("mechanism") in mechanisms:
                how = ctx.show("game_management.%s.how" % decision["id"], decision.get("how") or "not recorded")
                if decision.get("record"):
                    how += "; " + link(ctx, "record", decision["record"])
                entries.append("%s (%s)" % (DECISION_LABEL.get(decision["id"], decision["id"]), how))
        if entries:
            sentences.append("%s: %s" % (heading, "; ".join(entries)))
    return ". ".join(sentences)


def relay_value(ctx):
    relay = ((current_job.appointment(ctx.job) or {}).get("delegation") or {}).get("relay") or {}
    carriers = ["%s: %s" % (name(ctx, c["party"]), ctx.show("relay.carries", c["carries"]))
                for c in relay.get("carriers") or ()]
    text = "; ".join(carriers) or "not recorded"
    return text + (" (%s)" % link(ctx, "record", relay["record"]) if relay.get("record") else "")


def emergency_value(ctx):
    emergency = ((current_job.appointment(ctx.job) or {}).get("delegation") or {}).get("emergency") or {}
    leads = [name(ctx, p) for p in emergency.get("practice_lead") or ()]
    text = "Practice: " + (", then ".join(leads) or "not appointed")
    if emergency.get("from"):
        text += ", from " + day(emergency["from"])
    if emergency.get("limits"):
        text += ": " + ctx.show("emergency.limits", emergency["limits"])
    if emergency.get("unchanged"):
        text += ". Unchanged: " + ctx.show("emergency.unchanged", emergency["unchanged"])
    if emergency.get("record"):
        text += " (%s)" % link(ctx, "record", emergency["record"])
    caller = emergency.get("game_day_caller")
    note = first_clause(ctx.show("emergency.game_day_note", emergency.get("game_day_note") or "not recorded"))
    return text + ". Game-day caller: " + (name(ctx, caller) if caller else note)


def authority_value(ctx):
    """One sentence grouping Document 3's rows by who decides and the
    holder's part, in the row order. A row the holder decides in part also
    names its final authority, unless that is the holder alone."""
    current = current_job.appointment(ctx.job) or {}
    rows = (current.get("authority") or {}).get("domains") or []
    holder, who = ctx.job["holder"], short(ctx, ctx.job["holder"])
    decides = [r["row"] for r in rows if r["stone_action"] == "decides"]
    part = [r["row"] for r in rows if r["stone_action"] == "decides_part"]
    head = ([rows_text(decides)] if decides else []) + (["in part " + rows_text(part)] if part else [])
    clauses = ["%s decides %s" % (name(ctx, holder), ", and ".join(head))] if head else []
    groups = {}
    for row in rows:
        action = row["stone_action"]
        if action in ("decides", "not_applicable") or (action == "decides_part" and row["final"] == [holder]):
            continue
        scope = ctx.show("authority.%s.scope" % row["row"], row.get("scope")) if action == "decides_part" else None
        groups.setdefault(tuple(row["final"]), {}).setdefault((action, scope), []).append(row["row"])
    for final, actions in groups.items():
        parts = [rows_text(numbers) + AUTHORITY_NOTE.get(action, "").format(who=who, scope=scope)
                 for (action, scope), numbers in actions.items()]
        parties = join(name(ctx, p, lower=True) for p in final)
        clauses.append("%s %s %s" % (parties, verb(ctx, list(final)), join(parts)))
    taxonomy = (current.get("authority") or {}).get("taxonomy")
    return "; ".join(clauses) + (" (%s)" % link(ctx, "Document 3 section 5", taxonomy) if taxonomy else "")


def instruction_lines(ctx):
    """(label, text, record link) for each standing instruction."""
    lines = []
    for item in current_job.instructions(ctx.job, None):
        subject = item.get("subject") or ""
        label = SUBJECT_LABEL.get(subject, subject.replace("_", " ").capitalize() or item.get("id"))
        status = STATUS_LABEL.get(item.get("status"), str(item.get("status")))
        if item.get("effective"):
            status += ", from " + day(item["effective"])
        text = ctx.show("standing_instructions.%s.summary" % item.get("id"), item.get("summary") or "not recorded")
        if item.get("applies"):
            text += "; " + ctx.show("standing_instructions.%s.applies" % item.get("id"), item["applies"])
        lines.append(("%s (%s)" % (label, status), text, link(ctx, "record", item["record"])))
    return lines


def job_fields(ctx):
    """(field, value) rows of Document 5's current-job block; the desk
    reuses the game-day rows."""
    current = current_job.appointment(ctx.job)
    if current is None:
        return [("Job", "Between jobs; no current appointment")]
    employer = current.get("employer") or {}
    holder = ctx.job["holder"]
    job = "%s, %s (%s), since %s" % (ctx.show("title", current["title"]), employer.get("club"),
                                     employer.get("league"), day(current["start"]))
    links = [link(ctx, "job record", current_job.JOB.as_posix())]
    term = current_job.term(ctx.job, ctx.root, ctx.master)
    if term["contract"] is not None:
        job += "; contract through the %d season, ending %s" % (max(term["seasons"]), first_clause(
            ctx.show("contract.end", term["end_text"] or "on a date not recorded")))
        links.append(link(ctx, "contract", CONTRACT_PAGE))
        links.append(link(ctx, "signed terms", term["contract"]["signed"]["source"]))
    for entry in current.get("history") or ():
        if entry.get("kind") != "accepted":
            job += "; %s %s" % (entry["kind"], day(entry["date"]))
            if entry.get("note"):
                job += " " + first_clause(ctx.show("history.note", entry["note"]))
        links.append(link(ctx, HISTORY_LABEL.get(entry.get("kind"), entry.get("kind")), entry["record"]))
    fields = [("Job", "%s (%s)" % (job, "; ".join(links)))]
    reporting = current.get("reporting") or {}
    decided = reporting.get("employment_decided_by") or []
    text = join(name(ctx, p) for p in decided) or "not recorded"
    if reporting.get("employment_row"):
        text += " (Document 3 row %s)" % reporting["employment_row"]
    unset = [label for key, label in REPORTING_LABEL if reporting.get(key) is None]
    known = ["%s: %s" % (label, name(ctx, reporting[key]) if key in ("direct_supervisor", "evaluator")
                         else reporting[key]) for key, label in REPORTING_LABEL if reporting.get(key) is not None]
    text += "".join("; " + k for k in known) + ("; %s not recorded" % join(unset) if unset else "")
    if reporting.get("unset_basis"):
        text += " (%s)" % link(ctx, "Document 3", reporting["unset_basis"])
    fields.append(("Employment decided by", text))
    fields.append(("Employer's measures", measures_value(ctx, current)))
    requests = [r for r in current.get("employer_requests") or () if r.get("status") == "OPEN"]
    fields.append(("Employer's requests", "; ".join(
        "%s: %s (%s)" % (name(ctx, r["by"]), ctx.show("employer_requests.text", r["text"]),
                         link(ctx, "record", r["record"])) for r in requests) or "none open"))
    for phase in current_job.PHASES:
        fields.append((PHASE_LABEL[phase], phase_value(ctx, phase)))
    fields.append(("Retained by %s" % short(ctx, holder), management_value(ctx)))
    fields.append(("Game-day information", relay_value(ctx)))
    fields.append(("Emergency leads", emergency_value(ctx)))
    fields.append(("Final authority", authority_value(ctx)))
    fields.append(("Standing instructions", " ".join(
        "%s: %s (%s)." % (label, text, record) for label, text, record in instruction_lines(ctx)) or "none"))
    return fields


def measures_value(ctx, current):
    entries = current.get("evaluation") or []
    latest = max((e.get("season") or 0 for e in entries), default=None)
    shown = []
    for entry in entries:
        if (entry.get("season") or 0) != latest:
            continue
        who = "The contract" if entry.get("by") == "contract" else name(ctx, entry["by"])
        what = "; ".join(entry.get("measures") or ()) or entry.get("text") or "not recorded"
        label = ctx.show("evaluation.label", entry["label"]) if entry.get("label") else entry.get("season")
        shown.append("%s, %s: %s (%s)" % (who, label, ctx.show("evaluation.measures", what),
                                          link(ctx, "record", entry["record"])))
    return "; ".join(shown) or "not recorded"


def current_job_block(ctx):
    return table(("Field", "Current value"), job_fields(ctx))


# ---- the decision queue -----------------------------------------------------

def ordered_items(ctx):
    """The OPEN items: the holder's first, then the others, each by deadline
    (none last) and id."""
    holder = ctx.job.get("holder")
    def key(item):
        deadline = (item.get("deadline") or {}).get("date")
        return (item.get("owner") != holder, deadline is None, deadline or "", item.get("id") or "")
    return sorted(decision_queue.unresolved(ctx.queue), key=key)


def holds_text(item, brief):
    """What the item holds; ``brief`` names a held week's game without the
    note on what stays unfrozen."""
    held = [decision_queue.describe(dict(b, kind="week_close") if brief and b.get("kind") == "week_inputs" else b)
            for b in item.get("blocks") or ()]
    return join(held) or "nothing"


def owner_text(ctx, item):
    text = name(ctx, item["owner"])
    if item.get("advisers"):
        text += ", with " + join(name(ctx, p) for p in item["advisers"])
    return text


def waits_text(ctx, item, dated=True):
    waits = []
    for wait in item.get("waits_on") or ():
        what = ctx.show("waits_on.what", wait["what"])
        waits.append("%s (%s)" % (what, day(wait["date"], False)) if dated and wait.get("date") else what)
    return waits


def decision_queue_block(ctx):
    items = ordered_items(ctx)
    rows = []
    for item in items:
        holds = holds_text(item, True)
        if item.get("fallback"):
            holds += "; otherwise: " + item["fallback"]
        rows.append((item["title"], owner_text(ctx, item), (item.get("deadline") or {}).get("label") or "no deadline",
                     holds, "; ".join(waits_text(ctx, item)) or "nothing", link(ctx, "record", item["record"])))
    headers = ("Decision", "Owner", "Needed", "Holds", "Waiting on", "Record")
    body = table(headers, rows) if rows else "No decision is open."
    return (body + "\n\nGenerated from the %s. Only these items stop a build, a close or a season opening; prose "
            "elsewhere does not." % link(ctx, "decision queue", decision_queue.QUEUE.as_posix()))


# ---- the desk ---------------------------------------------------------------

def _game_text(ctx, game):
    text = "Week %d, %s at %s, %s, %s, %s, %s" % (
        game["week"], ctx.places[game["away"]], ctx.places[game["home"]], game.get("weekday"),
        day(game["date"], False), kickoff(game["kickoff_et"]), game.get("stadium"))
    return text + (", " + game["city"] if game.get("city") else "")


def _week_readme(ctx, week, label):
    readme = ctx.paths.week_folder(week) / "README.md"
    return link(ctx, label, readme.relative_to(ctx.root).as_posix()) if readme.is_file() else label


def render_desk(ctx):
    """The active season's README, whole: today and the last result, the job, what is waiting
    on him, the next event, then everything else."""
    profile = current_job.desk_profile(ctx.job)
    if profile not in current_job.BUILT_DESKS:
        raise NotImplementedError("desk for role %s is defined (ROLE_SECTIONS) but not built" % profile)
    current = current_job.appointment(ctx.job)
    holder = ctx.job["holder"]
    last, upcoming = last_and_next(ctx)
    out = ["# %s %d" % (place_name(ctx), ctx.season), ""]
    today = "**%s.**" % day(ctx.master)
    result = last_game(ctx.root, ctx.season, current["employer"]["club"], ctx.master)
    if result is not None:
        game, mine, theirs = result
        other = game["home"] if game["away"] == current["employer"]["club"] else game["away"]
        verb_ = "beat" if mine > theirs else "lost to" if mine < theirs else "tied"
        where = "at home" if game["home"] == current["employer"]["club"] else "away"
        today += " Last game: Week %d, %s %s %d-%d %s. Record: %s." % (
            game["week"], verb_, ctx.places[other], max(mine, theirs), min(mine, theirs), where,
            club_record(ctx.root, ctx.season, current["employer"]["club"], game["week"]))
    out += [today, ""]
    out += ["%s, %s of the %s since %s. %s" % (name(ctx, holder), ctx.show("title", current["title"]).lower(),
                                              current["employer"]["club"], day(current["start"]),
                                              link(ctx, "Coach page", COACH_PAGE)), ""]
    items = ordered_items(ctx)
    out += ["## Waiting on you", ""] + _waiting(ctx, [i for i in items if i.get("owner") == holder]) + [""]
    out += ["## Next event", ""]
    if upcoming is None:
        out += ["No regular-season game remains; see the %s."
                % link(ctx, "calendar", ctx.paths.calendar.relative_to(ctx.root).as_posix()), ""]
    else:
        out += ["**Next game:** %s. %s" % (_game_text(ctx, upcoming), _week_readme(ctx, upcoming["week"],
                                                                                   "Week %d" % upcoming["week"])), ""]
    out += ["## Coming up", ""]
    events = []
    for when, what in ctx.scheduled:
        what = football(ctx.show("Document 5 section 9 event", what))
        if what:
            events.append("- %s: %s" % (ctx.show("Document 5 section 9 date", when), what))
    out += (events or ["Nothing else is scheduled."]) + [""]
    out += ["## With others", ""] + _with_others(ctx, [i for i in items if i.get("owner") != holder]) + [""]
    out += ["## Standing instructions", ""] + _instructions(ctx) + [""]
    out += ["## Who calls what", ""] + _callers(ctx) + ["", link(ctx, "Coaching staff", rel(ctx, ctx.paths.staff_page)), ""]
    links = [season_link(ctx, label, logical) for label, logical in DESK_LINKS]
    links += [link(ctx, "Coaching staff", rel(ctx, ctx.paths.staff_page)), link(ctx, "Coach page", COACH_PAGE),
              link(ctx, "Contract and jobs", CONTRACT_PAGE), link(ctx, "Calendar", rel(ctx, ctx.paths.calendar)),
              link(ctx, "Record", rel(ctx, ctx.paths.annual_record))]
    out += ["## Records", "", " · ".join(links), ""]
    out += ["## Season folders", ""] + _folders(ctx) + [""]
    return render_season_hub.insert_dashboard(ctx, "\n".join(out).rstrip() + "\n")


def rel(ctx, path):
    return Path(path).relative_to(ctx.root).as_posix()


def place_name(ctx):
    club = (current_job.appointment(ctx.job) or {}).get("employer", {}).get("club") or ""
    return ctx.places.get(club, club)


# A verb the record writes about the head coach, as the desk writes it to him.
IRREGULAR = {"has": "have", "is": "are", "does": "do", "goes": "go"}


def addressed(verb):
    """The verb of a third-person clause as the second person says it: calls, call; takes, take."""
    if verb in IRREGULAR:
        return IRREGULAR[verb]
    if re.search(r"(?:ch|sh|ss|x|z)es$", verb):
        return verb[:-2]
    if re.search(r"[^aeiou]ies$", verb):
        return verb[:-3] + "y"
    return verb[:-1] if verb.endswith("s") else verb


def second_person(ctx, text):
    """A standing instruction as the desk says it to the head coach. The record words it about
    him in the third person, as Document 5 shows it ("Stone calls, delegates or takes back any
    phase ...; the arrangement stands until he changes it"); the desk reads "You call, delegate or
    take back any phase ...; the arrangement stands until you change it". A line that does not
    open with his name is shown as recorded."""
    holder = short(ctx, ctx.job.get("holder"))
    if not text.startswith(holder + " "):
        return text
    rest = text[len(holder) + 1:]
    # The opening series of verbs, "calls, delegates or takes back": each word in it ending in s is
    # a verb (the particles and the conjunctions do not end in s).
    series = re.match(r"[a-z]+s(?: (?:back|up|out|in|off|over))?(?:(?:,| or| and|, or|, and) [a-z]+s"
                      r"(?: (?:back|up|out|in|off|over))?)*\b", rest)
    if series:
        rest = re.sub(r"\b[a-z]+s\b", lambda m: addressed(m.group(0)), series.group(0)) + rest[series.end():]
    rest = re.sub(r"\bhe ([a-z]+)\b", lambda m: "you " + addressed(m.group(1)), rest)
    rest = re.sub(r"\bhimself\b", "yourself", rest)
    rest = re.sub(r"\bhis\b", "your", rest)
    rest = re.sub(r"\bhim\b", "you", rest)
    return "You " + rest


def football(text):
    """The clauses of a recorded line that are football, without process words."""
    kept = [c.strip() for c in str(text).split(";") if c.strip() and not DESK_WORDS.search(c)]
    return "; ".join(kept)


def _week_of(item):
    """The season week an item is due for, from its deadline or what it waits for, or None."""
    for event in [(item.get("deadline") or {}).get("before") or {}] + list(item.get("blocks") or ()):
        if event.get("week") is not None:
            return event["week"]
    return None


def _waiting(ctx, items):
    lines = []
    games = {g["week"]: g for g in ctx.games}
    for n, item in enumerate(items, 1):
        field = "decision_queue.%s." % item["id"]
        line = "%d. **%s.**" % (n, ctx.show(field + "title", item["title"]).rstrip("."))
        question = ctx.show(field + "question", item.get("question") or "")
        if ":" in question:
            settle = football(question.split(":", 1)[1])
            if settle and settle == question.split(":", 1)[1].strip():
                line += " To settle: %s" % settle
        week = _week_of(item)
        game = games.get(week)
        deadline = (item.get("deadline") or {}).get("date")
        if game is not None:
            line += " Due before kickoff, %s, %s, %s." % (game.get("weekday"), day(game["date"], False),
                                                        kickoff(game["kickoff_et"]))
        elif deadline:
            line += " Due by %s." % day(deadline, False)
        waits = []
        for wait in item.get("waits_on") or ():
            what = football(ctx.show("waits_on.what", wait["what"]).split(";")[0])
            if what:
                waits.append("%s (%s)" % (what, day(wait["date"], False)) if wait.get("date") else what)
        if waits:
            line += " Still to come: %s." % "; ".join(waits)
        if week is not None and (ctx.paths.week_folder(week) / "README.md").is_file():
            line += " " + _week_readme(ctx, week, "Week %d" % week)
        elif _readable(ctx, item.get("record")):
            line += " " + page_link(ctx, item["record"])
        lines.append(line)
    return lines or ["Nothing is waiting on you."]


def _readable(ctx, record):
    """Whether a record is a football page the desk may link."""
    return bool(record) and str(record.get("path", "")).startswith("career/") and record["path"].endswith(".md")


def page_link(ctx, record):
    """A desk link to a football page, labelled by what the page is, its anchor dropped when the
    anchor carries a code or a real-world date."""
    record = {"path": record} if isinstance(record, str) else dict(record)
    target = resolve_path(ctx.root, record["path"], ctx.mapping)
    record["anchor"] = football_anchor(record.get("anchor"), ctx.master)
    label = next((label for label, logical in PAGE_LABELS if ctx.paths.record(logical) == target), None)
    if label is None and target == ctx.paths.staff_page:
        label = "Coaching staff"
    for week in sorted({g["week"] for g in ctx.games}):
        if label is None and target.parent == ctx.paths.week_folder(week):
            label = "Week %d" % week if target.name == "README.md" else "Week %d report" % week
    return link(ctx, label or heading(target), record)


def _with_others(ctx, items):
    lines = []
    for item in items:
        line = "- **%s** (%s)" % (ctx.show("decision_queue.%s.title" % item["id"], item["title"]).rstrip("."),
                                  owner_text(ctx, item))
        waits = [football(w) for w in waits_text(ctx, item, dated=False)]
        if any(waits):
            line += "; waiting on " + join(w for w in waits if w)
        line += "."
        if _readable(ctx, item.get("record")):
            line += " " + page_link(ctx, item["record"])
        lines.append(line)
    return lines or ["Nothing open."]


def _instructions(ctx):
    """Each standing instruction in force, in plain words, linked to the football page it was
    given in (a rule frozen into a game file links to the page of the event that set it)."""
    lines = []
    for item in current_job.instructions(ctx.job):
        subject = item.get("subject") or ""
        label = SUBJECT_LABEL.get(subject, subject.replace("_", " ").capitalize() or item.get("id"))
        if item.get("effective"):
            label += ", from " + day(item["effective"])
        text = second_person(ctx, football(ctx.show("standing_instructions.%s.summary" % item.get("id"),
                                                     item.get("summary") or "")))
        record = item.get("record") or {}
        if subject == "play_calling":
            record = {"path": rel(ctx, ctx.paths.staff_page), "anchor": CALLING_SECTION}
        if not _readable(ctx, record):
            event = (item.get("given") or {}).get("event")
            owner = ctx.events.get(event).owner if event in ctx.events else None
            record = {"path": owner} if owner else {}
        line = "- **%s:** %s." % (label, text.rstrip(".") or "recorded")
        if record:
            line += " " + (link(ctx, "Who calls what", record) if subject == "play_calling" else page_link(ctx, record))
        lines.append(line)
    return lines or ["None."]


def _callers(ctx):
    lines = []
    for phase in current_job.PHASES:
        interval = _current_interval(ctx, phase)
        if interval is None:
            continue
        text = "- **%s.** %s%s calls" % (PHASE_LABEL[phase], name(ctx, interval["caller"]),
                                         ", interim," if interval.get("interim") else "")
        if interval.get("from"):
            text += ", since %s" % day(interval["from"])
        parts = [text]
        prepares, transmits = interval.get("prepares"), interval.get("transmits")
        if prepares and prepares != interval["caller"]:
            parts.append("%s prepares%s" % (name(ctx, prepares), " and sends in the call" if transmits == prepares else ""))
        if transmits and transmits != prepares:
            parts.append("%s sends in the call" % name(ctx, transmits))
        if interval.get("front_declaration"):
            parts.append("%s declares the front" % name(ctx, interval["front_declaration"]))
        lines.append("; ".join(parts) + ".")
    return lines


def _folders(ctx):
    rows = []
    for folder in NUMBERED_FOLDERS.values():
        readme = ctx.paths.career / folder / "README.md"
        label = folder.replace("_", " ").capitalize().replace("Ota", "OTA")
        cell = link(ctx, label, rel(ctx, readme)) if readme.is_file() else label
        rows.append((cell, FOLDER_NOTES.get(folder, "")))
    lines = table(("Folder", "What belongs here"), rows).split("\n")
    lines += ["", "The draft overlaps spring training; the calendar gives the dates within each phase. The season "
              "review follows the last game of the season, playoffs included."]
    seasons = []
    before = SeasonPaths(ctx.season - 1, ctx.root).desk
    if before.is_file():
        seasons.append(link(ctx, "%d season" % (ctx.season - 1), rel(ctx, before)))
    after = SeasonPaths(ctx.season + 1, ctx.root).calendar
    if after.is_file():
        seasons.append(link(ctx, "%d calendar" % (ctx.season + 1), rel(ctx, after)))
    if seasons:
        lines += ["", " · ".join(seasons)]
    return lines


# ---- docs/career_layer.md ---------------------------------------------------

def classes_block(ctx):
    rows = []
    holder = short(ctx, ctx.job["holder"])
    for key, cls in decision_queue.CLASSES.items():
        owner = "the job holder (%s)" % holder if cls.default_owner == "holder" else name(ctx, cls.default_owner)
        blocks = ", ".join("`%s`" % k for k in decision_queue.BLOCK_KINDS if k in cls.may_block) or "nothing"
        rows.append(("`%s`" % key, owner, ", ".join(cls.rows) or "none", blocks,
                     "yes" if cls.closable_by_standing else "no", "yes" if cls.raised_only_by_user else "no"))
    body = table(("Class", "Default owner", "Document 3 rows", "May block", "Closable by a standing instruction",
                  "Raised only by the user"), rows)
    return (body + "\n\nGenerated from `CLASSES` in `runtime/decision_queue.py` by "
            "`python scripts/render_career_views.py`.")


# ---- blocks, files and markers -----------------------------------------------

def _pattern(name):
    return re.compile(r"<!-- %s:begin(?: [^>]*)? -->.*?<!-- %s:end -->" % (re.escape(name), re.escape(name)), re.S)


def _counts(text, name):
    return text.count("<!-- %s:begin" % name), text.count("<!-- %s:end -->" % name)


def _voice(ctx, name, text):
    plain = "\n".join(line for line in re.sub(r"\]\([^)]*\)", "]", text).splitlines() if not line.startswith("<!-- "))
    found = BANNED.search(plain)
    if found:
        source = next((f for f, v in ctx.fields if re.search(r"\b%s\b" % re.escape(found[0]), v, re.I)),
                      "the view's own wording")
        raise ValueError("Banned word '%s' in %s text from %s; reword the source" % (found[0], name, source))


def _manifest(ctx, text):
    """Document 5 with both files' blob rows directly after Document 4's."""
    start = text.index("## Effective source-version manifest")
    end = text.find("\n## ", start + 1)
    end = len(text) if end < 0 else end
    lines = [line for line in text[start:end].split("\n")
             if not any(line.startswith("| %s |" % label) for label, _, _ in MANIFEST_ROWS)]
    at = next((i for i, line in enumerate(lines) if line.startswith("| Document 4 |")), None)
    if at is None:
        raise ValueError("Document 5's manifest has no Document 4 row")
    lines[at + 1:at + 1] = ["| %s | `%s` | %s |" % (label, git_blob((ctx.root / path).read_bytes()),
                                                    link(ctx, title, path)) for label, path, title in MANIFEST_ROWS]
    return text[:start] + localize("\n".join(lines), STATE.as_posix()) + text[end:]


def _readmes(root):
    return sorted(Path(root).glob("career/*/README.md"))


def managed(root):
    """Marker name -> the file holding that block (repository-relative)."""
    root = Path(root).resolve()
    season = int(repository_map(root)["active_season"])
    paths = SeasonPaths(season, root)
    return {"current-job": STATE, "decision-queue": STATE,
            "desk": paths.desk.relative_to(root),
            "calendar": paths.calendar.relative_to(root),
            "medical": paths.record("medical/current_injury_report.md").relative_to(root),
            "statbook": (paths.career / "Regular_Season/Statistics/README.md").relative_to(root),
            "decision-classes": DOC}


BUILDERS = {"current-job": current_job_block, "decision-queue": decision_queue_block,
            "desk": render_desk, "calendar": render_season_hub.calendar_page,
            "medical": render_season_hub.medical_page, "statbook": render_season_hub.statistics_page,
            "decision-classes": classes_block}
WHOLE = frozenset({"desk", "calendar", "medical", "statbook"})     # built as the whole file, with no markers


def _render(root):
    """(expected text of every managed file, block names per file, marker problems)."""
    ctx = context(root)
    root = ctx.root
    files = managed(root)
    desk_home = root / files["desk"]
    plan = [(files[name], name, BUILDERS[name]) for name in files]
    texts, names, problems = {}, {}, []
    for rel, name, build in plan:
        path = root / rel
        if path not in texts:
            texts[path] = path.read_text(encoding="utf-8") if path.is_file() else ""
        names.setdefault(path, []).append(name)
        ctx.fields = []
        body = localize(build(ctx), Path(rel).as_posix())
        if name in VOICED:
            _voice(ctx, name, body)
        if name in WHOLE:
            texts[path] = body
            continue
        block = "<!-- %s:begin -->\n%s\n<!-- %s:end -->" % (name, body.rstrip("\n"), name)
        counts = _counts(texts[path], name)
        if counts == (1, 1) and _pattern(name).search(texts[path]):
            texts[path] = _pattern(name).sub(lambda _: block, texts[path], count=1)
        else:
            problems.append("Career view markers missing or duplicated: %s %s" % (Path(rel).as_posix(), name))
    texts[root / STATE] = _manifest(ctx, texts[root / STATE])
    names[root / STATE].append("manifest")
    for readme in _readmes(root):
        if readme != desk_home:
            text = texts.get(readme, readme.read_text(encoding="utf-8"))
            stripped = re.sub(r"\n\n<!-- desk:begin[^>]*-->.*?<!-- desk:end -->", "", text, flags=re.S)
            texts[readme] = _pattern("desk").sub("", stripped)
            names.setdefault(readme, []).append("desk-block")
    return texts, names, problems


def render(root):
    """The full expected text of every managed file."""
    return _render(root)[0]


def _section(text, name):
    if name == "manifest":
        start = text.find("## Effective source-version manifest")
        return text[start:text.find("\n## ", start + 1)] if start >= 0 else None
    found = _pattern("desk" if name == "desk-block" else name).search(text)
    return found[0] if found else None


def desk_count_errors(root):
    """The desk is the whole of the active season's README; no README carries a desk block."""
    root = Path(root).resolve()
    home = SeasonPaths(int(repository_map(root)["active_season"]), root).desk
    errors = []
    for readme in _readmes(root):
        count = readme.read_text(encoding="utf-8").count("<!-- desk:begin")
        if count:
            errors.append("Career view desk block found: %s has %d; the desk is the whole of %s"
                          % (readme.relative_to(root).as_posix(), count, home.relative_to(root).as_posix()))
    return errors


def check(root):
    root = Path(root).resolve()
    errors = desk_count_errors(root)
    try:
        expected, names, problems = _render(root)
    except (OSError, ValueError, KeyError, IndexError, TypeError, NotImplementedError) as exc:
        return errors + ["Career views cannot render: %s" % exc]
    errors += problems
    for path, text in expected.items():
        actual = path.read_text(encoding="utf-8") if path.is_file() else ""
        whole = [n for n in names.get(path, ()) if n in WHOLE]
        if whole:
            rel_path = path.relative_to(root).as_posix()
            errors += page_errors(rel_path, text, (), root)
        if actual != text:
            stale = whole or [n for n in names.get(path, ()) if _section(actual, n) != _section(text, n)] or ["text"]
            errors.append("Stale career view: %s (%s); run python scripts/render_career_views.py"
                          % (path.relative_to(root).as_posix(), ", ".join(stale)))
    return errors


def paused_games(root):
    """Every paused Jacksonville game record of the active season: regular
    season, postseason and preseason."""
    paths = SeasonPaths(int(repository_map(root)["active_season"]), root)
    records = [paths.paused_game(week, post) for week in range(1, 22 if paths.year < 2021 else 23)
               for post in (False, True)]
    records += [paths.paused_game(game, preseason=True) for game in range(1, 6)]
    return [p for p in records if decision_queue._paused(p)]


def write(root):
    """Write every stale managed file; refused while a game is paused."""
    root = Path(root).resolve()
    paused = paused_games(root)
    if paused:
        raise Paused("A Jacksonville game is paused (%s); Document 5, the job record and the queue must not change "
                     "until it closes" % paused[0].relative_to(root).as_posix())
    expected, _, problems = _render(root)
    if problems:
        raise ValueError("; ".join(problems))
    written = []
    for path, text in expected.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="report stale views without writing")
    args = parser.parse_args()
    if args.check:
        errors = check(ROOT)
        print("\n".join(errors) if errors else "CAREER VIEWS CURRENT")
        return 1 if errors else 0
    try:
        written = write(ROOT)
    except Paused as exc:
        print("CAREER VIEWS BLOCKED: %s" % exc)
        return 1
    except (OSError, ValueError, KeyError, IndexError, TypeError, NotImplementedError) as exc:
        print("Career views cannot render: %s" % exc)
        return 1
    print("\n".join("wrote " + p.relative_to(ROOT).as_posix() for p in written) or "CAREER VIEWS CURRENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
