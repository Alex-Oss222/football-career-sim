#!/usr/bin/env python3
"""Build a game week's pages (game week version 2, docs/game_week_v2.md): the
Game Week Briefing, the blank Game Plan and the week folder's index.

  python scripts/render_game_week.py [--week N] [--check] [--root PATH]

The week is the next Jacksonville game that has not closed, unless --week
names another. After the regular season it is Jacksonville's next playoff game
(runtime/game_weeks.py): the bracket set from the closed games only, its pages
in the round's folder under the postseason folder; a first-round bye, a round
still awaiting results and a season ended by a loss issue nothing, and the
briefing's section 1 gives the playoff game's own facts (``playoff_rows``: the
round and seeds, the site, the rest, what a win and a loss mean, any earlier
meeting, the 2014-era overtime rule and the game-day limit) in place of the
regular season's standings. Every page is built from its stored owners only:

- the Game Week Briefing, on the layout of foundation/templates/game_week/
  game_week_briefing_template.md, sections 1 to 8: the game and what is at
  stake (both records, the venue, the rest each club has had and the
  standings owner's division order and conference places); our last game and
  the self-scout (the statistics owner's figures for the last game); medical
  and game-day availability (only active-roster players under a restriction
  or with an exam still to come, and a reserve-list player only when he may
  return or practise before the game; the game-day numbers his standing
  inactive rule leaves to him; who decides medical status); the opponent
  with the ball and without it (its game records, leaders and the roster as
  the league's transactions have made it public by the issue date, never a
  move after it); special teams and game operations; the staff proposals;
  what is owed by the head coach (the decision queue), his standing
  directions and what the club decides. Every authored part, the staff's
  central question, the two things to carry forward, each coordinator's
  recommendation and questions, the special-teams report, the contingencies
  and the staff proposals, is stored text in the week's data folder
  (``staff_briefing.json``: each entry with its author and date), written by
  whoever prepares the week; code never writes it. A missing required part
  renders "To come"; an optional one (what the game book does not settle, what
  is not established, an operational question) is left out until it is
  stored. The builder checks each entry's author, date and form, that it is a
  clean page and that it cites only figures the page shows.
- the Game Plan, Stone's page (runtime/game_plan.py, the layout of
  foundation/templates/game_week/game_plan_template.md): written blank once,
  when the week opens, and never rewritten by this builder; he fills it in
  place or uploads a file with the same headings.
- the week index (the folder's README): the three pages, the date and the
  opponent.

A briefing is dated the day it is issued. Every issue is entered in the
week's issue record (``briefings.json`` in the week's data folder: the date,
the revision, that is the n-th issue of its day, the file and the sha256 of
the page as it went out), which owns the issue dates and revisions; nothing
reads a date back from a page. From the second issue of a day the pages name
an issue with its revision ("October 5, 2014, revision 2"), and Stone's
"Briefing used" must name the current one so. If the situation changes after
a briefing goes out (anything the page shows other than its date), writing
issues a new one and keeps the old one beside it, as what he saw, named for
its issue (Game_Week_Briefing_October_5.md, Game_Week_Briefing_October_5_2.md). A briefing that no longer matches
its recorded issue was edited by hand: writing refuses until it is restored,
so a hand edit is never kept as what he saw. Stone settling the week's own
items on his Game Plan is not such a change (``overtaken``); a briefing
issued later shows them "Set on your Game Plan". Writing opens the week's two
decision items first (scripts/open_game_week.py), so the briefing lists them.
Opening or building a page never moves time or creates an event; the week
index carries the event line of the applied Game Plan from its record.

The season statistics, leaders and penalties are the statistics owner's
(runtime/statbook.aggregate_receipts and the penalty split of
scripts/render_season_stats.py: where a season's games were counted under two
penalty methods, only the comparable count, the way every game is counted
now, is shown, labelled with its weeks, and never added to the other), an
opponent's player who leads more than one category has one row naming each
lead, players tied for a lead each have a row, an ask tied to a date already
past is left out of section 8, the standings are the
standings owner's (runtime/standings.compute, with the tiebreakers), and the
medical table reads the roster record in its one medical format
(runtime/season_summary.py).

``--check`` writes nothing. It reports, for every week whose folder holds a
game week page (played weeks included; with ``--week N`` that week alone), a
missing or out-of-date index, briefings that differ from their issue record
or that no issue produced, malformed staff texts and, while the week is open,
a missing Game Plan beside a briefing, a briefing not yet issued or one the
situation has overtaken (a new one is due). Repository validation runs
``validation_errors``: the same checks without the overtaken briefing, which
is the weekly workflow's to re-issue, not a defect.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import current_job, decisions, game_plan, roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.player_pages import club_short  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
# The authority domains a game week touches, shown under "Who else decides" when the final word
# is someone else's (the club's wording is the team page's: render_club_pages.DECISIONS).
GAME_WEEK_DOMAINS = ("Medical diagnosis", "Medical clearance and return-to-participation status",
                     "Injury reporting and official availability designation",
                     "Professional trades, waivers, claims, releases, reserve mechanisms, and practice-squad "
                     "transactions", "Special-teams decisions and calls",
                     "Media policy, access, and official communications")
# What an open item asks, when its question names no clauses to settle.
SETTLE = {"weekly_game_plan": "the plan for the game", "game_day_inactives": "who does not dress"}
# Stone's part in a decision someone else makes, in plain words.
YOUR_PART = {"recommends": "you recommend", "consulted": "you are consulted", "responds": "you respond",
             "informs": "you supply information", "none": "you have no part", "decides_part": "you decide a part",
             "unset": "your part is not recorded"}
LEADERS = (("Passing", "passing_yards", lambda l: "%d of %d, %s yards, %d TD, %d INT" % (
                l.get("completions", 0), l.get("pass_attempts", 0), yards(l.get("passing_yards", 0)),
                l.get("passing_touchdowns", 0), l.get("interceptions_thrown", 0))),
           ("Rushing", "rushing_yards", lambda l: "%d carries, %s yards, %d TD" % (
                l.get("rushing_attempts", 0), yards(l.get("rushing_yards", 0)), l.get("rushing_touchdowns", 0))),
           ("Receiving", "receiving_yards", lambda l: "%d catches, %s yards, %d TD" % (
                l.get("receptions", 0), yards(l.get("receiving_yards", 0)), l.get("receiving_touchdowns", 0))),
           ("Tackles", "tackles", lambda l: "%d" % l.get("tackles", 0)),
           ("Sacks", "sacks", lambda l: "%s" % number(l.get("sacks", 0))),
           ("Interceptions", "defensive_interceptions", lambda l: "%d" % l.get("defensive_interceptions", 0)))
# The team figures the briefing shows, each a field of the statistics owner's season totals
# (runtime/statbook.aggregate_receipts); third downs and penalties have rows of their own.
TEAM_ROWS = (("Points", "points"), ("First downs", "first_downs"), ("Passing yards", "passing_yards"),
             ("Rushing yards", "rushing_yards"), ("Turnovers", "turnovers"), ("Sacks allowed", "sacks_allowed"))


def yards(value):
    return "{:,}".format(int(value))


def number(value):
    return ("%.1f" % value).rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def day(value, year=True):
    d = date.fromisoformat(value) if isinstance(value, str) else value
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year) if year else "%s %d" % (d.strftime("%B"), d.day)


def link(page_rel, target_rel, label, anchor=""):
    path = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, path.replace(" ", "%20"), "#" + anchor if anchor else "")


def table(head, rows):
    return game_plan.table(head, rows)


# ---------------------------------------------------------------- the week
class Week:
    """Everything a game week's pages read, loaded once."""

    def __init__(self, root=ROOT, week=None):
        from runtime import game_weeks
        from scripts import render_career_views as views
        self.root = Path(root).resolve()
        self.views = views
        self.cv = views.context(self.root)
        self.season, self.paths, self.master = self.cv.season, self.cv.paths, self.cv.master
        self.job = self.cv.job
        self.receipts = self._receipts()
        # Postseason games (runtime/game_weeks.py): the bracket set from the closed games only.
        self.post_receipts = [r for r in game_weeks.postseason_receipts(self.paths) if JAX in (r["home"], r["away"])]
        closed = {int(r["week"]) for r in self.receipts + self.post_receipts if JAX in (r["home"], r["away"])}
        games = self.cv.games
        self.waiting = None     # why no game is open (a playoff round awaiting results, the season over)
        if week is None:
            open_games = [g for g in games if g["week"] not in closed]
            self.game = open_games[0] if open_games else None
            if self.game is None and games:
                self.game, self.waiting = game_weeks.next_postseason_game(self.paths, JAX)
        elif game_weeks.is_postseason(self.paths, week):
            try:
                self.game = game_weeks.club_game(self.paths, week, JAX)
            except game_weeks.NotSet as exc:
                raise ValueError("Jacksonville's %s game is not set: %s" % (game_weeks.round_name(week), exc))
            if self.game is None:
                raise ValueError("Jacksonville has no %s game in %d" % (game_weeks.round_name(week), self.season))
        else:
            self.game = next((g for g in games if g["week"] == week), None)
            if self.game is None:
                raise ValueError("Jacksonville has no game in Week %d of %d" % (week, self.season))
        self.postseason = self.game is not None and self.game.get("game_type") == "postseason"
        self.closed = self.game is not None and self.game["week"] in closed
        if self.game is not None:
            self.pages = decisions.week_pages(self.season, self.game["week"], self.root, postseason=self.postseason)
            self.opponent = self.game["home"] if self.game["away"] == JAX else self.game["away"]

    def label(self):
        """The game's name: "Week 6", or its playoff round ("Wild Card")."""
        from runtime import game_weeks
        return game_weeks.label(self.game)

    def _receipts(self):
        folder = self.paths.receipts
        fixtures = {(g["week"], g["away"], g["home"]): g for g in self.paths.regular_games()}
        out = []
        for path in sorted(folder.glob("week_*.json")) if folder.is_dir() else ():
            r = json.loads(path.read_text(encoding="utf-8"))
            game = fixtures.get((int(r["week"]), r["away"], r["home"]))
            if game is not None and date.fromisoformat(game["date"]) <= self.master:
                out.append(r)
        return out

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def place(self, club):
        return self.cv.places.get(club, club_short(club))

    def where(self):
        return ("at %s" if self.game["away"] == JAX else "against %s") % self.place(self.opponent)

    def title_where(self):
        return ("at %s" if self.game["away"] == JAX else "%s") % self.place(self.opponent)

    def when(self):
        g = self.game
        return "%s, %s, %s, %s" % (g.get("weekday"), day(g["date"]), self.views.kickoff(g["kickoff_et"]),
                                   g.get("stadium"))

    def club_games(self, club):
        return sorted((r for r in self.receipts if club in (r["home"], r["away"])), key=lambda r: int(r["week"]))

    def record(self, club):
        w = l = t = 0
        for r in self.club_games(club):
            other = r["away"] if r["home"] == club else r["home"]
            mine, theirs = r["final_score"][club], r["final_score"][other]
            w, l, t = w + (mine > theirs), l + (mine < theirs), t + (mine == theirs)
        return "%d-%d" % (w, l) + ("-%d" % t if t else "")


