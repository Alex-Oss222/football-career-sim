"""The player pages (rebuild step 3a): one builder for every player page.

Every page is built from the player's permanent record (runtime/people.py)
and the owners runtime/people.READ_THROUGH names, in the order it gives
(awards from the award results), in the layout of the user's player card
template (foundation/templates/player_card_template.md, October 20, 2026;
docs/rebuild_plan.md, "The pages to read", Player):

    header line (name; club, position, number, age, status)
    height, weight, birth date, college and draft; "As of"; the photo with its credit
    Current assignment: one plain confirmed role (runtime/assignments.py), from
        the game depth chart for a Jaguar on the active roster, else his slot on
        the season's Week 1 depth chart while nothing since has moved him
    the position statistic (QB passer rating, RB yards per carry, ...) for the
        active season, from the closed games only (``position_metric``), through
        the week the As of line names
    Staff assessment (only for a player a Jacksonville staff assessed): the
        latest assessment's short summary, two to four sentences with its
        season figures resolved from his closed Jacksonville games
        (``resolve_tokens``) and one dated line (``date_line``: the date of the
        view it summarizes, or the original date and the figures' cutoff); no
        grade is shown (the grades stay in the record). A record whose latest
        assessment has no short yet shows its staff read
    Contract (salary by year, where Jacksonville holds the contract; else "Contract
        not established.")
    Statistics (regular season and playoffs apart, every table led by
        Season, Team, Age and #; the quarterback's column is "Passer rating")
    Awards
    Transactions (one dated line each)

There is no weekly section and no career-card image. The same page is
written at the player's league page (career/league_players/<club>/, the club
of his latest game) and, for a player Jacksonville controls or its staff
assessed this season, in the season's player folder, so the two can never
differ. The league index, the club pages and the season folder's index are
written here too. Once the season is closed (its season review exists), its
player folder is history: it is no longer written or checked, and the next
season's folder takes over when that season becomes active. A page is built, never hand-edited: ``check`` rebuilds
every page in memory and reports each that differs, and ``write`` creates an
identity-only record for a player who first reaches the game records (no
other fact is ever created, and no record holds an award: the award results
own them). The pages carry no system wording; the clean-page
check in scripts/validate_repository.py reads ``MARKERS``.
"""
from __future__ import annotations

import json
import os
import posixpath
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

from . import assignments, people, player_bios, player_cards
from . import roster as roster_record
from .league import DIVISION_OF, DIVISIONS
from .season_layout import LEAGUE_PLAYER_PAGES, PHOTO_REGISTRY, PLAYER_RECORDS
from .seasons import SeasonPaths, active_season

ROOT = Path(__file__).resolve().parents[1]
PAGE_MARK = "<!-- player-page -->"
INDEX_MARK = "<!-- player-index -->"
MARKERS = (PAGE_MARK, INDEX_MARK)
JAX = player_cards.JAX
N_A = "N/A"
POSITION_NAMES = {
    "QB": "Quarterback", "RB": "Running back", "HB": "Running back", "FB": "Fullback", "WR": "Wide receiver",
    "TE": "Tight end", "OT": "Offensive tackle", "T": "Offensive tackle", "LT": "Offensive tackle",
    "RT": "Offensive tackle", "G": "Guard", "OG": "Guard", "LG": "Guard", "RG": "Guard", "C": "Center",
    "OL": "Offensive lineman", "DE": "Defensive end", "DT": "Defensive tackle", "NT": "Nose tackle",
    "DL": "Defensive lineman", "LB": "Linebacker", "OLB": "Outside linebacker", "ILB": "Inside linebacker",
    "MLB": "Middle linebacker", "CB": "Cornerback", "S": "Safety", "FS": "Free safety", "SS": "Strong safety",
    "DB": "Defensive back", "K": "Kicker", "PK": "Kicker", "P": "Punter", "LS": "Long snapper",
}
POSITION_ORDER = ("QB", "RB", "FB", "WR", "TE", "OT", "G", "C", "DE", "DT", "LB", "CB", "DB", "S", "K", "P", "LS")
CLUB_CODES = {
    "ARI": "Arizona", "ATL": "Atlanta", "BAL": "Baltimore", "BUF": "Buffalo", "CAR": "Carolina", "CHI": "Chicago",
    "CIN": "Cincinnati", "CLE": "Cleveland", "DAL": "Dallas", "DEN": "Denver", "DET": "Detroit", "GNB": "Green Bay",
    "HOU": "Houston", "IND": "Indianapolis", "JAX": "Jacksonville", "KAN": "Kansas City", "MIA": "Miami",
    "MIN": "Minnesota", "NOR": "New Orleans", "NWE": "New England", "NYG": "the New York Giants",
    "NYJ": "the New York Jets", "OAK": "Oakland", "PHI": "Philadelphia", "PIT": "Pittsburgh", "SDG": "San Diego",
    "SEA": "Seattle", "SFO": "San Francisco", "STL": "St. Louis", "TAM": "Tampa Bay", "TEN": "Tennessee",
    "WAS": "Washington",
}
ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh"}
NUMBER_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven"}
ROUND_NAMES = {18: "the Wild Card round", 19: "the Divisional round", 20: "the Conference Championships",
               21: "the Super Bowl"}
STATUS_NAMES = {"Active 53": "Active roster", "Reserve/Injured": "Reserve/injured",
                "Reserve/Injured, designated for return": "Reserve/injured, designated for return",
                "Practice squad": "Practice squad"}
DEPARTURES = ("traded", "released", "waived", "tender_withdrawn", "not_tendered", "contract_expired", "retired")


# ------------------------------------------------------------------ small formats
def long_date(value):
    d = date.fromisoformat(value) if isinstance(value, str) else value
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def club_short(team):
    """The club as a season row names it: its city, or the New York club's nickname."""
    if team.startswith("New York "):
        return "N.Y. " + team.split()[-1]
    return team.rsplit(" ", 1)[0]


def money(v):
    return "${:,.0f}".format(v)


def fi(v):
    return N_A if v is None else "{:,}".format(int(v))


def f1(v):
    return N_A if v is None else "%.1f" % v


def ratio(a, b, scale=1.0):
    return None if not b else a / b * scale


def cell(v):
    return str(v).replace("|", "\\|")


def relink(text, source_dir, target):
    """Markdown links written relative to ``source_dir`` (repository-relative, '' for the root),
    made relative to the page at ``target``."""
    def link(m):
        dest = m.group(1)
        parts = urlsplit(dest)
        if parts.scheme or parts.netloc or dest.startswith("#"):
            return m.group(0)
        resolved = posixpath.normpath(posixpath.join(source_dir, unquote(parts.path)))
        rel = posixpath.relpath(resolved, posixpath.dirname(target))
        return "](" + rel + ("#" + parts.fragment if parts.fragment else "") + ")"
    return re.sub(r"\]\(([^\s)]+)\)", link, text)


