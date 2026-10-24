"""The league's head coaches in season, and the weekly check for a change at every club.

Rebuild step 5, D2 (docs/event_inserts.md, section D; docs/season_end.md, section C, "How the club
decides"). One method for all 32 clubs, Jacksonville included, adopted by the user on October 23,
2026 ("One draw for all 32 (Recommended)"): after each closed week of the regular season, each
club that played is drawn once from a sourced per-game rate of in-season head-coach changes in
the real 2002 to 2012 seasons (library/data/2012_hc_inseason_hazard.json, two passes), keyed on
the club's losses minus wins after the game and on whether its coach is in his first season with
the club. The method is ``method.json`` in the season's head-coach changes folder (the data twin
of SeasonPaths.coaching_changes); each week's check is ``week_NN.json`` beside it. The draw itself
is made by scripts/coaching_check.py through the private client; this module reads the records,
builds the inputs and the pages, and validates them.

A career-layer module (tests/test_career_layer_isolation.py, ``LAYER``): it reads the job record,
the decision queue (to see which periods have opened) and the event store, and writes the
head-coach-change news events. No game module imports it and no game input reads its records.

Nothing the draw reads names the protagonist: the inputs are each club's record from the closed
games and whether its head coach changed in January; coach names are labels on the records and
pages only. The club the job holder coaches is drawn the same way; only what follows a drawn
change differs, as the user's answer says (Khan and Caldwell's decision, written as the Club
Decision in step 6; until step 6's pages exist the career holds with a plain message).
"""
from __future__ import annotations

from collections import Counter, namedtuple
from datetime import date, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import re

from . import current_job, decision_queue
from .open_events import raise_event, resolve as resolve_event
from .decisions import BY_KIND, NEWS_KIND, event_folder, event_store, file_name, name_part
from .events import EVENT_META
from .packets import canonical
from .player_bios import master_date
from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
METHOD_SCHEMA = "inseason-hc-change-2014-v1"
CHECK_SCHEMA = "inseason-hc-check-v1"
TABLE_SCHEMA = "hc-inseason-hazard-v1"
STATUSES = ("awaiting the user's answer", "adopted")
KIND = "head_coach_change"
INTERIM = "an interim head coach from its staff"
METHOD_FILE = "method.json"
INDEX = "README.md"
# The record of a week's check: its draw inputs are these fields of each club drawn.
INPUT_FIELDS = ("club", "game", "wins", "losses", "ties", "tenure")
ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
            "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth")
ClubGame = namedtuple("ClubGame", "week date us them")


# ------------------------------------------------------------------ places and records
def folder(season, root=ROOT):
    """The season's head-coach changes page folder (its index and one page per change)."""
    return SeasonPaths(season, root).coaching_changes


def data_folder(season, root=ROOT):
    paths = SeasonPaths(season, root)
    return paths.data_for(paths.coaching_changes)


def method_path(season, root=ROOT):
    return data_folder(season, root) / METHOD_FILE


def week_path(season, week, root=ROOT):
    return data_folder(season, root) / ("week_%02d.json" % week)


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rel(root, path):
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def load_method(season, root=ROOT):
    """The season's method, or None when the season has none."""
    path = method_path(season, root)
    return _json(path) if path.is_file() else None


def adopted(method):
    return bool(method) and method.get("status") == "adopted"


def load_table(method, root=ROOT):
    return _json(Path(root) / method["table"]["file"])


def checks(season, root=ROOT):
    """{week: the week's check record} for every week checked so far."""
    out = {}
    for path in sorted(data_folder(season, root).glob("week_[0-9][0-9].json")):
        record = _json(path)
        out[record["week"]] = record
    return out


def event_id(season, week):
    """The private event of a week's check."""
    return "%d-week-%02d-head-coach-check" % (season, week)


# ------------------------------------------------------------------ the closed games
def closed_games(season, root=ROOT):
    """{club: [ClubGame]} from the season's closed regular-season games, in week order, each dated
    by its fixture."""
    paths = SeasonPaths(season, root)
    dates = {g["game_id"]: g["date"] for g in paths.regular_games()}
    out = {}
    for path in sorted(paths.receipts.glob("*.json")):
        r = _json(path)
        if r.get("season") != season or type(r.get("week")) is not int:
            continue
        when = dates.get(r["event_id"])
        if when is None:
            raise ValueError("a closed game is not a dated fixture: %s" % r["event_id"])
        for us, them in ((r["away"], r["home"]), (r["home"], r["away"])):
            out.setdefault(us, []).append(ClubGame(r["week"], when, r["final_score"][us], r["final_score"][them]))
    for games in out.values():
        games.sort()
    return out


