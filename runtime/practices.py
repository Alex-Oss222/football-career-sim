"""Dated practice and rest records, every week, byes included (rebuild step 5, C1; docs/rebuild_plan.md,
step 5; docs/bye_week.md, sections 3 to 7; the rules are library/2014_cba_practice_rest_and_rookie_
renegotiation.md, P1 to P10, B1 to B6, D1 and D2).

One record per week (``SeasonPaths(year).practice_log(week)``, ``practices.json`` in the week's data
folder), schema ``practice-week-v1``:

- ``basis``: ``recorded`` (what was held, against the week's applied schedule), ``closed_record`` (a
  week closed before the log existed, transcribed from what its closed owners actually record) or
  ``not_set`` (no schedule was given: no sessions, a gaps line, and a padded count unknown);
- ``schedule``: where the week's schedule came from ({source, sha256}: the standing practice
  instruction or Stone's "Practice week" answer) or null;
- ``sessions``: each session's date, type, whether players are required, who attends, the equipment
  required, whether it was held, the P6 exceptions, and the participation. In a session whose
  participation is recorded a player not listed took full part; in one whose participation is not
  recorded (every closed record) a player not listed is unknown, never full;
- ``days_off``: each day off, whom it is for and its exceptions (D2: an injured player's treatment,
  quarterback meetings);
- ``gaps``: what the owners do not record, in words.

Practice produces facts, never invented performance (the user's method of October 20, 2026, recorded
October 23): no adjective, quote or practice result is stored, performance evidence comes only from
the game's plays, and no practice injury is generated until a practice-injury rate is sourced in two
passes. A padded practice is worked out when read (held or cancelled, helmets and shoulder pads
required, P5; the P6 exceptions do not make one), never stored.

The module stays outside the career layer (tests/test_career_layer_isolation.py): nothing on the game
path imports it, and it imports nothing from runtime.current_job, runtime.decision_queue, scripts.
render_career_views or any module in that test's LAYER, at module level or inside a function. It
takes the standing instruction, the week's schedule and the medical reading as arguments; it reads
only the practice records, the fixtures and the pages a source names.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re

from .seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
JAX = "Jacksonville Jaguars"
SCHEMA = "practice-week-v1"

# The record's vocabulary (docs/rebuild_plan.md, step 5): the days of a practice week, each session's
# type and equipment, and whom a day off is for. The job record's standing practice instruction is
# written in the same words (runtime/current_job.py validates it against these).
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
SESSION_TYPES = ("practice", "walkthrough", "meeting", "film", "conditioning", "treatment")
EQUIPMENT = ("helmets_and_shoulder_pads", "helmets", "none")
PADDED = "helmets_and_shoulder_pads"
DAY_OFF_SCOPES = ("team", "players")
KINDS = ("game", "bye")
BASES = ("recorded", "closed_record", "not_set")
STATUSES = ("held", "cancelled", "cancelled_beyond_control")
ATTENDEES = ("team", "quarterbacks", "injured")
PARTICIPATION = ("full", "limited", "did_not_participate", "not_with_team", "treatment_only")
REASONS = ("medical_instruction", "coach_rest", "personal", "not_with_club")
PAD_EXCEPTIONS = ("P6(i)", "P6(ii)", "P6(iii)")
EXCEPTION_KINDS = ("treatment", "quarterback_meetings")
NOT_SET_GAP = "No practice schedule was set for the week; what was held is not recorded"

# The 2011 agreement's limits as the library records them: fourteen padded practices, eleven in the
# first eleven weeks and three in the last six (P1, P2), two in one week in one week only, inside the
# first eleven (P3); a bye's four consecutive days off (B1 to B3); four days off a month (D1).
REGULAR_WEEKS = 17
FIRST_WEEKS = 11
LIMITS = {"first": 11, "last": 3}
BREAK_DAYS = 4
DAYS_PER_MONTH = 4

RECORD_KEYS = ("schema", "season", "week", "kind", "basis", "schedule", "source", "sessions", "days_off", "gaps")
RECORD_OPTIONAL = ("padded_count_basis",)
SESSION_KEYS = ("date", "type", "required", "attendees", "equipment", "status", "pad_exceptions",
                "participation_recorded", "participation")
SESSION_OPTIONAL = ("change",)
ENTRY_KEYS = ("player", "status", "basis", "medical", "source")
DAY_OFF_KEYS = ("date", "scope", "players", "exceptions")
DAY_OFF_OPTIONAL = ("source",)

# Words for the pages (render_table) and the messages.
TYPE_WORDS = {"practice": "Practice", "walkthrough": "Walkthrough", "meeting": "Meeting", "film": "Film",
              "conditioning": "Conditioning", "treatment": "Treatment"}
WORK_WORDS = {"practice": "practice", "walkthrough": "walkthrough", "meeting": "meeting", "film": "film",
              "conditioning": "conditioning", "treatment": "treatment"}
EQUIPMENT_WORDS = {"helmets_and_shoulder_pads": "Helmets and shoulder pads", "helmets": "Helmets",
                   "none": "No helmets", None: "Not recorded"}
STATUS_WORDS = {"full": "full", "limited": "limited", "did_not_participate": "did not take part",
                "not_with_team": "not with the team", "treatment_only": "treatment only"}
REASON_WORDS = {"medical_instruction": "medical instruction", "coach_rest": "the coaches' decision",
                "personal": "personal", "not_with_club": "not with the club"}
EXCEPTION_WORDS = {"P6(i)": "helmet or shoulder pads at his option as a quarterback, kicker, punter or long snapper",
                   "P6(ii)": "a precautionary helmet on the club physician's direction",
                   "P6(iii)": "a helmet for the helmet radio"}


class NotCovered(ValueError):
    """The standing instruction does not set this week's schedule (a bye, a game on another day, a
    week before the instruction applies); the week's schedule is then Stone's answer or not set."""


# ------------------------------------------------------------------ dates and the week
def _date(value):
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(value)


def long_day(day):
    """"Wednesday, October 15"."""
    day = _date(day)
    return "%s, %s %d" % (day.strftime("%A"), day.strftime("%B"), day.day)


def weeks_words(weeks):
    """"Week 6", "Weeks 12 and 13", "Weeks 12, 13 and 14"."""
    weeks = [str(w) for w in weeks]
    if len(weeks) == 1:
        return "Week " + weeks[0]
    return "Weeks %s and %s" % (", ".join(weeks[:-1]), weeks[-1])


def _span_words(first, last):
    if first.month == last.month:
        return "%s %d to %d" % (first.strftime("%B"), first.day, last.day)
    return "%s %d to %s %d" % (first.strftime("%B"), first.day, last.strftime("%B"), last.day)


def fixtures(season, root=ROOT):
    """Every regular-season fixture of the season (all clubs)."""
    return SeasonPaths(season, Path(root)).regular_games()


def club_games(season, root=ROOT, games=None, club=JAX):
    """{week: fixture} of the club's regular-season games."""
    games = fixtures(season, root) if games is None else games
    return {int(g["week"]): g for g in games if club in (g["away"], g["home"])}


