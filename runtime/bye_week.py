"""The bye week: its open period, Stone's My Adjustments and the Bye Week Report's checks (rebuild
step 5, C3; docs/bye_week.md, sections 3 to 7; the templates in foundation/templates/bye_week/).

A bye is a regular-season week between the club's first and last game in which it does not play. It
is the open period (``active_bye``) from the close of the club's game before it until the bye's own
close event is recorded on its Bye Week Report (``bye_closed``): while it is open no game week is open,
so the next game's briefing and items wait for the bye's close, and the other clubs' games of the
week close as usual (the bye's ``bye_adjustments`` item holds only the bye's own close).

My Adjustments (``ADJ_SECTIONS``) is Stone's page: the template's fixed headings and lines, in
ordinary football language. ``compile_adjustments`` reads only what each line commits to, so the same
decision in other words compiles to the same record: each direction's parts as keep, correct, reduce,
remove, test or defer (or "No change", a full answer), the calls he names in quotation marks (held to
the active books, runtime/offensive_words.py and runtime/defensive_calls.py), the players he names
(held to the roster and coach records), the immediate role or depth changes in the Game Plan's own
forms (each player medically available), his recommendation to the general manager (recorded as his
recommendation, never a transaction), and the bye's work and the players' days off of section 6, which
are the bye's schedule and are checked against the four-day break and the padded-practice budget
(runtime/practices.check_schedule). Nothing is defaulted and nothing is assumed: no medical clearance,
no install, no transaction. ``report_errors`` holds the staff's Bye Week Report to the records.

The career layer (tests/test_career_layer_isolation.py, LAYER): nothing that resolves a game imports
this module.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re

from . import current_job, decisions, open_events, practices
from .events import EVENT_META
from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
JAX = "Jacksonville Jaguars"
CLASS = "bye_adjustments"
APPLIED_SCHEMA = "bye-adjustments-v1"
APPLIED_ABOUT = ("Stone's My Adjustments for the bye as applied: the page's digest and date, and the choices compiled "
                 "from it (each area's keep, correct, reduce, remove, test or defer parts, the calls and players "
                 "named, the immediate role or depth changes, his recommendation to the general manager, the bye's "
                 "work and days off, which are the bye's schedule, and what carries into the next game week). "
                 "Written only by scripts/apply_bye_adjustments.py; validation holds the page to its digest.")


# ------------------------------------------------------------------ the bye and its period
def club_fixtures(season, root=ROOT):
    return open_events.club_fixtures(season, root)


def byes(season, root=ROOT):
    """The club's bye weeks of the regular season, in order."""
    weeks = {int(g["week"]) for g in club_fixtures(season, root)}
    return [w for w in range(min(weeks) + 1, max(weeks)) if w not in weeks] if weeks else []


def around(season, week, root=ROOT):
    """(the club's game before the bye, its game after it), fixtures or None."""
    games = club_fixtures(season, root)
    before = [g for g in games if int(g["week"]) < week]
    after = [g for g in games if int(g["week"]) > week]
    return (max(before, key=lambda g: int(g["week"])) if before else None,
            min(after, key=lambda g: int(g["week"])) if after else None)


def dates(season, week, root=ROOT):
    """(Monday, Sunday) of the bye week: the day after the game before it to the league week's Sunday."""
    return practices.week_span(season, week, root)


def close_id(season, week, root=ROOT):
    """The event-record id of the bye's close: its Sunday and the week ("2014-11-16-week-11-bye-closed")."""
    _, last = dates(season, week, root)
    return "%s-week-%d-bye-closed" % (last.isoformat(), week)


def report_events(path):
    """The event-record lines of a page, by id."""
    if not Path(path).is_file():
        return {}
    out = {}
    for raw in EVENT_META.findall(Path(path).read_text(encoding="utf-8")):
        data = json.loads(raw)
        out[data.get("id")] = data
    return out


def bye_closed(paths, root=ROOT, week=None):
    """Whether the bye's close is recorded: its close event-record line on its Bye Week Report. With
    no week named, whether every bye of the season has closed."""
    root = Path(root)
    season = paths.year
    weeks = [week] if week is not None else byes(season, root)
    if not weeks:
        return False
    return all(close_id(season, w, root) in report_events(decisions.bye_pages(season, w, root).report) for w in weeks)