def closed_weeks(season, root=ROOT):
    """The regular-season weeks every one of whose fixtures has closed."""
    paths = SeasonPaths(season, root)
    scheduled = Counter(g["week"] for g in paths.regular_games())
    played = Counter()
    for path in paths.receipts.glob("*.json"):
        r = _json(path)
        if r.get("season") == season and type(r.get("week")) is int:
            played[r["week"]] += 1
    return sorted(w for w in scheduled if played[w] == scheduled[w])


def record_after(games, week):
    """(game number, wins, losses, ties, date) after the club's last game through ``week``."""
    played = [g for g in games if g.week <= week]
    wins = sum(g.us > g.them for g in played)
    losses = sum(g.us < g.them for g in played)
    return len(played), wins, losses, len(played) - wins - losses, played[-1].date


def record_text(wins, losses, ties):
    return "%d-%d-%d" % (wins, losses, ties) if ties else "%d-%d" % (wins, losses)


# ------------------------------------------------------------------ the January changes and the coaches
def january(method, root=ROOT):
    """{club: {"changed": bool, "coach": his 2013 head coach, "hire": the January hire's name or
    None}} from the January head-coach changes of the league year. A club the January draws left
    out is read from the method's ``january_retained`` (its own January decision kept its coach)."""
    out = {}
    for rel in method["inputs"]["january_changes"]:
        for row in _json(Path(root) / rel)["head_coach_changes"]:
            if row.get("changed") is None:      # deferred: drawn in the later file
                continue
            hire = None
            if row["changed"] and row.get("hired_from") not in (None, "external"):
                found = re.search(r"\(([^()]+)\)\s*$", row["hired_from"])
                hire = found[1] if found else None
            out[row["club"]] = {"changed": bool(row["changed"]), "coach": row["coach"], "hire": hire}
    for club, why in method["inputs"].get("january_retained", {}).items():
        if club in out:
            raise ValueError("%s is both drawn in January and retained by its own decision" % club)
        out[club] = {"changed": False, "coach": None, "hire": None, "retained": why}
    return out


def tenures(method, root=ROOT):
    """{club: "first season" or "later season"} for the season's head coaches before any in-season
    change: first when the club changed its head coach in January."""
    return {club: ("first season" if row["changed"] else "later season") for club, row in january(method, root).items()}


def holder_club(root=ROOT):
    """The club whose head coach the job record's holder is, or None."""
    job = current_job.load(root)
    if job.get("status") != "EMPLOYED":
        return None
    appt = current_job.appointment(job)
    if not appt or appt.get("role") != "head_coach":
        return None
    return appt["employer"]["club"]


def coach_names(method, root=ROOT):
    """{club: the name of its head coach when the season opened, or None for an unnamed outside
    hire}: labels for the records and pages, never an input of the draw."""
    names = {club: (row["hire"] if row["changed"] else row["coach"]) for club, row in january(method, root).items()}
    club = holder_club(root)
    if club is not None:
        job = current_job.load(root)
        names[club] = current_job.party_name(job, job["holder"])
    return names


