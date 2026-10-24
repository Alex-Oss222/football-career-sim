"""The decisions in a year (docs/rebuild_plan.md, "How a decision works" and
"The decisions in a year"): every phase decision and its three pages, and the
events that come up inside a week or phase.

A phase decision has a brief (named for whoever really brings it), his page (a
fill-in page with fixed headings) and a result (named for where it is
decided), all in one folder (``REGISTRY``). An event inside a week or phase (an
injury replacement, a trade call, Stone's own contract extension, another club
calling, an offer after an interview, another club asking to interview an
assistant) is not a decision of three pages
(``EVENTS``, docs/event_inserts.md): it appears as an insert at the top of the
active brief (ACTION REQUIRED, FOR YOUR INFORMATION or COMING UP), is answered
on that week's or phase's one My Responses page, and each resolved event gets
its own dated result page in its owner's folder, linked from the week or phase
index and never pasted into the weekly report. News decided outside
Jacksonville (another club's head-coach change, ``NEWS``) reaches him only as
FOR YOUR INFORMATION and gets its dated result page the same way. Only the game
week is built so far (``implemented``); the build steps that fill in the rest
are named beside them. Nothing here reads or writes a record: the registries
and the page paths are data (``result_file`` only looks whether a file name is
taken), and opening a page never moves time or creates an event.

Folders are found through the folder map (runtime/seasons.SeasonPaths and
runtime/season_layout): a decision's ``place`` and an event's ``owner`` name
where its pages live, and ``folder``, ``event_folder`` and ``event_store``
resolve them for a season. The reserved My Responses headings
(``RESERVED_HEADINGS``) are the week's own answers, not events.
"""
from __future__ import annotations

from dataclasses import dataclass
import datetime
from pathlib import Path
import re
import unicodedata

from .season_layout import (GAME_DAY_CHANGES, PRACTICE_LOG, RESPONSES_RECORD, STONE_PAGES)
from .seasons import SeasonPaths


@dataclass(frozen=True)
class Decision:
    kind: str          # the registry key
    when: str          # when in the year it comes up
    brief: str         # the brief's page name
    page: str          # his page's name
    result: str        # the result page's name
    place: str         # where the three pages live (``PLACES``, or "week")
    brings: str        # who brings the brief
    step: int          # the rebuild step that builds it
    implemented: bool = False


# Where a decision's pages live: a logical season record of the folder map, and how many folders
# up from it the pages sit; "week" is the game week's own folder; "stone" is Stone's own folder.
PLACES = {
    "trades": ("trades/README.md", 1),
    "season_review": ("closeouts", 0),
    "early_offseason": ("offseason", 0),
    "free_agency": ("offseason/free_agency", 0),
    "offseason_training": ("offseason/README.md", 1),
    "draft": ("draft", 0),
    "training_camp_and_preseason": ("preseason", 1),
}

REGISTRY = (
    Decision("game_week", "Every game week", "Game Week Briefing", "Game Plan", "Game Report", "week",
             "The coaching staff: the coordinators, with the medical update and the pro scouting report", 4, True),
    Decision("bye_week", "Bye week", "Bye Week Review", "My Adjustments", "Bye Week Report", "week",
             "The coaching staff", 5),
    # The season's own page, apart from any week's My Responses page (the user's answer of October 20,
    # 2026: "Keep them separate, and give the season one a different name").
    Decision("season_end", "Season ends", "Season Review Briefing", "My Season Response", "Club Decision", "season_review",
             "The owner and the general manager", 6),
    Decision("contract_ending", "Fired, or contract ending", "Agent's Report", "Instructions to My Agent",
             "Interviews and Offers", "stone", "His agent", 6),
    Decision("january_staff", "January staff", "Staff Status Report", "My Staff Decisions", "Staff Moves",
             "early_offseason", "The coaching staff and the general manager", 6),
    Decision("staff_vacancy", "Staff vacancy", "Candidate Report", "My Hire", "Staff Hire", "early_offseason",
             "The general manager", 6),
    Decision("re_signing", "February", "Re-signing Report", "My Re-signing Priorities", "Front Office Moves",
             "free_agency", "The general manager", 7),
    Decision("free_agency", "March", "Pro Personnel Report", "My Free-Agent Priorities", "Free Agency Results",
             "free_agency", "The pro personnel department", 7),
    Decision("offseason_program", "April", "Offseason Program Brief", "My Program Plan", "Program Report",
             "offseason_training", "The coaching staff and the strength staff", 7),
    Decision("draft", "May", "Scouting Department Report", "My Draft Recommendations", "Draft Room Results",
             "draft", "The scouting department", 7),
    Decision("otas", "May and June", "OTA Brief", "My Install Plan", "OTA Report", "offseason_training",
             "The coaching staff", 7),
    Decision("camp", "Camp", "Position Battle Report", "My Depth Calls", "Depth Chart",
             "training_camp_and_preseason", "The position coaches", 8),
    Decision("preseason_game", "Preseason games", "Preseason Game Briefing", "Preseason Game Plan",
             "Preseason Game Report", "training_camp_and_preseason", "The coaching staff", 8),
    Decision("final_cuts", "Final cuts", "Roster Cutdown Report", "My Cut Recommendations", "Final 53",
             "training_camp_and_preseason", "The general manager and the coaching staff", 8),
)
BY_KIND = {d.kind: d for d in REGISTRY}