def active_bye(paths, root=ROOT):
    """The bye week while it is the open period (from the close of the club's game before it until
    the bye's own close), else None. Games close in order, so the bye opens once that game's result
    is recorded."""
    from .week_inputs import receipt_name
    root = Path(root)
    season = paths.year
    for week in byes(season, root):
        before, _ = around(season, week, root)
        if before is None or not (paths.receipts / receipt_name(before)).is_file():
            return None
        if not bye_closed(paths, root, week):
            return week
    return None


def bye_item_id(season, week):
    return "%d-w%02d-bye-adjustments" % (season, week)


def bye_item(queue, season, week):
    """The bye's adjustments item (class ``bye_adjustments``, holding the bye's close), or None."""
    return next((i for i in queue["items"] if i.get("class") == CLASS and any(
        b.get("kind") == "bye_close" and b.get("season") == season and b.get("week") == week
        for b in i.get("blocks") or ())), None)


def long_day(value, year=False):
    value = value if isinstance(value, dt.date) else dt.date.fromisoformat(value)
    text = "%s, %s %d" % (value.strftime("%A"), value.strftime("%B"), value.day)
    return text + (", %d" % value.year if year else "")


# ------------------------------------------------------------------ My Adjustments: the fixed page
HEADER = (("head_coach", "Head coach"), ("bye", "Bye"), ("briefing", "Briefing answered"),
          ("approach", "Current approach"))
CONTINGENCY = re.compile(r"^If the medical staff does not clear .+$")
CONTINGENCY_LABEL = "If the medical staff does not clear a player"


def sections(job=None, on=None):
    """The page's fixed headings and lines: [(heading, [(key, label)])]. The special-teams and general
    manager lines name the coach who prepares the special teams on ``on`` and the general manager on
    the job record, as the template does."""
    job = job or {}
    st = surname(_preparer(job, "special_teams", on)) or "the special-teams coordinator"
    gm = surname(current_job.party_name(job, "caldwell") if (job.get("parties") or {}).get("caldwell") else None) \
        or "the general manager"
    return [
        ("1. What I think we should keep and change",
         [("keep", "Keep"), ("correction", "Highest-priority correction"), ("not_add", "What I will not add"),
          ("ready", "How I will know if a change is ready")]),
        ("2. Offense", [("offense", "Direction"), ("offense_why", "Why"), ("offense_owner", "Who owns the work"),
                        ("offense_shown", "What must be shown before it is used more"), ("offense_fallback", "Fallback")]),
        ("3. Defense", [("defense", "Direction"), ("defense_why", "Why"), ("defense_owner", "Who owns the work"),
                        ("defense_check", "What must be checked"), ("defense_fallback", "Fallback")]),
        ("4. Special teams", [("special_teams", "Direction to %s" % st), ("st_reason", "Reason"),
                              ("st_evaluation", "Evaluation")]),
        ("5. Personnel and medical contingencies",
         [("roles", "Actual eligible role/depth decisions"), ("if_not_cleared", CONTINGENCY_LABEL),
          ("recommendation", "Any recommendation to %s" % gm),
          ("development", "Development/evaluation opportunities")]),
        ("6. Work calendar and player time off",
         [("days_off", "Mandatory consecutive player days off"), ("staff_work", "Staff self-scout work"),
          ("player_work", "Permitted player work before/after rest"), ("test", "What we will actually test"),
          ("removed", "What work is removed to make room"), ("medical", "Medical limits")]),
        ("7. What carries into the next game week",
         [("durable", "Durable coaching changes I am making now"),
          ("ideas", "Ideas for the next opponent, not yet a frozen game plan"),
          ("retained", "Instructions that stay in force"), ("open_issues", "Open issues that still require my answer"),
          ("finished", "I have finished the bye-week decisions")]),
    ]


def surname(name):
    return name.split()[-1] if name else None


def _preparer(job, phase, on=None):
    """The coach who prepares a phase on ``on`` (the master date by default): its caller, or, when
    Stone calls it, the coach who prepares it; None when the job record names none."""
    if on is None:
        from .player_bios import master_date
        on = master_date(ROOT)
    interval = current_job.interval_on(job, phase, on) if job else None
    if not interval:
        return None
    holder = job.get("holder")
    who = interval.get("prepares") if interval.get("caller") == holder else interval.get("caller")
    return current_job.party_name(job, who) if who and who != holder else None