# ---------------------------------------------------------------- the briefing's facts
# A reserve status from which no return this season is possible (runtime/roster.status_name).
SEASON_ENDING = frozenset({"Reserve/Injured"})


def coordinators(wk):
    """(name, phase) of each coach who prepares a phase, from the current-job record."""
    holder = wk.job.get("holder")
    out = []
    for phase, label in (("offense", "offense"), ("defense", "defense"), ("special_teams", "special teams")):
        interval = current_job.interval_on(wk.job, phase, wk.master)
        if not interval:
            continue
        who = interval.get("prepares") if interval.get("caller") == holder else interval["caller"]
        if who and who != holder:
            out.append((current_job.party_name(wk.job, who), label))
    return out


# A playoff game in 2014-era rules (library/2013_nfl_playing_rules_for_simulation.md R2 and R5,
# library/2013_postseason_format_and_schedule.md R-P1 and R-P3; unchanged in 2014, the postseason
# possession rule changing only in 2022): no tie, modified sudden death, and the season's game-day limit.
PLAYOFF_OVERTIME = ("A playoff game cannot end tied: overtime is played in 15-minute periods until there is a "
                    "winner. A touchdown on the first possession wins, as does a safety or a touchdown by the "
                    "defense; if the first possession ends in a field goal, the other club gets the ball, its "
                    "touchdown wins and its field goal leads to sudden death; after a first possession without a "
                    "score, the next score wins.")
AFTER_A_WIN = {"wild_card": "We play in the Divisional round; the opponent and the site are set by the other "
                            "Wild Card games.",
               "divisional": "We play in the Conference Championship; the opponent and the site are set by the "
                             "other Divisional game.",
               "conference": "We play in the Super Bowl; the opponent is set by the other conference's "
                             "championship game.",
               "super_bowl": "We are the league champions."}


def playoff_rows(wk):
    """A playoff game's own rows of section 1, from the bracket and the closed games (docs/game_week_v2.md,
    section 7): the round and both seeds, what a loss and a win mean, any earlier meeting this season,
    the overtime rule and the game-day limit (the site, the kickoff and the rest are the section's own
    rows). Empty for a season game."""
    if not wk.postseason:
        return []
    from runtime.rules import RULES
    g = wk.game
    ours, theirs = ("away", "home") if g["away"] == JAX else ("home", "away")
    seeds = "%s No. %s, %s No. %s" % (club_short(JAX), g.get(ours + "_seed"), club_short(wk.opponent),
                                      g.get(theirs + "_seed"))
    rows = [["Seeds", seeds], ["If we lose", "The season is over."], ["If we win", AFTER_A_WIN[g["round"]]]]
    met = []
    for r in wk.receipts:
        if wk.opponent in (r["home"], r["away"]) and JAX in (r["home"], r["away"]):
            mine, other = r["final_score"][JAX], r["final_score"][wk.opponent]
            verb = "beat" if mine > other else "lost to" if mine < other else "tied"
            met.append("Week %d, %s %s %d-%d %s" % (int(r["week"]), verb, wk.place(wk.opponent), max(mine, other),
                                                    min(mine, other), "at home" if r["home"] == JAX else "away"))
    rows.append(["Earlier meeting", "; ".join(met) + "." if met else "None this season."])
    rows.append(["Overtime", PLAYOFF_OVERTIME])
    rows.append(["Game-day roster", "%d dress, as in the regular season; every other player on the active roster "
                                    "is inactive." % RULES.active_limit])
    return rows


def game_type(wk):
    """Section 1's game type: the regular season, or the playoff round and its conference."""
    if not wk.postseason:
        return "Regular season"
    g = wk.game
    return g["round_name"] if g.get("conference") in (None, "NFL") else "%s, %s" % (g["round_name"], g["conference"])



def availability_rows(wk, page_rel):
    """One row per player under a medical instruction, read from the roster record in its one
    medical format (runtime/season_summary.medical_entry): his list as the roster names it, the
    instruction, the injury and its severity, the projected return ("Out for the season" on a
    reserve list he cannot come back from), the exams still to come and the limits."""
    from runtime import season_summary as summary
    from runtime.week_pages import status_text
    data = roster_record.load(wk.paths.roster)
    roster_page = wk.rel(wk.paths.roster_page)
    rows = []
    for p in roster_record.players(data):
        entry = summary.medical_entry(p, wk.master)
        if entry is None:
            continue
        target = ""
        if entry["record"]:
            label, dest = entry["record"]
            dest, _, anchor = dest.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(roster_page), dest)).replace(os.sep, "/")
            target = link(page_rel, resolved, label[:1].upper() + label[1:], anchor)
        if roster_record.status_name(p["status"]) in SEASON_ENDING:
            back = "Out for the season"
        else:
            back = day(entry["projected"]) if entry["projected"] else "Not set"
        exams = "; ".join(day(d, d.year != wk.master.year) for d in entry["reviews"]) or "None communicated"
        rows.append([p["name"], p["position"], status_text(p["status"]), entry["instruction"],
                     "%s (%s)" % (entry["injury"], entry["severity"]), back, exams,
                     "; ".join(l[:1].upper() + l[1:] for l in entry["limits"]), target])
    return rows



def season_book(games):
    """The statistics owner's totals over ``games`` (runtime/statbook.aggregate_receipts), the
    same aggregation every statistics page reads."""
    from runtime.statbook import aggregate_receipts
    return aggregate_receipts(games)



def penalty_rows(games, club):
    """([label, club, its opponents] rows, None) for the penalties over ``games``. A season whose games
    were counted under two penalty methods shows only the games counted the way every game is now
    (each accepted foul charged to the club that committed it), labelled with the weeks they cover:
    the earlier count is not comparable, so it is neither shown beside it nor added to it
    (scripts/render_season_stats.penalty_split). The page carries no accounting note."""
    from scripts.render_season_stats import penalty_split

    def cell(count, total):
        return "%d for %d yards" % (count, total)

    split = penalty_split(games)
    if split is None:
        book = season_book(games)["teams"].get(club) or {}
        own, opp = book.get("team_stats") or {}, book.get("opponent_stats") or {}
        return [["Penalties", cell(own.get("penalties", 0), own.get("penalty_yards", 0)),
                 cell(opp.get("penalties", 0), opp.get("penalty_yards", 0))]], None
    empty = {"counter": [0, 0, 0], "records": [0, 0, 0, 0, 0, 0]}
    mine = split.get(club, empty)
    others = [v for team, v in split.items() if team != club]

    def theirs(kind):
        return [sum(v[kind][i] for v in others) for i in range(3)]

    before = [int(r["week"]) for r in games if not isinstance(r.get("penalties"), dict)]
    after = [int(r["week"]) for r in games if isinstance(r.get("penalties"), dict)]
    if before and after:
        since = "Penalties since Week %d" % min(after)
        return [[since, cell(*mine["records"][1:3]), cell(*theirs("records")[1:3])]], None
    kind = "records" if after else "counter"
    return [["Penalties", cell(*mine[kind][1:3]), cell(*theirs(kind)[1:3])]], None



def team_rows(games, club):
    """([label, club, its opponents] rows, note or None): the club's totals over ``games`` and its
    opponents', from the statistics owner."""
    team = season_book(games)["teams"].get(club) or {}
    own, opp = team.get("team_stats") or {}, team.get("opponent_stats") or {}
    rows = [[label, yards(own.get(field, 0)), yards(opp.get(field, 0))] for label, field in TEAM_ROWS]
    rows.append(["Third downs converted"] + ["%d of %d" % (side.get("third_down_conversions", 0),
                                                          side.get("third_down_attempts", 0)) for side in (own, opp)])
    penalties, note = penalty_rows(games, club)
    return rows + penalties, note



def leaders(games, club):
    """[category, player, pos, season] for each category: every player tied for the club's lead
    has a row, the category reading "Sacks, tied" (runtime/season_summary.tied_leaders)."""
    from runtime import season_summary as summary
    players = (season_book(games)["teams"].get(club) or {}).get("players") or {}
    rows = []
    for label, field, fmt in LEADERS:
        top = summary.tied_leaders(players, field)
        for name, line in top:
            rows.append([label + (", tied" if len(top) > 1 else ""), name, line.get("position", ""), fmt(line)])
    return rows





# ---------------------------------------------------------------- the staff's stored texts
# The week's authored parts (``staff_briefing.json`` in the week's data folder), each with its author
# and date, written by whoever prepares the week; nothing here writes one. Shapes: a text, a list of
# points (each a point and its text), rows by label (a player, a measure), or the proposals.
TEXT_SHAPES = {"central_question": "text", "carry_forward": "items", "not_settled": "text", "self_scout": "rows",
               "contingencies": "rows", "defense_questions": "rows", "defense_recommendation": "text",
               "defense_not_established": "text", "offense_tests": "rows", "offense_recommendation": "text",
               "offense_not_established": "text", "special_teams_report": "text", "operational_question": "text",
               "proposals": "proposals"}