@dataclass(frozen=True)
class Event:
    """An event that comes up inside a week or phase (docs/event_inserts.md): an insert in the active
    brief, his answer on the week's or phase's one My Responses page, and one dated result page of its
    own in its owner's folder for each event resolved."""
    kind: str          # the registry key
    when: str          # when it comes up
    result: str        # the result page's name
    owner: str         # the folder its result lives in (``OWNERS``)
    brings: str        # who brings it
    step: int          # the rebuild step that builds it
    implemented: bool = False


# The owner folders of event results: a logical season record of the folder map and how many folders
# up from it the result sits; "stone" is Stone's own folder (career/Stone), whoever employs him. Each
# is the folder of an event or a news kind below, or of the records an event's result links to (the
# signing records in Team_Operations/Free_Agency, linked from a Transaction page, which are not
# result pages and carry no event line of their own).
OWNERS = {
    "roster": ("team/roster", 0),                 # roster moves: Team_Operations/Team/Roster
    "trades": ("trades/README.md", 1),            # trades: Team_Operations/Trades
    "staff": ("team/coaching_staff", 0),          # staff: Team_Operations/Staff
    "free_agency": ("free_agency", 0),            # signing records: Team_Operations/Free_Agency
    "league_coaches": ("league/coaching_changes", 0),   # other clubs' coaches: League/Coaching_Changes
}

EVENTS = (
    Event("injury_replacement", "Injury replacement in season", "Transaction", "roster",
          "The general manager and the medical staff", 5, implemented=True),
    Event("trade_talks", "Trade talks", "Trade Result", "trades", "The general manager", 5),
    Event("extension", "Stone's contract extension", "New Contract or Unchanged", "stone", "The club", 6),
    # Shad Khan alone answers another club's request (Document 3 row 1a); Stone is not open to job offers,
    # so the call reaches him as news, and the result is Khan's decision (no permission is an interview).
    Event("club_calls", "Another club calls", "Permission Granted or Refused", "stone",
          "The calling club, through Shad Khan", 6),
    Event("after_interview", "After an interview", "Signed or Talks Ended", "stone", "The interviewing club", 6),
    # Answered under that season's league permission rules and Jacksonville's standing assistant-permission
    # instruction (docs/event_inserts.md, section D), which reach Stone as news; he is asked only about a
    # request the instruction does not cover.
    Event("assistant_interview", "Another club seeks an assistant interview", "Assistant Permission Result", "staff",
          "The asking club", 6),
)
EVENT_KIND = {e.kind: e for e in EVENTS}
# News: an event decided outside Jacksonville that reaches Stone only as FOR YOUR INFORMATION. Its
# record names the deciding party "other_club", with the club as its subject, and is brought to
# Jacksonville by a Jacksonville party; it has a dated result page in its owner's folder like any
# event, and never an answer of his.
NEWS = (
    Event("head_coach_change", "Another club changes its head coach in season", "Head Coach Change",
          "league_coaches", "The club", 5),
)
NEWS_KIND = {e.kind: e for e in NEWS}
# The week's or phase's one answer page for the events inserted in its brief.
RESPONSES = "My Responses"
# The headings on a My Responses page that belong to the week's own answers rather than to an event
# (builder C's checks and applies; the event checks skip them): Stone's depth or inactives change
# after the Game Plan is applied ("Depth and inactives change", the second in a week "Depth and
# inactives change 2", and so on) and his practice week while no standing practice instruction is
# in force.
GAME_DAY_CHANGE = "Depth and inactives change"
PRACTICE_WEEK = "Practice week"
RESERVED_HEADINGS = (GAME_DAY_CHANGE, PRACTICE_WEEK)
_NUMBERED_CHANGE = re.compile(r"^%s(?: ([2-9]|[1-9][0-9]+))?$" % re.escape(GAME_DAY_CHANGE))


def game_day_change_heading(n):
    """The heading of the week's n-th depth or inactives change (1 is unnumbered)."""
    if type(n) is not int or n < 1:
        raise ValueError("a game-day change is numbered from 1: %r" % (n,))
    return GAME_DAY_CHANGE if n == 1 else "%s %d" % (GAME_DAY_CHANGE, n)