def blank_page(title, header_values, job=None, on=None):
    """My Adjustments with its fixed headings and lines and nothing answered (the template's fill-in
    guide left out): ``header_values`` fills the header lines the staff knows (the head coach, the bye)."""
    out = ["# %s" % title, ""]
    header = []
    for key, label in HEADER:
        value = header_values.get(key, "")
        header.append(("**%s:** %s" % (label, value)).rstrip())
    out += [line + "  " for line in header[:-1]] + header[-1:] + [""]
    for heading, lines in sections(job, on):
        out += ["## %s" % heading, ""]
        for _, label in lines:
            out += ["**%s:**" % label, ""]
    return "\n".join(out).rstrip("\n") + "\n"


LABELLED = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*)$")


class Field:
    def __init__(self, key, label, text, line):
        self.key, self.label, self.text, self.line = key, label, text, line


def parse(text, job=None, on=None):
    """({key: Field}, problems): the page's lines under its exact headings. A line's answer runs on in
    the lines below its label until the next label or heading."""
    wanted = sections(job, on)
    by_heading = {h: lines for h, lines in wanted}
    fields, problems, current, section = {}, [], None, None
    found = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if raw.startswith("# ") or line.startswith(">") or not line and current is None:
            continue
        if raw.startswith("## "):
            name = raw[3:].strip()
            if name not in by_heading:
                problems.append("The page has a heading %r that is not one of My Adjustments' headings" % name)
                section, current = None, None
                continue
            if name in found:
                problems.append("%s: the heading appears twice" % name)
            found.append(name)
            section, current = name, None
            continue
        m = LABELLED.match(line)
        if m:
            label, value = m[1].strip(), m[2].strip()
            if section is None:
                key = next((k for k, l in HEADER if l == label), None)
            else:
                key = next((k for k, l in by_heading[section] if l == label or (
                    k == "if_not_cleared" and CONTINGENCY.match(label))), None)
            if key is None:
                problems.append("%s: %r is not one of its lines" % (section or "The page's header", label))
                current = None
                continue
            if key in fields:
                problems.append("%s: the line %r appears twice" % (section or "The page's header", label))
            fields[key] = Field(key, label, value, number)
            current = key
            continue
        if current is not None and line:
            f = fields[current]
            f.text = (f.text + "\n" + line).strip()
        elif line:
            problems.append("%s: %r is not on a line of its own label; write it after the label it answers"
                            % (section or "The page's header", line[:80]))
    for heading, lines in wanted:
        if heading not in found:
            problems.append("%s: the heading is missing" % heading)
            continue
        for key, label in lines:
            if key not in fields:
                problems.append("%s: the line %r is missing" % (heading, label))
    for key, label in HEADER:
        if key not in fields:
            problems.append("The page's header: the line %r is missing" % label)
    order = [h for h, _ in wanted]
    if [h for h in found if h in order] != [h for h in order if h in found]:
        problems.append("The headings are out of order; keep the page's order")
    return fields, problems


# ------------------------------------------------------------------ what a line commits to
KINDS = ("keep", "correct", "reduce", "remove", "test", "defer")
KIND_WORDS = {"keep": ("keep", "retain", "continue"), "correct": ("correct", "fix"),
              "reduce": ("reduce", "cut back", "limit"), "remove": ("remove", "drop", "stop"),
              "test": ("test", "try", "evaluate"), "defer": ("defer", "postpone", "hold off on")}
LEAD = re.compile(r"^(?:(?:we|i)(?:\s+will|'ll)?\s+)?", re.I)
NO_CHANGE = re.compile(r"^(?:no change|no changes|none|same as current|current system unchanged|no specific change|"
                       r"carry current menu|carry current response|no new evaluation|no new requirement|"
                       r"no additional restriction|no new test|no recommendation|no additional adjustment)\.?$", re.I)
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")
INSTALLED = re.compile(r"\binstall(?:ed|ing)?\b", re.I)
CLEARED = re.compile(r"\b(?:is|are|was|were|been|now|as|gets?|being)\s+(?:medically\s+|fully\s+)?cleared\b", re.I)
ORDER_WORDS = re.compile(r"^(?:sign|release|waive|cut|trade|claim|promote|activate|place|elevate|acquire)\b", re.I)
RECOMMEND = re.compile(r"^(?:i\s+)?recommend(?:s|ed)?\b", re.I)
YES = re.compile(r"^yes\b", re.I)
NO = re.compile(r"^no\b", re.I)
DIRECTIONS = ("offense", "defense", "special_teams")
AREA_WORDS = {"offense": "Offense", "defense": "Defense", "special_teams": "Special teams"}
FREE = ("keep", "correction", "not_add", "ready", "offense_why", "offense_owner", "offense_shown", "offense_fallback",
        "defense_why", "defense_owner", "defense_check", "defense_fallback", "st_reason", "st_evaluation",
        "if_not_cleared", "development", "staff_work", "test", "removed", "medical", "durable", "ideas", "retained",
        "open_issues", "approach")