TO_COME = "To come."


def staff_texts_path(wk):
    return wk.pages.staff_texts


def staff_texts(wk):
    """{part: entry} of the week's stored staff texts ({} before any); ValueError when one is malformed
    (an unknown part, no author or date, a date after today, or a part not in its shape)."""
    path = staff_texts_path(wk)
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data.get("texts") if isinstance(data, dict) else None
    where = wk.rel(path)
    if not isinstance(texts, dict) or set(data) - {"about", "texts"}:
        raise ValueError("%s holds an optional about and the texts by part" % where)
    nonempty = lambda v: isinstance(v, str) and v.strip()
    for part, entry in texts.items():
        shape = TEXT_SHAPES.get(part)
        if shape is None:
            raise ValueError("%s: %r is not a part of the briefing (%s)" % (where, part, ", ".join(TEXT_SHAPES)))
        if not isinstance(entry, dict) or not nonempty(entry.get("date")) or (
                shape != "proposals" and not nonempty(entry.get("author"))):
            raise ValueError("%s: %s needs its author and date" % (where, part))
        if date.fromisoformat(entry["date"]) > wk.master:
            raise ValueError("%s: %s is dated %s, after today (%s)" % (where, part, entry["date"], wk.master))
        keys = {"text": {"author", "date", "text"}, "items": {"author", "date", "items"},
                "rows": {"author", "date", "rows"}, "proposals": {"date", "rows"}}[shape]
        if set(entry) != keys:
            raise ValueError("%s: %s holds exactly %s" % (where, part, ", ".join(sorted(keys))))
        ok = {"text": lambda e: nonempty(e["text"]),
              "items": lambda e: isinstance(e["items"], list) and e["items"] and all(
                  isinstance(i, dict) and set(i) == {"point", "text"} and nonempty(i["point"]) and nonempty(i["text"])
                  for i in e["items"]),
              "rows": lambda e: isinstance(e["rows"], dict) and e["rows"] and all(
                  nonempty(k) and nonempty(v) for k, v in e["rows"].items()),
              "proposals": lambda e: isinstance(e["rows"], list) and e["rows"] and all(
                  isinstance(r, dict) and set(r) == {"author", "recommendation", "evidence", "cost"}
                  and all(nonempty(v) for v in r.values()) for r in e["rows"])}[shape]
        if not ok(entry):
            raise ValueError("%s: %s is not in its form (%s)" % (where, part, shape))
    return texts


def text_strings(texts):
    """Every string the staff wrote, for the clean-page and figure checks."""
    out = []
    for entry in texts.values():
        out += [entry[k] for k in ("text",) if k in entry]
        for item in entry.get("items") or ():
            out += [item["point"], item["text"]]
        rows = entry.get("rows")
        if isinstance(rows, dict):
            out += list(rows.values())
        elif isinstance(rows, list):
            out += [r[k] for r in rows for k in ("recommendation", "evidence", "cost")]
    return out


def by(entry, author=True):
    """The dated line saying whose view an entry is: " (Mike Tice, October 6)"."""
    when = day(entry["date"], False)
    return " (%s, %s)" % (entry["author"], when) if author and entry.get("author") else " (%s)" % when


def authored(texts, part, label):
    entry = texts.get(part)
    if entry is None:
        return "**%s:** %s" % (label, TO_COME)
    return "**%s:** %s%s" % (label, entry["text"].rstrip(), by(entry))


def optional(texts, part, label):
    entry = texts.get(part)
    return ["**%s:** %s%s" % (label, entry["text"].rstrip(), by(entry)), ""] if entry else []


def row_text(texts, part, key):
    entry = texts.get(part)
    value = ((entry or {}).get("rows") or {}).get(key)
    return value if value else "To come"


# ---------------------------------------------------------------- the briefing
def coordinator(wk, label):
    """The coach who prepares a phase ("offense", "defense", "special teams"), or None."""
    return next((name for name, phase in coordinators(wk) if phase == label), None)


def surname(name, fallback):
    return name.split()[-1] if name else fallback


def label_of(issue):
    """An issue (its date and revision) as the pages name it: "October 5, 2014", or from the second
    issue of a day "October 5, 2014, revision 2"."""
    return game_plan.issue_label(*issue)


def header_lines(wk, issued, previous, revision=1):
    g = wk.game
    names = coordinators(wk)
    staff = ", ".join("%s (%s)" % n for n in names)
    status = ("Revised: it replaces the briefing of %s" % label_of(previous) if previous else "Initial briefing")
    lines = ["**Issued:** %s" % label_of((issued, revision)),
             "**Game:** %s at %s, %s, %s, %s, %s" % (wk.place(g["away"]), wk.place(g["home"]), g.get("weekday"),
                                                   day(g["date"]), wk.views.kickoff(g["kickoff_et"]), g.get("stadium")),
             "**Prepared for:** Head Coach %s" % current_job.party_name(wk.job, wk.job.get("holder")),
             "**Football staff:** %s, the medical staff and pro personnel" % (staff or "the coordinators"),
             "**Status:** %s." % status]
    return [l + "  " for l in lines[:-1]] + lines[-1:] + [""]


def previous_game(wk, club):
    """The club's last game before this one, a playoff game the bracket has set included
    (runtime/game_weeks.club_games), or None."""
    from runtime import game_weeks
    games = game_weeks.club_games(wk.paths, club) if wk.postseason else [
        g for g in wk.paths.regular_games() if club in (g["away"], g["home"])]
    before = [g for g in games if g["date"] < wk.game["date"]]
    return max(before, key=lambda g: g["date"]) if before else None


def game_name(wk, game):
    """A game's name in football words: "Week 6", or the playoff round ("Wild Card")."""
    from runtime import game_weeks
    week = int(game["week"])
    return game_weeks.round_name(week) if game_weeks.is_postseason(wk.paths, week) else "Week %d" % week


def rest_text(wk):
    from runtime import game_weeks
    parts = []
    for club in (JAX, wk.opponent):
        last = previous_game(wk, club)
        where = ("at a neutral site" if wk.game.get("site") == "neutral"
                 else "on the road" if wk.game["away"] == club else "at home")
        if last is None:
            parts.append("%s: its first game, %s" % (wk.place(club), where))
            continue
        days = (date.fromisoformat(wk.game["date"]) - date.fromisoformat(last["date"])).days
        # The game before this one in the calendar: the week before, or for a Wild Card game the season's
        # last regular-season week (a club that skipped it had a bye; a first-round bye before the Divisional).
        expected = (game_weeks.last_regular_week(wk.paths) if wk.postseason and wk.game["week"] == game_weeks.FIRST_ROUND
                    else wk.game["week"] - 1)
        bye = " after its bye" if int(last["week"]) < expected else ""
        parts.append("%s: %d days since its %s game%s, %s" % (wk.place(club), days, game_name(wk, last), bye, where))
    return "; ".join(parts)


def place_words(n):
    return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def stakes_text(wk):
    """The division order and conference places, from the standings owner (with the tiebreakers)."""
    from runtime import standings
    from runtime.league import DIVISION_OF, conference_of
    picture = standings.compute(wk.receipts)
    division = DIVISION_OF[JAX]
    same = DIVISION_OF.get(wk.opponent) == division
    if not picture["played"]:
        return ("A division game. " if same else "") + "No regular-season game has been played."
    order = picture["division_ranks"][division]
    record = lambda club: wk.record(club)
    text = ("A division game. " if same else "") + "%s through Week %d: %s." % (
        division, picture["through_week"], ", ".join("%s %s" % (wk.place(c), record(c)) for c in order))
    conference = conference_of(JAX)
    places = picture["conferences"][conference]
    ranked = list(places["division_winners"]) + list(places["others"])
    if JAX in ranked:
        n = ranked.index(JAX) + 1
        if JAX in places["division_winners"]:
            role = "a division leader's place"
        elif n <= 4 + picture["wild_cards"]:
            role = "a wild-card place"
        else:
            role = "outside the playoff places"
        text += " In the %s order Jacksonville is %s, %s." % (conference, place_words(n), role)
    return text


def stakes_section(wk, texts):
    g = wk.game
    rows = [["Records entering the week", "%s %s; %s %s" % (wk.place(JAX), wk.record(JAX), wk.place(wk.opponent),
                                                            wk.record(wk.opponent))],
            ["Venue and kickoff", "%s, %s, %s, %s" % (g.get("stadium"), g.get("weekday"), day(g["date"]),
                                                     wk.views.kickoff(g["kickoff_et"]))],
            ["Rest and travel", rest_text(wk)],
            ["Game type", game_type(wk)]]
    # A playoff game's own facts (seeds, what a loss and a win mean, an earlier meeting, overtime and the
    # game-day limit) take the place of the regular season's division and conference order.
    rows += playoff_rows(wk) if wk.postseason else [["Stakes", stakes_text(wk)]]
    return (["## 1. The game and what is at stake", ""] + table(["Item", "This game"], rows) + [""]
            + [authored(texts, "central_question", "Staff's central football question"), ""])


def fixture_of(wk, receipt):
    """The fixture of a closed game, a playoff game the bracket set included, or None."""
    from runtime import game_weeks
    games = (game_weeks.club_games(wk.paths, receipt["home"]) if game_weeks.is_postseason(wk.paths, receipt["week"])
             else wk.paths.regular_games())
    return next((g for g in games if int(g["week"]) == int(receipt["week"])
                 and g["away"] == receipt["away"] and g["home"] == receipt["home"]), None)