def head_coach(club, day, season=None, root=ROOT):
    """The club's head coach on ``day`` (a date or ISO date, never after the master date):
    {"club", "name" (None when unnamed), "description", "interim"}. The season is the league year
    the day belongs to (from March), or the season named."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    season = (day.year if day.month >= 3 else day.year - 1) if season is None else season
    if day > master_date(root):
        raise ValueError("%s is after the master date; no later head coach is known" % day.isoformat())
    method = load_method(season, root)
    if method is None:
        raise ValueError("no head-coach method for %d" % season)
    for record in checks(season, root).values():
        for row in record["clubs"]:
            if row["club"] == club and row["changed"] and date.fromisoformat(row["effective"]) <= day:
                return {"club": club, "name": None, "description": INTERIM, "interim": True}
    name = coach_names(method, root).get(club)
    return {"club": club, "name": name, "interim": False,
            "description": name if name else "a head coach hired from outside the club in January"}


# ------------------------------------------------------------------ the draw
def band(margin):
    return "0 or fewer" if margin <= 0 else "1 to 2" if margin <= 2 else "3 to 4" if margin <= 4 else "5 or more"


def cell(row):
    return band(row["losses"] - row["wins"]) + "|" + row["tenure"]


def changed_before(season, week, root=ROOT, records=None):
    """The clubs whose change was drawn in a check of an earlier week."""
    records = checks(season, root) if records is None else records
    return {r["club"] for w, rec in records.items() if w < week for r in rec["clubs"] if r["changed"]}


def week_inputs(season, week, root=ROOT, method=None, records=None, games=None):
    """The draw inputs of a week's check: each club that played that week, in alphabetical order,
    with its game number, its record after the game and its coach's season with the club; and the
    clubs that played but are not drawn, with the reason. A club on its bye has no line."""
    method = load_method(season, root) if method is None else method
    table = load_table(method, root)
    last = table["games_at_risk"]["last"]
    games = closed_games(season, root) if games is None else games
    tenure = tenures(method, root)
    before = changed_before(season, week, root, records)
    clubs, not_drawn = [], []
    for club in sorted(games):
        if not any(g.week == week for g in games[club]):
            continue
        if club not in tenure:
            raise ValueError("%s has no January head-coach record" % club)
        game, wins, losses, ties, _ = record_after(games[club], week)
        if club in before:
            not_drawn.append({"club": club, "reason": "changed earlier this season"})
        elif game > last:
            not_drawn.append({"club": club, "reason": "its last regular-season game; a change after it is the season-end draw's"})
        else:
            clubs.append({"club": club, "game": game, "wins": wins, "losses": losses, "ties": ties,
                          "tenure": tenure[club]})
    return {"season": season, "week": week, "clubs": clubs, "not_drawn": not_drawn}


def inputs_digest(inputs):
    return hashlib.sha256(canonical(inputs)).hexdigest()


def packet(method, inputs, snapshot, root, code):
    """The private event's packet, the January carousel's pattern."""
    return {"procedure": method["procedure"], "event_id": event_id(inputs["season"], inputs["week"]),
            "snapshot": snapshot, "method_sha256": _digest(method_path(inputs["season"], root)),
            "table_sha256": _digest(Path(root) / method["table"]["file"]), "code_sha256": code,
            "inputs_sha256": inputs_digest(inputs)}


def draw(inputs, table, uniform):
    """Each club at risk with its cell, chance and number from ``uniform`` (one call each, in order),
    changed when the number falls below the chance."""
    rows = []
    for row in inputs["clubs"]:
        key = cell(row)
        chance = table["rates"][key]["rate"]
        number = uniform()
        rows.append(dict(row, cell=key, chance=chance, draw=number, changed=number < chance))
    return rows


def effective_on(games, after_week):
    """The day after the club's latest closed game through ``after_week``."""
    return (date.fromisoformat(record_after(games, after_week)[4]) + timedelta(days=1)).isoformat()


def build_record(method, inputs, pkt, ref, rows, order, root, after_week, games=None, recorded_on=None):
    """The week's check record from the drawn rows: when it was drawn (the master date, the latest
    closed week and the latest period open), its packet and private reference, and every club."""
    season = inputs["season"]
    games = closed_games(season, root) if games is None else games
    names = coach_names(method, root)
    clubs = []
    for row in rows:
        row = dict(row, coach=names.get(row["club"]))
        if row["changed"]:
            game, wins, losses, ties, when = record_after(games[row["club"]], after_week)
            row["effective"] = effective_on(games[row["club"]], after_week)
            row["at_change"] = {"game": game, "wins": wins, "losses": losses, "ties": ties, "date": when}
        clubs.append(row)
    return {"schema_version": CHECK_SCHEMA, "season": season, "week": inputs["week"],
            "event_id": pkt["event_id"], "order": order,
            "retroactive": inputs["week"] in method.get("retroactive", {}).get("weeks", ()),
            "recorded_on": (recorded_on or master_date(root)).isoformat(), "after_week": after_week,
            "opened_through": max(opened_periods(season, root) | {after_week}),
            "packet": pkt, "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(), "result_ref": ref,
            "clubs": clubs, "not_drawn": inputs["not_drawn"]}


# ------------------------------------------------------------------ what is due
def at_risk_weeks(season, root=ROOT, method=None):
    """The closed weeks in which some club played a game the table covers (its games 1 to 15): the
    weeks a check is due for. A week whose every game is a club's last (Week 17) has none."""
    method = load_method(season, root) if method is None else method
    last = load_table(method, root)["games_at_risk"]["last"]
    games = closed_games(season, root)
    out = []
    for week in closed_weeks(season, root):
        if any(record_after(g, week)[0] <= last for g in games.values() if any(x.week == week for x in g)):
            out.append(week)
    return out


def due_weeks(season, root=ROOT, through=None):
    """The closed weeks still to check, in order, through ``through`` (all closed weeks when None):
    nothing while the method is not adopted."""
    method = load_method(season, root)
    if not adopted(method):
        return []
    done = checks(season, root)
    return [w for w in at_risk_weeks(season, root, method) if w not in done and (through is None or w <= through)]