INSTALL_MESSAGE = ("You marked a new coverage adjustment 'installed' but no legal installed or practiced call has been "
                   "identified. Mark it 'study/test only' or settle the additional coaching and install decision.")
CLEARED_MESSAGE = ("Your role change names a player who has not been medically cleared for the assignment. Record a "
                   "conditional option or wait for the staff's medical determination.")


def _norm(text):
    return re.sub(r"\s+", " ", str(text or "").strip()).rstrip(".")


def _kind(clause):
    """(kind, rest) of a direction's part: its leading keep, correct, reduce, remove, test or defer word."""
    text = LEAD.sub("", clause.strip(), count=1)
    for kind in KINDS:
        for word in KIND_WORDS[kind]:
            m = re.match(r"^%s\b[\s:,-]*" % re.escape(word), text, re.I)
            if m:
                return kind, text[m.end():]
    return None, text


class Context:
    """What the compiler checks names and calls against: the roster's players (and their medical
    notes), the coach and party names, the clubs, and the active books."""

    def __init__(self, season, root=ROOT):
        from . import roster as roster_record
        self.season, self.root = season, Path(root)
        paths = SeasonPaths(season, self.root)
        self.paths = paths
        roster = roster_record.load(paths.roster)
        self.players = {p["name"]: p for p in roster.get("players") or ()}
        self.job = current_job.load(self.root)
        names = set(self.players)
        for record in (self.root / "data/people/coaches").glob("*.json"):
            try:
                names.add(json.loads(record.read_text(encoding="utf-8"))["name"])
            except (OSError, ValueError, KeyError):
                continue
        names |= {p.get("name") for p in (self.job.get("parties") or {}).values() if p.get("name")}
        for game in paths.regular_games():
            for club in (game["away"], game["home"]):
                names |= {club, club.rsplit(" ", 1)[0], club.rsplit(" ", 1)[-1]}
        self.names = {n for n in names if n}
        from .defensive_calls import active_defensive_book
        book = active_defensive_book(self.root)
        self.defensive_text = (self.root / book).read_text(encoding="utf-8") if book else ""

    def call_problem(self, call):
        """Why a quoted call is not a call or term of the active books, or None."""
        from . import offensive_words
        from .defensive_calls import _occurs
        if not offensive_words.call_errors({"name": call}, list(self.players)):
            return None
        if self.defensive_text and _occurs(call, self.defensive_text):
            return None
        return ("%r is not a call or term of the active playbooks; name a call from the active offensive or defensive "
                "book, in quotation marks" % call)

    def players_in(self, text):
        return sorted(p for p in self.players if re.search(r"(?<![\w'-])%s(?![\w'-])" % re.escape(p), text))


WORD = r"[A-Z](?:(?:\.[A-Z])+\.|[a-zA-Z'-]*)"
NAME_RUN = re.compile(r"\b%s(?: %s)+" % (WORD, WORD))
NOT_NAMES = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
             "ET", "I", "We", "My", "Our", "The", "If", "Only", "Keep", "Correct", "Reduce", "Remove", "Test", "Defer",
             "No", "None", "Week", "Recommend", "Carry", "Current", "Same", "Yes"}


def unknown_names(text, ctx):
    """The two-word capitalized names in ``text`` that are neither a roster player, a coach or party,
    nor a club (words in quotation marks are calls, checked apart)."""
    text = QUOTED.sub(" ", text)
    out = []
    for run in NAME_RUN.findall(text):
        words = run.split()
        while words and words[0] in NOT_NAMES:
            words = words[1:]
        while words and words[-1] in NOT_NAMES:
            words = words[:-1]
        if len(words) < 2:
            continue
        name = " ".join(words)
        if not any(name == k or name in k or k in name for k in ctx.names):
            out.append(name)
    return out