def reserved_heading(heading):
    """The reserved heading a My Responses heading is (``GAME_DAY_CHANGE`` for any numbered change),
    or None for an event's heading."""
    text = str(heading).strip()
    if text == PRACTICE_WEEK:
        return PRACTICE_WEEK
    return GAME_DAY_CHANGE if _NUMBERED_CHANGE.match(text) else None


def event_kind(kind):
    """The registry entry of an event kind (``EVENTS``) or a news kind (``NEWS``)."""
    if kind in EVENT_KIND:
        return EVENT_KIND[kind]
    if kind in NEWS_KIND:
        return NEWS_KIND[kind]
    raise ValueError("unknown event kind: %r" % (kind,))


def file_name(page_name):
    """A page's file name from its fixed name: "Game Week Briefing" is Game_Week_Briefing.md."""
    return page_name.replace("'", "").replace(" ", "_") + ".md"


def folder(decision, year, root=None, week=None, postseason=False):
    """The folder a decision's three pages live in, through the folder map."""
    decision = BY_KIND[decision] if isinstance(decision, str) else decision
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    if decision.place == "week":
        if week is None:
            raise ValueError("%s pages live in a week's folder; name the week" % decision.brief)
        return paths.week_folder(week, postseason)
    if decision.place == "stone":
        return paths.root / STONE_PAGES
    return _resolve(paths, PLACES[decision.place])


def event_folder(event, year, root=None):
    """The owner folder an event's dated result pages live in, through the folder map."""
    event = event_kind(event) if isinstance(event, str) else event
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    if event.owner == "stone":
        return paths.root / STONE_PAGES
    return _resolve(paths, OWNERS[event.owner])


def event_store(event, year, root=None):
    """The folder of an event kind's open-event records: one JSON file per event in the data-area
    twin of its owner folder (SeasonPaths.event_store)."""
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    return paths.event_store(event_folder(event, year, root))


def name_part(subject):
    """A result page's subject as a file-name part: "Club A" is Club_A, "Ka'imi Fairbairn" is
    Kaimi_Fairbairn, "St. Louis" is St_Louis."""
    text = unicodedata.normalize("NFKD", str(subject)).encode("ascii", "ignore").decode("ascii")
    part = re.sub(r"[^A-Za-z0-9]+", "_", re.sub(r"['.]", "", text)).strip("_")
    if not part:
        raise ValueError("a result page needs a subject: %r" % (subject,))
    return part


def result_file(kind, date, subject, root=None, season=None):
    """The file a resolved event's result page is written to, in its owner's folder:
    ``<Result>_<ISO date>_<Subject>.md`` (Trade_Result_2014-10-21_Club_A.md,
    Transaction_2014-10-14_Player_X.md, Head_Coach_Change_2014-10-13_Club_B.md). A second
    result of the same kind, date and subject takes ``_2``, then ``_3``, when the name is taken
    there. The season is the date's year unless named; a January or February date may belong to
    the season before (its postseason) or the one after (its offseason), so it must be named."""
    event = event_kind(kind) if isinstance(kind, str) else kind
    when = date if isinstance(date, str) else date.isoformat()
    on = datetime.date.fromisoformat(when)
    if season is None:
        if on.month <= 2:
            raise ValueError("name the season of a result dated %s: January and February belong to "
                             "either side of the league year" % when)
        season = on.year
    folder = event_folder(event, season, root)
    stem = "%s_%s_%s" % (file_name(event.result)[:-len(".md")], when, name_part(subject))
    target, n = folder / (stem + ".md"), 1
    while target.exists():
        n += 1
        target = folder / ("%s_%d.md" % (stem, n))
    return target


def _resolve(paths, place):
    logical, up = place
    target = paths.record(logical)
    for _ in range(up):
        target = target.parent
    return target