def self_scout_section(wk, texts):
    out = ["## 2. Our last game and the self-scout", ""]
    games = wk.club_games(JAX)
    if not games:
        return out + ["**Last result:** No regular-season game has been played.", ""]
    # The last game may be a playoff game (runtime/game_weeks.py).
    last = max(games + wk.post_receipts, key=lambda r: int(r["week"]))
    other = last["away"] if last["home"] == JAX else last["home"]
    mine, theirs = last["final_score"][JAX], last["final_score"][other]
    verb = "beat" if mine > theirs else "lost to" if mine < theirs else "tied"
    fixture = fixture_of(wk, last)
    out += ["**Last result:** %s, %s %s %d-%d %s%s." % (
        game_name(wk, last), verb, wk.place(other), max(mine, theirs), min(mine, theirs),
        "at home" if last["home"] == JAX else "away", ", %s" % day(fixture["date"]) if fixture else ""), ""]
    rows, note = team_rows([last], JAX)
    out += table(["Relevant measure", club_short(JAX), club_short(other), "Why it matters this week"],
                 [r + [row_text(texts, "self_scout", r[0])] for r in rows]) + [""] + ([note, ""] if note else [])
    entry = texts.get("carry_forward")
    if entry is None:
        out += ["**Two things to carry forward:** %s" % TO_COME, ""]
    else:
        out += ["**Two things to carry forward:**%s" % by(entry), ""]
        out += ["- **%s.** %s" % (i["point"].rstrip("."), i["text"].rstrip()) for i in entry["items"]] + [""]
    out += optional(texts, "not_settled", "What the game book does not settle")
    return out


# A reserve status from which no return this season is possible, and the depth groups in words.
GROUP_WORDS = {"QB": "quarterback", "RB": "running back", "FB": "fullback", "WR": "receiver", "TE": "tight end",
               "OL": "offensive line", "DL": "defensive line", "LB": "linebacker", "DB": "defensive back",
               "K": "kicker", "P": "punter", "LS": "long snapper"}
LIMIT_DATE = re.compile(r"No (?:practice|return) before ((?:%s) \d{1,2})" % MONTHS)


def may_return(entry, game_day, year):
    """Whether a reserve-list player may practise or return before the game (a communicated limit
    date on or before it), so his status bears on a decision this week."""
    from datetime import datetime
    for limit in entry["limits"]:
        m = LIMIT_DATE.search(limit)
        if m and datetime.strptime("%s %d" % (m[1], year), "%B %d %Y").date() <= game_day:
            return True
    return False


def medical_rows(wk, page_rel, texts):
    """One row per active-roster player under a medical restriction or with an exam still to come
    (and a reserve-list player only when he may practise or return before the game): his status as
    the medical staff communicated it, the next medical decision, and the football contingency (the
    staff's, else the next player in his group's order on the chart)."""
    from runtime import season_summary as summary
    data = roster_record.load(wk.paths.roster)
    roster_page = wk.rel(wk.paths.roster_page)
    game_day = date.fromisoformat(wk.game["date"])
    chart = json.loads(wk.paths.depth_chart.read_text(encoding="utf-8"))
    groups = {p: g for g, order in (chart.get("depth") or {}).items() for p in order}
    rows = []
    for p in roster_record.players(data):
        entry = summary.medical_entry(p, wk.master)
        if entry is None:
            continue
        if p.get("list") != "active" and not may_return(entry, game_day, wk.season):
            continue
        name = "%s, %s" % (p["name"], p["position"])
        if entry["record"]:
            label, dest = entry["record"]
            dest, _, anchor = dest.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(roster_page), dest)).replace(os.sep, "/")
            name = "%s, %s" % (link(page_rel, resolved, p["name"], anchor), p["position"])
        status = "%s: %s (%s)" % (entry["instruction"], entry["injury"], entry["severity"])
        if entry["projected"]:
            status += "; projected return %s" % day(entry["projected"])
        status += "".join("; %s" % (l[:1].lower() + l[1:]) for l in entry["limits"])
        nxt = "; ".join("Reassessment, %s" % day(d, d.year != wk.master.year) for d in entry["reviews"]) \
            or "Not communicated"
        contingency = ((texts.get("contingencies") or {}).get("rows") or {}).get(p["name"])
        if not contingency:
            group = groups.get(p["name"])
            order = (chart.get("depth") or {}).get(group) or []
            behind = order[order.index(p["name"]) + 1:] if p["name"] in order else []
            contingency = ("Next in the chart's %s order: %s" % (GROUP_WORDS.get(group, group), behind[0]) if behind
                           else "No one behind him in the chart's %s order" % GROUP_WORDS.get(group, group)
                           if group else "Not on the game chart")
        rows.append([name, status, nxt, contingency])
    return rows


def medical_authority(wk):
    """Who diagnoses, restricts and clears, from the club's authority record."""
    current = current_job.appointment(wk.job) or {}
    owners = []
    for d in (current.get("authority") or {}).get("domains", ()):
        if d.get("domain") in ("Medical diagnosis", "Medical clearance and return-to-participation status"):
            for pid in d.get("final") or ():
                name = current_job.party_name(wk.job, pid)
                if name not in owners:
                    owners.append(name)
    who = " and ".join(owners) or "The medical staff"
    if who.startswith("Team "):
        who = "The team " + who[5:]
    return ("**Medical authority:** %s diagnoses, restricts and clears. You choose football roles only among the "
            "players eligible to play, and the inactives are declared before kickoff." % who)


def availability_section(wk, page_rel, texts):
    out = ["## 3. Medical and game-day availability", ""]
    rows = medical_rows(wk, page_rel, texts)
    if rows:
        out += table(["Player", "Status as of issue", "Next medical decision / date", "Football contingency"], rows)
    else:
        out += ["No player on the active roster is under a medical restriction or waiting on an exam."]
    ask = inactive_ask(wk)
    out += [""]
    if ask:
        out += ["**Game-day numbers:** %s." % (ask[:1].upper() + ask[1:]), ""]
    return out + [medical_authority(wk), ""]


OFFENSE_SPOTS = ("QB", "RB", "FB", "WR", "TE", "LT", "LG", "C", "RG", "RT", "T", "G")
SPECIAL_SPOTS = ("K", "PK", "P", "LS")


def opening_chart(wk, club):
    """[(spot, player, number)] of the opponent's opening-week chart, first at each spot, or None."""
    try:
        library = json.loads(wk.paths.background_depth.read_text(encoding="utf-8"))
        players = library["clubs"][club]["players"]
    except (OSError, ValueError, KeyError):
        return None
    first = []
    for p in players:
        spots = [s for s in str(p.get("slots", "")).split(",") if re.search(r"(?<!\d)1$", s)
                 and not re.match(r"^(KR|PR|KO|KOR|H|FG)\d", s)]
        if spots:
            first.append((spots[0][:-1], p["player_id"], p.get("jersey") or ""))
    return first


def side_of(spot):
    return "offense" if spot in OFFENSE_SPOTS else "special" if spot in SPECIAL_SPOTS else "defense"


def public_moves(wk, club):
    """[(date, move, player, position)] of the club's moves the league made public by today."""
    from runtime import rails
    from scripts.render_inseason_rails import move_words
    try:
        library = json.loads(wk.paths.background_depth.read_text(encoding="utf-8"))
        code = (library["clubs"][club] or {}).get("code")
    except (OSError, ValueError, KeyError):
        return []
    data = rails.load(wk.season, wk.root)
    moves = []
    for row in (data.rows if data is not None else ()):
        if row.get("club") != code or row.get("outcome") != "APPLY" or not row.get("gate_date"):
            continue
        if date.fromisoformat(row["gate_date"]) > wk.master:
            continue
        moves.append((row["gate_date"], row.get("player", ""), move_words(row.get("kind")), row.get("position", "")))
    return sorted(moves)


POSITION_SIDE = {"offense": OFFENSE_SPOTS + ("OL", "OT", "OG", "HB", "WR", "TE"), "special": SPECIAL_SPOTS}


def move_side(position):
    position = str(position or "").upper()
    for side, spots in POSITION_SIDE.items():
        if position in spots:
            return side
    return "defense"


def roster_lines(wk, club, side):
    chart = opening_chart(wk, club)
    out = []
    if chart is None:
        return ["No opening-week roster for %s is on file." % club_short(club), ""]
    starters = ["%s %s%s" % (spot, player, " (%s)" % number if number else "") for spot, player, number in chart
                if side_of(spot) == side]
    label = {"offense": "Opening-week starters", "defense": "Opening-week starters",
             "special": "Opening-week specialists"}[side]
    out += ["**%s:** %s." % (label, ", ".join(starters) if starters else "None on file"), ""]
    moves = [[day(d, False), move, player, pos] for d, player, move, pos in public_moves(wk, club) if move_side(pos) == side]
    out += ["**Moves made public since the opening week:**" + (" None on file." if not moves else ""), ""]
    if moves:
        out += table(["Date", "Move", "Player", "Pos"], moves) + [""]
    return out


def opponent_book(wk):
    games = wk.club_games(wk.opponent)
    team = (season_book(games)["teams"].get(wk.opponent) or {}) if games else {}
    return games, team.get("team_stats") or {}, team.get("opponent_stats") or {}


def evidence_through(wk, games):
    return "through Week %d (%d game%s)" % (int(games[-1]["week"]), len(games), "" if len(games) == 1 else "s")


def results_line(wk, games):
    club, parts = wk.opponent, []
    for r in games:
        other = r["away"] if r["home"] == club else r["home"]
        mine, theirs = r["final_score"][club], r["final_score"][other]
        result = "W" if mine > theirs else "L" if mine < theirs else "T"
        parts.append("%s %d-%d %s %s" % (result, mine, theirs, "vs." if r["home"] == club else "at", wk.place(other)))
    return "; ".join(parts)