def _line_substance(text, ctx, where, problems):
    """What a free line commits to: none ("No change" and its like), or the calls and players it
    names; the words stay on his page."""
    value = _norm(text)
    calls = sorted({_norm(c) for c in QUOTED.findall(text)})
    for call in calls:
        problem = ctx.call_problem(call)
        if problem:
            problems.append("%s: %s" % (where, problem))
    for name in unknown_names(text, ctx):
        problems.append("%s: %s is not on the roster or the coach records" % (where, name))
    if CLEARED.search(text) and where.split(", ")[-1] != CONTINGENCY_LABEL:
        problems.append("%s: no medical clearance is assumed on this page; the medical staff's dated determination "
                        "clears a player" % where)
    return {"none": bool(NO_CHANGE.match(value)), "calls": calls, "players": ctx.players_in(text)}


def _direction(text, ctx, where, problems):
    """A direction: "No change", or parts separated by semicolons, each led by keep, correct, reduce,
    remove, test or defer."""
    value = _norm(text)
    if NO_CHANGE.match(value):
        return {"no_change": True, "parts": []}
    parts = []
    for clause in [c.strip() for c in re.split(r";|\n", text) if c.strip()]:
        kind, rest = _kind(clause)
        if kind is None:
            problems.append("%s: %r does not say whether to keep, correct, reduce, remove, test or defer; write No "
                            "change, or start each part with one of them" % (where, clause[:80]))
            continue
        if INSTALLED.search(clause):
            problems.append("%s: %s" % (where, INSTALL_MESSAGE))
            continue
        found = _line_substance(rest, ctx, where, problems)
        parts.append({"kind": kind, "calls": found["calls"], "players": found["players"]})
    if not parts and not problems:
        problems.append("%s: write No change, or what to keep, correct, reduce, remove, test or defer" % where)
    parts.sort(key=lambda p: (KINDS.index(p["kind"]), p["calls"], p["players"]))
    return {"no_change": False, "parts": parts}


def _roles(text, ctx, chart, on, where, problems):
    """The immediate role or depth changes, in the Game Plan's own forms, each player on the active
    roster and medically available on ``on``; "none" for No change."""
    from . import game_plan
    value = _norm(text)
    if NO_CHANGE.match(value):
        return "none"
    found = []
    read = game_plan.READERS["depth"]("depth", game_plan.Field("depth", 0, text.replace("\n", "; "), where), found)
    problems += ["%s: %s" % (where, p.split(": ", 1)[-1]) for p in found]
    if read is None or read == "none" or found:
        return read
    from types import SimpleNamespace
    from scripts.check_game_plan import depth_problems
    problems += ["%s: %s" % (where, p.split(": ", 1)[-1]) for p in
                 depth_problems(SimpleNamespace(choices={"depth": read}, chart=chart))]
    from .week_inputs import roster_available
    named = list((read.get("roles") or {}).values())
    for name in named:
        row = ctx.players.get(name)
        if row is None or row.get("list") != "active":
            problems.append("%s: %s is not on the active roster" % (where, name))
            continue
        note = row.get("availability") or ""
        try:
            fit = note.startswith("No communicated restriction") or roster_available(note, on, ctx.season)
        except ValueError:
            fit = False
        if not fit:
            problems.append("%s: %s" % (where, CLEARED_MESSAGE))
    return read


DATE = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
                  r"\s+(\d{1,2})\b")


def _days_off(text, season, week, root, where, problems):
    """The players' days off of the bye: a run of dates ("Thursday, November 13 to Sunday, November
    16", "November 13 to 16") or the days by name, each a day of the bye week."""
    first, last = dates(season, week, root)
    span = [first + dt.timedelta(days=n) for n in range((last - first).days + 1)]
    value = _norm(text)
    month = lambda name: practices.MONTH_NAMES.index(name) + 1
    short = re.search(r"\b(%s)\s+(\d{1,2})\s*(?:to|through|-|\u2013)\s*(\d{1,2})\b" % "|".join(practices.MONTH_NAMES),
                      value)
    found = [dt.date(first.year, month(m[1]), int(m[2])) for m in DATE.finditer(value)]
    if short:
        start, end = dt.date(first.year, month(short[1]), int(short[2])), dt.date(first.year, month(short[1]),
                                                                                    int(short[3]))
        days = [start + dt.timedelta(days=n) for n in range((end - start).days + 1)]
    elif len(found) == 2 and re.search(r"\b(?:to|through)\b|\u2013", value):
        start, end = found
        days = [start + dt.timedelta(days=n) for n in range((end - start).days + 1)]
    elif found:
        days = found
    else:
        names = re.findall(r"\b(%s)\b" % "|".join(practices.WEEKDAYS), value)
        days = [d for d in span if d.strftime("%A") in names]
    if not days:
        problems.append("%s: write the players' days off as dates, as \"Thursday, November 13 to Sunday, November 16\""
                        % where)
        return []
    for day in days:
        if day not in span:
            problems.append("%s: %s is outside the bye week (%s to %s)" % (where, long_day(day), long_day(first),
                                                                           long_day(last)))
    return [{"date": d.isoformat(), "scope": "players", "players": "all", "exceptions": []} for d in days if d in span]