def due_point(method, week):
    """The period whose opening the check of ``week`` must precede: the next week's, or for a
    retroactive week the period after the week its checks precede."""
    retro = method.get("retroactive", {})
    if week in retro.get("weeks", ()):
        return retro["due_before_check_of_week"] + 1
    return week + 1


_WEEK_ITEM = re.compile(r"^(\d{4})-w(\d{2})-")
_WEEK_HOLDS = {"week_inputs", "week_close", "call_sheet_part", "bye_close"}


def opened_periods(season, root=ROOT):
    """The weeks whose period has opened: the week's brief issued or its practice record written,
    one of its own decision items in the queue, or the week closed."""
    paths = SeasonPaths(season, root)
    weeks = set(closed_weeks(season, root))
    for week in sorted({g["week"] for g in paths.regular_games()}):
        if (paths.week_data(week) / "briefings.json").is_file() or paths.practice_log(week).is_file():
            weeks.add(week)
    queue_path = Path(root) / decision_queue.QUEUE
    if queue_path.is_file():
        for item in _json(queue_path).get("items", []):
            found = _WEEK_ITEM.match(str(item.get("id", "")))
            if found and int(found[1]) == season:
                weeks.add(int(found[2]))
            deadline = item.get("deadline") or {}
            for ref in [deadline.get("before") or {}] + list(item.get("blocks") or []):
                if ref.get("kind") in _WEEK_HOLDS and ref.get("season") == season and type(ref.get("week")) is int:
                    weeks.add(ref["week"])
    return weeks


def first_practice_day(season, week, root=ROOT, job=None):
    """The day of Week ``week``'s first practice: the first session the standing practice
    instruction sets for the week, or, for a week it does not set (the bye, a Thursday game, a week
    before it applies), the first day of the week's practice span (runtime/practices.week_span)."""
    from . import practices
    job = current_job.load(root) if job is None else job
    try:
        schedule = practices.schedule_from_instruction(current_job.practice_instruction(job, season), season, week,
                                                       root)
        if schedule["sessions"]:
            return date.fromisoformat(schedule["sessions"][0]["date"])
    except practices.NotCovered:
        pass
    # A week the instruction does not set is asked on My Responses: once Stone's "Practice week"
    # answer is applied, its first session is the week's first practice.
    from scripts.record_practice_week import answered_schedule
    answered = answered_schedule(root, season, week)
    if answered and answered["sessions"]:
        return min(date.fromisoformat(s["date"]) for s in answered["sessions"])
    return practices.week_span(season, week, root)[0]


def practice_weeks_opened(season, root=ROOT):
    """The weeks whose practice week has opened: the week closed, its practice record written, or the
    master date past the day of its first practice. A brief issued or an item opened for the week
    does not count: both open at the previous week's close, before that week's check is drawn."""
    paths = SeasonPaths(season, root)
    weeks = set(closed_weeks(season, root))
    today = master_date(root)
    job = current_job.load(root)
    for week in sorted({g["week"] for g in paths.regular_games()}):
        if week in weeks:
            continue
        if paths.practice_log(week).is_file():
            weeks.add(week)
            continue
        try:
            if today > first_practice_day(season, week, root, job):
                weeks.add(week)
        except ValueError:
            continue
    return weeks


def coverage_errors(root=ROOT, season=None):
    """Every closed week's check is recorded before the practice week it must precede opens (the
    next week's; for the retroactive Weeks 1 to 5, Week 7's, since they come before Week 6's check),
    and the checks were made in week order. The next week's brief and items open at the close,
    before the check runs, so they do not count (``practice_weeks_opened``). Nothing is due while the
    method is not adopted."""
    root = Path(root)
    season = _season(root) if season is None else season
    method = load_method(season, root)
    if not adopted(method):
        return []
    done = checks(season, root)
    opened = practice_weeks_opened(season, root)
    latest = max(opened) if opened else 0
    errors = []
    due = at_risk_weeks(season, root, method)
    for week in due:
        if week not in done and latest >= due_point(method, week):
            errors.append("Week %d's head-coach check is missing, and Week %d's practice week has opened; "
                          "scripts/coaching_check.py %d --season %d --close draws every week due, in order"
                          % (week, latest, max(due), season))
    order = [done[w]["order"] for w in sorted(done)]
    if order != list(range(1, len(order) + 1)):
        errors.append("the head-coach checks were not made in week order: %s" % order)
    for w in done:
        missing = [x for x in due if x < w and x not in done]
        if missing:
            errors.append("Week %d's head-coach check was made before Week %s's" % (w, missing))
    return errors