def threat_rows(wk, games, categories, question):
    """[player, evidence, question] for the opponent's leaders in ``categories``: one row per player,
    his leads (a tie each named tied) together in it, in the order the categories first name him;
    ``question`` gives the staff's stored text for a player, or "To come"."""
    rows, at = [], {}
    for category, name, pos, line in leaders(games, wk.opponent):
        kind = category.split(",")[0]
        if kind not in categories:
            continue
        lead = "%s leader%s: %s" % (kind, ", tied" if "tied" in category else "", line)
        if name in at:
            rows[at[name]][1] += "; " + lead
            continue
        at[name] = len(rows)
        rows.append(["%s, %s" % (name, pos), lead, question(name)])
    return rows


def opponent_offense_section(wk, texts):
    club = club_short(wk.opponent)
    out = ["## 4. Opponent scouting: when they have the ball", ""]
    games, own, opp = opponent_book(wk)
    if not games:
        out += ["**Recorded evidence:** %s has not played a regular-season game." % club, ""]
    else:
        out += ["**Recorded evidence, %s:** %s. %s has scored %s points, with %s first downs, %s passing yards "
                "and %s rushing yards, %s turnovers, %d of %d on third down and %s sacks allowed." % (
                    evidence_through(wk, games), results_line(wk, games), club, yards(own.get("points", 0)),
                    yards(own.get("first_downs", 0)), yards(own.get("passing_yards", 0)),
                    yards(own.get("rushing_yards", 0)), yards(own.get("turnovers", 0)),
                    own.get("third_down_conversions", 0), own.get("third_down_attempts", 0),
                    yards(own.get("sacks_allowed", 0))), ""]
        rows = threat_rows(wk, games, ("Passing", "Rushing", "Receiving"),
                           lambda name: row_text(texts, "defense_questions", name))
        if rows:
            out += table(["Threat / personnel", "Verified evidence", "Matchup or question for our defense"], rows) + [""]
    out += roster_lines(wk, wk.opponent, "offense")
    crennel = coordinator(wk, "defense")
    out += [authored(texts, "defense_recommendation", "%s's recommendation" % surname(crennel, "The defensive staff")),
            ""]
    out += optional(texts, "defense_not_established", "Not established")
    return out


def opponent_defense_section(wk, texts):
    club = club_short(wk.opponent)
    out = ["## 5. Opponent scouting: when we have the ball", ""]
    games, own, opp = opponent_book(wk)
    tice = coordinator(wk, "offense")
    if not games:
        out += ["**Recorded evidence:** %s has not played a regular-season game." % club, ""]
    else:
        out += ["**Recorded evidence, %s:** %s has allowed %s points; its opponents gained %s passing yards and "
                "%s rushing yards and converted %d of %d third downs; %s takeaways and %s sacks." % (
                    evidence_through(wk, games), club, yards(opp.get("points", 0)), yards(opp.get("passing_yards", 0)),
                    yards(opp.get("rushing_yards", 0)), opp.get("third_down_conversions", 0),
                    opp.get("third_down_attempts", 0), yards(opp.get("turnovers", 0)),
                    yards(opp.get("sacks_allowed", 0))), ""]
        rows = threat_rows(wk, games, ("Tackles", "Sacks", "Interceptions"),
                           lambda name: row_text(texts, "offense_tests", name))
        if rows:
            out += table(["Defender / area", "Verified evidence", "What %s wants to test" % surname(tice, "the staff")],
                         rows) + [""]
    out += roster_lines(wk, wk.opponent, "defense")
    out += [authored(texts, "offense_recommendation", "%s's recommendation" % surname(tice, "The offensive staff")), ""]
    out += optional(texts, "offense_not_established", "Not established")
    return out


def kicking_rows(wk):
    rows = []
    books = {}
    for club in (JAX, wk.opponent):
        games = wk.club_games(club)
        books[club] = ((season_book(games)["teams"].get(club) or {}).get("team_stats") or {}) if games else {}
    for label, show in (("Field goals", lambda s: "%d of %d" % (s.get("field_goals", 0), s.get("field_goal_attempts", 0))),
                        ("Punts", lambda s: yards(s.get("punts", 0))),
                        ("Kick returns", lambda s: yards(s.get("kick_returns", 0))),
                        ("Punt returns", lambda s: yards(s.get("punt_returns", 0))),
                        ("Special-teams touchdowns", lambda s: yards(s.get("special_teams_touchdowns", 0)))):
        rows.append([label] + [show(books[c]) for c in (JAX, wk.opponent)])
    return rows


def game_management(wk):
    """The calling responsibilities and the standing rules in force, briefly."""
    holder = wk.job.get("holder")
    phases = []
    for phase, words in (("offense", "the offense"), ("defense", "the defense"), ("special_teams", "the kicking game")):
        interval = current_job.interval_on(wk.job, phase, wk.master) or {}
        if interval.get("caller"):
            phases.append((current_job.party_name(wk.job, interval["caller"]) if interval["caller"] != holder
                           else "You", words))
    grouped = []
    for who in dict.fromkeys(w for w, _ in phases):
        grouped.append("%s call%s %s" % (who, "" if who == "You" else "s",
                                        " and ".join(words for w, words in phases if w == who)))
    rules = [label for subject, label in (("fourth_down", "fourth downs"), ("two_point", "two-point tries"),
                                          ("kickoff", "kickoffs"))
             if any(i.get("subject") == subject for i in current_job.instructions(wk.job))]
    text = "; ".join(grouped) + "."
    if rules:
        text += " %s follow your standing rules (section 8) unless your Game Plan changes them." % (
            ", ".join(rules[:-1]) + (" and " if len(rules) > 1 else "") + rules[-1]).capitalize()
    return "**Game management:** " + text


def special_teams_section(wk, texts):
    out = ["## 6. Special teams and game operations", ""]
    out += table(["Kicking game", club_short(JAX), club_short(wk.opponent)], kicking_rows(wk)) + [""]
    games = wk.club_games(wk.opponent)
    if games:
        rows, note = penalty_rows(games, wk.opponent)
        out += table(["Penalties, %s" % club_short(wk.opponent), club_short(wk.opponent), "Its opponents"],
                     [[r[0]] + r[1:] for r in rows]) + [""] + ([note, ""] if note else [])
    out += roster_lines(wk, wk.opponent, "special")
    westhoff = coordinator(wk, "special teams")
    out += [authored(texts, "special_teams_report", "%s's report" % surname(westhoff, "The special-teams staff")), ""]
    out += [game_management(wk), ""]
    out += optional(texts, "operational_question", "Possible operational question")
    return out


def proposals_section(wk, texts):
    out = ["## 7. Staff proposals, alternatives and costs", ""]
    entry = texts.get("proposals")
    head = ["Staff", "Recommendation", "Evidence / intended test", "Cost or alternative"]
    if entry is None:
        rows = [[surname(name, name), "To come", "To come", "To come"] for name, _ in coordinators(wk)]
        return out + table(head, rows) + [""]
    rows = [[r["author"], r["recommendation"], r["evidence"], r["cost"]] for r in entry["rows"]]
    return out + table(head, rows) + ["", "Proposals as of %s; each is a staff proposal, not a decision made for you."
                                      % day(entry["date"], False), ""]


def first_practice(wk):
    """The first day of the game's practice week, when it is still to come (the scheduled events,
    runtime/season_summary.first_practice); else None."""
    from runtime import season_summary as summary
    return summary.first_practice(wk.cv.scheduled, wk.game["week"], wk.master)


def plan_settled(wk):
    """The week's items Stone settled on his own Game Plan (resolved by the user with the page as
    their record): the briefing keeps them in its asks, marked set."""
    holder, week, page = wk.job.get("holder"), wk.game["week"], wk.rel(wk.pages.plan)
    return [i for i in wk.cv.queue["items"] if i.get("status") == "RESOLVED" and i.get("owner") == holder
            and wk.views._week_of(i) == week and (i.get("resolution") or {}).get("by") == "user"
            and ((i.get("resolution") or {}).get("record") or {}).get("path") == page]


def inactive_ask(wk):
    """What the week's inactives ask of him (scripts/check_game_plan.inactive_ask), or None."""
    from scripts.check_game_plan import Plan, inactive_ask as ask
    try:
        return ask(Plan(wk.root, wk.season, wk.game["week"]))
    except (OSError, ValueError, KeyError):
        return None


def asks_section(wk, page_rel, plan_open=False, issued=None):
    """Section 8: what is owed by the head coach for the week. The items he settled on his Game Plan
    stay in the table, marked set on it (``plan_open`` shows them as they were before he set it, which
    is how a briefing is compared: settling his own items does not overtake it). The dependencies list
    only the exams dated on or after the briefing's issue date (``issued``, by default today). The
    inactives say how many sit and what his standing rule leaves to him. Then his standing
    directions, what the club decides, and what happens if facts change."""
    issued = issued or wk.master
    holder = wk.job.get("holder")
    week = wk.game["week"]
    items = [i for i in wk.views.ordered_items(wk.cv) if i.get("owner") == holder
             and wk.views._week_of(i) == week]
    settled = {i["id"]: i for i in plan_settled(wk)}
    items = sorted(items + list(settled.values()), key=lambda i: (
        (i.get("deadline") or {}).get("date") is None, (i.get("deadline") or {}).get("date") or "", i.get("id") or ""))
    out = ["## 8. What is owed by the head coach", ""]
    if not items:
        out += ["Nothing is waiting on you for this game.", ""]
    else:
        rows = []
        kickoff = "Before kickoff, %s, %s, %s" % (wk.game.get("weekday"), day(wk.game["date"], False),
                                                   wk.views.kickoff(wk.game["kickoff_et"]))
        practice = first_practice(wk)
        for item in items:
            question = item.get("question") or ""
            settle = wk.views.football(question.split(":", 1)[1]) if ":" in question else ""
            deadline = item.get("deadline") or {}
            before = deadline.get("before") or {}
            due = kickoff if before.get("week") == week else ("By %s" % day(deadline["date"], False)
                                                             if deadline.get("date") else "Not set")
            if item.get("class") == "weekly_game_plan" and before.get("week") == week and practice:
                # The plan's practice work is needed before the week's first practice; the rest by kickoff.
                due = "Practice work before the first practice, %s, %s; the rest %s" % (
                    practice.strftime("%A"), day(practice, False), kickoff[:1].lower() + kickoff[1:])
            if item["id"] in settled and not plan_open:
                due = "Set on your Game Plan, %s" % day(item["resolution"]["date"], False)
            waits = []
            for w in decisions.waits_ahead(item, issued):
                text = wk.views.football(w["what"].split(";")[0]) + (" (%s)" % day(w["date"], False)
                                                                     if w.get("date") else "")
                if text not in waits:
                    waits.append(text)
            if item.get("class") == "game_day_inactives":
                settle = inactive_ask(wk) or settle
            settle = current_ask(settle, issued) or SETTLE.get(item.get("class"), "")
            rows.append([item["title"].rstrip("."), settle[:1].upper() + settle[1:] if settle else "",
                         "%s; after: %s" % (due, "; ".join(w for w in waits if w)) if waits else
                         "%s; nothing still to come" % due])
        out += table(["Decision", "Choice required", "Deadline / dependency"], rows) + [""]
        out += ["Write your decisions on the %s; the staff checks it and tells you what is missing before "
                "anything is set for the game." % link(page_rel, wk.rel(wk.pages.plan), "Game Plan"), ""]
    out += ["**Standing directions:**", ""] + [wk.views.localize(l, page_rel) for l in wk.views._instructions(wk.cv, current_job.SUBJECTS)]
    out += ["", "**What the club, not Stone, decides:**", ""] + club_decides(wk) + [""]
    out += ["**If facts change:** The staff issues a new briefing, dated and, when it is the day's second or later, "
            "numbered as that day's revision; this one is kept as what you knew when you answered.", ""]
    return out


