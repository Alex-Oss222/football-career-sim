"""The open-event store and the clock inside a week (rebuild step 5: docs/rebuild_plan.md, step 5;
docs/event_inserts.md, sections A to C).

An event inside a week or phase (an injury replacement, a trade call, another club's head-coach
change) is one JSON record (``open-event-v1``) in its owner's event store, the data-area twin of its
owner folder (runtime/decisions.event_store), from the moment it is raised: one file per event,
named by its id. The record keeps its dated process (each call, set of terms, counter, criteria,
response, the other side's act, a medical entry, the decision), appended only, and once it resolves
its resolution and its one result page, which carries the event's id on its event-record line so
the year's Record.md lists it. A live negotiation keeps its process entries and gets no result.

Nothing here invents an event. ``raise_event`` records one only from a sourced record (and
scripts/raise_event.py is the one way in); no code here generates a call, an offer, a salary, an
interest or a market price, and opening or building a page never creates an event or moves time.
Silence is never yes or no: an item past its due time is reported overdue, never resolved.

The clock. Document 5's master date is a date with no time (runtime/player_bios.master_date). Three
forms of the master-date line are read here (``master_clock``):

- on game day, before kickoff ("..., after the game-day clock advance for Week 6 at Tennessee"):
  the start of the date;
- after the game ("..., after the Week 6 game at Tennessee (...)"): the game's kickoff;
- the mid-week record, made between a week's opening and its game day ("October 7, 2014, after the
  10:30 a.m. ET record of the Week 6 preparation (...)"): the date at the time it names.

Any other line reads as the start of its date. That datetime is the floor: the clock is never taken
as later than recorded. A raised, process or resolution time must be at or before it when the line
names a time (the mid-week form), and on or before the master date otherwise; an item is overdue
only once its due time is before it. Every time is an ISO datetime with its ET offset (-04:00 before
the first Sunday of November, -05:00 from it, until the second Sunday of March).

Stamps and windows. Every event, process entry and resolution is stamped when it is written with
``after_issue`` (the period, date and revision of the open period's latest issued brief, or None
before its first) and ``period`` (the open period: ``{"week": N}``, ``{"bye": N}`` or
``{"phase": name}``). Windows are counted by issue, never by game dates (``route``): an issue shows
under FOR YOUR INFORMATION the events resolved since the issue before it (the period's previous
issue, or for a period's first issue the previous period's last issue), so each appears in exactly
one issue, and a brief is rebuilt as of its own issue from the events stamped before it, so a later
event never makes an issued brief stale.

The career layer: this module reads the job record, the decision queue and the event store, so it
is in tests/test_career_layer_isolation.py's LAYER, and nothing that resolves a game imports it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime as dt
import json
from pathlib import Path
import re

from . import current_job, decision_queue, decisions
from .events import EVENT_ID, EVENT_META, load_events, repository_map
from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "open-event-v1"
STATE = Path("state/05_Current_Season_State.md")
STATES = ("open", "answered", "offered", "countered", "agreed_in_principle", "awaiting_conditions", "resolved")
PROCESS_KINDS = ("call", "terms", "counter", "criteria", "response", "withdrawn_by_other_side",
                 "other_side_deadline_passed", "medical", "decision")
# The other side's acts that end a question without Stone's answer (docs/rebuild_plan.md step 5, A1).
OTHER_SIDE_ENDINGS = ("withdrawn_by_other_side", "other_side_deadline_passed", "medical")
# A recorded finding that changes a choice still pending (the one reissue rule, (b)); the criteria,
# Stone's own response, the decision and the other side's endings are not (an ended question is news).
CHANGES = ("call", "terms", "counter", "medical")
OUTCOMES = ("executed", "no_move", "accepted", "rejected", "declined", "withdrawn", "lapsed",
            "ended_without_agreement")
# A decision made by a Jacksonville party other than Stone: its criteria come first.
DECIDED = frozenset({"executed", "no_move", "accepted", "rejected", "declined"})
# How the other side's act or the due time ends an event.
ENDED = frozenset({"withdrawn", "ended_without_agreement", "no_move"})
ANSWERS = ("recommends", "consulted", "decides")       # a part that needs his answer
STONE_PARTS = ANSWERS + ("none",)                       # or "standing:<instruction id>"
OTHER_CLUB = "other_club"
# Stone's answer reduced to what it commits to (docs/rebuild_plan.md step 5, the record's response):
# his reasons stay on his page. "lapse" is his explicit permission to let the due time pass (F10).
SUBSTANCE_KINDS = ("support", "oppose", "recommend", "condition", "lapse")
RECORD_KEYS = ("schema", "id", "kind", "season", "period", "subject", "raised", "known_to", "authority",
               "stone_part", "summary", "staff_position", "consequence", "facts", "options", "deadline", "state",
               "process", "queue_item", "response", "resolution")
OPTIONAL_KEYS = ("staff_position", "consequence", "deadline", "queue_item", "response", "resolution")
# The decision class of Stone's item for an event that needs his answer, by kind and part.
ITEM_CLASS = {("injury_replacement", "recommends"): "personnel_recommendation",
              ("trade_talks", "recommends"): "personnel_recommendation",
              ("trade_talks", "consulted"): "quarterback_consultation"}
# The fact an injury replacement records when the active roster cannot dress a legal team for the
# next game (its value begins "No", its source usage.lineup_errors on the date): only then may its
# items hold that game (decision_queue, the hold rule).
LEGAL_TEAM_FACT = "Legal team for the next game"
# The queue item's summary when the other side ended the question, and when Caldwell decided an
# injury replacement at its due time with no recommendation on file (decision_queue rule 8).
OTHER_SIDE_SUMMARY = "The question ended without his answer"
DUE_TIME_SUMMARY = "decided at the due time with no recommendation on file"
TITLES = {"injury_replacement": "Roster place: %s", "trade_talks": "Trade call from %s",
          "head_coach_change": "%s changes its head coach"}
CLUB = "Jacksonville Jaguars"


class Refused(ValueError):
    """A write the store refuses, in words for the runner (nothing was written)."""


# ------------------------------------------------------------------ times in ET
def _nth_sunday(year, month, n):
    first = dt.date(year, month, 1)
    return first + dt.timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))


def et_offset(day):
    """The ET offset on ``day``: daylight time from the second Sunday of March to the first Sunday of
    November (by date: 2014's -04:00 runs to November 1 and -05:00 starts November 2)."""
    summer = _nth_sunday(day.year, 3, 2) <= day < _nth_sunday(day.year, 11, 1)
    return dt.timezone(dt.timedelta(hours=-4 if summer else -5))


def et(day, hour=0, minute=0):
    """``day`` at hour:minute ET, with its offset."""
    return dt.datetime(day.year, day.month, day.day, hour, minute, tzinfo=et_offset(day))


def parse_at(value):
    """An ISO datetime with its ET offset (2014-10-28T16:00:00-04:00); ValueError for a time with no
    offset, or with an offset that is not ET's on that date."""
    if not isinstance(value, str):
        raise ValueError("a time is an ISO datetime with its ET offset: %r" % (value,))
    at = dt.datetime.fromisoformat(value)
    if at.tzinfo is None or at.utcoffset() != et_offset(at.date()).utcoffset(None):
        raise ValueError("%s does not carry the ET offset of its date (%s)" % (
            value, et(at.date()).isoformat()[-6:]))
    return at


def iso(at):
    return at.isoformat()


def at_text(at, weekday=True):
    """A time as the pages say it: "Wednesday, October 15, 4 p.m. ET" ("10:30 a.m.", "noon")."""
    if at.hour == 12 and at.minute == 0:
        clock = "noon"
    else:
        hour = at.hour % 12 or 12
        clock = "%d%s %s" % (hour, ":%02d" % at.minute if at.minute else "", "a.m." if at.hour < 12 else "p.m.")
    day = "%s %d" % (at.strftime("%B"), at.day)
    return "%s%s, %s ET" % (at.strftime("%A") + ", " if weekday else "", day, clock)


# ------------------------------------------------------------------ the clock
MASTER = re.compile(r"^\| Master date/time \| (.+?) \|\s*$", re.M)
DAY = re.compile(r"^([A-Za-z]+ \d{1,2}, \d{4})")
# The mid-week form: "<date>, after the 10:30 a.m. ET record of ...".
TIMED = re.compile(r"^[A-Za-z]+ \d{1,2}, \d{4}, after the (\d{1,2})(?::(\d{2}))? ([ap])\.m\. ET record of\b")
AFTER_GAME = re.compile(r"^[A-Za-z]+ \d{1,2}, \d{4}, after the Week (\d+) game\b")


@dataclass(frozen=True)
class Clock:
    at: dt.datetime          # the floor: never later than recorded
    date: dt.date            # the master date
    timed: bool              # the line names a time (the mid-week form)
    line: str

    def allows(self, at):
        """Whether ``at`` is at or before the clock (by its time when the line names one, otherwise
        by its date)."""
        return at <= self.at if self.timed else at.date() <= self.date

    def overdue(self, due):
        return due is not None and due < self.at


def club_fixtures(season, root=ROOT, on=None):
    """The employer club's regular-season fixtures, each with the schedule's amendments effective on
    or before ``on`` applied (as the desk applies them)."""
    paths = SeasonPaths(season, root)
    data = json.loads(paths.schedule.read_text(encoding="utf-8"))
    club = employer_club(root)
    changes = {}
    for amendment in data.get("amendments") or ():
        effective = amendment.get("effective")
        if effective and (on is None or dt.date.fromisoformat(effective) <= on):
            changes.setdefault(amendment["game_id"], []).append(amendment["change"])
    out = []
    for game in paths.regular_games():
        if club in (game["away"], game["home"]):
            game = dict(game)
            for change in changes.get(game["game_id"], ()):
                game.update({k: change[k] for k in ("date", "weekday", "kickoff_et", "stadium") if k in change})
            out.append(game)
    return sorted(out, key=lambda g: (g["date"], int(g["week"])))


def kickoff(game):
    """A fixture's kickoff, ET."""
    hour, minute = (int(x) for x in str(game["kickoff_et"]).split(":"))
    return et(dt.date.fromisoformat(game["date"]), hour, minute)


def employer_club(root=ROOT):
    job = current_job.load(root)
    return ((current_job.appointment(job) or {}).get("employer") or {}).get("club") or CLUB


def master_clock(root=ROOT):
    """Document 5's master date/time as the clock (the three forms above)."""
    root = Path(root)
    text = (root / STATE).read_text(encoding="utf-8")
    cell = MASTER.search(text)
    day = DAY.match(cell[1].strip()) if cell else None
    if not day:
        raise ValueError("Cannot parse Document 5 master date")
    line = cell[1].strip()
    on = dt.datetime.strptime(day[1], "%B %d, %Y").date()
    timed = TIMED.match(line)
    if timed:
        hour = int(timed[1]) % 12 + (12 if timed[3] == "p" else 0)
        return Clock(et(on, hour, int(timed[2] or 0)), on, True, line)
    after = AFTER_GAME.match(line)
    if after:
        season = int(repository_map(root)["active_season"])
        game = next((g for g in club_fixtures(season, root, on) if int(g["week"]) == int(after[1])
                     and g["date"] == on.isoformat()), None)
        if game is not None:
            return Clock(kickoff(game), on, False, line)
    return Clock(et(on), on, False, line)


def master_at(root=ROOT):
    """The master date with the time the line names (``master_clock``): the clock's floor."""
    return master_clock(root).at


# ------------------------------------------------------------------ periods and issues
def period_order(period):
    """A period's place in the season: a week or bye by its number (the bye of Week 11 sits between
    Weeks 10 and 12), a phase after the games."""
    if not isinstance(period, dict) or len(period) != 1:
        raise ValueError("a period is {\"week\": N}, {\"bye\": N} or {\"phase\": name}: %r" % (period,))
    (kind, value), = period.items()
    if kind in ("week", "bye") and type(value) is int and 1 <= value <= 22:
        return (value, "")
    if kind == "phase" and isinstance(value, str) and value.strip():
        return (100, value)
    raise ValueError("a period is {\"week\": N}, {\"bye\": N} or {\"phase\": name}: %r" % (period,))


def period_label(period):
    (kind, value), = period.items()
    return {"week": "Week %s", "bye": "the Week %s bye", "phase": "%s"}[kind] % value


def issues_path(season, period, root=ROOT):
    """The issue record of a period's brief: a game week's or the bye's ``briefings.json`` in the
    week's data folder (the bye of Week 11 and Week 11's folder are one)."""
    (kind, value), = period.items()
    if kind == "phase":
        return None
    return decisions.week_pages(season, value, root).data / "briefings.json"


def issues(season, period, root=ROOT):
    """The period's issued briefs, oldest first ([] before the first)."""
    path = issues_path(season, period, root)
    if path is None or not path.is_file():
        return []
    return [dict(e) for e in json.loads(path.read_text(encoding="utf-8")).get("issued") or ()]


def issue_identity(period, entry):
    return {"period": dict(period), "date": entry["date"], "revision": int(entry["revision"])}


def issued_at(entry):
    """An issue's time: its ``at``, or for an entry written before step 5 the start of its date."""
    if entry.get("at"):
        return parse_at(entry["at"])
    return et(dt.date.fromisoformat(entry["date"]))


def latest_issue(season, period, root=ROOT):
    """The ``after_issue`` stamp of the period now: its latest issue, or None before its first."""
    entries = issues(season, period, root)
    return issue_identity(period, entries[-1]) if entries else None


class Issues:
    """The season's issue order, read once: each period's issue record, so that a stamp and an issue
    have a place ("key") in one order across periods."""

    def __init__(self, season, root=ROOT):
        self.season, self.root, self._cache = season, Path(root), {}

    def of(self, period):
        key = json.dumps(period, sort_keys=True)
        if key not in self._cache:
            self._cache[key] = issues(self.season, period, self.root)
        return self._cache[key]

    def index(self, after_issue):
        """The 1-based position of a stamp's issue in its period's record; ValueError when the record
        holds no such issue."""
        entries = self.of(after_issue["period"])
        for n, entry in enumerate(entries, 1):
            if entry.get("date") == after_issue.get("date") and int(entry.get("revision", 0)) == after_issue.get("revision"):
                return n
        raise ValueError("no issue of %s on %s revision %s" % (period_label(after_issue["period"]),
                                                               after_issue.get("date"), after_issue.get("revision")))

    def stamp_key(self, after_issue, period):
        """A stamp's place: after its issue, or before its period's first issue (index 0)."""
        if after_issue is None:
            return period_order(period) + (0,)
        return period_order(after_issue["period"]) + (self.index(after_issue),)

    def previous(self, period, index):
        """The key of the issue before issue ``index`` of ``period`` (the period's previous issue, or
        for its first issue the last issue of the nearest earlier period that has one), or None."""
        if index > 1:
            return period_order(period) + (index - 1,)
        order = period_order(period)
        for n in range(order[0] - 1 if order[0] < 100 else 22, 0, -1):
            entries = self.of({"week": n})
            if entries:
                return (n, "", len(entries))
        return None


def stamp_key(record, issues_, which="raised"):
    """The place of one of a record's stamps: its raising, a process entry (an index) or its
    resolution."""
    if which == "raised":
        return issues_.stamp_key(record["raised"].get("after_issue"), record["period"])
    if which == "resolution":
        res = record["resolution"]
        return issues_.stamp_key(res.get("after_issue"), res.get("period") or record["period"])
    entry = record["process"][which]
    return issues_.stamp_key(entry.get("after_issue"), entry.get("period") or record["period"])


def open_period(season, root=ROOT):
    """The open period: the bye while it is open (``active_bye``), otherwise Jacksonville's next game
    not yet closed (a playoff round once the regular season has closed), or None."""
    from . import game_weeks
    from .week_inputs import receipt_name
    root = Path(root)
    paths = SeasonPaths(season, root)
    bye = active_bye(paths, root)
    if bye is not None:
        return {"bye": int(bye)}
    for game in club_fixtures(season, root):
        if not (paths.receipts / receipt_name(game)).is_file():
            return {"week": int(game["week"])}
    game, _ = game_weeks.next_postseason_game(paths, employer_club(root))
    return {"week": int(game["week"])} if game else None


def active_bye(paths, root):
    """STUB until builder C3's runtime/bye_week.py lands: the bye week while it is the open period
    (``bye_week.active_bye(paths, root)``, the week or None). Without that module no bye is open."""
    try:
        from . import bye_week
    except ImportError:
        return None
    found = bye_week.active_bye(paths, root)
    if found is None or found is False:
        return None
    return found if isinstance(found, int) else getattr(found, "week", None)


def stamp(season, root=ROOT, period=None):
    """{after_issue, period} for a write now: the open period and its latest issue."""
    period = period or open_period(season, root)
    if period is None:
        raise Refused("no period is open: name the phase the event belongs to")
    return {"after_issue": latest_issue(season, period, root), "period": dict(period)}


# ------------------------------------------------------------------ the store
def store(kind, season, root=ROOT):
    return decisions.event_store(kind, season, root)


def path_of(record, root=ROOT):
    return store(record["kind"], record["season"], root) / ("%s.json" % record["id"])


def stores(season, root=ROOT):
    """Every owner's event store of the season, once each."""
    out = []
    for event in decisions.EVENTS + decisions.NEWS:
        folder = store(event.kind, season, root)
        if folder not in out:
            out.append(folder)
    return out


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("%s: %s" % (path.name, exc)) from None


def load(season, root=ROOT):
    """Every event record of the season, by the time it was raised and its id."""
    found = []
    for folder in stores(season, root):
        for path in sorted(folder.glob("*.json")) if folder.is_dir() else ():
            found.append(_read(path))
    return sorted(found, key=lambda r: (str((r.get("raised") or {}).get("at")), str(r.get("id"))))


def get(season, event_id, root=ROOT):
    """The record of one event, or None."""
    for folder in stores(season, root):
        path = folder / ("%s.json" % event_id)
        if path.is_file():
            return _read(path)
    return None


def _write(record, root):
    path = path_of(record, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def needs_answer(record):
    """Whether the event needs Stone's answer: known to him, with a part that needs one."""
    return "stone" in (record.get("known_to") or ()) and record.get("stone_part") in ANSWERS


def known_to_stone(record, job=None):
    holder = (job or {}).get("holder", "stone")
    return holder in (record.get("known_to") or ())


def title(record):
    """The event's notice title in football words."""
    return TITLES.get(record["kind"], "%s") % record["subject"]


def cannot_dress(record):
    """Whether an injury replacement's facts record, with a source, that the active roster cannot
    dress a legal team for the next game."""
    return record.get("kind") == "injury_replacement" and any(
        f.get("label") == LEGAL_TEAM_FACT and str(f.get("value", "")).startswith("No") and f.get("source")
        for f in record.get("facts") or ())


def held_week(record, root=ROOT):
    """The week whose game an injury replacement's items hold: the game whose kickoff is its due
    time (the next game), when the active roster cannot dress a legal team for it; else None."""
    if not cannot_dress(record) or not record.get("deadline"):
        return None
    due = parse_at(record["deadline"]["at"])
    return next((int(g["week"]) for g in club_fixtures(record["season"], root) if kickoff(g) == due), None)


# ------------------------------------------------------------------ validation
def _party(job, pid, other_club=False):
    return pid in (job.get("parties") or {}) or (other_club and pid == OTHER_CLUB)


def _text_errors(rel, text, root):
    from .clean_pages import page_errors
    return [e.split(": ", 1)[-1] for e in page_errors(rel, str(text), root=root)]


def _authored(value, say, where, root, rel, clock):
    if not isinstance(value, dict) or set(value) != {"text", "author", "date"} or \
            not all(isinstance(value[k], str) and value[k].strip() for k in value):
        return say("%s must be {text, author, date}" % where)
    if "\n" in value["text"]:
        say("%s must be one line" % where)
    try:
        if dt.date.fromisoformat(value["date"]) > clock.date:
            say("%s is dated %s, after the master date" % (where, value["date"]))
    except ValueError:
        say("%s date is not an ISO date" % where)
    for problem in _text_errors(rel, value["text"], root):
        say("%s is not in football words (%s)" % (where, problem))


def _record_ok(root, mapping, record):
    return current_job.record_error(root, mapping, record)


def record_errors(record, root, mapping=None, job=None, clock=None, issues_=None, queue=None, closed=None):
    """Every rule one event record must satisfy, as lines (docs/rebuild_plan.md step 5, A1)."""
    root = Path(root)
    mapping = repository_map(root) if mapping is None else mapping
    job = current_job.load(root) if job is None else job
    clock = master_clock(root) if clock is None else clock
    errors = []
    rid = record.get("id") if isinstance(record, dict) else None
    say = lambda text: errors.append("Event %s: %s" % (rid, text))
    if not isinstance(record, dict):
        return ["Event record must be an object"]
    missing = [k for k in RECORD_KEYS if k not in record and k not in OPTIONAL_KEYS]
    unknown = sorted(set(record) - set(RECORD_KEYS))
    if missing or unknown:
        return ["Event %s: lacks %s / has unknown keys %s" % (rid, ", ".join(missing) or "nothing",
                                                            ", ".join(unknown) or "none")]
    if record["schema"] != SCHEMA:
        say("schema must be %s" % SCHEMA)
    if not isinstance(rid, str) or not EVENT_ID.fullmatch(rid):
        return errors + ["Event %r: the id is an event-record id (lowercase words joined by hyphens)" % (rid,)]
    try:
        kind = decisions.event_kind(record["kind"])
    except ValueError:
        return errors + ["Event %s: unknown kind %r" % (rid, record["kind"])]
    news = record["kind"] in decisions.NEWS_KIND
    if type(record["season"]) is not int:
        say("season must be an int")
        return errors
    rel = (decisions.event_folder(kind, record["season"], root) / "README.md").relative_to(root).as_posix()
    try:
        period_order(record["period"])
    except ValueError as exc:
        say(str(exc))
    if not isinstance(record["subject"], str) or not record["subject"].strip():
        say("needs the subject its result page is named for")
    # Raised.
    raised = record["raised"] if isinstance(record["raised"], dict) else {}
    try:
        raised_at = parse_at(raised.get("at"))
        if not rid.startswith(raised_at.date().isoformat() + "-"):
            say("the id must begin with the date it was raised (%s)" % raised_at.date().isoformat())
        if not clock.allows(raised_at):
            say("was raised at %s, after the master date/time" % raised["at"])
    except ValueError as exc:
        raised_at = None
        say("raised.at: %s" % exc)
    if not _party(job, raised.get("by")):
        say("raised.by %r is not a party in the job record" % (raised.get("by"),))
    problem = _record_ok(root, mapping, raised.get("source"))
    if problem:
        say("raised.source: %s" % problem)
    if not isinstance(record["known_to"], list) or not all(_party(job, p) for p in record["known_to"]):
        say("known_to must list parties of the job record")
    # Authority.
    authority = record["authority"] if isinstance(record["authority"], dict) else {}
    rows = authority.get("rows")
    if not isinstance(rows, list) or not rows or any(r not in current_job.AUTHORITY_ROWS for r in rows):
        say("authority.rows must name Document 3 rows")
    decides = authority.get("decides")
    if not _party(job, decides, other_club=news):
        say("authority.decides %r is not a party in the job record%s" % (
            decides, "" if not news else " or %s" % OTHER_CLUB))
    if news and (decides != OTHER_CLUB or record["stone_part"] != "none"):
        say("is news decided outside Jacksonville: authority.decides %s and stone_part none" % OTHER_CLUB)
    part = record["stone_part"]
    standing = part[len("standing:"):] if isinstance(part, str) and part.startswith("standing:") else None
    if part not in STONE_PARTS and standing is None:
        say("stone_part must be one of %s or standing:<instruction id>" % ", ".join(STONE_PARTS))
    if standing is not None and standing not in {i.get("id") for i in current_job.instructions(job, None)}:
        say("stone_part names unknown standing instruction %s" % standing)
    # Authored texts.
    _authored(record["summary"], say, "summary", root, rel, clock)
    for key in ("staff_position", "consequence"):
        if record.get(key) is not None:
            _authored(record[key], say, key, root, rel, clock)
    # Facts and options: names, positions, dates and sourced terms; a digit needs a source.
    for where, entries, keys in (("facts", record["facts"], ("label", "value", "source")),
                                 ("options", record["options"], ("name", "position", "basis", "source"))):
        if not isinstance(entries, list):
            say("%s must be a list" % where)
            continue
        for n, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) != set(keys):
                say("%s %d must hold exactly %s" % (where, n + 1, ", ".join(keys)))
                continue
            texts = [str(entry[k]) for k in keys if k != "source"]
            if any(re.search(r"\d", t) for t in texts) and (entry["source"] is None or _record_ok(
                    root, mapping, entry["source"])):
                say("%s %d carries a figure or date without a source that resolves" % (where, n + 1))
            elif entry["source"] is not None:
                problem = _record_ok(root, mapping, entry["source"])
                if problem:
                    say("%s %d source: %s" % (where, n + 1, problem))
            for text in texts:
                for problem in _text_errors(rel, text, root):
                    say("%s %d is not in football words (%s)" % (where, n + 1, problem))
    # Deadline: only a sourced one.
    deadline = record.get("deadline")
    due = None
    if deadline is not None:
        if not isinstance(deadline, dict) or set(deadline) != {"at", "label", "source"}:
            say("deadline must be {at, label, source} or null")
        else:
            try:
                due = parse_at(deadline["at"])
            except ValueError as exc:
                say("deadline.at: %s" % exc)
            problem = _record_ok(root, mapping, deadline["source"])
            if problem:
                say("deadline.source: %s (a due time comes only from the other side's sourced deadline, the "
                    "calendar, a sourced league rule or the game's kickoff)" % problem)
    # State and process.
    if record["state"] not in STATES:
        say("state must be one of %s" % ", ".join(STATES))
    process = record["process"] if isinstance(record["process"], list) else []
    if not isinstance(record["process"], list):
        say("process must be a list")
    previous = raised_at
    response_at = None
    for n, entry in enumerate(process):
        where = "process %d" % (n + 1)
        if not isinstance(entry, dict) or not {"at", "kind", "what", "by", "source", "after_issue", "period"} \
                <= set(entry) or set(entry) - {"at", "kind", "what", "by", "source", "after_issue", "period"}:
            say("%s must hold at, kind, what, by, source, after_issue and period" % where)
            continue
        if entry["kind"] not in PROCESS_KINDS:
            say("%s kind must be one of %s" % (where, ", ".join(PROCESS_KINDS)))
        try:
            at = parse_at(entry["at"])
            if not clock.allows(at):
                say("%s is at %s, after the master date/time" % (where, entry["at"]))
            if previous is not None and at < previous:
                say("%s is earlier than the entry before it (the process is appended in order)" % where)
            previous = at
            if entry["kind"] == "response":
                response_at = (n, at)
        except ValueError as exc:
            say("%s at: %s" % (where, exc))
        if not _party(job, entry["by"], other_club=True):
            say("%s by %r is not a party in the job record" % (where, entry["by"]))
        problem = _record_ok(root, mapping, entry["source"])
        if problem:
            say("%s source: %s" % (where, problem))
        for problem in _text_errors(rel, entry["what"], root):
            say("%s is not in football words (%s)" % (where, problem))
    # The queue link.
    holder = job.get("holder")
    items = [i for i in (queue or {}).get("items") or () if i.get("event") == rid]
    item_id = record.get("queue_item")
    if item_id is not None:
        bound = next((i for i in (queue or {}).get("items") or () if i.get("id") == item_id), None)
        if bound is None:
            say("names queue item %s, which the decision queue does not hold" % item_id)
        elif bound.get("event") != rid:
            say("names queue item %s, which does not name this event back" % item_id)
    for item in items:
        if item.get("id") != item_id and not (item.get("class") == "personnel_transaction"
                                              and item.get("owner") != holder):
            say("is named by queue item %s, which the event does not name" % item.get("id"))
    if (not needs_answer(record)) and any(i.get("status") == "OPEN" and i.get("owner") == holder for i in items):
        say("needs no answer from %s (%s), but an OPEN item of his carries it" % (
            current_job.party_name(job, holder), part))
    if needs_answer(record) and record["state"] != "resolved" and item_id is None:
        say("needs his answer but names no queue item")
    # His response.
    response = record.get("response")
    if response is not None:
        if not isinstance(response, dict) or set(response) != {"page", "heading", "sha256", "date", "substance"}:
            say("response must be {page, heading, sha256, date, substance}")
        else:
            problem = _record_ok(root, mapping, {"path": response["page"]})
            if problem:
                say("response.page: %s" % problem)
            substance = response["substance"]
            if not isinstance(substance, dict) or substance.get("kind") not in SUBSTANCE_KINDS:
                say("response.substance must name its kind (%s)" % ", ".join(SUBSTANCE_KINDS))
            if response_at is None:
                say("has a response but no response process entry")
    # Resolution.
    resolution = record.get("resolution")
    if (resolution is None) != (record["state"] != "resolved"):
        say("a resolved event has its resolution, and only a resolved one")
    if resolution is not None:
        errors += _resolution_errors(record, resolution, root, mapping, job, clock, kind, process, response_at,
                                     items, closed, say)
    elif closed is not None and rid in closed:
        say("its id is already a closed event's (%s); an event id is never reused" % closed[rid].owner)
    # Stamps.
    if issues_ is not None:
        for which in ["raised"] + list(range(len(process))) + (["resolution"] if resolution else []):
            try:
                stamp_key(record, issues_, which)
            except (ValueError, KeyError, TypeError) as exc:
                say("stamp of %s: %s" % ("the raising" if which == "raised" else "the resolution"
                                         if which == "resolution" else "process %d" % (which + 1), exc))
    return errors


def _resolution_errors(record, resolution, root, mapping, job, clock, kind, process, response_at, items,
                       closed, say):
    keys = {"at", "outcome", "by", "decision", "result_page", "after_issue", "period"}
    if not isinstance(resolution, dict) or set(resolution) != keys:
        say("resolution must hold %s" % ", ".join(sorted(keys)))
        return []
    rid = record["id"]
    news = record["kind"] in decisions.NEWS_KIND
    if resolution["outcome"] not in OUTCOMES:
        say("resolution.outcome must be one of %s" % ", ".join(OUTCOMES))
    if resolution["outcome"] == "executed" and record["kind"] == "trade_talks":
        say("a trade is not executed here; the agreed terms stay on the event and the decision is put to the user")
    if resolution["outcome"] == "lapsed" and ((record.get("response") or {}).get("substance") or {}).get("kind") != "lapse":
        say("lapsed only with Stone's explicit permission to let it lapse on his page")
    try:
        at = parse_at(resolution["at"])
        if not clock.allows(at):
            say("was resolved at %s, after the master date/time" % resolution["at"])
        last = max((parse_at(e["at"]) for e in process if isinstance(e, dict) and "at" in e), default=None)
        if last is not None and at < last:
            say("was resolved before its last process entry")
    except (ValueError, TypeError) as exc:
        say("resolution.at: %s" % exc)
    by = resolution["by"]
    if not _party(job, by, other_club=True):
        say("resolution.by %r is not a party in the job record" % (by,))
    holder = job.get("holder")
    decision = resolution["decision"] if isinstance(resolution["decision"], dict) else None
    if decision is None or not {"text", "author", "date", "criteria"} <= set(decision) or \
            set(decision) - {"text", "author", "date", "criteria"}:
        say("resolution.decision must be {text, author, date, criteria}")
        decision = {}
    elif not isinstance(decision["text"], str) or not decision["text"].strip():
        say("resolution.decision needs its text")
    else:
        rel = (decisions.event_folder(kind, record["season"], root) / "README.md").relative_to(root).as_posix()
        for problem in _text_errors(rel, decision["text"], root):
            say("the decision is not in football words (%s)" % problem)
    criteria = decision.get("criteria")
    if criteria is not None:
        entry = process[criteria] if type(criteria) is int and 0 <= criteria < len(process) else None
        if entry is None or entry.get("kind") != "criteria":
            say("resolution.decision.criteria must index the criteria process entry it applies")
        elif entry.get("by") != by:
            say("the criteria the decision applies are not the deciding party's")
        elif response_at is not None and criteria > response_at[0]:
            say("the criteria were recorded after Stone's response; criteria come before the case")
    elif not news and by != holder and by != OTHER_CLUB and resolution["outcome"] in DECIDED:
        say("is decided by %s without a criteria entry recorded before Stone's response (Document 1 sections 9.1 "
            "and 9.4)" % current_job.party_name(job, by))
    page = resolution["result_page"]
    target = (root / page) if isinstance(page, str) else None
    folder = decisions.event_folder(kind, record["season"], root)
    if target is None or not target.is_file():
        say("its result page %s is missing" % page)
    else:
        if target.resolve().parent != folder.resolve():
            say("its result page is not in its owner's folder (%s)" % folder.relative_to(root).as_posix())
        ids = [json.loads(m).get("id") for m in EVENT_META.findall(target.read_text(encoding="utf-8"))]
        if ids != [rid]:
            say("its result page must carry exactly one event-record line, with the event's id")
        if closed is not None and rid in closed and closed[rid].owner != Path(page).as_posix():
            say("its id is a closed event of another page (%s)" % closed[rid].owner)
    if any(i.get("status") == "OPEN" for i in items):
        say("is resolved, but its queue item %s is still OPEN" % next(i["id"] for i in items if i.get("status") == "OPEN"))
    return []


def validation_errors(root=ROOT):
    """Every event record of the active season against its rules and the decision queue (the lead
    wires this into scripts/validate_repository.py). An open event or an overdue item is never an
    error by itself."""
    root = Path(root)
    mapping = repository_map(root)
    season = int(mapping["active_season"])
    try:
        job = current_job.load(root)
        queue = decision_queue.load(root)
        clock = master_clock(root)
        closed = load_events(root, mapping)
    except (OSError, ValueError, KeyError) as exc:
        return ["Event store: cannot be read: %s" % exc]
    errors, seen = [], {}
    issues_ = Issues(season, root)
    for folder in stores(season, root):
        for path in sorted(folder.glob("*")) if folder.is_dir() else ():
            rel = path.relative_to(root).as_posix()
            if path.suffix != ".json":
                errors.append("Event store: %s is not an event record" % rel)
                continue
            try:
                record = _read(path)
            except ValueError as exc:
                errors.append("Event store: %s" % exc)
                continue
            errors += record_errors(record, root, mapping, job, clock, issues_, queue, closed)
            rid = record.get("id")
            if path.name != "%s.json" % rid:
                errors.append("Event store: %s is not named by its id" % rel)
            elif record.get("season") == season and isinstance(record.get("kind"), str):
                try:
                    if path_of(record, root).resolve() != path.resolve():
                        errors.append("Event store: %s is not in its owner's store" % rel)
                except ValueError:
                    pass
            if rid in seen:
                errors.append("Event store: %s is recorded twice (%s, %s)" % (rid, seen[rid], rel))
            seen[rid] = rel
    for item in queue.get("items") or ():
        if item.get("event") is not None and item["event"] not in seen:
            errors.append("Decision queue: %s names event %s, which no event record holds" % (item.get("id"),
                                                                                             item["event"]))
    return errors


# ------------------------------------------------------------------ writers
def _refuse_if_paused(root):
    from scripts.render_career_views import paused_games
    paused = paused_games(root)
    if paused:
        raise Refused("A Jacksonville game is paused; nothing is recorded until it is finished")


# Who raises an item, by the party that brings its event (decision_queue.RAISED_BY): the owner, the
# general manager and the communications staff are the organization; the medical staff is medical;
# the holder is the user; the coaching staff and its coaches are the staff.
ORGANIZATION = ("khan", "caldwell", "communications_staff")


def _raised_by(pid, job):
    if pid == "medical_staff":
        return "medical"
    if pid == job.get("holder"):
        return "user"
    return "organization" if pid in ORGANIZATION else "staff"


def items_for(record, root=ROOT, job=None):
    """The queue items an event opens when it is raised: Stone's item when his part needs his answer
    (``ITEM_CLASS``), holding its own event; and, for an injury replacement whose facts record that
    the active roster cannot dress a legal team for the next game, Caldwell's transaction item bound
    to the event, both holding that game's inputs (the hold rule, decision_queue)."""
    job = current_job.load(root) if job is None else job
    holder = job.get("holder")
    rid, season = record["id"], record["season"]
    out = []
    week = held_week(record, root)
    held = [decision_queue.event("event_resolution", season, event=rid)]
    before = None
    if week is not None:
        before = decision_queue.event("week_inputs", season, week)
        held.append(before)
    deadline = None
    if record.get("deadline"):
        due = parse_at(record["deadline"]["at"])
        deadline = {"date": due.date().isoformat(), "at": iso(due), "label": record["deadline"]["label"]}
        if before is not None:
            deadline["before"] = dict(before)
    raised = {"date": parse_at(record["raised"]["at"]).date().isoformat(), "by": _raised_by(record["raised"]["by"], job)}
    if needs_answer(record):
        cls = ITEM_CLASS.get((record["kind"], record["stone_part"]))
        if cls is None:
            raise Refused("no decision class carries Stone's %s part in a %s event" % (record["stone_part"],
                                                                                    record["kind"]))
        out.append({"id": rid, "title": title(record), "class": cls, "owner": holder,
                    "authority_rows": [r for r in record["authority"]["rows"] if r in decision_queue.CLASSES[cls].rows]
                    or list(decision_queue.CLASSES[cls].rows),
                    "question": "Your football answer on the %s, for %s, who decides: %s" % (
                        title(record)[:1].lower() + title(record)[1:],
                        current_job.party_name(job, record["authority"]["decides"]),
                        record["summary"]["text"].rstrip(".") + "."),
                    "raised": raised, "status": "OPEN", "waits_on": [], "deadline": deadline,
                    "blocks": [dict(b) for b in held], "fallback": None, "can_continue": None,
                    "record": dict(record["raised"]["source"]), "sources": [], "event": rid, "resolution": None})
    if week is not None:
        cls = "personnel_transaction"
        out.append({"id": rid + "-transaction", "title": "Roster move for the next game: %s" % record["subject"],
                    "class": cls, "owner": decision_queue.CLASSES[cls].default_owner,
                    "authority_rows": list(decision_queue.CLASSES[cls].rows),
                    "question": "The roster move that lets the club dress a legal team for the Week %d game." % week,
                    "raised": dict(raised), "status": "OPEN", "waits_on": [], "deadline": dict(deadline),
                    "blocks": [dict(b) for b in held], "fallback": None, "can_continue": None,
                    "record": dict(record["raised"]["source"]), "sources": [], "event": rid, "resolution": None})
    return out


def prepare(record, root=ROOT):
    """(the record as ``raise_event`` would write it, the queue with its new items, the items): every
    check of a new event, with nothing written (scripts/raise_event.py --check)."""
    root = Path(root).resolve()
    _refuse_if_paused(root)
    record = json.loads(json.dumps(record))
    for key in OPTIONAL_KEYS:
        record.setdefault(key, None)
    record.setdefault("schema", SCHEMA)
    if record.get("state") != "open" or record.get("resolution") is not None or record.get("response") is not None:
        raise Refused("a new event is open, with no response and no resolution")
    if record.get("queue_item") is not None:
        raise Refused("a new event's queue item is opened here, never named in advance")
    season = record.get("season")
    if type(season) is not int:
        raise Refused("a new event names its season")
    if not isinstance((record.get("raised") or {}).get("source"), dict) or not record["raised"]["source"].get("path"):
        raise Refused("an event is recorded only from a source page")
    if get(season, record.get("id"), root) is not None:
        raise Refused("event %s is already recorded" % record.get("id"))
    named = record.get("period")
    stamped = stamp(season, root, named if (named or {}).get("phase") else None)
    if named is not None and named != stamped["period"]:
        raise Refused("the event belongs to the open period, %s, not %s" % (period_label(stamped["period"]),
                                                                           period_label(named)))
    record["period"] = stamped["period"]
    record["raised"]["after_issue"] = stamped["after_issue"]
    for entry in record.get("process") or ():
        entry.setdefault("after_issue", stamped["after_issue"])
        entry.setdefault("period", dict(stamped["period"]))
    job = current_job.load(root)
    queue = decision_queue.load(root)
    items = items_for(record, root, job) if not record.get("kind") in decisions.NEWS_KIND else []
    ids = {i.get("id") for i in queue["items"]}
    if any(i["id"] in ids for i in items):
        raise Refused("the decision queue already holds an item %s" % next(i["id"] for i in items if i["id"] in ids))
    mine = next((i for i in items if i["owner"] == job.get("holder")), None)
    record["queue_item"] = mine["id"] if mine else None
    queue = dict(queue, items=queue["items"] + items)
    errors = record_errors(record, root, job=job, issues_=Issues(season, root), queue=queue,
                           closed=load_events(root))
    if errors:
        raise Refused("; ".join(errors))
    return record, queue, items


def raise_event(record, root=ROOT):
    """Record a new event: validated, stamped (``after_issue`` and ``period`` on the raising and on
    any process entry it carries), written to its owner's store and, when Stone's part needs his
    answer, its queue item opened. Refused, with nothing written, while a game is paused, for a time
    after the clock, an id already used, or a record that breaks a rule. Returns the paths written."""
    root = Path(root).resolve()
    record, queue, items = prepare(record, root)
    written = [_write(record, root)]
    if items:
        written.append(decision_queue.save(root, queue))
    return written


def add_process(season, event_id, entry, root=ROOT, state=None):
    """Append one dated process entry (stamped) to an open event, optionally moving its state.
    Refused for a resolved event, while a game is paused, for a time after the clock or before the
    last entry."""
    root = Path(root).resolve()
    _refuse_if_paused(root)
    record = get(season, event_id, root)
    if record is None:
        raise Refused("no event %s is recorded" % event_id)
    if record["state"] == "resolved":
        raise Refused("event %s is resolved; its process is closed" % event_id)
    entry = dict(entry, **stamp(season, root))
    record["process"] = list(record["process"]) + [entry]
    if state is not None:
        if state == "resolved":
            raise Refused("an event resolves only through its resolution")
        record["state"] = state
    errors = record_errors(record, root, issues_=Issues(season, root), queue=decision_queue.load(root))
    if errors:
        raise Refused("; ".join(errors))
    return _write(record, root)


def resolve(season, event_id, resolution, root=ROOT):
    """Record an event's resolution (stamped), its result page already written in its owner's folder
    with the event's event-record line. Refused while a game is paused, for a time after the clock,
    for a decision by another party without its preceding criteria entry, for ``executed`` on a trade,
    and while one of its queue items is OPEN (the item is settled first)."""
    root = Path(root).resolve()
    _refuse_if_paused(root)
    record = get(season, event_id, root)
    if record is None:
        raise Refused("no event %s is recorded" % event_id)
    if record["state"] == "resolved":
        raise Refused("event %s is already resolved" % event_id)
    record["resolution"] = dict(resolution, **stamp(season, root))
    record["state"] = "resolved"
    errors = record_errors(record, root, issues_=Issues(season, root), queue=decision_queue.load(root),
                           closed=load_events(root))
    if errors:
        raise Refused("; ".join(errors))
    return _write(record, root)


# ------------------------------------------------------------------ routing
@dataclass
class Notice:
    """One insert: an event's notice, C2's game-day item, or a COMING UP window."""
    section: str                       # "action", "fyi" or "coming_up"
    key: str                           # the event id, the item id, or the window's key
    record: dict | None = None         # the event record (as of the issue)
    item: dict | None = None           # the queue item carrying his answer
    due: dt.datetime | None = None     # the answer's due time, when set
    window: dict | None = None         # a COMING UP window (runtime/deadlines.coming_up)


@dataclass
class Route:
    action: list = field(default_factory=list)
    fyi: list = field(default_factory=list)
    coming_up: list = field(default_factory=list)

    def notices(self):
        return self.action + self.fyi + self.coming_up


def issue_index(season, period, at, root=ROOT, issue=None):
    """The 1-based index of the issue built at ``at`` in the period's record: ``issue`` when named;
    the recorded issue issued exactly then; otherwise the next issue."""
    if issue is not None:
        return int(issue)
    entries = issues(season, period, root)
    for n, entry in enumerate(entries, 1):
        if entry.get("at") and parse_at(entry["at"]) == at:
            return n
    return len(entries) + 1


def _as_of(record, issues_, key):
    """The record as it stood at issue ``key``: only the process entries stamped before it, its
    response only if stamped before it, its resolution only if stamped before it."""
    shown = json.loads(json.dumps(record))
    kept = [e for n, e in enumerate(record["process"]) if stamp_key(record, issues_, n) < key]
    shown["process"] = kept
    if record.get("response") is not None and not any(e["kind"] == "response" for e in kept):
        shown["response"] = None
    if record.get("resolution") is not None and stamp_key(record, issues_, "resolution") >= key:
        shown["resolution"] = None
        shown["state"] = "answered" if shown.get("response") else "open"
    return shown


def game_day_items(queue, season, week, job):
    """C2's game-day depth or inactives item(s) of the week (decision_queue.game_day_item)."""
    return [i for i in queue["items"] if decision_queue.game_day_item(i, job.get("holder"))
            and ((i.get("deadline") or {}).get("before") or {}).get("week") == week
            and ((i.get("deadline") or {}).get("before") or {}).get("season") == season]


def route(season, issued_at, period, root=ROOT, issue=None):
    """The three insert lists of a brief issued at ``issued_at`` for ``period`` (the ``issue``-th of
    the period when named, otherwise as ``issue_index`` finds it), in the order of
    docs/event_inserts.md section C:

    - ACTION REQUIRED: the answers Stone owes as of the issue (an event known to him whose part needs
      his answer, not yet answered or resolved before the issue; and C2's game-day item of a game
      week), those with a due time first, earliest first, then the others;
    - FOR YOUR INFORMATION: the events known to him resolved since the issue before this one (the
      clock section's window), by their resolution time;
    - COMING UP: the league's dated windows (runtime/deadlines.coming_up).

    Built as of the issue from the events stamped before it, so a later event never changes what an
    issued brief showed."""
    from . import deadlines
    root = Path(root)
    job = current_job.load(root)
    queue = decision_queue.load(root)
    issues_ = Issues(season, root)
    index = issue_index(season, period, issued_at, root, issue)
    key = period_order(period) + (index,)
    before = issues_.previous(period, index)
    out = Route()
    for record in load(season, root):
        if not known_to_stone(record, job) or stamp_key(record, issues_) >= key:
            continue
        shown = _as_of(record, issues_, key)
        resolved_key = stamp_key(record, issues_, "resolution") if record.get("resolution") else None
        if shown.get("resolution") is None and needs_answer(record) and shown.get("response") is None:
            item = next((i for i in queue["items"] if i.get("id") == record.get("queue_item")), None)
            due = parse_at(record["deadline"]["at"]) if record.get("deadline") else None
            out.action.append(Notice("action", record["id"], shown, item, due))
        elif resolved_key is not None and resolved_key < key and (before is None or resolved_key >= before):
            out.fyi.append(Notice("fyi", record["id"], shown))
    (kind, week), = period.items()
    if kind == "week":
        day = issued_at.date().isoformat()
        for item in game_day_items(queue, season, week, job):
            settled = (item.get("resolution") or {}).get("date")
            if item["raised"]["date"] <= day and (item.get("status") == "OPEN" or (settled and settled >= day)):
                due = parse_at(item["deadline"]["at"]) if (item.get("deadline") or {}).get("at") else None
                out.action.append(Notice("action", item["id"], None, item, due))
    out.action.sort(key=lambda n: (n.due is None, n.due or issued_at, n.key))
    out.fyi.sort(key=lambda n: (n.record["resolution"]["at"], n.key))
    out.coming_up = [Notice("coming_up", w["key"], window=w) for w in deadlines.coming_up(season, issued_at, root)]
    return out


def period_events(season, period, root=ROOT):
    """(results, open events) of a period, for its index and its report: the resolved events whose
    resolution's ``period`` is the period, by resolution time; and the events raised in it still
    open, by due time (none last)."""
    results, still = [], []
    for record in load(season, root):
        res = record.get("resolution")
        if res is not None and res.get("period") == period:
            results.append(record)
        elif res is None and record.get("period") == period:
            still.append(record)
    results.sort(key=lambda r: (r["resolution"]["at"], r["id"]))
    still.sort(key=lambda r: (r.get("deadline") is None, (r.get("deadline") or {}).get("at") or "", r["id"]))
    return results, still