def table(head, rows, numeric_from=4):
    lines = ["| " + " | ".join(head) + " |",
             "|" + "|".join("---" if i < numeric_from else "---:" for i in range(len(head))) + "|"]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


# ------------------------------------------------------------------ statistics columns
def _count(field):
    def fn(b):
        if field in b["available"] and not b["available"][field]:
            return N_A
        return fi(b["totals"].get(field, 0))
    return fn


def _sacks(b):
    v = b["totals"].get("sacks", 0)
    return f1(v) if v % 1 else fi(v)


def _rate(num, den, scale=1.0):
    return lambda b: f1(ratio(b["totals"].get(num, 0), b["totals"].get(den, 0), scale))


def _per_game(field):
    return lambda b: f1(ratio(b["totals"].get(field, 0), b["games"]))


def _long(field, base):
    def fn(b):
        if not b["available"].get(field, True):
            return N_A
        return fi(b["totals"].get(field, 0)) if b["totals"].get(base, 0) else N_A
    return fn


def _tile(label):
    return lambda b: dict(b["tiles"]).get(label, N_A)


def _games(b):
    return str(b["games"])


def _interceptions(b):
    return fi(player_cards.thrown(b["totals"]))


def _rating(b):
    return f1(player_cards.rating_value(b["totals"]))


QB_PASSING = (("G", _games), ("CMP", _count("completions")), ("ATT", _count("pass_attempts")),
              ("CMP%", _rate("completions", "pass_attempts", 100)), ("YDS", _count("passing_yards")),
              ("Y/A", _rate("passing_yards", "pass_attempts")), ("YDS/G", _per_game("passing_yards")),
              ("TD", _count("passing_touchdowns")), ("INT", _interceptions), ("Passer rating", _rating))
QB_OTHER = (("Sacked", _count("sacks_taken")), ("Sack yards", _count("sack_yards")),
            ("Rushes", _count("rushing_attempts")), ("Rush yards", _count("rushing_yards")),
            ("Rush TD", _count("rushing_touchdowns")), ("Fumbles", _count("fumbles")), ("Lost", _count("fumbles_lost")))
RUSHING = (("G", _games), ("Rushes", _count("rushing_attempts")), ("Rush yards", _count("rushing_yards")),
           ("Y/C", _rate("rushing_yards", "rushing_attempts")), ("Rush TD", _count("rushing_touchdowns")),
           ("Long", _long("long_rush", "rushing_attempts")), ("YDS/G", _per_game("rushing_yards")))
BACK_RECEIVING = (("Targets", _count("targets")), ("Rec", _count("receptions")),
                  ("Rec yards", _count("receiving_yards")), ("Y/R", _rate("receiving_yards", "receptions")),
                  ("Rec TD", _count("receiving_touchdowns")), ("Fumbles", _count("fumbles")),
                  ("Lost", _count("fumbles_lost")))
RECEIVING = (("G", _games), ("Targets", _count("targets")), ("Rec", _count("receptions")),
             ("Yards", _count("receiving_yards")), ("Y/R", _rate("receiving_yards", "receptions")),
             ("TD", _count("receiving_touchdowns")), ("Long", _long("long_reception", "receptions")),
             ("YDS/G", _per_game("receiving_yards")), ("Catch%", _rate("receptions", "targets", 100)))
RECEIVER_OTHER = (("Rushes", _count("rushing_attempts")), ("Rush yards", _count("rushing_yards")),
                  ("Rush TD", _count("rushing_touchdowns")), ("Fumbles", _count("fumbles")),
                  ("Lost", _count("fumbles_lost")))
DEFENSE = (("G", _games), ("Tackles", _count("tackles")), ("Solo", _count("solo_tackles")),
           ("Assisted", _count("assisted_tackles")), ("TFL", _count("tackles_for_loss")), ("Sacks", _sacks),
           ("Pressures", _count("pressures")))
DEFENSE_BALL = (("INT", _count("defensive_interceptions")), ("INT yards", _count("interception_return_yards")),
                ("PD", _count("passes_defended")), ("FF", _count("forced_fumbles")),
                ("FR", _count("fumble_recoveries")), ("ST tackles", _count("special_teams_tackles")))
KICKING = (("G", _games), ("FGM", _count("field_goals_made")), ("FGA", _count("field_goals_attempted")),
           ("FG%", _rate("field_goals_made", "field_goals_attempted", 100)), ("Long", _tile("LONG")),
           ("XPM", _count("extra_points_made")), ("XPA", _count("extra_points_attempted")),
           ("XP%", _rate("extra_points_made", "extra_points_attempted", 100)), ("Points", _tile("PTS")))
KICK_DISTANCE = (("FG 1-39", _tile("FG 1-39")), ("FG 40-49", _tile("FG 40-49")), ("FG 50+", _tile("FG 50+")))
PUNTING = (("G", _games), ("Punts", _count("punts")), ("Yards", _count("punt_yards")),
           ("Avg", _rate("punt_yards", "punts")), ("Net", _tile("NET")), ("Inside 20", _count("punts_inside_20")),
           ("Touchbacks", _count("punt_touchbacks")), ("Long", _long("long_punt", "punts")))
LINE = (("G", _games), ("Starts", _count("line_starts")), ("Offensive snaps", _count("offensive_snaps")),
        ("Sacks allowed", _count("sacks_allowed")), ("Special teams snaps", _count("special_teams_snaps")))
SNAPPING = (("G", _games), ("Long snaps", _count("long_snaps")), ("Special teams snaps", _count("special_teams_snaps")),
            ("ST tackles", _count("special_teams_tackles")), ("Tackles", _count("tackles")))
RETURNS = (("Kick returns", _count("kick_returns")), ("KR yards", _count("kick_return_yards")),
           ("KR avg", _rate("kick_return_yards", "kick_returns")), ("Punt returns", _count("punt_returns")),
           ("PR yards", _count("punt_return_yards")), ("PR avg", _rate("punt_return_yards", "punt_returns")))
# (columns, shown always) per position group; a later table appears only when the career has a
# value in it.
TABLES = {
    "QB": ((QB_PASSING, True), (QB_OTHER, True)),
    "RB": ((RUSHING, True), (BACK_RECEIVING, True), (RETURNS, False)),
    "WR": ((RECEIVING, True), (RECEIVER_OTHER, False), (RETURNS, False)),
    "TE": ((RECEIVING, True), (RECEIVER_OTHER, False), (RETURNS, False)),
    "DL": ((DEFENSE, True), (DEFENSE_BALL, True), (RETURNS, False)),
    "LB": ((DEFENSE, True), (DEFENSE_BALL, True), (RETURNS, False)),
    "DB": ((DEFENSE, True), (DEFENSE_BALL, True), (RETURNS, False)),
    "K": ((KICKING, True), (KICK_DISTANCE, True)),
    "P": ((PUNTING, True),),
    "OL": ((LINE, True), (RETURNS, False)),
    "LS": ((SNAPPING, True),),
}
FIELDS_OF = {
    id(RECEIVER_OTHER): ("rushing_attempts", "rushing_yards", "rushing_touchdowns", "fumbles", "fumbles_lost"),
    id(RETURNS): ("kick_returns", "punt_returns"),
}


