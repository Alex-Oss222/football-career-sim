"""The pages a game week's close rewrites on the result side (rebuild step 4).

Every page here is built from its stored owners and passes the clean-page
rule (runtime/clean_pages.py); scripts/render_week_pages.py writes them and
checks them, and repository validation runs its check.

- The Games index (``regular_season/README.md``, Jacksonville's season): one
  row per week from the released fixtures, the result of each closed game
  from its closed-game record, linked to the game's result page
  (SeasonPaths.game_report), and the next game from the master date.
- The league-results index (``league_results/README.md``): one row per closed
  week, its dates, games and byes from the fixtures, Jacksonville's result.
- The league-results week page (``league_results/week_NN.md``), from the
  first Game Report week (GAME_REPORT_FROM) once every game of the week has
  closed: the dates, byes, links, the score table from the closed games, and
  one section per game in the table's order. The highlights under each game
  heading and the reactive-events section are stored text, written by whoever
  writes the week's roundup, in the page's twin in the data area
  (``highlights_path``: ``{"games": {event id: highlights}, "reactive_events":
  text}``); the page is never read back. A game without stored highlights
  reads "Highlights to come."; a stored entry that names no other game of the
  week, or is not text, stops the build instead of being dropped. The pages of
  earlier weeks are history and are never rewritten.
- The medical pages (``medical/``): the current injury report, rewritten from
  the roster record (the owner of each player's current medical
  communication) each time it is built, in short (runtime/season_summary.py:
  the status and the next medical date, each player linked to his page and
  each status to its medical record); and, for each Jacksonville game from
  the first Game Report week, the medical history's dated entry for the
  game's injuries, with its event-record line, appended once from the game's
  record (a history page only gains entries), and one incident record per new
  injury, created once in the medical report layout and then kept by hand
  (later findings are dated rows added to its updates table). Both link the
  game's Game Report (SeasonPaths.game_report), written before them.

A game counts once its closed-game record exists (a week's slate closes in
one batch, its Monday game included); the as-of line and the next game read
the master date (runtime/player_bios.master_date).
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

from . import injury_model, people, roster as roster_record, season_summary as summary
from .player_bios import master_date
from .player_pages import club_short
from .play_detail import DRIVE_SUMMARY_FIELDS
from .seasons import GAME_REPORT_FROM, SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
JAX = "Jacksonville Jaguars"
NO_RESTRICTION = "No communicated restriction"
TO_COME = "Highlights to come."
REACTIVE = "Reactive events"
NONE_RECORDED = "None recorded."
NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
           9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
           16: "sixteen"}
PERIODS = {1: "first", 2: "second", 3: "third", 4: "fourth"}
CLASSES = {"head_neck": "head/neck", "upper_extremity": "upper extremity", "lower_extremity": "lower extremity",
           "trunk": "trunk"}
RESTRICTIONS = {"out": "out", "limited": "limited"}
# The roster record's instruction for each restriction an injury carries (runtime/season_summary's
# one medical format); a restriction not named here is refused, never written as out.
INSTRUCTIONS = {"out": "Out", "limited": "Limited", injury_model.HOLD: "Independent medical hold"}
# The practice participation and permitted work each restriction the game records allows, as the
# incident page writes them: an independent medical hold is no football work until it is released,
# as the hand-written holds of August and September 2014 read.
PARTICIPATION = {"out": ("out until reassessed", "None until reassessed"),
                 "limited": ("limited until reassessed", "Limited until reassessed"),
                 injury_model.HOLD: ("none until the independent medical process releases the hold",
                                     "None until the independent process releases the hold")}
# Each injury severity the game records in football words, as the medical pages write them
# ("Out, multi-week: lower extremity"). An unlisted one reads with its underscores as spaces.
SEVERITIES = {"minor": "minor", "short": "short", "multi_week": "multi-week", "long_term": "long term"}
# A roster status as the roster page names it (scripts/render_club_pages.py STATUS_NAMES).
STATUS_NAMES = {"Active 53": "Active roster", "Offseason roster": "Offseason roster",
                "Reserve/Injured": "Reserve/injured",
                "Reserve/Injured, designated for return": "Reserve/injured, designated for return",
                "Practice squad": "Practice squad"}


def status_text(status):
    name = roster_record.status_name(status)
    return STATUS_NAMES.get(name, name)


# ------------------------------------------------------------------ small formats
def long_date(value):
    return "%s %d, %d" % (value.strftime("%B"), value.day, value.year)


def month_day(value):
    return "%s %d" % (value.strftime("%B"), value.day)


def span(first, last):
    if first == last:
        return long_date(first)
    if first.year == last.year and first.month == last.month:
        return "%s %d to %d, %d" % (first.strftime("%B"), first.day, last.day, last.year)
    return "%s to %s" % (month_day(first) if first.year == last.year else long_date(first), long_date(last))


def kickoff(clock):
    hour, minute = (int(part) for part in clock.split(":"))
    if (hour, minute) == (12, 0):
        return "noon"
    hand = hour % 12 or 12
    return ("%d" % hand if minute == 0 else "%d:%02d" % (hand, minute)) + (" a.m." if hour < 12 else " p.m.")


def count_word(n):
    return NUMBERS.get(n, str(n))


def join(items):
    items = list(items)
    if len(items) < 3:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def table(head, rows, right=()):
    lines = ["| " + " | ".join(head) + " |",
             "|" + "|".join("---:" if i in right else "---" for i in range(len(head))) + "|"]
    return lines + ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]


def relative(page, target):
    """The link destination from the page at repository path ``page`` to ``target``."""
    return os.path.relpath(target, os.path.dirname(page)).replace(os.sep, "/").replace(" ", "%20")


def link(page, target, label):
    return "[%s](%s)" % (label, relative(page, target))


LINK = re.compile(r"\]\(([^)\s]+)\)")


def rebase(text, source, page):
    """``text`` written for the page at ``source``, with its relative links pointing from ``page``."""
    def one(match):
        dest = match.group(1)
        if "://" in dest or dest.startswith("#"):
            return match.group(0)
        path, _, anchor = dest.partition("#")
        target = os.path.normpath(os.path.join(os.path.dirname(source), path)).replace(os.sep, "/")
        return "](%s%s)" % (relative(page, target), "#" + anchor if anchor else "")
    return LINK.sub(one, text)


# ------------------------------------------------------------------ the season
def game_key(game):
    return int(game["week"]), game["away"], game["home"]


def overtime(receipt):
    half = DRIVE_SUMMARY_FIELDS.index("half")
    return any(row[half] == "OT" for row in receipt.get("drives", ()))


class Season:
    """The fixtures, the closed games up to the master date and the roster record of one season."""

    def __init__(self, root=ROOT, year=None):
        from .seasons import active_season
        self.root = Path(root).resolve()
        self.year = active_season(self.root) if year is None else year
        self.paths = SeasonPaths(self.year, self.root)
        self.as_of = master_date(self.root)
        self.fixtures = self.paths.regular_games()
        self.by_key = {game_key(g): g for g in self.fixtures}
        self.receipts = {}
        directory = self.paths.receipts
        for path in sorted(directory.glob("*.json")) if directory.is_dir() else ():
            receipt = json.loads(path.read_text(encoding="utf-8"))
            if game_key(receipt) in self.by_key:
                self.receipts[game_key(receipt)] = receipt
        self.roster = roster_record.load(self.paths.roster)
        self.teams = sorted({g[side] for g in self.fixtures for side in ("away", "home")})
        self.pending = set()    # repository paths a write is about to create (they count as present)

    def exists(self, rel):
        return rel in self.pending or (self.root / rel).is_file()

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def week_games(self, week):
        return [g for g in self.fixtures if g["week"] == week]

    def weeks(self):
        return sorted({g["week"] for g in self.fixtures})

    def closed_weeks(self):
        """Weeks every game of which has closed."""
        return [w for w in self.weeks() if all(game_key(g) in self.receipts for g in self.week_games(w))]

    def jacksonville(self, week):
        return next((g for g in self.week_games(week) if JAX in (g["away"], g["home"])), None)

    def receipt(self, game):
        return self.receipts.get(game_key(game)) if game else None

    def byes(self, week):
        playing = {g[side] for g in self.week_games(week) for side in ("away", "home")}
        return [t for t in self.teams if t not in playing]

    def next_game(self):
        ours = [g for g in self.fixtures if JAX in (g["away"], g["home"]) and game_key(g) not in self.receipts]
        return min(ours, key=lambda g: g["date"]) if ours else None

    def record(self):
        won = lost = tied = 0
        for receipt in self.receipts.values():
            if JAX not in (receipt["away"], receipt["home"]):
                continue
            ours, theirs = jax_score(receipt)
            won, lost, tied = won + (ours > theirs), lost + (ours < theirs), tied + (ours == theirs)
        return "%d-%d" % (won, lost) + ("-%d" % tied if tied else "")

    def result_page(self, week):
        page = self.paths.game_report(week)
        return page if page.is_file() else None


def jax_score(receipt):
    other = receipt["home"] if receipt["away"] == JAX else receipt["away"]
    return receipt["final_score"][JAX], receipt["final_score"][other]


def opponent_text(game):
    home = game["home"] == JAX
    other = game["away"] if home else game["home"]
    return ("vs. %s" if home else "at %s") % club_short(other)


def result_text(receipt):
    ours, theirs = jax_score(receipt)
    word = "Won" if ours > theirs else "Lost" if ours < theirs else "Tied"
    return "%s %d-%d%s" % (word, max(ours, theirs), min(ours, theirs), " (OT)" if overtime(receipt) else "")


def score_line(receipt):
    """"Pittsburgh 27, Jacksonville 10": the winner first, the away club first in a tie."""
    score = receipt["final_score"]
    first, second = receipt["away"], receipt["home"]
    if score[second] > score[first]:
        first, second = second, first
    return "%s %d, %s %d" % (club_short(first), score[first], club_short(second), score[second])


def site_text(game):
    return game["stadium"] + (", %s" % game["city"] if game.get("city") else "")


# ------------------------------------------------------------------ the Games index
def games_index(season):
    page = season.rel(season.paths.regular_season / "README.md")
    games = {g["week"]: g for g in season.fixtures if JAX in (g["away"], g["home"])}
    closed = [w for w in games if season.receipt(games[w])]
    lines = ["# Jacksonville %d regular season" % season.year, ""]
    head = "**%s" % season.record()
    head += " through Week %d.**" % max(closed) if closed else " before the opener.**"
    upcoming = season.next_game()
    if upcoming:
        when = date.fromisoformat(upcoming["date"])
        head += " Next: Week %d %s, %s, %s, %s ET, %s." % (
            upcoming["week"], opponent_text(upcoming).replace("vs.", "against"), upcoming["weekday"],
            month_day(when), kickoff(upcoming["kickoff_et"]), site_text(upcoming))
    lines += [head, ""]
    rows = []
    for week in season.weeks():
        folder = season.paths.week_folder(week)
        label = "Week %d" % week
        if (folder / "README.md").is_file():
            label = link(page, season.rel(folder / "README.md"), label)
        game = games.get(week)
        if game is None:
            rows.append([label, "", "Bye", "", "", ""])
            continue
        when = date.fromisoformat(game["date"])
        receipt = season.receipt(game)
        result = ""
        if receipt:
            result = result_text(receipt)
            report = season.result_page(week)
            if report:
                result = link(page, season.rel(report), result)
        elif game is upcoming:
            result = "Next"
        rows.append([label, "%s, %s" % (game["weekday"], month_day(when)), opponent_text(game),
                     kickoff(game["kickoff_et"]), site_text(game), result])
    lines += table(["Week", "Date", "Opponent", "Kickoff (ET)", "Site", "Result"], rows) + [""]
    released = date.fromisoformat(json.loads(season.paths.schedule.read_text(encoding="utf-8"))["released"][:10])
    lines.append("Dates, sites and kickoffs are the league's schedule as released %s, Eastern Time; a later "
                 "change applies from the date it was announced." % long_date(released))
    lines += ["", " · ".join(link(page, season.rel(target), label) for label, target in (
        ("Schedule", season.paths.record("schedule/fixtures.md")),
        ("Schedule sources", season.paths.record("schedule/sources.md")),
        ("Standings", season.paths.record("standings.md")),
        ("League results", season.paths.record("league_results/README.md")),
        ("Statistics", season.paths.record("statbook.md")),
        ("Calendar", season.paths.calendar)) if target.is_file()), ""]
    return page, "\n".join(lines)


# ------------------------------------------------------------------ league results
def results_folder(season):
    return season.paths.record("league_results")


def week_page_path(season, week):
    return results_folder(season) / ("week_%02d.md" % week)


def built_weeks(season):
    """The closed weeks whose league-results page this builder writes: from the first Game
    Report week on (earlier pages are history)."""
    year, first = GAME_REPORT_FROM
    start = 1 if season.year > year else first if season.year == year else None
    return [w for w in season.closed_weeks() if start is not None and w >= start]


def week_dates(season, week):
    days = sorted(date.fromisoformat(g["date"]) for g in season.week_games(week))
    return days[0], days[-1]


def results_index(season):
    folder = results_folder(season)
    page = season.rel(folder / "README.md")
    lines = ["# %d league results" % season.year, "",
             "Every closed week's scores and highlights; Jacksonville's own game has its full report in its "
             "week's folder.", ""]
    rows = []
    built = set(built_weeks(season))
    for week in season.closed_weeks():
        target = week_page_path(season, week)
        label = "Week %d" % week
        if week in built or target.is_file():
            label = link(page, season.rel(target), label)
        game = season.jacksonville(week)
        ours = "Bye"
        if game:
            ours = "%s %s" % (result_text(season.receipt(game)), opponent_text(game))
            report = season.result_page(week)
            if report:
                ours = link(page, season.rel(report), ours)
        byes = season.byes(week)
        rows.append([label, span(*week_dates(season, week)), len(season.week_games(week)),
                     join(club_short(t) for t in byes) or "None", ours])
    if rows:
        lines += table(["Week", "Played", "Games", "Byes", "Jacksonville"], rows, right=(2,)) + [""]
    else:
        lines += ["No week has closed.", ""]
    lines += [" · ".join(link(page, season.rel(target), label) for label, target in (
        ("Standings", season.paths.record("standings.md")),
        ("Jacksonville's games", season.paths.regular_season / "README.md"),
        ("Statistics", season.paths.record("statbook.md"))) if target.is_file()), ""]
    return page, "\n".join(lines)


def ordered_games(season, week):
    """Jacksonville's game first, then the rest by away club, as the score table lists them."""
    games = season.week_games(week)
    return sorted(games, key=lambda g: (JAX not in (g["away"], g["home"]), g["away"]))