def _season(root):
    return int(json.loads((Path(root) / "docs/repository_map.json").read_text(encoding="utf-8"))["active_season"])


# ------------------------------------------------------------------ the held career
def held_changes(season, root=ROOT):
    """The drawn changes at the club the job holder coaches, while step 6's pages do not exist."""
    if BY_KIND["season_end"].implemented:
        return []
    club = holder_club(root)
    return [(record["week"], row) for record in checks(season, root).values() for row in record["clubs"]
            if row["changed"] and row["club"] == club]


def career_hold(season, root=ROOT):
    """The plain message that holds the career, or None."""
    held = held_changes(season, root)
    if not held:
        return None
    week, row = held[0]
    when = date.fromisoformat(row["effective"])
    return ("The Week %d head-coach check drew a change at %s, effective %s %d, %d. It is Shad Khan and David "
            "Caldwell's decision (Document 3, row 1), written as the Club Decision, whose pages are built in step 6 "
            "of the rebuild plan; the career holds here until they exist. Nothing further is opened, played or "
            "drawn." % (week, row["club"], when.strftime("%B"), when.day, when.year))


def hold_errors(root=ROOT, season=None):
    """The hold, once a period after the ones open at the held check has opened or the clock has
    moved past the day it was drawn."""
    season = _season(root) if season is None else season
    held = held_changes(season, root)
    if not held:
        return []
    record = checks(season, root)[held[0][0]]
    moved = any(w > record["opened_through"] for w in opened_periods(season, root))
    later = master_date(root) > date.fromisoformat(record["recorded_on"])
    return [career_hold(season, root)] if moved or later else []


# ------------------------------------------------------------------ pages and news
def _long(day):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return "%s %d, %d" % (day.strftime("%B"), day.day, day.year)


def _weekday(day):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return "%s, %s" % (day.strftime("%A"), _long(day))


def page_path(season, row, root=ROOT):
    """A change's dated page: Head_Coach_Change_<date>_<Club>.md (a club changes once a season)."""
    stem = file_name(NEWS_KIND[KIND].result)[:-len(".md")]
    return event_folder(KIND, season, root) / ("%s_%s_%s.md" % (stem, row["effective"], name_part(row["club"])))


def news_id(row):
    slug = re.sub(r"[^a-z0-9]+", "-", row["club"].lower()).strip("-")
    return "%s-head-coach-change-%s" % (row["effective"], slug)


def _coach_words(row):
    """The head coach as the pages name him: his name, or for an unnamed coach how he came."""
    if row.get("coach"):
        return row["coach"]
    return "Hired from outside the club in January" if row["tenure"] == "first season" else "Not named in the record"


def possessive(club):
    return club + "'" if club.endswith("s") else club + "'s"


def summary(row):
    """The change's one line in the annual record."""
    at = row["at_change"]
    return ("The %s made a change at head coach after a %s record in their first %s games; an interim head coach "
            "from the club's staff takes over." % (row["club"], record_text(at["wins"], at["losses"], at["ties"]),
                                                   _count(at["game"])))


NUMBERS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
           "thirteen", "fourteen", "fifteen", "sixteen", "seventeen")


def _count(n):
    return NUMBERS[n - 1]


def effective_changes(season, root=ROOT, through=None):
    """(week record, row) of every drawn change, other than one the career holds on, effective on
    or before ``through`` (the master date by default)."""
    through = master_date(root) if through is None else through
    held = {(w, r["club"]) for w, r in held_changes(season, root)}
    out = []
    for record in checks(season, root).values():
        for row in record["clubs"]:
            if row["changed"] and (record["week"], row["club"]) not in held and \
                    date.fromisoformat(row["effective"]) <= through:
                out.append((record, row))
    return sorted(out, key=lambda p: (p[1]["effective"], p[1]["club"]))


