"""The league's dated windows shown under COMING UP (rebuild step 5, A5; docs/event_inserts.md,
sections B, C and D; the COMING UP layout of
foundation/templates/event_inserts/brief_action_inserts_template.md).

Two kinds of window reach a brief, neither of them an event:

- the league's dates of the season, from its record (``league_dates.json`` in the season's schedule
  data, SeasonPaths.league_dates): the trading deadline, shown in the briefs of the last
  Jacksonville game before it (from the kickoff of the game before that one, when that game's brief
  is first issued) and in any brief issued after that game and before the deadline itself, with
  the trade calls open at the issue ("No proposal is on record." when there are none) and "No
  answer is required."; the veteran waivers date is in the record for the transaction checks
  (``waivers_from``) and is not shown. A season with no record shows nothing, so one season's date
  is never reused for another;
- each player's eligibility windows, from the roster record's availability note in its one format
  (runtime/season_summary.py: "no practice before <Month D>, no return before <Month D>"), each
  shown in the briefs issued before its date.

A window holds nothing, opens no queue item, writes no result page or Record.md line, and drops out
once its time has passed. Nothing here generates a call, an offer, a salary, an interest or a market
price: the trade calls a window names are the recorded events, and a window that names none says so.

A window is a dict: ``key`` (a stable name), ``title``, ``at`` (an ISO datetime with its ET offset,
or None), ``date`` (an ISO date when only the day is known, or None), ``why``, ``state``, ``action``
and ``source`` ({path, anchor} of the page that records it).

The career layer (tests/test_career_layer_isolation.py, LAYER): this module reads the event store
and the job record, and nothing that resolves a game imports it.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import re

from . import current_job, open_events
from .seasons import SeasonPaths

SCHEMA = "league-dates-v1"
KINDS = ("trading_deadline", "veteran_waivers")
NO_PROPOSAL = "No proposal is on record."
NO_ANSWER = "No answer is required."
ENTRY_KEYS = {"key", "kind", "title", "at", "date", "brought_by", "why", "status", "sources", "coming_up"}
# When a league date shows under COMING UP: the trading deadline from the brief of the last
# Jacksonville game before it (docs/rebuild_plan.md step 5, A5); a date with null shows nowhere.
SHOWN = ("last_game_before",)
LIMIT = re.compile(r"\bno (practice|return) before ([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)")


# ------------------------------------------------------------------ the season's record
def path(season, root):
    return SeasonPaths(season, Path(root)).league_dates


def load(season, root):
    """The season's league-dates record, or None when the season has none."""
    target = path(season, root)
    if not target.is_file():
        return None
    return json.loads(target.read_text(encoding="utf-8"))


def league_date(season, name, root):
    """The entry of the season's record whose key or kind is ``name``, or None."""
    data = load(season, root)
    return next((e for e in (data or {}).get("dates") or () if name in (e.get("key"), e.get("kind"))), None)


def trading_deadline(season, root):
    """The season's trading deadline (a datetime, ET), or None when the season records none."""
    entry = league_date(season, "trading_deadline", root)
    return open_events.parse_at(entry["at"]) if entry and entry.get("at") else None


def waivers_from(season, root):
    """The first day a released vested veteran is subject to waivers for the rest of the season (a
    date), or None when the season records none (the transaction checks read it)."""
    entry = league_date(season, "veteran_waivers", root)
    return dt.date.fromisoformat(entry["date"]) if entry and entry.get("date") else None


# ------------------------------------------------------------------ the windows
def _source(entry):
    sources = entry.get("sources") or []
    page = next((s for s in sources if str(s.get("path", "")).startswith("career/")), None)
    return dict(page or (sources[0] if sources else {}))


def _open_calls(season, issued_at, root, job):
    """The trade calls known to Stone open at ``issued_at``: raised by then and not yet resolved."""
    out = []
    for record in open_events.load(season, root):
        if record.get("kind") != "trade_talks" or not open_events.known_to_stone(record, job):
            continue
        if open_events.parse_at(record["raised"]["at"]) > issued_at:
            continue
        res = record.get("resolution")
        if res is not None and open_events.parse_at(res["at"]) <= issued_at:
            continue
        out.append(record)
    return out


def _deadline_window(season, entry, issued_at, root, job):
    deadline = open_events.parse_at(entry["at"])
    if issued_at >= deadline:
        return None
    games = [g for g in open_events.club_fixtures(season, root, issued_at.date())
             if open_events.kickoff(g) < deadline]
    if not games:
        return None
    games.sort(key=open_events.kickoff)
    start = open_events.kickoff(games[-2]) if len(games) > 1 else None
    if start is not None and issued_at < start:
        return None
    calls = _open_calls(season, issued_at, root, job)
    if calls:
        state = "Open: %s." % "; ".join(
            "the trade call from %s, %s" % (r["subject"], "due %s" % open_events.at_text(
                open_events.parse_at(r["deadline"]["at"])) if r.get("deadline") else "no due time set")
            for r in calls)
    else:
        state = NO_PROPOSAL
    return {"key": entry["key"], "title": entry["title"], "at": entry["at"], "date": None, "why": entry["why"],
            "state": state, "action": NO_ANSWER, "source": _source(entry)}