# ------------------------------------------------------------------ inputs
class Context:
    """Everything the pages read, loaded once."""

    def __init__(self, root=ROOT):
        root = Path(root).resolve()
        self.root = root
        self.records = people.load_all(root)
        self.data = player_cards.card_data(root)
        player_cards.assign_slugs(self.data["players"])
        self.ident = player_cards.Identity(root)
        self.births = player_bios.load(root)
        self.active = active_season(root)
        self.paths = SeasonPaths(self.active, root)
        self.by_gsis = {p["gsis"]: p for p in self.data["players"] if p["gsis"]}
        self.by_key = {p["key"]: p for p in self.data["players"]}
        self.roster = roster_rows(self.paths.roster)
        from . import player_contracts
        self.finances = {p["name"]: p for p in player_contracts.rows(root)}
        self.league = {p["player_id"]: p for p in league_database(root, self.active) if p.get("player_id")}
        photos = json.loads((root / PHOTO_REGISTRY).read_text(encoding="utf-8"))
        self.photos = photos.get("players", {})
        from scripts.build_annual_player_sheets import season_is_complete
        self.complete = {y: season_is_complete(y, root) for y in self.data["years"]}
        # A closed season's player folder is history: built while the season is open, then kept.
        self.folder_open = not season_is_complete(self.active, root)
        self.weeks = {}
        self.latest_week = {}
        rec = player_cards.collect(root)
        for r in rec["games"]:
            self.weeks[(r["team"], r["date"])] = r["week"]
            key = (r["year"], r["type"])
            self.latest_week[key] = max(self.latest_week.get(key, 0), r["week"])
        self.jax_latest = max((d for (t, d) in self.weeks if t == JAX), default=None)
        # The current assignment's owners (people.READ_THROUGH "current_assignment").
        self.lists = ({row["name"]: row["list"] for row in roster_record.load(self.paths.roster)["players"]}
                      if roster_record.is_record(self.paths.roster) else {})
        self.chart = _json(self.paths.depth_chart)
        self.working = _json(self.paths.record("offseason/depth_chart_working.json"))
        week = self.latest_week.get((self.active, "regular"))
        self.library = {}
        self.week1, self.week1_added, self.rails_moved, self.branch_reserve = {}, set(), set(), set()
        if week and self.paths.background_depth.is_file():
            self.library = _json(self.paths.background_depth)
            for club, data in self.library.get("clubs", {}).items():
                for entry in data.get("players", ()):
                    if entry.get("gsis_id"):
                        self.week1[(club, entry["gsis_id"])] = entry
                for line in data.get("branch_changes", ()):
                    added = re.match(r"^Added (.+?) \(", line)
                    if added:
                        self.week1_added.add((club, added.group(1)))
            self.rails_moved, self.branch_reserve = moved_since_week1(root, self.active, week,
                                                                      rec["receipts"].get(self.active, {}))

    def league_player(self, record):
        if record["gsis_id"]:
            return self.by_gsis.get(record["gsis_id"])
        return self.by_key.get(record.get("game_key"))


def _json(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def moved_since_week1(root, season, week, receipts):
    """({gsis ids}, {(club, player)}): the players the in-season rails have moved by ``week`` (an
    applied move effective by then), and the branch reserve placements from the closed games
    (runtime/rails.c6_events on runtime/week_inputs.projected_returns). Their Week 1 slot no
    longer says where they play."""
    from . import rails, week_inputs
    data = rails.load(season, root)
    if data is None:
        return set(), set()
    moved = {row["uid"] for row in data.rows if row.get("outcome") == "APPLY" and row.get("uid")
             and int(row["effective_from_week"]) <= int(week)}
    regular = receipts.get("regular", [])
    events = rails.c6_events(week_inputs.projected_returns(regular, season), week_inputs.last_regular_date(season),
                             week_inputs.season_last_cutoffs(season), lambda r: r["week"],
                             data.effective_from_week) if regular else []
    return moved, {(e["team"], e["player_id"]) for e in events}


def league_database(root, season):
    """The league player database's rows: the season's own, else the latest earlier season's
    (a new season opens before its own is built); none before the first."""
    for year in range(season, 2013, -1):
        path = SeasonPaths(year, root).record("league/personnel/league_players.json")
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))["players"]
    return []


def roster_rows(path):
    """{name: (pos, status)} for every player Jacksonville controls: the current controlled
    players' tables and the practice squad's."""
    out, section, header = {}, None, None
    if not Path(path).is_file():
        return out
    if roster_record.is_record(path):
        return {row["name"]: (row["position"], STATUS_NAMES.get(roster_record.status_name(row["status"]),
                                                                  roster_record.status_name(row["status"])))
                for row in roster_record.load(path)["players"]}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            header = None
            continue
        if not (section == "Current controlled players" or (section or "").startswith("Practice squad")):
            continue
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Player" in cells:
            header = cells
            continue
        if header is None or set(cells[0]) <= {"-", ":"}:
            continue
        row = dict(zip(header, cells))
        status = re.sub(r"\s*\(.*\)$", "", row["Status"]).strip()
        out[row["Player"]] = (row["Pos"], STATUS_NAMES.get(status, status))
    return out


# ------------------------------------------------------------------ one player
def latest_assessment(record):
    if not record["assessments"]:
        return None
    return max(record["assessments"], key=lambda a: (a["season"], a["stage"] == "final"))


def sheet_read(root, pointer):
    """A frozen final player sheet's staff read (its "Player identity" line) and its date, read
    through its pointer; shown only while the assessment has no short summary."""
    text = (Path(root) / pointer["owner"]).read_text(encoding="utf-8")
    read = re.search(r"^\*\*Player identity:\*\*\s*(.*?)\s*$", text, re.M).group(1).rstrip("\\").rstrip()
    return read, long_date(people.assessment_date(pointer, root))


# ------------------------------------------------------------------ the staff assessment
def words(n, capital=False):
    """A count in the template's style: zero to nine spelled out, 10 and above in digits."""
    if n != int(n):
        raise ValueError("a count written in words must be whole: %s" % n)
    n = int(n)
    out = SPELLED[n] if 0 <= n < 10 else "{:,}".format(n)
    return out[0].upper() + out[1:] if capital else out