def change_page(season, record, row, root=ROOT):
    """The text of a change's dated page (foundation/templates/event_inserts/event_result_template.md)."""
    at = row["at_change"]
    paths = SeasonPaths(season, root)
    page = page_path(season, row, root)
    standings = Path(os.path.relpath(paths.record("standings.md"), page.parent)).as_posix()
    if row.get("coach"):
        coach = "their head coach, %s" % row["coach"]
    elif row["tenure"] == "first season":
        coach = "their head coach, hired from outside the club in January"
    else:
        coach = "their head coach"
    meta = {"date": row["effective"], "id": news_id(row), "season": season, "status": "closed", "summary": summary(row)}
    lines = [
        "# Head Coach Change: %s" % row["club"], "",
        "**Event date:** %s" % _weekday(row["effective"]), "",
        "**Resolved on:** %s" % _weekday(row["effective"]), "",
        "**Involving:** The %s and %s." % (row["club"], coach), "",
        "**What happened:** The %s made a change at head coach on %s, the day after their %s game of the season, "
        "which left them %s. An interim head coach from the club's staff takes over." % (
            row["club"], _long(row["effective"]), ORDINALS[at["game"] - 1],
            record_text(at["wins"], at["losses"], at["ties"])), "",
        "**Stone's answer:** No response required.", "",
        "**Final decision:** The %s own decision." % possessive(row["club"]), "",
        "**Outcome:** Executed.", "",
        "**Changes effective:** From %s, an interim head coach from the %s staff leads the club for the rest of "
        "the season." % (_long(row["effective"]), possessive(row["club"])), "",
        "**Outstanding issue:** None.", "",
        "**Source records:** [Head-coach changes this season](%s) and [the standings](%s)." % (INDEX, standings), "",
        "<!-- event-record: %s -->" % json.dumps(meta, sort_keys=True),
    ]
    return "\n".join(lines) + "\n"


def index_page(season, root=ROOT, through=None):
    """The folder's index, or None before the first check."""
    records = checks(season, root)
    if not records:
        return None
    method = load_method(season, root)
    lines = ["# Head-coach changes, %d" % season, "",
             "Every club's head coach, Jacksonville's included, is checked in the same way after each of the club's "
             "regular-season games: from the club's record after the game and whether the coach is in his first "
             "season with the club. A club that changes its head coach is not checked again that season, and the "
             "change takes effect the day after the club's game.", "", "## Changes", ""]
    changes = effective_changes(season, root, through)
    if changes:
        lines += ["| Date | Club | Head coach | Record at the change | Takes over |", "|---|---|---|---|---|"]
        for record, row in changes:
            at = row["at_change"]
            lines.append("| %s | [%s](%s) | %s | %s | An interim head coach from the club's staff |" % (
                _long(row["effective"]), row["club"], page_path(season, row, root).name,
                _coach_words(row), record_text(at["wins"], at["losses"], at["ties"])))
    else:
        lines.append("No club has changed its head coach this season.")
    lines += ["", "## Weeks checked", "", "| Week | Checked | Clubs checked |", "|---|---|--:|"]
    for week in sorted(records):
        lines.append("| Week %d | %s | %d |" % (week, _long(records[week]["recorded_on"]), len(records[week]["clubs"])))
    retro = sorted(w for w in records if records[w].get("retroactive"))
    if retro:
        weeks = method["retroactive"]["weeks"]
        lines += ["", "Weeks %d to %d closed before the check began. They were checked once, in order, before Week %d's "
                      "check; a change from one of them takes effect the day after the club's latest game." % (
                          weeks[0], weeks[-1], method["retroactive"]["due_before_check_of_week"])]
    return "\n".join(lines) + "\n"


def pages(season, root=ROOT, through=None):
    """{path: text} of the folder's index and of each change page the clock has reached."""
    out = {}
    text = index_page(season, root, through)
    if text is not None:
        out[folder(season, root) / INDEX] = text
    for record, row in effective_changes(season, root, through):
        out[page_path(season, row, root)] = change_page(season, record, row, root)
    return out


def news_event(season, record, row, root=ROOT):
    """(event, resolution): the head-coach-change news event (open-event-v1) of an effective change,
    raised open, and the resolution that closes it with its page. Decided by the other club,
    brought to Stone by the communications staff, FOR YOUR INFORMATION only."""
    page = page_path(season, row, root)
    week_file = _rel(root, week_path(season, record["week"], root))
    index = record["clubs"].index(row)
    at = et_datetime(row["effective"])
    point = lambda key: {"path": week_file, "pointer": "/clubs/%d/%s" % (index, key)}
    facts = [{"label": "Club", "value": row["club"], "source": point("club")},
             {"label": "Head coach", "value": _coach_words(row), "source": point("coach")},
             {"label": "Record at the change", "value": record_text(row["at_change"]["wins"], row["at_change"]["losses"],
                                                                    row["at_change"]["ties"]),
              "source": point("at_change")},
             {"label": "Effective", "value": _long(row["effective"]), "source": point("effective")},
             {"label": "Takes over", "value": "An interim head coach from the club's staff",
              "source": {"path": _rel(root, method_path(season, root)), "pointer": "/effect/successor"}}]
    event = {
        "id": news_id(row), "kind": KIND, "season": season, "subject": row["club"],
        "raised": {"at": at, "by": "communications_staff",
                   "source": {"path": _rel(root, folder(season, root) / INDEX), "anchor": "changes"}},
        "known_to": ["stone", "khan", "caldwell"],
        "authority": {"rows": ["1"], "decides": "other_club"}, "stone_part": "none",
        "summary": {"text": summary(row), "author": "communications_staff", "date": row["effective"]},
        "staff_position": None, "consequence": None, "facts": facts, "options": [], "deadline": None,
        "state": "open",
        "process": [{"at": at, "kind": "criteria", "by": "other_club",
                     "what": ("The league's weekly head-coach check after the club's game, the one method all 32 "
                              "clubs share: the club's record after the game and its coach's season with the club."),
                     "source": {"path": week_file, "pointer": "/clubs/%d" % index}}],
        "queue_item": None, "response": None, "resolution": None,
    }
    resolution = {"at": at, "outcome": "executed", "by": "other_club",
                  "decision": {"text": "The club changed its head coach; an interim head coach from its staff takes over.",
                               "author": "other_club", "date": row["effective"], "criteria": 0},
                  "result_page": _rel(root, page)}
    return event, resolution