NO_WORK = re.compile(r"^no (?:on-field )?player work(?: during the bye)?\.?$|^none\.?$", re.I)


def compile_adjustments(text, season, week, root=ROOT, ctx=None, chart=None, on=None):
    """(compiled, problems): My Adjustments read into what it commits to, the same decisions in other
    words giving the same bytes; every problem in football words (docs/bye_week.md section 6). The
    bye's schedule (section 6) is checked against the four-day break and the padded budget the closed
    records leave (runtime/practices.check_schedule)."""
    root = Path(root)
    ctx = ctx or Context(season, root)
    paths = SeasonPaths(season, root)
    chart = chart if chart is not None else json.loads(paths.depth_chart.read_text(encoding="utf-8"))
    if on is None:
        from .player_bios import master_date
        on = master_date(root)
    fields, problems = parse(text, ctx.job, on)
    if problems:
        return None, problems
    where = {k: ("%s, %s" % (h.split(". ", 1)[1], l)) for h, lines in sections(ctx.job, on) for k, l in lines}
    where.update({k: l for k, l in HEADER})
    for key, f in fields.items():
        if key not in ("head_coach", "bye") and not f.text.strip():
            problems.append("%s: unanswered; write your answer, or No change where nothing changes" % where[key])
    if problems:
        return None, problems
    out = {"schema": APPLIED_SCHEMA, "season": season, "week": week}
    out["briefing"] = _norm(fields["briefing"].text)
    out["approach"] = _line_substance(fields["approach"].text, ctx, where["approach"], problems)
    out["areas"] = {area: _direction(fields[area].text, ctx, where[area], problems) for area in DIRECTIONS}
    out["lines"] = {key: _line_substance(fields[key].text, ctx, where[key], problems)
                    for key in FREE if key in fields and key != "approach"}
    out["roles"] = _roles(fields["roles"].text, ctx, chart, on, where["roles"], problems)
    rec = _norm(fields["recommendation"].text)
    if NO_CHANGE.match(rec):
        out["recommendation"] = None
    elif RECOMMEND.match(rec):
        found = _line_substance(fields["recommendation"].text, ctx, where["recommendation"], problems)
        out["recommendation"] = {"players": found["players"], "calls": found["calls"]}
    else:
        problems.append("%s: write No recommendation, or Recommend and the football need; %s decides transactions, "
                        "so this page orders none" % (where["recommendation"],
                                                      current_job.party_name(ctx.job, "caldwell")))
    off = _days_off(fields["days_off"].text, season, week, root, where["days_off"], problems)
    work = fields["player_work"].text
    sessions = []
    if not NO_WORK.match(_norm(work)):
        compiled, found = practices.compile_answer(work, season, week, root)
        problems += ["%s: %s" % (where["player_work"], p) for p in found]
        sessions = compiled["sessions"]
        off_named = [d for d in compiled["days_off"] if d["date"] not in {o["date"] for o in off}]
        off = sorted(off + off_named, key=lambda d: d["date"])
    out["schedule"] = {"sessions": sessions, "days_off": off}
    finished = _norm(fields["finished"].text)
    if YES.match(finished):
        out["finished"] = True
    elif NO.match(finished):
        out["finished"] = False
    else:
        problems.append("%s: write Yes once every decision is explicit and legal, or No" % where["finished"])
    if not problems:
        earlier = {w: r for w, r in practices.records(season, root).items() if w < week}
        problems += practices.check_schedule(season, week, sessions, off, root, earlier)
    return (out if not problems else None), problems