SPELLED = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
RATE_PARTS = {
    "passer_rating": None,
    "completion_percentage": ("completions", "pass_attempts", 100),
    "yards_per_attempt": ("passing_yards", "pass_attempts", 1),
    "yards_per_carry": ("rushing_yards", "rushing_attempts", 1),
    "yards_per_catch": ("receiving_yards", "receptions", 1),
    "yards_per_target": ("receiving_yards", "targets", 1),
    "catch_rate": ("receptions", "targets", 100),
    "field_goal_percentage": ("field_goals_made", "field_goals_attempted", 100),
    "extra_point_percentage": ("extra_points_made", "extra_points_attempted", 100),
    "punting_average": ("punt_yards", "punts", 1),
    "net_punting_average": None,
}


def jacksonville_block(p, year, kind):
    """His season block of Jacksonville games: the season's own when every game that season was
    with Jacksonville, else Jacksonville's part of it (runtime/player_cards.club_blocks), dated
    through his last Jacksonville game when he went on to another club; None when he has no such
    game."""
    season = p["seasons"].get(year) or {}
    if season.get("clubs") == [JAX]:
        return season.get(kind)
    return ((season.get("by_club") or {}).get(JAX) or {}).get(kind)


def token_value(p, year, kind, measure, fmt):
    """(text, block) for one season-figure token, from his closed Jacksonville games that season
    (the figures are his Jacksonville record: a season he also played for another club counts
    only its Jacksonville games). Refused (a ValueError) when he has no such game, a field is not
    in every game's record or a rate has no attempts."""
    if p is None:
        raise ValueError("no game records")
    block = jacksonville_block(p, year, kind)
    if not block:
        raise ValueError("no %d %s games with Jacksonville on record"
                         % (year, "regular-season" if kind == "regular" else "playoff"))
    totals, available = block["totals"], block["available"]
    if measure in people.RATES:
        if fmt:
            raise ValueError("a rate takes no format")
        if measure == "passer_rating":
            value = player_cards.rating_value(totals)
        elif measure == "net_punting_average":
            net = dict(block["tiles"]).get("NET") if p["group"] == "P" else None
            value = None if net in (None, N_A) else float(net)
        else:
            num, den, scale = RATE_PARTS[measure]
            value = ratio(totals.get(num, 0), totals.get(den, 0), scale)
        if value is None:
            raise ValueError("%s has no attempts" % measure)
        return "%.1f" % value, block
    if measure == "games":
        value = block["games"]
    else:
        if measure not in people.measures():
            raise ValueError("unknown measure %s" % measure)
        if available.get(measure, True) is False:
            raise ValueError("%s is not recorded in every game" % measure)
        value = player_cards.thrown(totals) if measure == "interceptions_thrown" else totals.get(measure, 0)
    if fmt:
        return words(value, fmt == "Words"), block
    return (player_cards.sack_text(value) if measure == "sacks" else "{:,}".format(int(value))), block


def resolve_tokens(ctx, p, text):
    """(text, [(season, kind, through)]) with every season-figure token replaced by its value
    from the closed games; a ValueError names the token that cannot resolve."""
    used = []

    def one(m):
        year, kind, measure, fmt = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        if year > ctx.active:
            raise ValueError("%s: season after the active season" % m.group(0))
        if measure in people.AMBIGUOUS:
            raise ValueError("%s: ambiguous; use %s" % (m.group(0), people.AMBIGUOUS[measure]))
        try:
            value, block = token_value(p, year, kind, measure, fmt)
        except ValueError as exc:
            raise ValueError("%s: %s" % (m.group(0), exc)) from None
        used.append((year, kind, block["through"]))
        return value
    out = people.TOKEN.sub(one, text)
    if "{{" in out or "}}" in out:
        raise ValueError("unresolved token in %r" % out)
    return out, used


def view_date(record, a, root=ROOT):
    """The date of the staff view a short summarizes: the latest of the dates of the assessments
    it summarizes and of their dated updates, no later than the short's own date (the day the
    summary was written, which is not itself an assessment)."""
    short = a["short"]
    wanted = {(i["season"], i["stage"]) for i in short["summarizes"]}
    dates = []
    for x in record["assessments"]:
        if (x["season"], x["stage"]) in wanted:
            dates.append(people.assessment_date(x, root))
            dates += [u["date"] for u in x.get("updates", ()) if u["date"] <= short["date"]]
    return max(dates)


def date_line(original, used, view=None):
    """The staff assessment's dated line. With no figure from games after the assessment's date:
    "Staff view," and the date of the view it summarizes (``view_date``; the assessment's own
    date when it has no dated update). With such figures: the assessment's original date, the
    season and the latest game day those figures cover, as the user's preview words it; should
    those figures end before the view's date (he left Jacksonville before it), the view's date
    leads instead, so the line is never dated before what the summary draws on."""
    view = view or original
    later = [(y, through) for y, _kind, through in used if through > original]
    if not later:
        return "Staff view, %s." % long_date(view)
    season = max(y for y, _ in later)
    last = max(t for y, t in later if y == season)
    cutoff = date.fromisoformat(last)
    when = ("%s %d" % (cutoff.strftime("%B"), cutoff.day) if cutoff.year == season else long_date(cutoff))
    if view > last:
        return "Staff view, %s; %d results current through %s." % (long_date(view), season, when)
    return "Staff assessment originally dated %s; %d results current through %s." % (long_date(original), season, when)


def staff_view(ctx, record, p, target):
    """(text, dated line) of the page's Staff assessment, or None when no Jacksonville staff
    assessed him. The latest assessment's short summary, its season figures resolved from the
    closed games (its words never change); until that assessment has a short, its staff read as
    written. No grade is shown."""
    a = latest_assessment(record)
    if a is None:
        return None
    short = a.get("short")
    if short is not None and not (isinstance(short, dict) and isinstance(short.get("text"), str)):
        raise ValueError("%s: a short staff assessment is an object with its text" % record["name"])
    if short is None:
        if "owner" in a:
            read, when = sheet_read(ctx.root, a)
            return (relink(read, posixpath.dirname(a["owner"]), target),
                    "Staff view at the %d season close, %s." % (a["season"], when))
        line = "Staff view, %s" % long_date(a["date"])
        if a.get("updates"):
            line += "; dated updates through %s" % long_date(max(u["date"] for u in a["updates"]))
        return relink(a["read"], "", target), line + "."
    try:
        text, used = resolve_tokens(ctx, p, short["text"])
    except ValueError as exc:
        raise ValueError("%s: staff assessment token %s" % (record["name"], exc)) from None
    return text, date_line(people.assessment_date(a, ctx.root), used, view_date(record, a, ctx.root))


