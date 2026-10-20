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
index and never pasted into the weekly report. Only the game week is built so
far (``implemented``); the build steps that fill in the rest are named beside
them. Nothing here reads or writes a record: the registries and the page paths
are data, and opening a page never moves time or creates an event.

Folders are found through the folder map (runtime/seasons.SeasonPaths and
runtime/season_layout): a decision's ``place`` and an event's ``owner`` name
where its pages live, and ``folder`` and ``event_folder`` resolve them for a
season.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .season_layout import STONE_PAGES
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
    Decision("season_end", "Season ends", "Season Review", "My Season Response", "Club Decision", "season_review",
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
# is the folder of an event below; an owner the plan names but no event uses yet (signings, in
# Team_Operations/Free_Agency) is added with its first event.
OWNERS = {
    "roster": ("team/roster", 0),                 # roster moves: Team_Operations/Team/Roster
    "trades": ("trades/README.md", 1),            # trades: Team_Operations/Trades
    "staff": ("team/coaching_staff", 0),          # staff: Team_Operations/Staff
}

EVENTS = (
    Event("injury_replacement", "Injury replacement in season", "Transaction", "roster",
          "The general manager and the medical staff", 5),
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
# The week's or phase's one answer page for the events inserted in its brief.
RESPONSES = "My Responses"


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
    event = EVENT_KIND[event] if isinstance(event, str) else event
    paths = SeasonPaths(year) if root is None else SeasonPaths(year, root)
    if event.owner == "stone":
        return paths.root / STONE_PAGES
    return _resolve(paths, OWNERS[event.owner])


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