def highlights_path(season, week):
    """The week's stored highlights and reactive events: the league-results page's twin in the
    data area."""
    return season.paths.file_in(results_folder(season), "week_%02d.json" % week)


HIGHLIGHT_KEYS = {"about", "games", "reactive_events"}


def highlights(season, week):
    """({event id: highlights}, reactive events or None): the week's stored text for its
    league-results page. ValueError for a record that is not an object of those keys, an entry
    that names no game of the week other than Jacksonville's (whose game has its own report), or
    a value that is not text."""
    path = highlights_path(season, week)
    if not path.is_file():
        return {}, None
    rel = season.rel(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - HIGHLIGHT_KEYS:
        raise ValueError("%s holds only %s" % (rel, ", ".join(sorted(HIGHLIGHT_KEYS))))
    games = data.get("games") or {}
    reactive = data.get("reactive_events")
    if not isinstance(games, dict) or not all(isinstance(v, str) and v.strip() for v in games.values()):
        raise ValueError("%s: each game's highlights are text, keyed by the game's event id" % rel)
    if reactive is not None and not (isinstance(reactive, str) and reactive.strip()):
        raise ValueError("%s: the reactive events are text" % rel)
    known = {season.receipt(g)["event_id"]: g for g in season.week_games(week) if season.receipt(g)}
    for key in sorted(games):
        game = known.get(key)
        if game is None:
            raise ValueError("%s: %s is not a closed Week %d game" % (rel, key, week))
        if JAX in (game["away"], game["home"]):
            raise ValueError("%s: Jacksonville's game has its own report, not a highlights entry" % rel)
    return {k: v.strip() for k, v in games.items()}, (reactive.strip() if reactive else None)


def week_page(season, week):
    path = week_page_path(season, week)
    page = season.rel(path)
    stored, reactive = highlights(season, week)
    first, last = week_dates(season, week)
    games = ordered_games(season, week)
    byes = season.byes(week)
    lines = ["# %d Week %d league results" % (season.year, week), ""]
    head = "**Played:** %s, %s games." % (span(first, last), count_word(len(games)))
    head += " **Byes:** %s." % join(club_short(t) for t in byes) if byes else " No club on bye."
    lines += [head, ""]
    links = [("Standings", season.paths.record("standings.md")),
             ("Week %d awards" % week, season.paths.awards / ("week_%02d" % week) / "README.md"),
             ("All weeks", results_folder(season) / "README.md")]
    lines += [" · ".join(link(page, season.rel(t), label) for label, t in links if t.is_file()), ""]
    ours = season.jacksonville(week)
    if ours:
        text = score_line(season.receipt(ours))
        report = season.result_page(week)
        lines += ["Jacksonville's game: %s." % (link(page, season.rel(report), text) if report else text), ""]
    rows = []
    for game in games:
        score = season.receipt(game)["final_score"]
        away, home = score[game["away"]], score[game["home"]]
        rows.append([game["away"], "**%d**" % away if away > home else away,
                     game["home"], "**%d**" % home if home > away else home])
    lines += table(["Away", "Score", "Home", "Score"], rows, right=(1, 3)) + [""]
    for game in games:
        if game is ours:
            continue
        receipt = season.receipt(game)
        heading = score_line(receipt) + (" (OT)" if overtime(receipt) else "")
        lines += ["## " + heading, "", stored.get(receipt["event_id"]) or TO_COME, ""]
    lines += ["## " + REACTIVE, "", reactive or NONE_RECORDED, ""]
    return page, "\n".join(lines)


# ------------------------------------------------------------------ medical
def medical_path(season, name):
    return season.paths.record("medical/" + name)


def as_of_line(season):
    line = "As of %s" % long_date(season.as_of)
    ours = [r for r in season.receipts.values() if JAX in (r["away"], r["home"])]
    if ours:
        last = max(ours, key=lambda r: int(r["week"]))
        game = season.by_key[game_key(last)]
        line += ", after the Week %d game %s (%s)" % (
            int(last["week"]), opponent_text(game).replace("vs.", "against"), score_line(last))
    return line + "."


def player_link(season, page, name):
    """The player's name, linked to his page when it exists."""
    target = season.paths.record("player_profiles") / (people.slugify(name) + ".md")
    return link(page, season.rel(target), name) if target.is_file() else name


def status_link(season, page, row):
    """The player's medical status in short (runtime/season_summary.medical_status), linked to the
    medical record the roster record names as its source."""
    text = summary.medical_status(row)
    source = (row.get("sources") or {}).get("availability")
    return link(page, source, text) if source and season.exists(source) else text


def injury_report(season):
    """The current injury report, from the roster record: each player under a medical instruction
    with his status and next medical date, the reserve lists with theirs, then the count of the
    rest. Each status links the medical record behind it."""
    path = medical_path(season, "current_injury_report.md")
    page = season.rel(path)
    players = season.roster["players"]
    held = summary.held(season.roster)
    reserve = summary.reserve(season.roster)

    def row(p, with_list=False):
        cells = [player_link(season, page, p["name"]), p["position"]]
        if with_list:
            cells.append(status_text(p["status"]))
        return cells + [status_link(season, page, p), summary.next_dates(p, season.as_of)]

    lines = ["# Jacksonville injury report", "",
             as_of_line(season) + " The medical staff control participation and return clearance.", "",
             " · ".join([link(page, season.rel(medical_path(season, "medical_history.md")), "Medical history"),
                         link(page, season.rel(season.paths.roster_page), "Roster"),
                         link(page, season.rel(season.paths.record("depth_chart.md")), "Depth chart"),
                         link(page, season.rel(medical_path(season, "README.md")), "Medical records"),
                         link(page, season.rel(season.paths.desk), "Head coach's desk")]), ""]
    lines += ["## Active roster", ""]
    if held:
        lines += table(["Player", "Pos", "Status", "Next medical date"], [row(p) for p in held]) + [""]
    else:
        lines += ["No player on the active roster is under a medical instruction.", ""]
    if reserve:
        lines += ["## Reserve lists", ""] + table(["Player", "Pos", "List", "Status", "Next medical date"],
                                                  [row(p, True) for p in reserve]) + [""]
    clear = sum(1 for p in players if p["list"] == "active" and p not in held)
    squad = sum(1 for p in players if p["list"] == "practice_squad")
    lines += ["The other %d players on the active roster and the %d on the practice squad carry no "
              "communicated restriction. A projected return is the medical staff's projection, not a "
              "clearance; each player's medical record holds his full instruction and its history." % (clear, squad), ""]
    return page, "\n".join(lines)


def injury_date(season, receipt):
    return date.fromisoformat(season.by_key[game_key(receipt)]["date"])


def report_games(season):
    """Jacksonville's closed games from the first Game Report week."""
    year, first = GAME_REPORT_FROM
    out = []
    for receipt in sorted(season.receipts.values(), key=lambda r: int(r["week"])):
        if JAX not in (receipt["away"], receipt["home"]):
            continue
        if season.year > year or (season.year == year and int(receipt["week"]) >= first):
            out.append(receipt)
    return out


def ours_injured(receipt):
    return [i for i in receipt.get("injuries", ()) if i.get("team") == JAX]


def roster_row(season, name):
    return next((p for p in season.roster["players"] if p["name"] == name), None)


def incident_path(season, injury, played):
    return medical_path(season, "incidents/%s_%s.md" % (people.slugify(injury["player"]), played.isoformat()))


def clock_text(injury):
    period = injury.get("period")
    where = "of the %s quarter" % PERIODS[period] if period in PERIODS else "of overtime"
    return "at %s %s" % (injury.get("clock"), where)


def participation(injury):
    """(practice participation, permitted work) for the injury's restriction; a restriction the
    table does not name is refused rather than written as limited work."""
    restriction = injury.get("restriction") or "limited"
    if restriction not in PARTICIPATION:
        raise ValueError("no practice wording for the restriction %r" % restriction)
    return PARTICIPATION[restriction]


def words(value, table):
    """``value`` (a code the game records) in football words: from ``table``, else with its
    underscores as spaces."""
    return table.get(value) or str(value).replace("_", " ")


def severity_words(injury):
    return words(injury.get("severity"), SEVERITIES)


def instruction_text(injury, played, days_shown=True):
    restriction = words(injury.get("restriction"), RESTRICTIONS) if injury.get("restriction") else "no restriction"
    parts = [restriction]
    days = injury.get("return_days") or 0
    if days:
        parts.append("projected return %s" % month_day(played + timedelta(days=days))
                     + (" (%s)" % ("1 day" if days == 1 else "%d days" % days) if days_shown else ""))
    else:
        parts.append("no time lost projected")
    if injury.get("reassessment_days"):
        parts.append("reassessment %s" % month_day(played + timedelta(days=injury["reassessment_days"])))
    return ", ".join(parts)


def availability_entry(season, receipt, injury):
    """(text, source): the roster record's medical communication for a player injured in a
    Jacksonville game, written from the game's record in the one medical format
    (runtime/season_summary.py), and the incident record it cites. The close records it on the
    player's roster row (``availability`` and ``sources.availability``); the injury report, the
    desk and the Game Week Briefing read it from there."""
    played = injury_date(season, receipt)
    days = injury.get("return_days") or 0
    restriction = injury.get("restriction")
    if restriction not in INSTRUCTIONS:
        raise ValueError("no medical instruction for the restriction %r" % restriction)
    instruction = INSTRUCTIONS[restriction]
    severity = severity_words(injury) if days or restriction != "limited" else "no projected absence"
    parts = ["%s, %s: %s, logged %s in the %s Week %d game, %s" % (
        instruction, severity, words(injury.get("injury_class"), CLASSES), clock_text(injury), month_day(played),
        int(receipt["week"]), "removed" if injury.get("removed") else "not removed")]
    parts.append("projected return %s" % long_date(played + timedelta(days=days)) if days
                 else "no time lost projected")
    if injury.get("reassessment_days"):
        parts.append("reassessment %s" % month_day(played + timedelta(days=injury["reassessment_days"])))
    incident = season.rel(incident_path(season, injury, played))
    page = season.rel(season.paths.roster_page)
    return "%s (%s)" % ("; ".join(parts), link(page, incident, "medical record")), incident


def injury_words(injury):
    return "%s, %s" % (words(injury.get("injury_class"), CLASSES), severity_words(injury))


def game_phrase(season, receipt):
    game = season.by_key[game_key(receipt)]
    return "the Week %d game %s" % (int(receipt["week"]), opponent_text(game).replace("vs.", "against"))


def game_closure(report, played):
    """The id of the closed event a week's Game Report carries for the game played on ``played``
    (its closure runs through that day), or None (no report, or none closed that day)."""
    if not report.is_file():
        return None
    found = None
    for match in re.finditer(r"<!-- event-record: (\{.*?\}) -->", report.read_text(encoding="utf-8")):
        data = json.loads(match.group(1))
        if (data.get("closure") or {}).get("through") == played.isoformat() and data.get("kind", "football") == "football":
            found = data["id"]
    return found


def history_entry(season, receipt):
    """The medical history's entry for one Jacksonville game's injuries, or None without one."""
    injuries = ours_injured(receipt)
    if not injuries:
        return None
    played = injury_date(season, receipt)
    page = season.rel(medical_path(season, "medical_history.md"))
    phrase = game_phrase(season, receipt)
    where = re.sub(r"^the Week \d+ game ", "", phrase)
    n = len(injuries)
    noun = "player was" if n == 1 else "players were"
    lead = "%s Jacksonville %s injured in %s (%s)" % (count_word(n).capitalize(), noun, phrase, score_line(receipt))
    summary = lead + ": " + join("%s (%s; %s; %s)" % (
        i["player"], injury_words(i), "removed" if i.get("removed") else "not removed",
        instruction_text(i, played, days_shown=False)) for i in injuries) + "."
    event = {"date": played.isoformat(), "id": "%s-week-%d-injuries-%s" % (
        played.isoformat(), int(receipt["week"]), people.slugify(where).replace("_", "-")),
        "status": "closed", "summary": summary}
    report = season.paths.game_report(int(receipt["week"]))
    # A Game Report (from 2014 Week 6) carries the game's closed event: the injuries follow it in
    # the annual record, after the day's earlier records (the applied Game Plan among them).
    game_event = game_closure(report, played)
    if game_event:
        event["follows"] = game_event
    game_link = link(page, season.rel(report), phrase[4:])
    lines = ["<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), "",
             "## %s: Week %d injuries %s" % (month_day(played), int(receipt["week"]), where), "",
             "%s Jacksonville %s injured in the %s (%s), each with its own incident record:" % (
                 count_word(n).capitalize(), noun, game_link, score_line(receipt)), ""]
    for injury in injuries:
        row = roster_row(season, injury["player"]) or {}
        name = link(page, season.rel(incident_path(season, injury, played)), injury["player"])
        lines.append("- %s%s: %s; injured %s, %s; %s." % (
            name, ", " + row["position"] if row.get("position") else "", injury_words(injury),
            clock_text(injury), "removed" if injury.get("removed") else "not removed",
            instruction_text(injury, played)))
    lines += ["", "A projected return is the medical staff's projection, not a clearance. No other Jacksonville "
              "injury was recorded in the game.", ""]
    return "\n".join(lines)


def incident_page(season, receipt, injury):
    played = injury_date(season, receipt)
    path = incident_path(season, injury, played)
    page = season.rel(path)
    row = roster_row(season, injury["player"]) or {}
    report = season.paths.game_report(int(receipt["week"]))
    phrase = game_phrase(season, receipt)
    game_text = link(page, season.rel(report), phrase[4:])
    days = injury.get("return_days") or 0
    removed = "removed from the game" if injury.get("removed") else "not removed; he finished the game"
    lines = ["# %s | %s | Medical report" % (injury["player"], long_date(played)), "",
             "**Team and position:** Jacksonville Jaguars, %s  " % (row.get("position") or "position not recorded"),
             "**Updated through:** %s  " % long_date(played),
             "**Incident:** Injured in the %s (%s), %s, %s." % (game_text, score_line(receipt), clock_text(injury),
                                                              removed), "",
             "## Current medical information", "",
             "- Injury: %s; no clinical diagnosis recorded" % injury_words(injury),
             "- Practice participation: %s" % participation(injury)[0],
             "- Game designation: none issued; the next game's designation follows the league's injury-report rules",
             "- Roster designation: %s (%s)" % (status_text(row["status"]) if row.get("status") else "Not on the roster",
                                                link(page, season.rel(season.paths.roster_page), "roster")),
             "- Communicated restrictions: %s" % instruction_text(injury, played),
             "- Clearance: not yet communicated",
             "- Expected return: %s" % ("%s, the medical staff's projection" % long_date(played + timedelta(days=days))
                                        if days else "no time lost projected"),
             "- Next medical review: %s" % (long_date(played + timedelta(days=injury["reassessment_days"]))
                                            if injury.get("reassessment_days") else "none set"), "",
             "## Dated updates", ""]
    lines += table(["Date", "Communicated finding", "Permitted work", "Source"],
                   [[long_date(played), "%s; %s; %s" % (injury_words(injury).capitalize(), "removed" if injury.get("removed")
                                                         else "not removed", instruction_text(injury, played)),
                     participation(injury)[1],
                     link(page, season.rel(report), "Game report")]]) + [""]
    lines += ["## Football effect", "",
              "Practices and games missed are recorded here as they occur.", "",
              "## Sources", "",
              " · ".join((link(page, season.rel(report), "Game report"),
                          link(page, season.rel(season.paths.roster_page), "Roster"),
                          link(page, season.rel(medical_path(season, "medical_history.md")), "Medical history"))), ""]
    return page, "\n".join(lines)


# ------------------------------------------------------------------ the whole set
def built(season):
    """{repository path: text} of every page rebuilt in full (the indexes, the league-results week
    pages from the first Game Report week, the injury report)."""
    out = dict([games_index(season), results_index(season), injury_report(season)])
    for week in built_weeks(season):
        rel, text = week_page(season, week)
        out[rel] = text
    return out


def history_entries(season):
    """[(event id, entry text)] the medical history must hold, in game order."""
    out = []
    for receipt in report_games(season):
        entry = history_entry(season, receipt)
        if entry:
            out.append((json.loads(entry.split("event-record: ", 1)[1].split(" -->", 1)[0])["id"], entry))
    return out


def incidents(season):
    """{repository path: text} of the incident record each new injury opens with."""
    out = {}
    for receipt in report_games(season):
        for injury in ours_injured(receipt):
            rel, text = incident_page(season, receipt, injury)
            out[rel] = text
    return out