def assessment_errors(ctx):
    """What would stop a page's Staff assessment or Current assignment from building: a short
    whose tokens do not resolve or whose words break the rules once resolved, a role label or a
    Week 1 slot code with no page words."""
    errors = []
    for rid, record in sorted(ctx.records.items()):
        a = latest_assessment(record)
        if a is None or "short" not in a:
            continue
        label = "%s/%s.json: %d %s staff assessment" % (PLAYER_RECORDS, rid, a["season"], a["stage"])
        if not isinstance(a["short"], dict) or not isinstance(a["short"].get("text"), str):
            errors.append("%s: a short staff assessment is an object with its text" % label)
            continue
        try:
            text, used = resolve_tokens(ctx, ctx.league_player(record), a["short"]["text"])
            date_line(people.assessment_date(a, ctx.root), used, view_date(record, a, ctx.root))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append("%s: %s" % (label, exc))
            continue
        errors += people.text_errors(label, text, ctx.root, resolved=True)
    errors += assignments.label_errors(ctx.working)
    errors += assignments.slot_errors(ctx.library)
    return errors


# ------------------------------------------------------------------ assignment and position statistic
def current_assignment(ctx, record, p, controlled):
    """One plain confirmed role, or None. A Jaguar on the active roster: his seat or role on the
    game depth chart (runtime/assignments.py, the depth chart page's own source); a Jaguar on a
    reserve list or the practice squad: none (the header names his list). Another club's player:
    his slot on the season's Week 1 depth chart with that club, unless the branch placed him
    there, an applied in-season move has moved him since, he was not available, or he is on his
    club's branch reserve list. Anyone else (a former Jaguar whose latest game was for
    Jacksonville, a player with no game this season): none."""
    if controlled:
        if ctx.lists.get(record["name"], "active") != "active":
            return None
        return assignments.jacksonville_assignment(record["name"], ctx.chart, ctx.working)
    if not p or p["team"] == JAX or not record["gsis_id"]:
        return None
    entry = ctx.week1.get((p["team"], record["gsis_id"]))
    if entry is None or (p["team"], entry.get("player_id")) in ctx.week1_added:
        return None
    if record["gsis_id"] in ctx.rails_moved:
        return None
    from .depth_library import available
    if not available(entry, ctx.latest_week.get((ctx.active, "regular"), 1)):
        return None
    if any((p["team"], n) in ctx.branch_reserve for n in p["record_names"]):
        return None
    return assignments.week1_assignment(entry)


# (label, value, opportunity) of each position group's statistic; the value reads one season's
# block, the opportunity is the field that must be nonzero (defenders: their snaps, else games).
def _metric_count(field):
    return lambda b: None if b["available"].get(field, True) is False else fi(b["totals"].get(field, 0))


def _metric_rate(num, den):
    return lambda b: f1(ratio(b["totals"].get(num, 0), b["totals"].get(den, 0)))


def _net(b):
    net = dict(b["tiles"]).get("NET")
    return None if net in (None, N_A) else net


METRICS = {
    "QB": ("Passer rating", lambda b: f1(player_cards.rating_value(b["totals"])), "pass_attempts"),
    "RB": ("Yards per carry", _metric_rate("rushing_yards", "rushing_attempts"), "rushing_attempts"),
    "WR": ("Yards per target", _metric_rate("receiving_yards", "targets"), "targets"),
    "TE": ("Yards per target", _metric_rate("receiving_yards", "targets"), "targets"),
    "DL": ("Sacks", lambda b: player_cards.sack_text(b["totals"].get("sacks", 0)), "defensive_snaps"),
    "LB": ("Tackles", _metric_count("tackles"), "defensive_snaps"),
    "DB": ("Passes defended", _metric_count("passes_defended"), "defensive_snaps"),
    "K": ("Field-goal percentage", lambda b: f1(ratio(b["totals"].get("field_goals_made", 0),
                                                       b["totals"].get("field_goals_attempted", 0), 100)),
          "field_goals_attempted"),
    "P": ("Net punting average", _net, "punts"),
    "LS": ("Long snaps", _metric_count("long_snaps"), "long_snaps"),
    "OL": ("Sacks allowed", _metric_count("sacks_allowed"), "offensive_snaps"),
}
DEFENSIVE = ("DL", "LB", "DB")


def period_week(ctx, year, gtype, week):
    """The week a partial season's figures are labelled through: the page's own cutoff (the week
    its As of line names, ``week``) when that is a week of this game type, else the latest such
    week in the game records (the regular season's last week once the playoffs have begun)."""
    if week is not None and (week in ROUND_NAMES) == (gtype == "playoffs"):
        return week
    return ctx.latest_week.get((year, gtype))


def position_metric(ctx, p, pos, week=None):
    """(label, value, period) of his position's statistic in the active season, from the closed
    games only (the template's list: QB passer rating, RB and FB yards per carry, WR and TE yards
    per target, a lineman's sacks, a linebacker's tackles, a defensive back's passes defended, the
    kicker's field-goal percentage, the punter's net average, the long snapper's long snaps, an
    offensive lineman's sacks allowed), or None: no game this season, no attempt, a field not in
    every game's record, or no value. A partial season reads through ``week``, the week the
    page's As of line names (``period_week``)."""
    group = player_cards.GROUP_OF.get(pos)
    if p is None or group not in METRICS:
        return None
    block = (p["seasons"].get(ctx.active) or {}).get("regular")
    if not block:
        return None
    label, value_of, opportunity = METRICS[group]
    if group == "P" and p["group"] != "P":
        return None  # the net average is a punter's tile
    if block["available"].get(opportunity, True) is False:
        if group not in DEFENSIVE:
            return None
        chances = block["games"]
    else:
        chances = block["totals"].get(opportunity, 0)
    if not chances:
        return None
    value = value_of(block)
    if value in (None, N_A):
        return None
    if ctx.complete.get(ctx.active, True):
        period = str(ctx.active)
    else:
        period = "%d, through Week %d" % (ctx.active, period_week(ctx, ctx.active, "regular", week))
    return label, value, period


def draft_view(ctx, record):
    """(year, round, pick, club text) of his draft: Jacksonville's own selection from his record,
    else the league database's for a draft before 2013 (later drafts are not read from it)."""
    for t in record["transactions"]:
        if t["kind"] == "drafted":
            pick = re.search(r"No\. (\d+)", t["text"])
            rnd = re.search(r"(\w+) round", t["text"])
            rnd = next((n for n, w in ORDINALS.items() if rnd and w == rnd.group(1)), None)
            return int(t["date"][:4]), rnd, int(pick.group(1)) if pick else None, "Jacksonville"
    row = ctx.league.get(record["gsis_id"]) if record["gsis_id"] else None
    d = (row or {}).get("draft")
    if d and str(d.get("season", "")).isdigit() and int(d["season"]) <= 2012 and d.get("team") in CLUB_CODES:
        return int(d["season"]), int(d["round"]), int(d["pick"]), CLUB_CODES[d["team"]]
    return None