ASK_DATE = re.compile(r"\b(%s) (\d{1,2})(?:, (\d{4}))?\b" % MONTHS)


def current_ask(text, issued):
    """An item's question as of the briefing's issue date: a part of it tied to a date already past
    (", and who takes his practice work after his October 7 exam" on a briefing issued after it) is
    no longer asked, and is left out."""
    from datetime import datetime
    if not text:
        return text
    end = "." if text.rstrip().endswith(".") else ""
    parts = re.split(r",\s+and\s+|;\s+", text.rstrip().rstrip("."))
    kept = []
    for part in parts:
        dates = [datetime.strptime("%s %s %s" % (m[1], m[2], m[3] or issued.year), "%B %d %Y").date()
                 for m in ASK_DATE.finditer(part)]
        if dates and max(dates) < issued:
            continue
        kept.append(part)
    if len(kept) == len(parts):
        return text
    if not kept:
        return ""
    joined = kept[0] if len(kept) == 1 else ", ".join(kept[:-1]) + ", and " + kept[-1]
    return joined + end


def club_decides(wk):
    from scripts.render_club_pages import DECISIONS
    current = current_job.appointment(wk.job) or {}
    holder = wk.job.get("holder")
    out = []
    for d in (current.get("authority") or {}).get("domains", ()):
        if d.get("domain") not in GAME_WEEK_DOMAINS or not d.get("final") or holder in d["final"]:
            continue
        if d.get("domain") == "Special-teams decisions and calls":
            continue        # the calling arrangement is game management (section 6)
        names = []
        for i, pid in enumerate(d["final"]):
            name = current_job.party_name(wk.job, pid)
            group = ((wk.job.get("parties") or {}).get(pid) or {}).get("kind") == "group"
            names.append(name[:1].lower() + name[1:] if i and group else name)
        part = YOUR_PART.get(d.get("stone_action"), "your part is not recorded")
        out.append("- **%s.** %s; %s." % (DECISIONS[d["domain"]], " and ".join(names), part))
    return out or ["- Nothing this week."]


def links_line(wk, page_rel):
    from runtime.seasons import SeasonPaths  # noqa: F401  (the folder map places every page)
    mapping = json.loads((wk.root / "docs/repository_map.json").read_text(encoding="utf-8"))
    books = mapping.get("active_playbooks") or []
    out = [link(page_rel, wk.rel(wk.pages.plan), "Game Plan"),
           link(page_rel, wk.rel(wk.pages.readme), wk.label()),
           link(page_rel, wk.rel(wk.paths.roster_page), "Roster"),
           link(page_rel, wk.rel(wk.paths.record("depth_chart.md")), "Depth chart"),
           link(page_rel, wk.rel(wk.paths.record("medical/medical_history.md")), "Medical history")]
    for book in books:
        side = "Offensive" if "offensive" in book else "Defensive" if "defensive" in book else None
        if side and (wk.root / book).is_file():
            out.append(link(page_rel, book, "%s playbook" % side))
    games = wk.club_games(JAX) + wk.post_receipts
    if games:
        last = max(games, key=lambda r: int(r["week"]))
        report = decisions.week_pages(wk.season, int(last["week"]), wk.root).report
        if report.is_file():
            out.append(link(page_rel, wk.rel(report), "%s report" % game_name(wk, last)))
    return " · ".join(out)


def briefing(wk, issued=None, plan_open=False, previous=None, revision=1):
    """The Game Week Briefing as of ``issued`` (by default today), the day's ``revision``-th issue;
    ``previous`` is the issue (date, revision) of the briefing it replaces, if any (its status line)."""
    page_rel = wk.rel(wk.pages.briefing)
    issued = issued or wk.master
    texts = staff_texts(wk)
    out = ["# %s Game Week Briefing: %s" % (wk.label(), wk.title_where()), ""]
    out += header_lines(wk, issued, previous, revision)
    out += stakes_section(wk, texts)
    out += self_scout_section(wk, texts)
    out += availability_section(wk, page_rel, texts)
    out += opponent_offense_section(wk, texts)
    out += opponent_defense_section(wk, texts)
    out += special_teams_section(wk, texts)
    out += proposals_section(wk, texts)
    out += asks_section(wk, page_rel, plan_open, issued)
    out += [links_line(wk, page_rel), ""]
    return "\n".join(out).rstrip("\n") + "\n"


# The week's issue record (in the week's data folder): every briefing issued, oldest first, with
# its date, its revision (the n-th issue of that day), its file in the week folder and the sha256 of
# its bytes as it went out.
ISSUES = "briefings.json"
ISSUES_ABOUT = ("Every Game Week Briefing issued for the week, oldest first: the day it went out, its revision (the "
                "n-th issue of that day, so two issues the same day are told apart), its file in the week folder "
                "(the latest is the current briefing, each earlier one kept as he saw it) and the sha256 of its "
                "bytes as issued. Written only by scripts/render_game_week.py; validation holds each briefing to "
                "its entry.")


def issues_path(wk):
    return wk.pages.data / ISSUES


def issues(wk):
    """[{date, revision, file, sha256}] of the week's issued briefings, oldest first ([] before the
    first)."""
    path = issues_path(wk)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [dict(e) for e in data.get("issued") or ()]