def compiled_bytes(compiled):
    return (json.dumps(compiled, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def page_sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def applied_record(season, week, root=ROOT):
    path = decisions.bye_pages(season, week, root).applied
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def applied_schedule(season, week, root=ROOT):
    """The bye's schedule as Stone's applied My Adjustments sets it (its work and days off), with where
    it was given and its digest, or None before the apply."""
    applied = applied_record(season, week, root)
    if applied is None:
        return None
    schedule = applied["choices"]["schedule"]
    page = decisions.bye_pages(season, week, root).adjustments.relative_to(Path(root).resolve()).as_posix()
    return {"sessions": [dict(s) for s in schedule["sessions"]], "days_off": [dict(d) for d in schedule["days_off"]],
            "source": {"page": page, "heading": "6. Work calendar and player time off"},
            "sha256": practices.schedule_digest(schedule)}


# ------------------------------------------------------------------ the Bye Week Report
REPORT_HEADINGS = ("1. What the staff established", "2. Work that actually occurred",
                   "3. Stone's adjustments and what changed", "4. Personnel and availability after the bye",
                   "5. League context and the next opponent", "6. Carry-forward and week closure")
RECORD_LINE = "**Record entering and leaving the bye:**"
ADJUSTMENT_HEAD = "| Decision | Ordered by Stone | Actually completed or adopted | Still subject to a later check |"
BOX_SCORE = re.compile(r"<!-- box-score|^#+ .*box score", re.I | re.M)


def record_words(season, week, root=ROOT):
    """The club's record through its game before the bye, from the closed games ("6-4")."""
    from .week_inputs import receipt_name
    paths = SeasonPaths(season, root)
    w = l = t = 0
    for game in club_fixtures(season, root):
        if int(game["week"]) >= week:
            continue
        path = paths.receipts / receipt_name(game)
        if not path.is_file():
            continue
        receipt = json.loads(path.read_text(encoding="utf-8"))
        other = receipt["away"] if receipt["home"] == JAX else receipt["home"]
        mine, theirs = receipt["final_score"][JAX], receipt["final_score"][other]
        w, l, t = w + (mine > theirs), l + (mine < theirs), t + (mine == theirs)
    return "%d-%d" % (w, l) + ("-%d" % t if t else "")


def adjustment_rows(applied, root=ROOT):
    """The rows of section 3 that the applied adjustments fix: each area's direction and the role or
    depth decision, each with Stone's order as written on the applied page (the staff fills what was
    completed and what is still to be checked)."""
    root = Path(root)
    page = root / applied["page"]
    job = current_job.load(root)
    on = dt.date.fromisoformat(applied["date"])
    fields, _ = parse(page.read_text(encoding="utf-8"), job, on) if page.is_file() else ({}, [])
    words = lambda key: re.sub(r"\s*\n\s*", "; ", fields[key].text.strip()).replace("|", "/") if key in fields \
        else "Not recorded"
    rows = [(AREA_WORDS[area], words(area)) for area in DIRECTIONS]
    rows.append(("Role and depth", words("roles")))
    return rows


def _section(text, heading):
    lines = text.split("\n")
    try:
        start = lines.index("## " + heading)
    except ValueError:
        return None
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:end])


