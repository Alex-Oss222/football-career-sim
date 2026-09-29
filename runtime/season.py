"""One season value for every closure, input, receipt and view path.

Every season-scoped path in the weekly workflow resolves here from a season
(int) and an optional workspace root (the canonical checkout by default; an
isolated temporary workspace in tests):

- `library/data/{season}_schedule.json`: the regular-season slate.
- `library/data/{season}_postseason_slots.json`: postseason dates and sites.
- `library/data/{season}_week1_depth_charts.json`: background-club units.
- `career/{season}/roster.md` and `career/{season}/depth_chart.json`: the
  Jacksonville controlled-roster and depth-chart owners for that season's games.
- `career/{season}/{regular_season,postseason,preseason}/week_NN_*/call_sheet.json`.
- `career/{season}/stats/{game,postseason,preseason}_receipts/`.
- `career/{season}/migrations/event_generations.json`: that season's voids only.
- `.sim_cache/` for 2013 (the closed season's documented location) and
  `.sim_cache/{season}/` for every later season.
- Event IDs begin `{season}-week`.

2013 resolves to exactly the paths the closed season has always used. A
later season never falls back to a 2013 file: a missing prerequisite raises
`SeasonDataMissing` naming what must exist first.
"""
from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEASON = 2013
CLOSED_SEASON = 2013
EVENT_ID = re.compile(r"^(\d{4})-week\d{2}-")
PHASE_DIRS = {"regular": "regular_season", "postseason": "postseason", "preseason": "preseason"}
RECEIPT_DIRS = {"regular": "game_receipts", "postseason": "postseason_receipts",
                "preseason": "preseason_receipts"}


class SeasonDataMissing(ValueError):
    """A season-scoped prerequisite does not exist; nothing falls back to another season."""


def _gate_note(season):
    if season == 2014:
        return ("The 2014 league slate is built and validated at the April 23, 2014 schedule gate "
                "(career/2014/calendar.md); career/2014/schedule/opponents.md is an undated "
                "opponent inventory, not a schedule.")
    return "Build and verify it before any %d game is prepared." % season


def _missing_text(season, what, path, root):
    rel = Path(path).relative_to(root).as_posix() if Path(path).is_relative_to(root) else str(path)
    notes = {
        "schedule": "no %d schedule: %s does not exist. %s" % (season, rel, _gate_note(season)),
        "postseason_slots": ("no %d postseason slots: %s does not exist. Verify the real %d-%02d "
                             "postseason dates, kickoffs and sites first." % (season, rel, season,
                                                                              (season + 1) % 100)),
        "depth_library": ("no %d background depth library: %s does not exist. %d TeamInputs need a "
                          "rebuilt, sourced library (runtime/defect_register.md); the league_rails "
                          "research inventory is not a depth-ordered TeamInput." % (season, rel, season)),
        "roster": ("no %d Jacksonville roster owner: %s does not exist. career/2013/roster.md stays "
                   "the offseason controlled-roster record until the first %d roster-changing event "
                   "(career/2014/README.md), but it never feeds a %d game input." % (season, rel, season, season)),
        "depth_chart": ("no %d Jacksonville depth chart: %s does not exist. Stone's %d depth chart "
                        "must be written before a %d game input is built." % (season, rel, season, season)),
    }
    return notes[what] + " A %d request never falls back to 2013 data." % season


@dataclass(frozen=True)
class SeasonPaths:
    season: int
    root: Path

    @property
    def career(self):
        return self.root / "career" / str(self.season)

    @property
    def library_data(self):
        return self.root / "library" / "data"

    @property
    def schedule(self):
        return self.library_data / ("%d_schedule.json" % self.season)

    @property
    def postseason_slots(self):
        return self.library_data / ("%d_postseason_slots.json" % self.season)

    @property
    def depth_library(self):
        return self.library_data / ("%d_week1_depth_charts.json" % self.season)

    @property
    def roster(self):
        return self.career / "roster.md"

    @property
    def depth_chart(self):
        return self.career / "depth_chart.json"

    @property
    def generations(self):
        return self.career / "migrations" / "event_generations.json"

    @property
    def stats(self):
        return self.career / "stats"

    @property
    def standings(self):
        return self.career / "standings.md"

    def receipts_dir(self, game_type="regular"):
        if game_type not in RECEIPT_DIRS:
            raise ValueError("unknown game type %r" % game_type)
        return self.stats / RECEIPT_DIRS[game_type]

    def phase_dir(self, game_type="regular"):
        if game_type not in PHASE_DIRS:
            raise ValueError("unknown game type %r" % game_type)
        return self.career / PHASE_DIRS[game_type]

    @property
    def cache(self):
        # The closed 2013 season keeps its documented location; any other
        # season has its own namespace, so no cached package or result of one
        # season can be read as another's.
        base = self.root / ".sim_cache"
        return base if self.season == CLOSED_SEASON else base / str(self.season)

    def inputs_cache(self, week):
        return self.cache / ("week_%02d_inputs.json" % int(week))

    def results_cache(self, week):
        return self.cache / ("week_%02d_results.json" % int(week))

    @property
    def event_prefix(self):
        return "%d-week" % self.season

    def require(self, what):
        """The named season file, or SeasonDataMissing explaining what must exist first."""
        path = getattr(self, what)
        if not path.is_file():
            raise SeasonDataMissing(_missing_text(self.season, what, path, self.root))
        return path


def season_paths(season=DEFAULT_SEASON, root=None):
    if isinstance(season, bool) or not isinstance(season, int):
        raise TypeError("season must be an int, not %r" % (season,))
    from .league import require_season
    require_season(season)
    return SeasonPaths(season, Path(root).resolve() if root is not None else ROOT)


def season_of_event(event_id):
    """The season an event ID belongs to (every event ID begins with its season)."""
    match = EVENT_ID.match(str(event_id))
    if not match:
        raise ValueError("event id %r does not begin with a season" % (event_id,))
    return int(match.group(1))


def season_dirs(root=None):
    """Seasons with a career folder, in order."""
    base = (Path(root) if root is not None else ROOT) / "career"
    return sorted(int(p.name) for p in base.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name))