def physical_line(ctx, record, p):
    gsis = record["gsis_id"]
    listed = ctx.ident.listed.get(gsis, {}) if gsis else {}
    parts = []
    height = (p or {}).get("height_in") or listed.get("height_in")
    weight = (p or {}).get("weight") or listed.get("weight")
    if height:
        parts.append("%d' %d\"" % (height // 12, height % 12) + (", %d lb" % weight if weight else ""))
    elif weight:
        parts.append("%d lb" % weight)
    born = birth_date(ctx, record, p)
    if born:
        parts.append("Born " + long_date(born))
    college = (p or {}).get("college") or (ctx.ident.college.get(gsis) if gsis else None) or listed.get("college")
    if college:
        parts.append(college)
    draft = draft_view(ctx, record)
    if draft:
        year, rnd, pick, club = draft
        if rnd:
            parts.append("Drafted in %d, %s round, by %s" % (year, ORDINALS[rnd], club))
        else:
            parts.append("Drafted in %d, No. %d overall, by %s" % (year, pick, club))
    elif any(t["kind"] == "signed" and "undrafted rookie" in t["text"] for t in record["transactions"]):
        parts.append("Undrafted")
    return " · ".join(parts)


def birth_date(ctx, record, p):
    """His birth date from the owners in people.READ_THROUGH, in their order: his league card's,
    worked out by Identity.birth_date, or for a player with no game on record the same owners
    read by his record's name and gsis id."""
    if p is not None:
        return p["birth_date"]
    gsis = record["gsis_id"]
    return ctx.ident.birth_date({record["name"]}, gsis, ctx.ident.week1_row(gsis, record["name"]))


def page_date(ctx, record, p, controlled):
    """The date the page covers: Jacksonville's latest game for a player it controls, else the
    latest game his record covers, else his latest dated transaction."""
    if controlled and ctx.jax_latest:
        return ctx.jax_latest, JAX
    if p:
        return p["through"], p["team"]
    dated = [t["date"] for t in record["transactions"] if len(t["date"]) == 10]
    return (max(dated), None) if dated else (None, None)


def page_week(ctx, team, when):
    """The week of the page's As of date for ``team``, or None."""
    return ctx.weeks.get((team, when)) if team else None


def week_text(ctx, team, when):
    week = page_week(ctx, team, when)
    if week is None:
        return ""
    return ", after %s" % (ROUND_NAMES[week] if week in ROUND_NAMES else "Week %d" % week)


NO_CONTRACT = "Contract not established."


def contract_view(ctx, record, controlled):
    """(line, rows) of the Contract section: the terms and salary by year of a contract
    Jacksonville holds, else the template's "not established" line and no rows (the records hold
    no other club's contract)."""
    f = ctx.finances.get(record["name"])
    if not controlled or not f or f.get("former_player") or f.get("control") not in ("signed",):
        return NO_CONTRACT, []
    term = f.get("term", "")
    m = re.match(r"^(\d+) / (\d{4})", term)
    if term.startswith("Weekly"):
        line = "Weekly practice-squad contract through the %d season." % f["contract_ends"]
    elif m and int(m.group(1)) in NUMBER_WORDS:
        line = "%s-year contract through %s." % (NUMBER_WORDS[int(m.group(1))], m.group(2))
    else:
        line = "Under contract through %d." % f["contract_ends"]
    rows = []
    for year, y in sorted(f["years"].items()):
        if y["status"] == "known":
            rows.append([year, money(y["base"]), money(y["cap"])])
        elif y["status"] == "approximate":
            rows.append([year, "about " + money(y["base"]) if y.get("base") is not None else "Not settled",
                         money(y["cap"]) if y.get("cap") is not None else "Not settled"])
        elif y["status"] == "option_unexercised":
            rows.append([year, "Club option", "Not exercised"])
    return line, rows


def stats_view(ctx, p, week=None):
    """The statistics section's tables for one league player; a partial season's row reads
    through ``week``, the week the page's As of line names (``period_week``)."""
    out = {}
    group = p["group"]
    for gtype in ("regular", "playoffs"):
        seasons = [(y, s) for y, s in sorted(p["seasons"].items(), reverse=True) if s[gtype]]
        if not seasons:
            out[gtype] = None
            continue
        clubs = {c for _, s in seasons for c in s["clubs"]}
        career_label = "With Jacksonville" if clubs == {JAX} else "Career"
        tables = []
        for columns, always in TABLES[group]:
            fields = FIELDS_OF.get(id(columns))
            career = p["career"][gtype]
            if not always and not any(career["totals"].get(f, 0) for f in fields):
                continue
            head = ["Season", "Team", "Age", "#"] + [c[0] for c in columns]
            rows = []
            for year, s in seasons:
                label = str(year)
                if year == ctx.active and not ctx.complete.get(year, True):
                    through = period_week(ctx, year, gtype, week)
                    if through:
                        label += " (through %s)" % (ROUND_NAMES[through] if through in ROUND_NAMES
                                                    else "Week %d" % through)
                rows.append([label, ", ".join(club_short(c) for c in s["clubs"]),
                             N_A if s.get("age") is None else s["age"],
                             N_A if s.get("number") is None else s["number"]]
                            + [fn(s[gtype]) for _, fn in columns])
            if len(seasons) > 1 and not tables:
                rows.append([career_label, "", "", ""] + [fn(career) for _, fn in columns])
            tables.append(table(head, rows, numeric_from=2))
        out[gtype] = tables
    return out


def departure(record):
    """His latest move away from Jacksonville, or None."""
    moves = [t for t in record["transactions"] if t["kind"] in DEPARTURES and "Jacksonville" in t["text"]]
    if not moves:
        moves = [t for t in record["transactions"] if t["kind"] in ("contract_expired", "retired")]
    return moves[-1] if moves else None


def status_text(ctx, record, p, controlled):
    if controlled:
        return ctx.roster[record["name"]][1]
    if any(t["kind"] == "retired" for t in record["transactions"]):
        return "Retired"
    if p and p["team"] != JAX:
        return "Last game %s" % long_date(p["through"])
    if departure(record) or p is None:
        return "Former player"
    return "Last game %s" % long_date(p["through"])


def controlled_name(ctx, record):
    row = ctx.births.get(record["name"])
    if record["name"] not in ctx.roster:
        return False
    return not record["gsis_id"] or not row or row.get("gsis_id") == record["gsis_id"]


def render(ctx, record, target):
    p = ctx.league_player(record)
    controlled = controlled_name(ctx, record)
    a = latest_assessment(record)
    if controlled:
        team, pos = JAX, ctx.roster[record["name"]][0]
    elif p:
        team, pos = p["team"], p["pos"]
    else:
        team, pos = JAX, (a or {}).get("position", "")
    when, when_team = page_date(ctx, record, p, controlled)
    cutoff = page_week(ctx, when_team, when)
    born = birth_date(ctx, record, p)
    head = [team, POSITION_NAMES.get(pos, pos)]
    if p and p["number"] is not None:
        head.append("No. %d" % p["number"])
    if born and when:
        head.append("Age %d" % player_bios.age_on(born, when))
    head.append(status_text(ctx, record, p, controlled))
    lines = ["# %s" % record["name"], "", "**%s**" % " · ".join(h for h in head if h), ""]
    physical = physical_line(ctx, record, p)
    if physical:
        lines += [physical, ""]
    if when:
        lines += ["As of %s%s." % (long_date(when), week_text(ctx, when_team, when)), ""]
    photo = ctx.photos.get(record["gsis_id"]) if record["gsis_id"] else None
    if photo and photo.get("name") == record["name"]:
        lines += ["![%s](%s)" % (record["name"], photo["url"]), "",
                  player_photo_credit(photo), ""]
    assignment = current_assignment(ctx, record, p, controlled)
    if assignment:
        lines += ["**Current assignment:** %s." % assignment, ""]
    metric = position_metric(ctx, p, pos, cutoff)
    if metric:
        lines += ["**%s:** %s (%s)." % metric, ""]
    view = staff_view(ctx, record, p, target)
    if view:
        lines += ["## Staff assessment", "", view[0], "", "*%s*" % view[1], ""]
    line, rows = contract_view(ctx, record, controlled)
    lines += ["## Contract", "", line, ""]
    if rows:
        lines += [table(["Year", "Base salary", "Cap charge"], rows, numeric_from=1), ""]
    lines += ["## Statistics", ""]
    stats = stats_view(ctx, p, cutoff) if p else {"regular": None, "playoffs": None}
    for gtype, heading, empty in (("regular", "Regular season", "No regular-season games on record."),
                                  ("playoffs", "Playoffs", "No playoff games on record.")):
        lines += ["### " + heading, ""]
        lines += (sum(([t, ""] for t in stats[gtype]), []) if stats[gtype] else [empty, ""])
    lines += ["## Awards", ""]
    awards = p["awards"] if p else []  # the award results' own, matched to him in card_data
    lines += ["- %s" % w for w in awards] if awards else ["None."]
    lines += ["", "## Transactions", ""]
    rows = transaction_rows(ctx, record)
    lines += [table(["Date", "Transaction"], rows, numeric_from=2)] if rows else ["None on record."]
    lines += ["", PAGE_MARK, ""]
    return "\n".join(lines)


def player_photo_credit(row):
    credit = "Photo: %s, " % row["credit"] if row.get("credit") else "Photo: "
    license_ = row.get("license") or "license unrecorded"
    if row.get("license_url"):
        license_ = "[%s](%s)" % (license_, row["license_url"])
    source = " ([source](%s))" % row["source_page"] if row.get("source_page") else ""
    return "*%s%s%s.*" % (credit, license_, source)


def transaction_rows(ctx, record):
    entries = list(record["transactions"])
    draft = draft_view(ctx, record)
    if draft and not any(t["kind"] == "drafted" for t in entries):
        year, rnd, pick, club = draft
        entries.append({"date": str(year), "kind": "drafted",
                        "text": "Drafted by %s in the %s round" % (club, ORDINALS[rnd])})
    entries.sort(key=people.sort_key)
    return [[people.transaction_date_text(t), t["text"]] for t in entries]


# ------------------------------------------------------------------ the page set
def jaguars_folder(ctx):
    return ctx.paths.record("player_profiles")


def jaguars_players(ctx):
    """Record ids with a page in the season's player folder: every player Jacksonville controls
    and every player its staff assessed in the season."""
    out = []
    for rid, record in ctx.records.items():
        if controlled_name(ctx, record) or any(a["season"] == ctx.active and "owner" not in a
                                               for a in record["assessments"]):
            out.append(rid)
    return sorted(out)


def build(root=ROOT, ctx=None):
    """({relative path: text} for every player page and index, [players in the game records with
    no record])."""
    ctx = ctx or Context(root)
    root = ctx.root
    files, missing = {}, []
    matched = set()
    for rid, record in sorted(ctx.records.items()):
        p = ctx.league_player(record)
        if p is not None:
            matched.add(p["key"])
            target = "%s/%s/%s.md" % (LEAGUE_PLAYER_PAGES, player_cards.club_slug(p["team"]), p["slug"])
            files[target] = render(ctx, record, target)
    missing = [p for p in ctx.data["players"] if p["key"] not in matched]
    if ctx.folder_open:
        folder = jaguars_folder(ctx).relative_to(root).as_posix()
        jags = jaguars_players(ctx)
        for rid in jags:
            target = "%s/%s.md" % (folder, people.slugify(ctx.records[rid]["name"]))
            files[target] = render(ctx, ctx.records[rid], target)
        files["%s/README.md" % folder] = jaguars_index(ctx, jags)
    by_club = {}
    for p in ctx.data["players"]:
        by_club.setdefault(p["team"], []).append(p)
    for team, ps in by_club.items():
        files["%s/%s/README.md" % (LEAGUE_PLAYER_PAGES, player_cards.club_slug(team))] = club_index(ctx, team, ps)
    files["%s/README.md" % LEAGUE_PLAYER_PAGES] = league_index(ctx, {t: len(ps) for t, ps in by_club.items()})
    return dict(sorted(files.items())), missing


def jaguars_index(ctx, rids):
    records = [ctx.records[r] for r in rids]
    current = [r for r in records if controlled_name(ctx, r)]
    former = [r for r in records if not controlled_name(ctx, r)]
    order = {pos: i for i, pos in enumerate(POSITION_ORDER)}
    names = list(ctx.roster)
    current.sort(key=lambda r: (order.get(ctx.roster[r["name"]][0], 99), names.index(r["name"])))
    lines = ["# Jacksonville Jaguars players, %d" % ctx.active, "",
             "Every player Jacksonville controls, by position, and the players who left after their %d staff "
             "assessment. Each page has the staff assessment, the contract where one is established, the "
             "statistics, the awards and the transactions." % ctx.active, ""]
    if ctx.jax_latest:
        lines += ["As of %s%s." % (long_date(ctx.jax_latest), week_text(ctx, JAX, ctx.jax_latest)), ""]
    lines += ["## Current players", "",
              table(["Player", "Position", "Status"],
                    [["[%s](%s.md)" % (r["name"], people.slugify(r["name"])),
                      POSITION_NAMES.get(ctx.roster[r["name"]][0], ctx.roster[r["name"]][0]),
                      ctx.roster[r["name"]][1]] for r in current], numeric_from=3), ""]
    if former:
        rows = []
        for r in sorted(former, key=lambda r: ((departure(r) or {}).get("date", ""), r["name"])):
            d = departure(r)
            pos = (latest_assessment(r) or {}).get("position", "")
            rows.append(["[%s](%s.md)" % (r["name"], people.slugify(r["name"])), POSITION_NAMES.get(pos, pos),
                         "%s, %s" % (d["text"], people.transaction_date_text(d)) if d else ""])
        lines += ["## Former players", "", table(["Player", "Position", "Left"], rows, numeric_from=3), ""]
    lines += ["[League players](%s)" % os.path.relpath(ctx.root / LEAGUE_PLAYER_PAGES / "README.md",
                                                       jaguars_folder(ctx)).replace(os.sep, "/"), "",
              INDEX_MARK, ""]
    return "\n".join(lines)


def club_index(ctx, team, players):
    years = sorted(ctx.data["years"], reverse=True)
    cols = ["%d G" % y for y in years]
    lines = ["# %s players" % team, "",
             "%s. The players whose latest game on record was with the %s. G counts regular-season games "
             "with any club. Records through %s." % (DIVISION_OF[team], team, long_date(ctx.data["as_of"])), "",
             "[All clubs](../README.md)", ""]
    for group, heading in player_cards.GROUPS:
        ps = sorted((p for p in players if p["group"] == group), key=lambda p: (p["name"], p["slug"]))
        if not ps:
            continue
        rows = []
        for p in ps:
            games = [((p["seasons"].get(y) or {}).get("regular") or {}).get("games", 0) for y in years]
            rows.append([N_A if p["number"] is None else p["number"], "[%s](%s.md)" % (p["name"], p["slug"]),
                         p["pos"] or N_A] + games)
        lines += ["## " + heading, "", table(["#", "Player", "Pos"] + cols, rows, numeric_from=3), ""]
    lines += [INDEX_MARK, ""]
    return "\n".join(lines)


def league_index(ctx, counts):
    years = ctx.data["years"]
    lines = ["# League players", "",
             "Every player in the %s game records, under the club of his latest game. Each page has his staff "
             "assessment where Jacksonville made one, his contract where Jacksonville holds it, his "
             "regular-season and playoff statistics by season, his awards and his transactions. Records "
             "through %s." % (" and ".join(str(y) for y in years), long_date(ctx.data["as_of"])), ""]
    for conf in ("AFC", "NFC"):
        lines += ["## " + conf, ""]
        for division, teams in DIVISIONS.items():
            if not division.startswith(conf):
                continue
            lines += ["### " + division, ""]
            lines += ["- [%s](%s/README.md) (%d players)" % (t, player_cards.club_slug(t), counts.get(t, 0))
                      for t in teams]
            lines.append("")
    lines += [INDEX_MARK, ""]
    return "\n".join(lines)


# ------------------------------------------------------------------ check and write
def owned_paths(ctx):
    """Every file under the folders the builder owns."""
    root = ctx.root
    out = set()
    for folder in owned_folders(ctx):
        if folder.is_dir():
            out.update(p.relative_to(root).as_posix() for p in folder.rglob("*") if p.is_file())
    return out


def owned_folders(ctx):
    """The league pages, and the active season's player folder while that season is open."""
    return (ctx.root / LEAGUE_PLAYER_PAGES,) + ((jaguars_folder(ctx),) if ctx.folder_open else ())


def check(root=ROOT):
    """Errors: a record that breaks the schema, an award decided on record whose winner is not in
    the game records, a player in the game records with no record, and every page that differs
    from its rebuild."""
    ctx = Context(root)
    errors = []
    for rid, record in sorted(ctx.records.items()):
        errors += people.record_errors(rid, record, ctx.root)
    refused = assessment_errors(ctx)
    if refused:
        return errors + refused  # no page can be built while a staff assessment or assignment cannot
    errors += ["Award with no winner in the game records: %s" % a for a in ctx.data["unmatched_awards"]]
    expected, missing = build(ctx=ctx)
    errors += ["Player record missing for %s (%s); run the player page builder" % (p["name"], p["team"])
               for p in missing]
    for rel, text in expected.items():
        path = ctx.root / rel
        if not path.is_file():
            errors.append("Player page missing: %s" % rel)
        elif path.read_bytes() != text.encode("utf-8"):
            errors.append("Player page stale or hand-edited: %s" % rel)
    for rel in sorted(owned_paths(ctx) - set(expected)):
        errors.append("Unexpected file among the player pages: %s" % rel)
    return errors


def write(root=ROOT):
    """Create the records of players new to the game records (identity only), then write every
    page and remove the folders' other files. Returns (records created, pages written, files
    removed). Refused before anything is written (a ValueError naming each cause) while a staff
    assessment, a role label or a Week 1 slot cannot be built (``assessment_errors``)."""
    root = Path(root).resolve()
    ctx = Context(root)
    refused = assessment_errors(ctx)
    if refused:  # nothing is written while a staff assessment or an assignment cannot be built
        raise ValueError("player pages not written:\n" + "\n".join(refused))
    _, missing = build(ctx=ctx)
    taken = set(ctx.records)
    created = 0
    for p in missing:
        record = people.new_record(p["name"], p["gsis"], None if p["gsis"] else p["key"])
        rid = people.record_id(record, taken, p["group"])
        taken.add(rid)
        ctx.records[rid] = record
        created += 1
    for rid, record in ctx.records.items():
        path = people.folder(root) / ("%s.json" % rid)
        text = people.dump(record)
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if created:
        ctx = Context(root)
    expected, _ = build(ctx=ctx)
    written = removed = 0
    for rel, text in expected.items():
        path = root / rel
        data = text.encode("utf-8")
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written += 1
    for rel in sorted(owned_paths(ctx) - set(expected), reverse=True):
        (root / rel).unlink()
        removed += 1
    for folder in owned_folders(ctx):
        for path in sorted(folder.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
    return created, written, removed


def built_page(text):
    """Whether a page is one this builder writes."""
    return text.rstrip().endswith(MARKERS)


def season_assessment_errors(year, root=ROOT):
    """The annual-assessment rule on the records: every player Jacksonville controls in the
    active season has a page in the season's player folder and, on his record, that season's
    opening or entry assessment (the one full assessment that accompanies him into the year)."""
    ctx = Context(root)
    if year != ctx.active:
        return []
    folder = jaguars_folder(ctx)
    by_name = {}
    for rid, record in ctx.records.items():
        by_name.setdefault(record["name"], []).append(rid)
    errors = []
    for name in ctx.roster:
        rids = [r for r in by_name.get(name, ()) if r in set(jaguars_players(ctx))]
        if not (folder / ("%s.md" % people.slugify(name))).is_file():
            errors.append("%d: missing player page for %s" % (year, name))
        if not any(a["season"] == year and a["stage"] in ("opening", "entry") and "owner" not in a
                   for r in rids for a in ctx.records[r]["assessments"]):
            errors.append("%d: no opening or entry assessment on the player record of %s" % (year, name))
    return errors