def et_datetime(day):
    """The start of ``day`` in ET with its offset (-04:00 in daylight time, from the second Sunday of
    March to the first Sunday of November, -05:00 otherwise)."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    march = date(day.year, 3, 8)
    start = march + timedelta(days=(6 - march.weekday()) % 7)
    november = date(day.year, 11, 1)
    end = november + timedelta(days=(6 - november.weekday()) % 7)
    offset = "-04:00" if start <= day < end else "-05:00"
    return datetime(day.year, day.month, day.day).isoformat() + offset




def stored_news(season, root=ROOT):
    """{id: record} of the season's head-coach-change news events in the event store."""
    store = event_store(KIND, season, root)
    return {p.stem: _json(p) for p in sorted(store.glob("*.json"))} if store.is_dir() else {}


# ------------------------------------------------------------------ validation
def method_errors(season, root=ROOT, method=None):
    method = load_method(season, root) if method is None else method
    if method is None:
        return []
    errors = []
    if method.get("schema_version") != METHOD_SCHEMA:
        errors.append("head-coach method: schema %r" % method.get("schema_version"))
    if method.get("status") not in STATUSES:
        errors.append("head-coach method: status %r" % method.get("status"))
    if adopted(method):
        given = method.get("adopted") or {}
        if not given.get("user_words") or not given.get("user_date"):
            errors.append("head-coach method: adopted without the user's words and date")
    table_file = Path(root) / method["table"]["file"]
    if not table_file.is_file():
        return errors + ["head-coach method: rate table missing: %s" % method["table"]["file"]]
    if _digest(table_file) != method["table"]["sha256"]:
        errors.append("head-coach method: the rate table differs from the digest the method records")
    table = _json(table_file)
    if table.get("schema_version") != TABLE_SCHEMA or table.get("source", {}).get("sha256") != method["table"]["source"]["sha256"]:
        errors.append("head-coach method: the rate table is not the sourced in-season table")
    retro = method.get("retroactive")
    if retro and (not retro.get("user_words") or not all(type(w) is int for w in retro.get("weeks", ()))
                  or type(retro.get("due_before_check_of_week")) is not int):
        errors.append("head-coach method: the retroactive weeks are not recorded with the user's answer")
    try:
        clubs = {g["away"] for g in SeasonPaths(season, root).regular_games()} | \
                {g["home"] for g in SeasonPaths(season, root).regular_games()}
        missing = sorted(clubs - set(january(method, root)))
        if missing:
            errors.append("head-coach method: no January head-coach record for %s" % ", ".join(missing))
    except (OSError, ValueError, KeyError) as exc:
        errors.append("head-coach method: January head-coach changes unreadable: %s" % exc)
    return errors