def _name_key(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


def eligibility_windows(season, issued_at, root):
    """Each player's windows from the roster record's availability note ("no practice before
    October 20, no return before November 3"), for a brief issued at ``issued_at``: the ones whose
    date is still to come."""
    from . import roster as roster_record, season_summary
    paths = SeasonPaths(season, Path(root))
    if not paths.roster.is_file():
        return []
    data = roster_record.load(paths.roster)
    out = []
    for row in data.get("players") or ():
        text = row.get("availability") or ""
        if not season_summary.under_instruction(row):
            continue
        for what, when in LIMIT.findall(text):
            day = season_summary.date_on(when, issued_at.date())
            if issued_at >= open_events.et(day):
                continue
            words = "%s %d" % (day.strftime("%B"), day.day)
            title = "%s's %s window" % (row["name"], "practice" if what == "practice" else "return")
            status = str(row.get("status") or row.get("list") or "").rstrip(".")
            out.append({"key": "%s-%s-%s" % (_name_key(row["name"]), what, day.isoformat()), "title": title,
                        "at": None, "date": day.isoformat(),
                        "why": "Eligibility: the medical communication sets no %s before %s." % (what, words),
                        "state": (status[:1].upper() + status[1:] + ".") if status else "On the roster record.",
                        "action": NO_ANSWER,
                        "source": {"path": paths.roster_page.relative_to(Path(root).resolve()).as_posix()}})
    return out


def coming_up(season, issued_at, root):
    """The windows a brief issued at ``issued_at`` shows under COMING UP, soonest first."""
    root = Path(root).resolve()
    job = current_job.load(root)
    out = []
    data = load(season, root)
    for entry in (data or {}).get("dates") or ():
        if entry.get("coming_up") == "last_game_before" and entry.get("kind") == "trading_deadline":
            window = _deadline_window(season, entry, issued_at, root, job)
            if window is not None:
                out.append(window)
    out += eligibility_windows(season, issued_at, root)

    def when(w):
        return open_events.parse_at(w["at"]) if w.get("at") else open_events.et(dt.date.fromisoformat(w["date"]))
    return sorted(out, key=lambda w: (when(w), w["key"]))


# ------------------------------------------------------------------ validation
def validation_errors(root):
    """The active season's league-dates record against its form: each date sourced (every source
    resolves), its time or day in ET, its kind known, the party who brings it in the job record,
    its keys unique (the lead wires this into scripts/validate_repository.py)."""
    from .events import repository_map
    root = Path(root).resolve()
    mapping = repository_map(root)
    season = int(mapping["active_season"])
    target = path(season, root)
    if not target.is_file():
        return []
    rel = target.relative_to(root).as_posix()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        job = current_job.load(root)
    except (OSError, ValueError) as exc:
        return ["League dates: %s cannot be read: %s" % (rel, exc)]
    errors = []
    say = lambda text: errors.append("League dates: %s" % text)
    if data.get("schema") != SCHEMA or data.get("season") != season:
        say("%s must be %s for the %d season" % (rel, SCHEMA, season))
    keys = []
    for n, entry in enumerate(data.get("dates") or ()):
        where = "entry %d" % (n + 1)
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            say("%s must hold exactly %s" % (where, ", ".join(sorted(ENTRY_KEYS))))
            continue
        keys.append(entry["key"])
        if entry["kind"] not in KINDS:
            say("%s kind must be one of %s" % (where, ", ".join(KINDS)))
        if not str(entry["key"]).startswith("%d-" % season):
            say("%s key must begin with its season" % where)
        if (entry["at"] is None) == (entry["date"] is None):
            say("%s has a time (at) or a day (date), not both" % where)
        try:
            day = open_events.parse_at(entry["at"]).date() if entry["at"] else dt.date.fromisoformat(entry["date"])
            if day.year not in (season, season + 1):
                say("%s is not a date of the %d season" % (where, season))
        except (TypeError, ValueError) as exc:
            say("%s time: %s" % (where, exc))
        if entry["brought_by"] not in (job.get("parties") or {}):
            say("%s brought_by %r is not a party in the job record" % (where, entry["brought_by"]))
        if entry["coming_up"] is not None and entry["coming_up"] not in SHOWN:
            say("%s coming_up must be one of %s, or null" % (where, ", ".join(SHOWN)))
        if entry["coming_up"] is not None and entry["kind"] != "trading_deadline":
            say("%s: only the trading deadline is shown under COMING UP" % where)
        if not entry["sources"]:
            say("%s needs its sources" % where)
        for source in entry["sources"] or ():
            problem = current_job.record_error(root, mapping, source)
            if problem:
                say("%s source: %s" % (where, problem))
        for field in ("title", "why"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                say("%s needs its %s" % (where, field))
    for key in sorted({k for k in keys if keys.count(k) > 1}):
        say("%s is recorded twice" % key)
    return errors