def report_errors(season, week, root=ROOT, results=None):
    """The staff's Bye Week Report against the records (the lead wires this into repository validation
    once the report exists): the template's headings in order; the club's record stated as the closed
    games give it and no Jacksonville game of the week; no box score; the practice table of section 2
    the bye's practice record as recorded; each applied adjustment in section 3 as it was applied, and
    no session held before the apply reported as run under it; each result of the bye linked and none
    pasted; the page clean. [] when it holds."""
    from .clean_pages import page_errors
    from .week_inputs import receipt_name
    root = Path(root).resolve()
    pages = decisions.bye_pages(season, week, root)
    rel = pages.report.relative_to(root).as_posix()
    label = "Week %d Bye Week Report" % week
    if not pages.report.is_file():
        return ["%s: the report is not written (%s)" % (label, rel)]
    text = pages.report.read_text(encoding="utf-8")
    errors = ["%s: %s" % (label, e.split(": ", 1)[-1]) for e in page_errors(rel, text, root=root)]
    found = [l[3:].strip() for l in text.split("\n") if l.startswith("## ")]
    if found != list(REPORT_HEADINGS):
        errors.append("%s: the headings must be the template's, in order (%s)" % (label, "; ".join(REPORT_HEADINGS)))
    paths = SeasonPaths(season, root)
    ours = [g for g in paths.regular_games() if int(g["week"]) == week and JAX in (g["away"], g["home"])]
    if ours or any(JAX in json.loads(p.read_text(encoding="utf-8")).get("matchup", "")
                   for p in paths.receipts.glob("week_%02d_*.json" % week)):
        errors.append("%s: Jacksonville has a game recorded in its bye week" % label)
    record = record_words(season, week, root)
    line = next((l for l in text.split("\n") if l.startswith(RECORD_LINE)), None)
    if line is None or not re.search(r"(?<![\d-])%s(?![\d-])" % re.escape(record), line) or \
            len(set(re.findall(r"\b\d{1,2}-\d{1,2}(?:-\d)?\b", line))) != 1:
        errors.append("%s: the record line must state the club's record through its last game, %s, unchanged "
                      "through the bye" % (label, record))
    if BOX_SCORE.search(text):
        errors.append("%s: a bye has no box score" % label)
    for heading in REPORT_HEADINGS:
        if "To come." in (_section(text, heading) or ""):
            errors.append("%s: section %s is not written yet (it says To come); the staff writes the report after "
                          "the work" % (label, heading.split(".", 1)[0]))
    from . import roster as roster_record
    active = [p["name"] for p in roster_record.players(roster_record.load(paths.roster), ("active",))]
    if active and all(name in text for name in active):
        errors.append("%s: the report repeats the whole roster; name only the players the work concerns" % label)
    work = _section(text, REPORT_HEADINGS[1]) or ""
    log = practices.load(season, week, root)
    table = practices.render_table(log)
    if not table:
        errors.append("%s: the bye's practice record is not recorded; record what was held before the report" % label)
    elif table.strip() not in work:
        errors.append("%s: section 2's practice table is not the bye's practice record as recorded" % label)
    applied = applied_record(season, week, root)
    adjust = _section(text, REPORT_HEADINGS[2]) or ""
    if applied is None:
        errors.append("%s: My Adjustments has not been applied; the report records only what Stone ordered" % label)
    else:
        rows = [r for r in adjust.split("\n") if r.startswith("| ") and not r.startswith(("| Decision", "|---", "| ---"))]
        cells = [[c.strip() for c in r.strip()[1:-1].split("|")] for r in rows]
        expected = adjustment_rows(applied, root)
        if ADJUSTMENT_HEAD not in adjust or [tuple(c[:2]) for c in cells] != expected:
            errors.append("%s: section 3's table must list each applied adjustment as it was applied, in order: %s"
                          % (label, "; ".join("%s (%s)" % row for row in expected)))
        applied_on = dt.date.fromisoformat(applied["date"])
        for c in cells:
            for m in DATE.finditer(" ".join(c[2:])):
                when = dt.date(season, practices.MONTH_NAMES.index(m[1]) + 1, int(m[2]))
                if when < applied_on:
                    errors.append("%s: section 3 reports work of %s under the adjustments, which were applied %s; a "
                                  "session held before the apply was not run under them"
                                  % (label, long_day(when), long_day(applied_on)))
    errors += ["%s: %s" % (label, e) for e in result_link_errors(text, rel, root,
                                                               results if results is not None else
                                                               open_events.period_events(season, {"bye": week}, root)[0])]
    return errors


def result_link_errors(text, rel, root, results):
    """Each result of the bye linked from the report and none of its words pasted: the one rule the
    Game Report keeps (runtime/game_report.result_link_errors), held to the report's own path."""
    from .game_report import result_link_errors as shared
    return shared(text, results, report_rel=rel, label="Bye Week Report")


def validation_errors(root=ROOT):
    """The active season's bye records (the lead wires this into repository validation): each applied
    My Adjustments page held to its digest, and once a bye has closed its report and practice record
    valid."""
    from .seasons import active_season
    root = Path(root).resolve()
    season = active_season(root)
    paths = SeasonPaths(season, root)
    errors = []
    for week in byes(season, root):
        pages = decisions.bye_pages(season, week, root)
        applied = applied_record(season, week, root)
        if applied is not None:
            if not pages.adjustments.is_file() or page_sha256(pages.adjustments.read_text(encoding="utf-8")) \
                    != applied.get("page_sha256"):
                errors.append("Week %d My Adjustments differs from the page applied on %s; an applied page stays as "
                              "written" % (week, applied.get("date")))
        if bye_closed(paths, root, week):
            errors += report_errors(season, week, root)
            if practices.load(season, week, root) is None:
                errors.append("The Week %d bye has closed without its practice record" % week)
    return errors