def is_bye(season, week, root=ROOT, games=None):
    """Whether ``week`` is the club's bye: a regular-season week between its first and last game in
    which it does not play."""
    ours = club_games(season, root, games)
    return min(ours) < week < max(ours) and week not in ours


def _bye_sunday(season, week, games):
    days = sorted(_date(g["date"]) for g in games if int(g["week"]) == week)
    sundays = [d for d in days if d.weekday() == 6]
    if sundays:
        return sundays[0]
    first = days[0]
    return first + dt.timedelta(days=(6 - first.weekday()) % 7)


def week_span(season, week, root=ROOT, games=None):
    """(first, last) day of Week ``week``'s practice week: from the day after the club's previous game
    (or the day after the bye that came before it) to the day before its game; a bye week runs from
    the day after its previous game to the league week's Sunday. The first week, with no game before
    it, is the six days before its game."""
    games = fixtures(season, root) if games is None else games
    ours = club_games(season, root, games)
    if week in ours:
        last = _date(ours[week]["date"]) - dt.timedelta(days=1)
        earlier = [w for w in range(1, week) if w in ours or is_bye(season, w, root, games)]
        if not earlier:
            return last - dt.timedelta(days=5), last
        before = max(earlier)
        end = _bye_sunday(season, before, games) if before not in ours else _date(ours[before]["date"])
        return end + dt.timedelta(days=1), last
    if is_bye(season, week, root, games):
        before = max(w for w in ours if w < week)
        return _date(ours[before]["date"]) + dt.timedelta(days=1), _bye_sunday(season, week, games)
    raise ValueError("Week %d of %d is neither a game week nor the bye of %s" % (week, season, JAX))


def _days(first, last):
    return [first + dt.timedelta(days=n) for n in range((last - first).days + 1)]


# ------------------------------------------------------------------ the records
def path(season, week, root=ROOT):
    return SeasonPaths(season, Path(root)).practice_log(week)


def load(season, week, root=ROOT):
    """The week's record, or None."""
    target = path(season, week, root)
    return json.loads(target.read_text(encoding="utf-8")) if target.is_file() else None


def records(season, root=ROOT):
    """{week: record} of every practice record of the regular season."""
    out = {}
    for week in range(1, REGULAR_WEEKS + 1):
        record = load(season, week, root)
        if record is not None:
            out[week] = record
    return out