@dataclass(frozen=True)
class WeekPages:
    """The game week's pages and its stored decision record, through the folder map. ``report`` is
    the game's result page as the folder map names it (SeasonPaths.game_report): the Game Report
    from the first Game Report week, the week's ``output.md`` before it."""
    folder: Path
    data: Path
    report: Path

    @property
    def readme(self): return self.folder / "README.md"
    @property
    def briefing(self): return self.folder / file_name(BY_KIND["game_week"].brief)
    @property
    def plan(self): return self.folder / file_name(BY_KIND["game_week"].page)
    @property
    def responses(self):
        """The week's one My Responses page: his answers to the events inserted in its briefing
        (docs/event_inserts.md); not a game page, and separate from the frozen Game Plan."""
        return self.folder / file_name(RESPONSES)
    @property
    def responses_record(self):
        """The binding of each heading on the week's My Responses page to its event or item, and
        the record of each applied block (its digest and date)."""
        return self.data / RESPONSES_RECORD
    @property
    def practice_log(self):
        """The week's practice and rest record (each session's date, type, equipment, attendance
        and participation, and the days off)."""
        return self.data / PRACTICE_LOG
    @property
    def game_day_changes(self):
        """The week's depth or inactives changes made after its Game Plan was applied."""
        return self.data / GAME_DAY_CHANGES
    @property
    def call_sheet(self): return self.data / "call_sheet.json"
    @property
    def staff_texts(self):
        """The staff's authored parts of the week's briefing, each with its author and date
        (scripts/render_game_week.py renders a missing one "To come")."""
        return self.data / "staff_briefing.json"
    @property
    def inactives(self):
        """The week's game-day inactives as Stone set them (``players``, ``set`` and ``note``): the
        permanent owner of the list, which the game depth chart carries only while it is the latest."""
        return self.data / "inactives.json"
    @property
    def applied(self):
        """The record of the Game Plan as applied (scripts/apply_game_plan.py): when and from which
        page bytes the call sheet was frozen, its depth-chart changes and the event of the apply."""
        return self.data / "applied_plan.json"

    @property
    def pregame(self):
        """The Game Report's pregame sections as they stood at the game-day commit (``sections``: each
        heading and the sha256 of its text; ``frozen``, the day), written by scripts/freeze_pregame.py
        before kickoff; validation holds the report's sections 1 and 2 to it (runtime/game_report.py)."""
        return self.data / "pregame.json"

    def earlier_briefing(self, label):
        """An earlier briefing kept as what he saw: Game_Week_Briefing_October_5.md."""
        return self.folder / (self.briefing.stem + "_" + label.replace(" ", "_") + ".md")


@dataclass(frozen=True)
class ByeWeekPages:
    """The bye week's pages and its stored records, through the folder map (docs/bye_week.md): the
    Bye Week Review (the brief), My Adjustments (his page), the Bye Week Report (the result), the
    week's My Responses page when an event needs his answer, and the index."""
    folder: Path
    data: Path

    @property
    def readme(self): return self.folder / "README.md"
    @property
    def review(self): return self.folder / file_name(BY_KIND["bye_week"].brief)
    @property
    def adjustments(self): return self.folder / file_name(BY_KIND["bye_week"].page)
    @property
    def report(self): return self.folder / file_name(BY_KIND["bye_week"].result)
    @property
    def responses(self): return self.folder / file_name(RESPONSES)
    @property
    def briefings(self):
        """The issue record of the Bye Week Review (as a game week's ``briefings.json``)."""
        return self.data / "briefings.json"
    @property
    def staff_review(self):
        """The staff's authored parts of the review (the self-scout, the recommendations and the
        assessment), each with its author and date; a missing one renders "To come"."""
        return self.data / "staff_bye_review.json"
    @property
    def applied(self):
        """The record of My Adjustments as applied (the page's digest and the compiled choices)."""
        return self.data / "applied_adjustments.json"
    @property
    def practice_log(self): return self.data / PRACTICE_LOG
    @property
    def responses_record(self): return self.data / RESPONSES_RECORD

    def earlier_review(self, label):
        """An earlier review kept as what he saw: Bye_Week_Review_November_10.md."""
        return self.folder / (self.review.stem + "_" + label.replace(" ", "_") + ".md")


def bye_pages(year, week, root=None):
    """The bye week's pages: the week's own folder and its data twin, through the folder map."""
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    return ByeWeekPages(paths.week_folder(week), paths.week_data(week))


def waits_ahead(item, as_of):
    """The waits of a decision-queue item still to come on ``as_of`` (a date): each dated on or after
    it (an exam that day is still to come) and each with no date, in their order. A wait whose date
    has passed is not shown on a page built for ``as_of``."""
    day = as_of.isoformat()
    return [w for w in item.get("waits_on") or () if not w.get("date") or w["date"] >= day]


def exams_ahead(item, as_of):
    """The dated waits still to come on ``as_of``. While one remains, his answer on his page is set but
    the item stays open: he confirms it once they are held (scripts/apply_game_plan.py)."""
    return [w for w in waits_ahead(item, as_of) if w.get("date")]


def week_pages(year, week, root=None, postseason=None):
    """The game week's pages; ``postseason`` None reads it from the week (a postseason round after the
    season's last regular-season week, runtime/game_weeks.is_postseason), so a playoff game's pages
    are in the postseason folder through the folder map."""
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    if postseason is None:
        from .game_weeks import is_postseason
        postseason = is_postseason(paths, week)
    return WeekPages(paths.week_folder(week, postseason), paths.week_data(week, postseason),
                     paths.game_report(week, postseason))