def save_issues(wk, entries):
    path = issues_path(wk)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"about": ISSUES_ABOUT, "issued": entries}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def sha256(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def issued_on(wk):
    """The day the current briefing was issued, from the issue record; None before the first."""
    entries = issues(wk)
    return date.fromisoformat(entries[-1]["date"]) if entries else None


def revisions(entries):
    """Each entry's revision as the record must number it: the n-th issue of its day."""
    out, seen = [], {}
    for entry in entries:
        seen[entry.get("date")] = seen.get(entry.get("date"), 0) + 1
        out.append(seen[entry.get("date")])
    return out


def issue_of(entry):
    """(date, revision) of an issue record entry; ValueError for an entry not in its form."""
    try:
        return date.fromisoformat(entry["date"]), int(entry["revision"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("an entry of the issue record is malformed (its date and revision): %r" % (entry,))


def current_issue(wk):
    """(date, revision) of the current briefing, from the issue record; None before the first."""
    entries = issues(wk)
    return issue_of(entries[-1]) if entries else None


def issue_errors(wk):
    """The week's briefings against the issue record: each recorded briefing present with the bytes
    it went out with, the latest the current briefing, dates in order and not after today, and no
    briefing in the folder that no issue produced."""
    label = wk.label()
    entries = issues(wk)
    current = wk.pages.briefing
    if not entries:
        return (["%s: the Game Week Briefing has no issue record (%s); a briefing goes out only through python "
                 "scripts/render_game_week.py" % (label, wk.rel(issues_path(wk)))] if current.is_file() else [])
    errors, previous, recorded = [], None, set()
    numbered = revisions(entries)
    for n, entry in enumerate(entries):
        try:
            when, name, digest = date.fromisoformat(entry["date"]), entry["file"], entry["sha256"]
            revision = int(entry["revision"])
        except (KeyError, TypeError, ValueError):
            errors.append("%s: issue record entry %d is malformed (%s)" % (label, n + 1, wk.rel(issues_path(wk))))
            continue
        if revision != numbered[n]:
            errors.append("%s: the briefing issued %s is recorded as revision %d of its day; it is revision %d"
                          % (label, day(when), revision, numbered[n]))
        recorded.add(name)
        path = wk.pages.folder / name
        if previous is not None and when < previous:
            errors.append("%s: the briefing of %s is recorded after a later one" % (label, day(when)))
        if when > wk.master:
            errors.append("%s: a briefing is recorded as issued %s, after today (%s)" % (label, day(when), day(wk.master)))
        previous = when
        if n == len(entries) - 1 and name != current.name:
            errors.append("%s: the latest issue (%s) is not the current Game Week Briefing" % (label, name))
        if not path.is_file():
            errors.append("%s: the briefing issued %s is missing (%s)" % (label, day(when), wk.rel(path)))
        elif sha256(path) != digest:
            errors.append("%s: %s differs from the briefing issued %s; a briefing is never edited by hand (restore "
                          "it as it went out; a changed situation is a new briefing)" % (label, wk.rel(path), day(when)))
    for path in sorted(wk.pages.folder.glob(current.stem + "_*.md")):
        if path.name not in recorded:
            errors.append("%s: %s is not a briefing the issue record holds" % (label, wk.rel(path)))
    return errors


def overtaken(wk, old=None):
    """Whether the situation has changed since the briefing ``old`` (by default the current one)
    went out: its rebuild for its own issue date differs from it. Stone settling the week's own
    items on his Game Plan is his answer to the briefing, not a change of situation, so it is also
    compared as it was before he set them. False before the first briefing."""
    current = current_issue(wk)
    if current is None or not wk.pages.briefing.is_file():
        return False
    when, revision = current
    if old is None:
        old = wk.pages.briefing.read_text(encoding="utf-8")
    previous = previous_issue(wk)
    return old != briefing(wk, when, previous=previous, revision=revision) and \
        old != briefing(wk, when, plan_open=True, previous=previous, revision=revision)


def previous_issue(wk, new=False):
    """The issue (date, revision) of the briefing the current one replaced (or, ``new``, the one a new
    issue would replace), from the issue record; None for the first."""
    entries = issues(wk)
    if new:
        return issue_of(entries[-1]) if entries else None
    return issue_of(entries[-2]) if len(entries) > 1 else None


def read_errors(wk, text):
    """The staff's stored texts against their rules: present form, clean, and only figures the page
    shows elsewhere."""
    try:
        texts = staff_texts(wk)
    except (OSError, ValueError) as exc:
        return ["Staff texts: %s" % exc]
    strings = text_strings(texts)
    errors = []
    for value in strings:
        errors += ["Staff texts: %s" % e for e in page_errors(wk.rel(staff_texts_path(wk)), value, root=wk.root)]
    rest = text
    for value in strings:
        rest = rest.replace(value, "")
    shown = {n.rstrip(".,") for n in re.findall(r"\d[\d,.]*", rest)}
    for value in strings:
        for figure in re.findall(r"\d[\d,.]*", value):
            figure = figure.rstrip(".,")
            if figure and figure not in shown:
                errors.append("Staff texts: %s is not a figure the briefing shows" % figure)
    return errors


# ---------------------------------------------------------------- the plan and the index
def pending_players(wk):
    """The active-roster players with a medical decision still to come before the game (a
    reassessment or a projected return on or before game day), in roster order."""
    from runtime import season_summary as summary
    game_day = date.fromisoformat(wk.game["date"])
    out = []
    for p in roster_record.players(roster_record.load(wk.paths.roster), ("active",)):
        entry = summary.medical_entry(p, wk.master)
        if entry is None:
            continue
        if entry["reviews"] and entry["reviews"][0] <= game_day or entry["projected"] and entry["projected"] <= game_day:
            out.append(p["name"])
    return out


def either(names):
    names = [n.split()[-1] for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]


def earlier_sheets(wk):
    """{week: frozen call sheet} of every earlier Jacksonville game whose plan is set, each through the
    folder map (a playoff round's sheet is in the postseason folder's data twin)."""
    out = {}
    for w in range(1, wk.game["week"]):
        path = decisions.week_pages(wk.season, w, wk.root).call_sheet
        if path.is_file():
            out[w] = json.loads(path.read_text(encoding="utf-8"))
    return out


def plan_facts(wk):
    """The builder's lines of the week's blank Game Plan: the head coach, the game, the briefing it
    answers, the pending players, and the guide line of each part, naming the legal choices."""
    from runtime.rules import RULES
    week = wk.game["week"]
    g = wk.game
    page_rel = wk.rel(wk.pages.plan)
    roster = roster_record.load(wk.paths.roster)
    active = len(roster_record.players(roster, ("active",)))
    inactive = active - RULES.active_limit
    earlier = earlier_sheets(wk)
    last = max(earlier) if earlier else None
    standing = {i.get("subject"): i.get("summary") for i in current_job.instructions(wk.job)}
    callers = {}
    for phase in current_job.PHASES:
        interval = current_job.interval_on(wk.job, phase, wk.master) or {}
        if interval.get("caller"):
            callers[phase] = current_job.party_name(wk.job, interval["caller"])
    pending = pending_players(wk)
    rule = lambda subject: ("Standing rule (%s)" % (standing[subject][:1].lower() + standing[subject][1:]).rstrip(".")
                            if standing.get(subject) else "Standing rule")
    calls = [c["name"] for c in (earlier.get(last) or {}).get("offensive_call_sheet") or () if isinstance(c, dict)]
    carry = "Carry Week %d" % last if last else "Carry Week N"
    guides = {
        "header": ("Answer every line under its heading. No change keeps the last legal instruction set; None means "
                   "intentionally nothing; a line left empty is unanswered, and nothing is set for the game until "
                   "every line is answered. Baseline: %s starts from that week's calls and defensive responses as "
                   "set; New plan starts from none." % carry),
        1: ("Your direction to the staff, in your words, on the line or in bullets below it. It is kept with the "
            "plan and never changes a call."),
        2: ("%d of the %d on the active roster do not dress. Inactives: %s, Standing rule with the others you name "
            "after it, the players by name with commas between them, or %s. Depth/role changes: No change, None, "
            "or the changes separated by semicolons: a role and its player (%s) or a group's new order (Wide "
            "receivers order: the names). Medical decisions cannot be overridden."
            % (inactive, active, rule("inactives"), carry, ", ".join(game_plan.ROLES))),
        3: ("Caller: who calls the offense on the staff page (%s), or No change. Opening ideas: %s Write them "
            "separated by semicolons, a call repeated for a return to it; or %s opening, No change or None."
            % (callers.get("offense", "not recorded"), game_plan.OPENING_GUIDE, carry)),
        "calls": ("One row for each call you add or change; with %s every call of that week stays as set unless you "
                  "change it here, list it as not available or remove it as a special play. Name a call by its full "
                  "name, as the active playbook and the earlier call sheets name it (%s); a shorter name is asked "
                  "about, never filled in. Any call in the active playbook may be named, whether or not it has been "
                  "practiced: a new call is its formation, concept and protection, and one whose words a longer "
                  "call's name holds is written New call: before it. A variation goes in parentheses after "
                  "the call, or (without the variation) to take one off. When I want it: the situations separated "
                  "by commas (%s); the opening ideas line puts a call in the opening sequence. Your reason and stop "
                  "condition are kept with the plan and never change a call."
                  % (carry, "Week %d: %s" % (last, "; ".join(calls)) if calls else "none yet",
                     ", ".join(game_plan.SITUATION_WORDS))),
        "situations": ("How you want each situation called is your direction to the staff; which calls are on each "
                       "situation's list is set by the table above. Special plays: each call by its full name with "
                       "Keep, Remove or Practice only, separated by semicolons; a special play may be named for any "
                       "situation in the table above. Calls not available "
                       "this week: the calls by their full names, separated by semicolons, or None. A call taken off "
                       "leaves the opening calls, and the calls after it move up."),
        4: ("Caller: who calls the defense on the staff page (%s), or No change. Rush rule: %s, as the active "
            "defensive playbook has it, or No change." % (callers.get("defense", "not recorded"),
                                                           game_plan.RUSH_CHOICE)),
        "responses": ("One row for each prepared response; with %s and no rows, that week's responses stay as set, "
                      "and any row replaces them all. First column: a situation the defense keys (%s) is that "
                      "situation's call; begin with If or When for a conditional response and with Counter for a "
                      "counter; anything else is a presentation. Response: the active defensive playbook's words, "
                      "one package, front and pressure at most, the coverages as alternatives (Quarters or Cover 6); "
                      "any word of the active defensive playbook may be named, whether or not it has been practiced."
                      % (carry, ", ".join(w.lower() for w in game_plan.DEF_MENU_WORDS.values()))),
        5: ("Kicking-game caller: %s calls it on the staff page, or No change. Fourth downs: %s. Two-point tries: "
            "%s. Kickoffs and onside situations: %s. Each also takes %s, No change, None (fourth downs only: your "
            "live call on each) or My rules, otherwise the decision, above a rule table."
            % (callers.get("special_teams", "no one"), rule("fourth_down"), rule("two_point"), rule("kickoff"), carry)),
        6: ("Information for the staff, one row for each priority: what you want practiced and who takes a "
            "limited player's work. It never decides which calls you may name; any call in the book stays "
            "available. These are intentions; the practices themselves are recorded when they happen."),
        7: ("Your directions, on the line or in bullets below it; nothing here is set for the game, and silence never "
            "means approval."),
    }
    holder = current_job.party_name(wk.job, wk.job.get("holder"))
    when = current_issue(wk)
    return {"head_coach": holder,
            "game": "%s at %s, %s, %s, %s, %s" % (wk.place(g["away"]), wk.place(g["home"]), g.get("weekday"),
                                                 day(g["date"]), wk.views.kickoff(g["kickoff_et"]), g.get("stadium")),
            "briefing": label_of(when) if when else "",
            "contingency_label": "If %s cannot dress" % either(pending) if pending else game_plan.CONTINGENCY_LABEL,
            "intro": ("Your decisions for the game, in football words: answer every line here, or upload a .md or "
                      ".txt file with the same headings. The staff checks the page and tells you what is missing or "
                      "invalid before anything is set for the game; the page stays as the record of your decisions. "
                      "%s" % link(page_rel, wk.rel(wk.pages.briefing), "Game Week Briefing")),
            "guides": guides}


def plan_page(wk):
    return game_plan.blank("%s Game Plan: %s" % (wk.label(), wk.title_where()), plan_facts(wk))


def earlier_briefings(wk):
    """[(path, issue (date, revision))] of the briefings the current one replaced, oldest first, from
    the issue record."""
    return [(wk.pages.folder / e["file"], issue_of(e)) for e in issues(wk)[:-1]]


def index_page(wk):
    page_rel = wk.rel(wk.pages.readme)
    week = wk.game["week"]
    rows = []
    if wk.pages.briefing.is_file():
        when = current_issue(wk)
        rows.append([link(page_rel, wk.rel(wk.pages.briefing), "Game Week Briefing"),
                     "The coaching staff's brief: the game and its stakes, our last game, availability, both sides of "
                     "the opponent, the kicking game, the staff's proposals and what is owed by you",
                     "Issued %s" % label_of(when) if when else "Issued"])
    else:
        rows.append(["Game Week Briefing", "The coaching staff's brief for the week", "To come"])
    plan_status = ("Set for the game" if wk.pages.call_sheet.is_file()
                   else "Waiting on you" if wk.pages.plan.is_file() else "To come")
    rows.append([link(page_rel, wk.rel(wk.pages.plan), "Game Plan") if wk.pages.plan.is_file() else "Game Plan",
                 "Your decisions for the game: what you want it to look like, availability, the offense, the "
                 "defense, the kicking game and game decisions, practice and your directions", plan_status])
    report = wk.pages.report
    rows.append([link(page_rel, wk.rel(report), "Game Report") if report.is_file() else "Game Report",
                 "What happened and what changed",
                 # Opened before the game with its preparation; written once the game has closed.
                 ("Written" if wk.closed else "Preparation written") if report.is_file() else "After the game"])
    out = ["# %s: %s" % (wk.label(), wk.title_where()), "", "%s." % wk.when(), ""]
    out += table(["Page", "What it holds", "Status"], rows) + [""]
    earlier = earlier_briefings(wk)
    if earlier:
        out += ["Earlier briefings, as they went out: " + "; ".join(
            link(page_rel, wk.rel(p), label_of(issue)) for p, issue in earlier) + ".", ""]
    applied = game_plan.applied_record(wk.pages.applied)
    if applied is not None and applied.get("event"):
        out += [game_plan.event_line(applied), ""]
    if wk.postseason:
        # No weekly awards are drawn for a playoff game (library/2013_postseason_format_and_schedule.md, R-P4).
        out += [" · ".join([link(page_rel, wk.rel(wk.pages.folder.parent / "README.md"), "Playoff games"),
                            link(page_rel, wk.rel(wk.paths.record("postseason/README.md")), "Postseason")]), ""]
        return "\n".join(out)
    out += [" · ".join([link(page_rel, wk.rel(wk.pages.folder.parent / "README.md"), "All weeks"),
                        link(page_rel, wk.rel(wk.paths.record("statbook.md")), "Regular-season statistics"),
                        link(page_rel, wk.rel(wk.paths.awards / ("week_%02d" % week) / "README.md"),
                             "Week %d awards" % week)]), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- write and check
def write(root=ROOT, week=None):
    """Issue the week's pages; returns the paths written. A briefing the situation has overtaken is
    kept beside the new one, named for its date, and every issue is entered in the week's issue
    record. A briefing that differs from its recorded issue (edited by hand) is never kept as what he
    saw: the write refuses until it is restored."""
    wk = Week(root, week)
    if wk.game is None:
        return []
    if wk.closed:
        raise ValueError("%s has closed; its briefing stays as it went out" % wk.label())
    written = []
    # The week's decision items, opened before its first briefing (scripts/open_game_week.py).
    from scripts import open_game_week
    if open_game_week.open_items(root, wk.game["week"]):
        written.append(Path(root).resolve() / open_game_week.QUEUE)
        wk = Week(root, week)
    wk.pages.folder.mkdir(parents=True, exist_ok=True)
    entries = issues(wk)
    problems = issue_errors(wk) if (entries or wk.pages.briefing.is_file()) else []
    if problems:
        raise ValueError("; ".join(problems))
    if not entries or overtaken(wk):
        if entries:
            # The briefing it replaces is kept beside it, named for its issue: its date, and from the
            # second issue of a day its revision (Game_Week_Briefing_October_5_2.md).
            when, revision = issue_of(entries[-1])
            label = day(when, False) + (" %d" % revision if revision > 1 else "")
            target, n = wk.pages.earlier_briefing(label), 2
            while target.exists():
                target, n = wk.pages.earlier_briefing("%s %d" % (label, n)), n + 1
            target.write_bytes(wk.pages.briefing.read_bytes())
            entries[-1]["file"] = target.name
            written.append(target)
        revision = 1 + sum(1 for e in entries if e["date"] == wk.master.isoformat())
        wk.pages.briefing.write_text(briefing(wk, previous=previous_issue(wk, new=True), revision=revision),
                                     encoding="utf-8")
        entries.append({"date": wk.master.isoformat(), "revision": revision, "file": wk.pages.briefing.name,
                        "sha256": sha256(wk.pages.briefing)})
        written += [wk.pages.briefing, save_issues(wk, entries)]
    if not wk.pages.plan.is_file():
        wk.pages.plan.write_text(plan_page(wk), encoding="utf-8")
        written.append(wk.pages.plan)
    index = index_page(wk)
    if not wk.pages.readme.is_file() or wk.pages.readme.read_text(encoding="utf-8") != index:
        wk.pages.readme.write_text(index, encoding="utf-8")
        written.append(wk.pages.readme)
    return written


def write_index(root=ROOT, week=None):
    """Rebuild only a week's index (after its Game Report is written, or its plan applied)."""
    wk = Week(root, week)
    if wk.game is None or not (wk.pages.briefing.is_file() or wk.pages.plan.is_file()):
        return []
    index = index_page(wk)
    if not wk.pages.readme.is_file() or wk.pages.readme.read_text(encoding="utf-8") != index:
        wk.pages.readme.write_text(index, encoding="utf-8")
        return [wk.pages.readme]
    return []


def has_pages(pages):
    """Whether a week's folder holds a game week page (a briefing, a Game Plan or an issue record);
    a week before the Game Week pages keeps its index as written."""
    return pages.briefing.is_file() or pages.plan.is_file() or (pages.data / ISSUES).is_file()


def page_weeks(root=ROOT):
    """The weeks of the season's Jacksonville games whose folder holds a game week page, played
    weeks included, the postseason games the bracket has set among them (runtime/game_weeks.py)."""
    from runtime import game_weeks
    wk = Week(root)
    weeks = [g["week"] for g in wk.cv.games]
    weeks += [g["week"] for g in game_weeks.club_games(wk.paths, JAX) if g.get("game_type") == "postseason"]
    return [w for w in weeks if has_pages(decisions.week_pages(wk.season, w, wk.root))]


def week_errors(wk):
    """One week's pages against their owners: the index current, the briefings as their issue record
    holds them, the staff texts well formed and, while the week is open, its Game Plan beside its
    briefing."""
    label = wk.label()
    errors = []
    if not has_pages(wk.pages):
        return errors
    if wk.pages.briefing.is_file() and not wk.pages.plan.is_file() and not wk.closed:
        errors.append("%s: the Game Week Briefing is issued without a Game Plan (%s)" % (label, wk.rel(wk.pages.plan)))
    issued = issue_errors(wk)
    if any("is malformed" in e for e in issued):
        return errors + issued      # nothing that reads the issue record can be checked past it
    index = index_page(wk)
    if not wk.pages.readme.is_file() or wk.pages.readme.read_text(encoding="utf-8") != index:
        errors.append("%s: the week index is missing or stale (%s); run python scripts/render_game_week.py%s"
                      % (label, wk.rel(wk.pages.readme), " --week %d" % wk.game["week"] if wk.closed else ""))
    errors += issued
    if wk.pages.briefing.is_file():
        errors += ["%s: %s" % (label, e) for e in read_errors(wk, wk.pages.briefing.read_text(encoding="utf-8"))]
    return errors


def validation_errors(root=ROOT):
    """Every game week's pages, played weeks included (week_errors). A dated briefing that the
    situation has overtaken is the weekly workflow's to re-issue, not a defect."""
    errors = []
    for week in page_weeks(root):
        errors += week_errors(Week(root, week))
    return errors


def check(root=ROOT, week=None):
    """``validation_errors`` (with ``week``, that week's alone, played or open), and for an open week
    a briefing not yet issued or overtaken by the situation, and an unclean briefing. A record the
    pages read that is not in its format (a medical note, say) is one line, as validation reports it."""
    try:
        return _check(root, week)
    except ValueError as exc:
        return ["game week pages: cannot be built: %s" % exc]


def _check(root, week):
    wk = Week(root, week)
    if wk.game is None:
        return []
    errors = validation_errors(root) if week is None else week_errors(wk)
    label = wk.label()
    if wk.closed:
        return errors
    if not wk.pages.briefing.is_file():
        return errors + ["%s: no Game Week Briefing has been issued; run python scripts/render_game_week.py" % label]
    if overtaken(wk):
        errors.append("%s: the situation has changed since the briefing of %s; a new briefing is due (run python "
                      "scripts/render_game_week.py, which keeps the old one as he saw it)"
                      % (label, label_of(current_issue(wk))))
    when, revision = current_issue(wk)
    errors += page_errors(wk.rel(wk.pages.briefing), briefing(wk, when, previous=previous_issue(wk), revision=revision),
                          root=wk.root)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--week", type=int)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        wk = Week(args.root, args.week)
    except ValueError as exc:
        print("game week pages: cannot be built: %s" % exc)
        return 1
    note = None
    if wk.game is not None and not wk.closed and not staff_texts_path(wk).is_file():
        note = "note: %s's staff texts are still to come (%s); the briefing says so" % (
            wk.label(), wk.rel(staff_texts_path(wk)))
    if args.check:
        errors = check(args.root, args.week)
        print("\n".join(errors) if errors else "GAME WEEK PAGES CURRENT")
        if note:
            print(note)
        return 1 if errors else 0
    try:
        if wk.game is not None and wk.closed:
            written = write_index(args.root, args.week)
        else:
            written = write(args.root, args.week)
    except ValueError as exc:
        # A record the pages read that is not in its format (a medical note, the issue record): named,
        # with nothing written past it.
        print("game week pages: cannot be built: %s" % exc)
        return 1
    for path in written:
        print("wrote %s" % Path(path).relative_to(Path(args.root).resolve()).as_posix())
    if not written:
        print("game week pages: nothing to write")
    if note:
        print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
