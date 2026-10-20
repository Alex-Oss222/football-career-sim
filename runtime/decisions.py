"""The decisions in a year (docs/rebuild_plan.md, "How a decision works" and
"The decisions in a year"): every decision point and its three pages.

Each decision has a brief (named for whoever really brings it), his page (a
fill-in page with fixed headings) and a result (named for where it is
decided), all in one folder. The registry below names each one; only the game
week is built so far (``implemented``), and the build steps that fill in the
others are named beside them. Nothing here reads or writes a record: the
registry and the page paths are data, and opening a page never moves time or
creates an event.

Folders are found through the folder map (runtime/seasons.SeasonPaths and
runtime/season_layout): ``place`` names where a decision's pages live, and
``folder`` resolves it for a season.
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
    Decision("injury_replacement", "Injury replacement in season", "Roster Move Request", "My Recommendation",
             "Transaction", "week", "The general manager and the medical staff", 5),
    Decision("trade_talks", "Trade talks", "Trade Call", "My Recommendation", "Trade Result", "trades",
             "The general manager", 5),
    Decision("season_end", "Season ends", "Season Review", "My Response", "Club Decision", "season_review",
             "The owner and the general manager", 6),
    Decision("extension", "Contract extension", "Extension Offer", "My Answer", "New Contract or Unchanged",
             "stone", "The club", 6),
    Decision("contract_ending", "Fired, or contract ending", "Agent's Report", "Instructions to My Agent",
             "Interviews and Offers", "stone", "His agent", 6),
    Decision("club_calls", "Another club calls", "Permission Request", "My Answer", "Interview or Declined",
             "stone", "The calling club, through his club", 6),
    Decision("after_interview", "After an interview", "Offer Sheet", "My Answer", "Signed or Talks Ended",
             "stone", "The interviewing club", 6),
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
    logical, up = PLACES[decision.place]
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
    def practice(self):
        """The practice week's record of the installs his Game Plan names (``installs``: each install's
        words as the page writes them, ``taught`` true or false, the ``date`` and the coach ``by``
        whom), written by whoever closes the practice week, never by code. The plan is set for the game
        only once every install it relies on is recorded taught (scripts/apply_game_plan.py)."""
        return self.data / "practice.json"
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