def record_errors(season, root=ROOT, method=None):
    """Each week's check against its method, its table, the closed games and its draws."""
    method = load_method(season, root) if method is None else method
    records = checks(season, root)
    if not records:
        return []
    if not adopted(method):
        return ["head-coach checks are recorded while the method is not adopted"]
    errors = []
    table = load_table(method, root)
    method_digest = _digest(method_path(season, root))
    table_digest = _digest(Path(root) / method["table"]["file"])
    games = closed_games(season, root)
    for week in sorted(records):
        record = records[week]
        label = "Week %d head-coach check" % week
        if record.get("schema_version") != CHECK_SCHEMA or record.get("season") != season:
            errors.append("%s: schema or season" % label)
            continue
        pkt = record["packet"]
        if pkt.get("method_sha256") != method_digest:
            errors.append("%s: the method changed after the draw" % label)
        if pkt.get("table_sha256") != table_digest:
            errors.append("%s: the rate table changed after the draw" % label)
        if pkt.get("event_id") != event_id(season, week) or record.get("event_id") != pkt.get("event_id"):
            errors.append("%s: event id" % label)
        if record.get("packet_sha256") != hashlib.sha256(canonical(pkt)).hexdigest():
            errors.append("%s: packet digest" % label)
        expected = week_inputs(season, week, root, method, {w: r for w, r in records.items() if w < week}, games)
        drawn = {"season": season, "week": week, "clubs": [{k: r[k] for k in INPUT_FIELDS} for r in record["clubs"]],
                 "not_drawn": record["not_drawn"]}
        if drawn != expected:
            errors.append("%s: its inputs differ from the closed games and the earlier checks" % label)
        if pkt.get("inputs_sha256") != inputs_digest(drawn):
            errors.append("%s: inputs digest" % label)
        for row in record["clubs"]:
            key = cell(row)
            if row.get("cell") != key or row.get("chance") != table["rates"][key]["rate"]:
                errors.append("%s: %s's cell or chance differs from the table" % (label, row["club"]))
            if row.get("changed") is not (row["draw"] < row["chance"]):
                errors.append("%s: %s's result differs from its number" % (label, row["club"]))
            if row["changed"]:
                if row.get("effective") != effective_on(games[row["club"]], record["after_week"]):
                    errors.append("%s: %s's change is not dated the day after its latest closed game" % (label, row["club"]))
                game, wins, losses, ties, when = record_after(games[row["club"]], record["after_week"])
                if row.get("at_change") != {"game": game, "wins": wins, "losses": losses, "ties": ties, "date": when}:
                    errors.append("%s: %s's record at the change" % (label, row["club"]))
            elif "effective" in row:
                errors.append("%s: %s has an effective date without a change" % (label, row["club"]))
        if type(record.get("after_week")) is not int or record["after_week"] < week:
            errors.append("%s: drawn before the week closed" % label)
        elif type(record.get("opened_through")) is not int or record["opened_through"] < record["after_week"]:
            errors.append("%s: the periods open at the draw are not recorded" % label)
        if type(record.get("order")) is not int or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("result_ref"))):
            errors.append("%s: order or private reference" % label)
        try:
            date.fromisoformat(record["recorded_on"])
        except (KeyError, TypeError, ValueError):
            errors.append("%s: the day it was drawn" % label)
    return errors


def page_errors(season, root=ROOT):
    """The index and each change page as their records build them; no page for a change the clock
    has not reached; and each effective change's news event in the event store."""
    from .clean_pages import text_errors
    errors = []
    expected = pages(season, root)
    for path, text in expected.items():
        rel = _rel(root, path)
        if not path.is_file():
            errors.append("%s is missing; run scripts/coaching_check.py --season %d --effective" % (rel, season))
        elif path.read_text(encoding="utf-8") != text:
            errors.append("%s is stale; run scripts/render_coaching_changes.py --season %d" % (rel, season))
        errors += text_errors(rel, text, root)
    there = folder(season, root)
    if there.is_dir():
        for path in sorted(there.glob("*.md")):
            if path not in expected:
                errors.append("%s is not built from a check the clock has reached" % _rel(root, path))
    news = stored_news(season, root)
    wanted = set()
    for record, row in effective_changes(season, root):
        wanted.add(news_id(row))
        event = news.get(news_id(row))
        if event is None:
            errors.append("the news of %s's head-coach change is not in the event store" % row["club"])
        elif (event.get("kind") != KIND or event.get("subject") != row["club"] or event.get("state") != "resolved"
              or (event.get("resolution") or {}).get("result_page") != _rel(root, page_path(season, row, root))):
            errors.append("the news of %s's head-coach change does not match its page" % row["club"])
    for extra in sorted(set(news) - wanted):
        errors.append("head-coach news %s has no effective change behind it" % extra)
    return errors


def validation_errors(root=ROOT, season=None):
    """Every check of the season's head-coach records (the lead wires this into
    scripts/validate_repository.py): the method, each week's check, the coverage of the closed
    weeks, the pages and news, and the hold."""
    root = Path(root)
    season = _season(root) if season is None else season
    if load_method(season, root) is None:
        return []
    errors = []
    # Each part on its own: the pages, the news and the hold are read from the week records, so they
    # are checked only once the records themselves hold.
    for part in (method_errors, record_errors, coverage_errors, page_errors, hold_errors):
        try:
            found = part(root, season) if part in (coverage_errors, hold_errors) else part(season, root)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            found = ["head-coach records invalid (%s): %s" % (part.__name__, exc)]
        errors += found
        if found and part in (method_errors, record_errors):
            return errors
    return errors