def write(record, root=ROOT):
    target = path(record["season"], record["week"], root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def not_set_record(season, week, source, root=ROOT, games=None):
    """The record of a week no schedule was given for: no sessions, the gaps line, padded unknown."""
    return {"schema": SCHEMA, "season": season, "week": week,
            "kind": "bye" if is_bye(season, week, root, games) else "game", "basis": "not_set",
            "schedule": None, "source": dict(source), "sessions": [], "days_off": [], "gaps": [NOT_SET_GAP]}


# ------------------------------------------------------------------ padded practices (P1 to P7)
def session_padded(session, closed=False):
    """Whether a session counts as a padded practice (P5): players required to wear helmets and
    shoulder pads, held or cancelled (a padded practice cancelled within its first hour for a reason
    beyond the club's control does not count, P7, which a second source has not confirmed). The P6
    exceptions never make a practice padded. None when its equipment is not recorded, unless the
    week's owner counts its padded practices (``closed`` with a padded-count basis)."""
    if session.get("status") == "cancelled_beyond_control":
        return False
    equipment = session.get("equipment")
    if equipment is None:
        return False if closed else None
    return equipment == PADDED


def participation_status(session, player):
    """A player's part in a session as the record holds it: his listed status; "full" when the
    session's participation is recorded and he is not listed in a team session; None (unknown) in a
    session whose participation is not recorded, every closed record's."""
    for entry in session.get("participation") or ():
        if entry.get("player") == player:
            return entry.get("status")
    if session.get("participation_recorded") and session.get("attendees") == "team":
        return "full"
    return None


def week_padded(record):
    """The week's padded practices, or None when the count is not known (a week not set, or a session
    whose equipment is not recorded with no owner counting the week's padded practices)."""
    if record is None or record.get("basis") == "not_set":
        return None
    closed = record.get("basis") == "closed_record" and bool(record.get("padded_count_basis"))
    found = [session_padded(s, closed) for s in record.get("sessions") or ()]
    return None if None in found else sum(found)


def _period(week):
    return "first" if week <= FIRST_WEEKS else "last"


def padded_status(season, through_week, root=ROOT, records_=None):
    """The padded practices counted through Week ``through_week``: for the first eleven weeks (the bye
    counted inside them, the reading U2 the defect register applies) and the last six, the limit, the
    used and left (None, and ``known`` False, while any counted week is not set or not recorded), the
    one double week (the first week of the first eleven with two padded practices) and whether it is
    used (None while a week before it is unknown), the weeks over the limits, and each week's count."""
    found = records(season, root) if records_ is None else records_
    out = {"through_week": through_week, "double_week": None, "double_week_used": False, "over": [], "by_week": {}}
    for name, (first, last) in (("first", (1, FIRST_WEEKS)), ("last", (FIRST_WEEKS + 1, REGULAR_WEEKS))):
        out[name] = {"weeks": [first, last], "limit": LIMITS[name], "used": 0, "left": LIMITS[name], "known": True,
                     "unknown_weeks": []}
    doubles = []
    for week in range(1, min(through_week, REGULAR_WEEKS) + 1):
        count = week_padded(found.get(week))
        out["by_week"][week] = count
        period = out[_period(week)]
        if count is None:
            period["known"] = False
            period["unknown_weeks"].append(week)
            continue
        period["used"] += count
        if count > 2:
            out["over"].append({"week": week, "padded": count, "why": "more than two padded practices in a week"})
        if count >= 2 and week > FIRST_WEEKS:
            out["over"].append({"week": week, "padded": count, "why": "two padded practices in a week of the last six"})
        elif count >= 2:
            if doubles or out["first"]["unknown_weeks"]:
                out["over"].append({"week": week, "padded": count, "why": "a second week with two padded practices"
                                    if doubles else "two padded practices with an earlier week not recorded"})
            doubles.append(week)
    if doubles:
        out["double_week"], out["double_week_used"] = doubles[0], True
    elif not out["first"]["known"]:
        out["double_week_used"] = None
    for name in ("first", "last"):
        period = out[name]
        if not period["known"]:
            period["used"] = period["left"] = None
            continue
        if period["used"] > period["limit"]:
            out["over"].append({"week": None, "padded": period["used"], "why": "more than the %d allowed in the %s"
                                % (period["limit"], "first eleven weeks" if name == "first" else "last six weeks")})
        period["left"] = max(period["limit"] - period["used"], 0)
    return out


# ------------------------------------------------------------------ the bye's break (B1 to B5)
def bye_break_windows(season, week, root=ROOT, games=None):
    """The four-day windows that satisfy the bye's player break (B1 to B3): four consecutive days of
    the bye week including its Saturday and Sunday, or Wednesday to Saturday when the club's next game
    is on the Thursday after the bye. [(first, last)] in order."""
    games = fixtures(season, root) if games is None else games
    if not is_bye(season, week, root, games):
        raise ValueError("Week %d of %d is not %s's bye" % (week, season, JAX))
    first, last = week_span(season, week, root, games)
    ours = club_games(season, root, games)
    following = ours[min(w for w in ours if w > week)]
    sunday = _bye_sunday(season, week, games)
    if _date(following["date"]).weekday() == 3:          # a Thursday game after the bye (B3)
        start = sunday - dt.timedelta(days=4)
        return [(start, start + dt.timedelta(days=BREAK_DAYS - 1))]
    saturday = sunday - dt.timedelta(days=1)
    out = []
    for start in _days(first, last):
        end = start + dt.timedelta(days=BREAK_DAYS - 1)
        if end <= last and start <= saturday and end >= sunday:
            out.append((start, end))
    return out


# ------------------------------------------------------------------ days off (D1, D2)
def _all_players(day_off):
    return day_off.get("players") == "all"


def days_off(season, root=ROOT, records_=None, games=None):
    """The players' days off counted by calendar month from the first regular-season game (D1), bye
    days not counted: {"months": [{month, first, last, days, count, complete}], "warnings": [...]},
    through the last day the records cover. D1's wording is on one source and "month" is not defined
    (U3), so a month short of four, or one not fully recorded, is a warning, never a refusal; the
    month still under way is not warned short."""
    games = fixtures(season, root) if games is None else games
    found = records(season, root) if records_ is None else records_
    ours = club_games(season, root, games)
    start = _date(ours[min(ours)]["date"])
    counted, bye_days, covered, not_set = set(), set(), set(), {}
    for week, record in sorted(found.items()):
        try:
            first, last = week_span(season, week, root, games)
        except ValueError:
            continue
        span = _days(first, last) + ([_date(ours[week]["date"])] if week in ours else [])
        if record.get("kind") == "bye":
            bye_days |= set(span)
        covered |= set(span)
        if record.get("basis") == "not_set":
            for day in span:
                not_set.setdefault(day.strftime("%Y-%m"), set()).add(week)
            continue
        for off in record.get("days_off") or ():
            if _all_players(off):
                counted.add(_date(off["date"]))
    months, warnings = [], []
    if not covered or max(covered) < start:
        return {"months": months, "warnings": warnings}
    end = max(covered)
    day = start
    while day <= end:
        month_last = (day.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
        last = min(month_last, end)
        span = [d for d in _days(day, last) if d not in bye_days]
        listed = sorted(d for d in span if d in counted)
        unset = sorted(not_set.get(day.strftime("%Y-%m"), ()))
        unrecorded = [d for d in span if d not in covered]
        complete = last == month_last and not unrecorded and not unset
        months.append({"month": day.strftime("%Y-%m"), "first": day.isoformat(), "last": last.isoformat(),
                       "days": [d.isoformat() for d in listed], "count": len(listed), "complete": complete})
        name = day.strftime("%B")
        if unset or unrecorded:
            what = ("%s not set" % weeks_words(unset)) if unset else \
                "%d day%s not recorded" % (len(unrecorded), "" if len(unrecorded) == 1 else "s")
            warnings.append("%s's days off are not all on record (%s); its count of %d may be short"
                            % (name, what, len(listed)))
        elif complete and len(listed) < DAYS_PER_MONTH:
            warnings.append("%s holds %d counted days off of the four a month the 2011 agreement sets (that wording "
                            "is on one source, and how a part month counts is not settled)" % (name, len(listed)))
        day = month_last + dt.timedelta(days=1)
    return {"months": months, "warnings": warnings}


# ------------------------------------------------------------------ the schedule check
def _work(session):
    return WORK_WORDS.get(session.get("type"), session.get("type"))


def _allowed_on_day_off(session):
    """D2: on a day off an injured player may be required to take treatment and the quarterbacks to
    attend coaches' meetings."""
    return (session.get("type") == "treatment" and session.get("attendees") == "injured") or \
        (session.get("type") == "meeting" and session.get("attendees") == "quarterbacks")


def check_schedule(season, week, sessions, days_off_, root=ROOT, records_=None, games=None):
    """The rules a week's practice schedule is checked against before any session, and what was held
    against when it is recorded: every date inside the week; the padded practices within the budget
    the earlier weeks leave (eleven in the first eleven weeks, three in the last six; refused while
    that count is unknown), two in a week only once, inside the first eleven; no required player work
    on a day off beyond D2's treatment and quarterback meetings; and in the bye a legal four-day
    break (``bye_break_windows``) with no required player work inside it but an injured player's
    treatment, quarterback meetings included (docs/bye_week.md section 4). Problems in football words,
    the messages of docs/bye_week.md section 6; [] when it passes."""
    games = fixtures(season, root) if games is None else games
    found = records(season, root) if records_ is None else records_
    problems = []
    first, last = week_span(season, week, root, games)
    bye = is_bye(season, week, root, games)
    name = "the Week %d bye" % week if bye else "the Week %d practice week" % week
    for entry, what in [(s, _work(s)) for s in sessions] + [(d, "day off") for d in days_off_]:
        day = _date(entry["date"])
        if not first <= day <= last:
            problems.append("%s (%s) is outside %s (%s); set it inside the week" % (
                long_day(day), what, name, _span_words(first, last)))
    padded = sorted((s for s in sessions if session_padded(s)), key=lambda s: s["date"])
    earlier = {w: r for w, r in found.items() if w < week}
    status = padded_status(season, week - 1, root, earlier)
    period = status[_period(week)]
    allocation = "first-eleven-week" if week <= FIRST_WEEKS else "last-six-week"
    if padded and not period["known"]:
        problems.append("This practice requests pads on %s, but the season's padded practices are not all on record "
                        "(%s not recorded), so no pad day can be shown to be left. Choose helmets-only work or no "
                        "field period." % (long_day(padded[0]["date"]), weeks_words(period["unknown_weeks"])))
    elif padded and len(padded) > period["left"]:
        if period["left"] == 0:
            problems.append("This practice requests pads but the earlier recorded practices have used the season's "
                            "available %s allocation. Choose helmets-only work or no field period." % allocation)
        else:
            problems.append("This week requests %d padded practices, but %d of the season's %s allocation %s left. "
                            "Make %s helmets only." % (len(padded), period["left"], allocation,
                                                       "is" if period["left"] == 1 else "are",
                                                       long_day(padded[-1]["date"])))
    if len(padded) >= 2:
        second = long_day(padded[1]["date"])
        if week > FIRST_WEEKS:
            problems.append("%s is a second padded practice this week; two in one week are allowed only once, in the "
                            "first eleven weeks. Make it helmets only." % second)
        elif status["double_week_used"] is None:
            problems.append("%s is a second padded practice this week, and whether the season's one week with two "
                            "padded practices is used is not known (a week not recorded). Make it helmets only."
                            % second)
        elif status["double_week_used"]:
            problems.append("%s is a second padded practice this week, and the season's one week with two padded "
                            "practices was used in Week %d. Make it helmets only." % (second, status["double_week"]))
        if len(padded) > 2:
            problems.append("At most two padded practices may fall in one week; make %s helmets only"
                            % ", ".join(long_day(s["date"]) for s in padded[2:]))
    off = {_date(d["date"]) for d in days_off_ if _all_players(d)}
    if bye:
        windows = bye_break_windows(season, week, root, games)
        held = [w for w in windows if all(d in off for d in _days(*w))]
        if not held:
            example = windows[0] if windows else None
            problems.append("The players' days off do not give the four consecutive days the bye requires%s. Set "
                            "the break%s." % (
                                " (including Saturday and Sunday)" if example and example[1].weekday() == 6 else
                                " (Wednesday to Saturday before the Thursday game)",
                                ", for example %s to %s" % (long_day(example[0]), long_day(example[1]))
                                if example else ""))
        breaks = set()
        for window in held:
            day = window[0]
            while day - dt.timedelta(days=1) in off:
                day -= dt.timedelta(days=1)
            while day in off:
                breaks.add(day)
                day += dt.timedelta(days=1)
        for session in sessions:
            day = _date(session["date"])
            if day in breaks and session.get("required") and not (
                    session.get("type") == "treatment" and session.get("attendees") == "injured"):
                problems.append("You scheduled required player %s work on %s, inside the four-day player break. "
                                "Move it before the break or make it staff-only." % (_work(session), long_day(day)))
        for entry in days_off_:
            day = _date(entry["date"])
            for exception in entry.get("exceptions") or ():
                if day in breaks and exception.get("kind") == "quarterback_meetings":
                    problems.append("You scheduled quarterback meetings on %s, inside the four-day player break. "
                                    "Move them before the break or make the work staff-only." % long_day(day))
    else:
        for session in sessions:
            day = _date(session["date"])
            if day in off and session.get("required") and not _allowed_on_day_off(session):
                problems.append("You scheduled required player %s work on %s, the players' day off. Move it to "
                                "another day or make it staff-only." % (_work(session), long_day(day)))
    return problems


# ------------------------------------------------------------------ the standing instruction
def schedule_digest(schedule):
    """The digest of a schedule's own words (the instruction's ``schedule`` or a compiled answer)."""
    return hashlib.sha256(json.dumps(schedule, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def schedule_from_instruction(instruction, season, week, root=ROOT, games=None):
    """The week's schedule set by the standing practice instruction (its ``schedule``, in this
    module's words): {"sessions", "days_off", "source", "sha256"} with each session dated in the six
    days before the game, its type, required, the team attending and the equipment (pads on the
    instruction's padded days, otherwise its unpadded equipment), each day off and each added day off
    inside the week. Raises NotCovered when the instruction does not set the week: another season, a
    week before it applies, the bye, or a game on a day other than its game day (Week 16's Thursday
    game in 2014)."""
    games = fixtures(season, root) if games is None else games
    schedule = (instruction or {}).get("schedule") or {}
    if schedule.get("season") != season:
        raise NotCovered("No standing practice instruction sets the %d season" % season)
    if week < schedule["from_week"]:
        raise NotCovered("The standing practice instruction sets the weeks from Week %d" % schedule["from_week"])
    ours = club_games(season, root, games)
    if week not in ours:
        raise NotCovered("Week %d is the bye; its work and break are set on My Adjustments" % week)
    game_day = _date(ours[week]["date"])
    shape = schedule["week"]
    if game_day.strftime("%A") != shape["game_day"]:
        raise NotCovered("The Week %d game is on %s; the standing practice instruction sets a week before a %s "
                         "game" % (week, long_day(game_day), shape["game_day"]))
    first, last = week_span(season, week, root, games)
    days = {d.strftime("%A"): d for d in _days(max(first, game_day - dt.timedelta(days=6)), last)}
    pads = {(p["week"], p["day"]) for p in schedule["equipment"].get("pads") or ()}
    sessions, out = [], []
    for item in shape.get("sessions") or ():
        if item["day"] not in days:
            raise NotCovered("The Week %d practice week has no %s before the game" % (week, item["day"]))
        sessions.append({"date": days[item["day"]].isoformat(), "type": item["type"], "required": True,
                         "attendees": "team",
                         "equipment": schedule["equipment"]["padded"] if (week, item["day"]) in pads
                         else schedule["equipment"]["otherwise"]})
    for item in shape.get("days_off") or ():
        if item["day"] not in days:
            raise NotCovered("The Week %d practice week has no %s before the game" % (week, item["day"]))
        out.append({"date": days[item["day"]].isoformat(), "scope": item["scope"], "players": "all", "exceptions": []})
    for added in schedule.get("added_days_off") or ():
        if first <= _date(added["on"]) <= last:
            out.append({"date": added["on"], "scope": added["scope"], "players": "all", "exceptions": []})
    sessions.sort(key=lambda s: s["date"])
    out.sort(key=lambda d: d["date"])
    return {"sessions": sessions, "days_off": out, "source": {"instruction": instruction.get("id")},
            "sha256": schedule_digest(schedule)}


# ------------------------------------------------------------------ Stone's answer ("Practice week")
# While no standing practice instruction sets a week, its schedule is Stone's answer under the
# reserved heading "Practice week" on the week's My Responses page: one line a day, the day, a colon
# and the day's work, as "Tuesday: day off", "Wednesday: practice in helmets and shoulder pads",
# "Saturday: walkthrough in helmets", "Monday: film for the quarterbacks"; a second session that day
# follows on its own line or after a semicolon without a day. A weekday that falls twice in the week
# takes its date ("Friday, December 26: ..."). ``compile_answer`` reads only these words: the same
# schedule in other words compiles to the same record, and anything it cannot read is named back to
# him, never guessed.
ANSWER_FORM = ("one line a day: the day, a colon and the day's work, as \"Tuesday: day off\", \"Wednesday: practice "
               "in helmets and shoulder pads\" or \"Saturday: walkthrough in helmets\"")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December")
_DAY_LINE = re.compile(r"^(?:[-*]\s+)?(%s)(?:,?\s+(%s)\s+(\d{1,2})(?:,\s*\d{4})?)?\s*[:\u2013\u2014]\s*(.*)$"
                       % ("|".join(WEEKDAYS), "|".join(MONTH_NAMES)), re.I)
_DAY_OFF = re.compile(r"^(?:the\s+)?(?:(players'?|team'?s?)\s+)?(?:day\s+)?off$", re.I)
SESSION_WORDS = (("walkthrough", ("walk-through", "walk through", "walkthrough")),
                 ("conditioning", ("conditioning",)),
                 ("treatment", ("treatment", "rehabilitation", "rehab")),
                 ("meeting", ("meetings", "meeting")),
                 ("film", ("film study", "film session", "film")),
                 ("practice", ("practice",)))
# Equipment, read in this order so "no helmets" and "helmets and shoulder pads" are not read as helmets.
EQUIPMENT_WORDS_IN = (("none", ("no helmets", "without helmets", "no equipment")),
                      (PADDED, ("helmets and shoulder pads", "shoulder pads and helmets", "full pads", "shoulder pads",
                                "shells", "pads", "padded")),
                      ("helmets", ("helmets only", "helmets", "helmet")))
ATTENDEE_WORDS = (("quarterbacks", ("the quarterbacks", "quarterbacks")),
                  ("injured", ("the injured players", "injured players", "the injured", "injured")))
VOLUNTARY_WORDS = ("voluntary", "optional")
FILLER = frozenset({"in", "with", "a", "an", "the", "for", "only", "all", "players", "player", "session", "sessions",
                    "team", "at", "full", "required", "and", "of", "by", "our", "whole", "squad", "on", "field"})


def _take(text, groups):
    """(value, rest) of the first group whose words are in ``text`` (whole words), or (None, text)."""
    for value, words in groups:
        for word in words:
            pattern = re.compile(r"(?<![\w'-])%s(?![\w'-])" % re.escape(word), re.I)
            if pattern.search(text):
                return value, pattern.sub(" ", text, count=1)
    return None, text


def _session_from(words, day, problems):
    """One session from a day's words, or None with the problem named."""
    text = re.sub(r"\([^()]*\)", " ", words)            # a note in parentheses is his, not the schedule's
    kind, rest = _take(text, SESSION_WORDS)
    if kind is None:
        problems.append("%s: write the day's work (practice, walkthrough, meeting, film, conditioning or treatment) "
                        "or day off (%r)" % (long_day(day), words.strip()))
        return None
    equipment, rest = _take(rest, EQUIPMENT_WORDS_IN)
    attendees, rest = _take(rest, ATTENDEE_WORDS)
    voluntary, rest = _take(rest, (("voluntary", VOLUNTARY_WORDS),))
    left = [w for w in re.findall(r"[\w'-]+", rest) if w.lower() not in FILLER]
    if left:
        problems.append("%s: %r is not part of a session I can record (the work, what the players wear, who "
                        "attends, voluntary); write it as %s" % (long_day(day), " ".join(left), ANSWER_FORM))
        return None
    if equipment is None:
        if kind in ("practice", "walkthrough", "conditioning"):
            problems.append("%s: say what the players wear for the %s: helmets and shoulder pads, helmets, or no "
                            "helmets" % (long_day(day), WORK_WORDS[kind]))
            return None
        equipment = "none"
    if attendees is None:
        attendees = "injured" if kind == "treatment" else "team"
    return {"date": day.isoformat(), "type": kind, "required": voluntary is None, "attendees": attendees,
            "equipment": equipment}


def compile_answer(text, season, week, root=ROOT, games=None):
    """(schedule, problems): Stone's "Practice week" answer read into the week's schedule
    ({"sessions": [...], "days_off": [...]}, in this module's words, sorted by date, so the same
    schedule in other words gives the same record), every day inside the week; or the problems in
    football words. Nothing defaults but the equipment of a meeting, film or treatment (none), who
    attends (the team; the injured players for treatment) and that a session is required unless
    he writes voluntary."""
    games = fixtures(season, root) if games is None else games
    first, last = week_span(season, week, root, games)
    span = _days(first, last)
    name = "the Week %d bye" % week if is_bye(season, week, root, games) else "the Week %d practice week" % week
    problems, sessions, offs, day = [], [], [], None
    # One day a line, or several after semicolons; a full stop before a weekday also starts a new day.
    lines = re.split(r"\n|;|\.\s+(?=(?:%s)\b)" % "|".join(WEEKDAYS), text or "", flags=re.I)
    chunks = [c.strip() for c in lines]
    for chunk in [c for c in chunks if c]:
        m = _DAY_LINE.match(chunk)
        if m:
            weekday = m[1].capitalize()
            if m[2]:
                try:
                    dated = dt.date(first.year if m[2].capitalize() != "January" or first.month == 1 else first.year + 1,
                                    MONTH_NAMES.index(m[2].capitalize()) + 1, int(m[3]))
                except ValueError:
                    problems.append("%s %s is not a date" % (m[2], m[3]))
                    day = None
                    continue
                if dated.strftime("%A") != weekday:
                    problems.append("%s is a %s, not a %s" % (long_day(dated).split(", ", 1)[1], dated.strftime("%A"),
                                                            weekday))
                    day = None
                    continue
                if dated not in span:
                    problems.append("%s is outside %s (%s); set it inside the week" % (
                        long_day(dated), name, _span_words(first, last)))
                    day = None
                    continue
                day = dated
            else:
                found = [d for d in span if d.strftime("%A") == weekday]
                if not found:
                    problems.append("%s is not a day of %s (%s); set it inside the week" % (
                        weekday, name, _span_words(first, last)))
                    day = None
                    continue
                if len(found) > 1:
                    problems.append("%s falls twice in %s (%s); write its date, as \"%s: ...\"" % (
                        weekday, name, " and ".join(long_day(d).split(", ", 1)[1] for d in found), long_day(found[-1])))
                    day = None
                    continue
                day = found[0]
            words = m[4].strip().rstrip(".")
        elif day is None:
            problems.append("%r does not start with a day; write %s" % (chunk, ANSWER_FORM))
            continue
        else:
            words = chunk.rstrip(".")
        if not words:
            problems.append("%s: write the day's work or day off" % long_day(day))
            continue
        off = _DAY_OFF.match(words.strip())
        if off:
            scope = "team" if off[1] and off[1].lower().startswith("team") else "players"
            if any(o["date"] == day.isoformat() for o in offs):
                problems.append("%s is a day off twice" % long_day(day))
                continue
            offs.append({"date": day.isoformat(), "scope": scope, "players": "all", "exceptions": []})
            continue
        session = _session_from(words, day, problems)
        if session is not None:
            sessions.append(session)
    if not sessions and not offs and not problems:
        problems.append("Name each day's work or day off for %s: %s" % (name, ANSWER_FORM))
    order = {k: n for n, k in enumerate(SESSION_TYPES)}
    sessions.sort(key=lambda s: (s["date"], order[s["type"]], s["attendees"] if isinstance(s["attendees"], str)
                                 else ",".join(s["attendees"]), s["equipment"], not s["required"]))
    offs.sort(key=lambda d: d["date"])
    return {"sessions": sessions, "days_off": offs}, problems


def schedule_from_answer(compiled, page, heading):
    """The week's schedule as Stone's applied answer sets it: its sessions and days off, where it was
    given (``source``: his page and the heading) and the digest of the compiled schedule."""
    return {"sessions": [dict(s) for s in compiled["sessions"]], "days_off": [dict(d) for d in compiled["days_off"]],
            "source": {"page": page, "heading": heading},
            "sha256": schedule_digest({"sessions": compiled["sessions"], "days_off": compiled["days_off"]})}


def schedule_lines(schedule):
    """The schedule in words, one line a day in date order ("Wednesday, October 15: practice, helmets")."""
    dated = [(off["date"], 0, "%s: the players' day off" % long_day(off["date"])) for off in schedule["days_off"]]
    for s in schedule["sessions"]:
        words = "%s, %s" % (TYPE_WORDS[s["type"]].lower(), EQUIPMENT_WORDS[s["equipment"]].lower())
        if s.get("attendees") not in (None, "team"):
            words += ", " + _who(s["attendees"]).lower()
        if not s.get("required", True):
            words += ", voluntary"
        dated.append((s["date"], 1, "%s: %s" % (long_day(s["date"]), words)))
    return [text for _, _, text in sorted(dated)]


# ------------------------------------------------------------------ validation
def _source_error(root, source, label):
    """Why a {page, anchor} source does not resolve, or None."""
    from .events import resolve_path
    if not isinstance(source, dict) or set(source) - {"page", "anchor"} or not isinstance(source.get("page"), str):
        return "%s: a source is {page, anchor} (%r)" % (label, source)
    try:
        target = resolve_path(root, source["page"])
    except ValueError as exc:
        return "%s: %s" % (label, exc)
    if not target.is_file():
        return "%s: no page %s" % (label, source["page"])
    if source.get("anchor"):
        from scripts.validate_repository import anchors, without_code
        if target.suffix != ".md" or source["anchor"] not in anchors(without_code(target.read_text(encoding="utf-8"))):
            return "%s: no heading %s#%s" % (label, source["page"], source["anchor"])
    return None


def record_errors(record, root=ROOT, *, players=None, master=None, out_on=None, schedule=None, records_=None,
                  games=None):
    """Every problem of one week's record: its form; every date inside the week and, given ``master``,
    on or before it; every source resolving; every player named on ``players`` (the roster record's
    names, departures included) when given; a recorded week's sessions held to ``schedule`` (the
    week's applied schedule: a session it does not name needs a change with its basis and source,
    and a session it names must be recorded, held or cancelled) and to ``check_schedule``; and, given
    ``out_on`` (a function of a player and a date: "out", "limited" or None, from his medical
    instruction), no participation contradicting the medical instruction. A closed record stands as
    written: its counts are reported by ``padded_status``, never refused."""
    root = Path(root)
    if not isinstance(record, dict):
        return ["Practice record: not a record"]
    week = record.get("week")
    label = "Week %s practice record" % week
    errors = []
    missing = [k for k in RECORD_KEYS if k not in record]
    unknown = sorted(set(record) - set(RECORD_KEYS) - set(RECORD_OPTIONAL))
    if missing or unknown or record.get("schema") != SCHEMA:
        return [label + ": needs schema %s and exactly the keys %s (missing %s, unknown %s)" % (
            SCHEMA, ", ".join(RECORD_KEYS), ", ".join(missing) or "none", ", ".join(unknown) or "none")]
    if type(record["season"]) is not int or type(week) is not int:
        return [label + ": season and week are ints"]
    games = fixtures(record["season"], root) if games is None else games
    try:
        first, last = week_span(record["season"], week, root, games)
        bye = is_bye(record["season"], week, root, games)
    except ValueError as exc:
        return ["%s: %s" % (label, exc)]
    if record["kind"] != ("bye" if bye else "game"):
        errors.append("%s: kind is %r; the week is %s" % (label, record["kind"], "the bye" if bye else "a game week"))
    basis = record["basis"]
    if basis not in BASES:
        errors.append("%s: basis must be one of %s" % (label, ", ".join(BASES)))
    problem = _source_error(root, record["source"], label + " source")
    if problem:
        errors.append(problem)
    if "padded_count_basis" in record:
        counted = record["padded_count_basis"] or {}
        if basis != "closed_record" or not isinstance(counted.get("text"), str) or not counted["text"].strip():
            errors.append(label + ": a padded-count basis belongs to a closed record and needs its text")
        for i, source in enumerate(counted.get("sources") or [None]):
            problem = _source_error(root, source, label + " padded-count source %d" % i)
            if problem:
                errors.append(problem)
    if basis == "not_set":
        if record["sessions"] or record["days_off"] or record["schedule"] is not None or \
                NOT_SET_GAP not in (record["gaps"] or ()):
            errors.append("%s: a week not set has no schedule, sessions or days off, and the gaps line %r"
                          % (label, NOT_SET_GAP))
        return errors
    if basis == "closed_record" and record["schedule"] is not None:
        errors.append(label + ": a closed record has no applied schedule")
    if basis == "recorded":
        held = record["schedule"]
        if not isinstance(held, dict) or set(held) != {"source", "sha256"} or not isinstance(held.get("sha256"), str):
            errors.append(label + ": a recorded week names its schedule {source, sha256}")
        elif schedule is not None and held["sha256"] != schedule.get("sha256"):
            errors.append(label + ": the schedule it records against is not the week's applied schedule")
    if not isinstance(record["gaps"], list) or not all(isinstance(g, str) and g.strip() for g in record["gaps"]):
        errors.append(label + ": gaps is a list of lines")
    names = None if players is None else set(players)
    sessions = record["sessions"] if isinstance(record["sessions"], list) else []
    dates = []
    for n, session in enumerate(sessions, 1):
        where = "%s, session %d" % (label, n)
        if not isinstance(session, dict):
            errors.append(where + ": not a session")
            continue
        missing = [k for k in SESSION_KEYS if k not in session]
        unknown = sorted(set(session) - set(SESSION_KEYS) - set(SESSION_OPTIONAL))
        if missing or unknown:
            errors.append("%s: needs exactly %s (missing %s, unknown %s)" % (
                where, ", ".join(SESSION_KEYS), ", ".join(missing) or "none", ", ".join(unknown) or "none"))
            continue
        try:
            day = _date(session["date"])
        except (TypeError, ValueError):
            errors.append(where + ": the date is an ISO date")
            continue
        dates.append(day)
        where = "%s, %s" % (label, long_day(day))
        if not first <= day <= last:
            errors.append("%s: outside the week (%s)" % (where, _span_words(first, last)))
        if master is not None and day > master:
            errors.append("%s: after the master date %s; a session is recorded once it is held" % (where, master))
        if session["type"] not in SESSION_TYPES:
            errors.append("%s: type must be one of %s" % (where, ", ".join(SESSION_TYPES)))
        if type(session["required"]) is not bool:
            errors.append(where + ": required is true or false")
        attendees = session["attendees"]
        if not (attendees in ATTENDEES or (isinstance(attendees, list) and attendees
                                           and all(isinstance(p, str) for p in attendees))):
            errors.append("%s: attendees are %s, or the players by name" % (where, ", ".join(ATTENDEES)))
        elif isinstance(attendees, list) and names is not None:
            errors += ["%s: %s is not on the roster" % (where, p) for p in attendees if p not in names]
        if session["equipment"] not in EQUIPMENT and not (session["equipment"] is None and basis == "closed_record"):
            errors.append("%s: equipment must be one of %s" % (where, ", ".join(EQUIPMENT)))
        if session["status"] not in STATUSES:
            errors.append("%s: status must be one of %s" % (where, ", ".join(STATUSES)))
        for exception in session["pad_exceptions"] if isinstance(session["pad_exceptions"], list) else [None]:
            if not isinstance(exception, dict) or set(exception) != {"player", "rule"} or \
                    exception.get("rule") not in PAD_EXCEPTIONS:
                errors.append("%s: a pad exception is {player, rule} with the rule one of %s"
                              % (where, ", ".join(PAD_EXCEPTIONS)))
            elif names is not None and exception["player"] not in names:
                errors.append("%s: %s is not on the roster" % (where, exception["player"]))
        if type(session["participation_recorded"]) is not bool or \
                (basis == "closed_record" and session["participation_recorded"]):
            errors.append(where + ": participation_recorded is true or false, and false in a closed record")
        seen = set()
        for entry in session["participation"] if isinstance(session["participation"], list) else [None]:
            if not isinstance(entry, dict) or set(entry) != set(ENTRY_KEYS):
                errors.append("%s: a participation entry is exactly %s" % (where, ", ".join(ENTRY_KEYS)))
                continue
            who = entry["player"]
            if who in seen:
                errors.append("%s: %s is listed twice" % (where, who))
            seen.add(who)
            if names is not None and who not in names:
                errors.append("%s: %s is not on the roster" % (where, who))
            if entry["status"] not in PARTICIPATION:
                errors.append("%s: %s's status must be one of %s" % (where, who, ", ".join(PARTICIPATION)))
            if entry["basis"] not in REASONS and not (entry["basis"] is None and entry["status"] == "full"):
                errors.append("%s: %s's basis must be one of %s (none only for full)" % (where, who, ", ".join(REASONS)))
            for key in ("medical", "source"):
                if entry[key] is None and key == "medical":
                    continue
                problem = _source_error(root, entry[key], "%s, %s's %s" % (where, who, key))
                if problem:
                    errors.append(problem)
            if entry["basis"] == "medical_instruction" and entry["medical"] is None:
                errors.append("%s: %s's medical instruction links its medical history entry" % (where, who))
        if "change" in session:
            change = session["change"] or {}
            if not isinstance(change.get("basis"), str) or not change["basis"].strip():
                errors.append(where + ": a change from the schedule names its basis")
            problem = _source_error(root, change.get("source"), where + " change")
            if problem:
                errors.append(problem)
        if out_on is not None and session["participation_recorded"] and session["status"] == "held":
            listed = {e["player"]: e for e in session["participation"] if isinstance(e, dict)}
            # In a team session a player not listed took full part; otherwise only the listed attended.
            for who in sorted((names or set()) | set(listed) if attendees == "team" else listed):
                instruction = out_on(who, day)
                status = (listed.get(who) or {}).get("status", "full")
                if instruction == "out" and status in ("full", "limited"):
                    errors.append("%s: %s is out on his medical instruction; he is recorded %s" % (
                        where, who, "full (not listed)" if who not in listed else STATUS_WORDS[status]))
                elif instruction == "limited" and status == "full":
                    errors.append("%s: %s is limited on his medical instruction; he is recorded full%s"
                                  % (where, who, " (not listed)" if who not in listed else ""))
    if dates != sorted(dates):
        errors.append(label + ": sessions are in date order")
    off_list = record["days_off"] if isinstance(record["days_off"], list) else []
    for entry in off_list:
        missing = [k for k in DAY_OFF_KEYS if k not in (entry if isinstance(entry, dict) else {})]
        if missing or set(entry) - set(DAY_OFF_KEYS) - set(DAY_OFF_OPTIONAL):
            errors.append("%s: a day off is exactly %s" % (label, ", ".join(DAY_OFF_KEYS)))
            continue
        try:
            day = _date(entry["date"])
        except (TypeError, ValueError):
            errors.append(label + ": a day off's date is an ISO date")
            continue
        where = "%s, %s" % (label, long_day(day))
        if not first <= day <= last:
            errors.append("%s: the day off is outside the week (%s)" % (where, _span_words(first, last)))
        if master is not None and day > master:
            errors.append("%s: the day off is after the master date %s" % (where, master))
        if entry["scope"] not in DAY_OFF_SCOPES:
            errors.append("%s: scope must be one of %s" % (where, ", ".join(DAY_OFF_SCOPES)))
        if entry["players"] != "all" and not (isinstance(entry["players"], list) and entry["players"]):
            errors.append(where + ": a day off is for all players or the players by name")
        for exception in entry["exceptions"] if isinstance(entry["exceptions"], list) else [None]:
            if not isinstance(exception, dict) or set(exception) != {"kind", "players"} or \
                    exception.get("kind") not in EXCEPTION_KINDS:
                errors.append("%s: an exception is {kind, players}, the kind one of %s"
                              % (where, ", ".join(EXCEPTION_KINDS)))
        if basis == "closed_record":
            problem = _source_error(root, entry.get("source"), where + " day off")
            if problem:
                errors.append(problem)
    if basis == "recorded":
        if any(s.get("equipment") is None for s in sessions if isinstance(s, dict)):
            errors.append(label + ": a recorded week records each session's equipment")
        named = {(s["date"], s["type"]) for s in (schedule or {}).get("sessions") or ()}
        held_keys = {(s.get("date"), s.get("type")) for s in sessions if isinstance(s, dict)}
        if schedule is not None:
            for s in sessions:
                if isinstance(s, dict) and (s.get("date"), s.get("type")) not in named and "change" not in s:
                    errors.append("%s, %s: the schedule names no %s that day; record it as a change with its basis "
                                  "and source" % (label, long_day(s["date"]), _work(s)))
            for key in sorted(named - held_keys):
                errors.append("%s, %s: the schedule's %s is not recorded; record it held or cancelled"
                              % (label, long_day(key[0]), WORK_WORDS.get(key[1], key[1])))
        if not errors:
            errors += ["%s: %s" % (label, p) for p in check_schedule(
                record["season"], week, sessions, off_list, root,
                records(record["season"], root) if records_ is None else records_, games)]
    return errors


def log_start(season, root=ROOT, records_=None):
    """The first week the log must hold a record for: the week after the last week closed before the
    log existed (a closed record), or Week 1 in a season that has none."""
    found = records(season, root) if records_ is None else records_
    closed = [w for w, r in found.items() if r.get("basis") == "closed_record"]
    return max(closed) + 1 if closed else 1


def validation_errors(season, root=ROOT, players=None):
    """Every practice record of the season valid (``record_errors``, the players named on the roster
    record), and every Jacksonville game week closed from the log's first week (``log_start``) with
    its record. The lead wires this into repository validation; a bye's record is checked once the
    bye has closed (rebuild step 5, C3)."""
    root = Path(root)
    paths = SeasonPaths(season, root)
    games = fixtures(season, root)
    found = records(season, root)
    if players is None and paths.roster.is_file():
        roster = json.loads(paths.roster.read_text(encoding="utf-8"))
        players = [p["name"] for p in roster.get("players") or ()] + \
                  [d["name"] for d in roster.get("departures") or ()]
    errors = []
    for week, record in sorted(found.items()):
        errors += record_errors(record, root, players=players, records_=found, games=games)
    start = log_start(season, root, found)
    played = set()
    if paths.receipts.is_dir():
        for receipt in paths.receipts.glob("week_*.json"):
            data = json.loads(receipt.read_text(encoding="utf-8"))
            if JAX in (data.get("matchup") or ""):
                played.add(int(data["week"]))
    for week in sorted(w for w in played if w >= start and w not in found):
        errors.append("Week %d has closed without its practice record (the practice-week commit records it)" % week)
    return errors


# ------------------------------------------------------------------ the table on the pages
def _who(attendees):
    if attendees == "team":
        return "The team"
    if attendees == "quarterbacks":
        return "The quarterbacks"
    if attendees == "injured":
        return "Injured players"
    return ", ".join(attendees)


def _participation(session):
    listed = ["%s (%s%s)" % (e["player"], STATUS_WORDS[e["status"]],
                             ", %s" % REASON_WORDS[e["basis"]] if e.get("basis") else "")
              for e in session.get("participation") or ()]
    if session.get("status") != "held":
        return "Not held"
    if session.get("participation_recorded"):
        return "Full, except " + "; ".join(listed) if listed else "Full"
    return ("Not recorded, except " + "; ".join(listed)) if listed else "Not recorded"


def _first_upper(text):
    return text[:1].upper() + text[1:]


def render_table(record):
    """The week's practice and rest table for the week index and the bye pages, in football words: one
    row per session and day off, in date order (the session, its equipment, who attended, who did not
    take full part and why), then what is not recorded. Only a recorded week has a table; a closed
    record or a week not set shows none (""), so a closed week's index keeps its bytes."""
    if not record or record.get("basis") != "recorded":
        return ""
    rows = []
    for session in record.get("sessions") or ():
        what = TYPE_WORDS[session["type"]]
        if not session.get("required"):
            what += ", voluntary"
        if session.get("status") == "cancelled":
            what += ", cancelled (counted as a padded practice if pads were required)"
        elif session.get("status") == "cancelled_beyond_control":
            what += (", cancelled within its first hour for a reason beyond the club's control (not counted as a "
                     "padded practice; that rule is on one source)")
        if session.get("change"):
            what += ", changed from the schedule: %s" % session["change"]["basis"]
        gear = EQUIPMENT_WORDS[session.get("equipment")]
        exceptions = ["%s, %s" % (e["player"], EXCEPTION_WORDS[e["rule"]]) for e in session.get("pad_exceptions") or ()]
        if exceptions:
            gear += " (%s)" % "; ".join(exceptions)
        rows.append((session["date"], 1, "| %s | %s | %s | %s | %s |" % (
            long_day(session["date"]), what, gear, _who(session["attendees"]), _participation(session))))
    for off in record.get("days_off") or ():
        what = "Day off" if off["scope"] == "team" else "Players' day off"
        whom = "All players" if off["players"] == "all" else ", ".join(off["players"])
        extra = []
        for exception in off.get("exceptions") or ():
            people = exception.get("players")
            people = "" if people in (None, "all", []) else ": " + ", ".join(people)
            extra.append(("treatment for injured players" if exception["kind"] == "treatment"
                          else "quarterback meetings") + people)
        rows.append((off["date"], 0, "| %s | %s | | %s | %s |" % (
            long_day(off["date"]), what, whom, _first_upper("; ".join(extra)))))
    lines = ["| Date | Session | Equipment | Attending | Taking part |", "| --- | --- | --- | --- | --- |"]
    lines += [row for _, _, row in sorted(rows)]
    text = "\n".join(lines) + "\n"
    if record.get("gaps"):
        text += "\n" + "\n".join("Not recorded: %s." % g.rstrip(".") for g in record["gaps"]) + "\n"
    return text
