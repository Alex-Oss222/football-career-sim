#!/usr/bin/env python3
"""Build a game week's pages (rebuild step 4): the Game Week Briefing, the
blank Game Plan and the week folder's index.

  python scripts/render_game_week.py [--week N] [--check] [--root PATH]

The week is the next Jacksonville game that has not closed, unless --week
names another. Every page is built from its stored owners only:

- the Game Week Briefing, brought by the coaching staff (the coordinators who
  prepare each phase, from the current-job record), with the medical update
  and the pro scouting report as sections of their own: the game and both
  records (the fixtures and the closed games); every player under a medical
  instruction with his status and next exam (the roster record); how
  Jacksonville played (the last game and the season's leaders, from the game
  records); the opponent (its results, season statistics and leaders from the
  game records, and its roster as the historical rosters give it: its opening
  week chart and the moves made public by today, never one after the date);
  what is being asked of Stone and by when (the decision queue; a deadline
  whose time no rule on file gives reads "before kickoff"); his standing
  instructions; who else decides what (the current-job record); and the staff
  read. The read is stored text in the week's data folder
  (``staff_read.json``: author, date and text), written by whoever prepares
  the week; the builder checks it names its author and date and cites only
  figures the page shows, and a missing read renders as "Staff read to come".
- the Game Plan, Stone's page (runtime/game_plan.py): written blank once, when
  the week opens, and never rewritten by this builder; he fills it in place
  or uploads a file with the same headings.
- the week index (the folder's README): the three pages, the date and the
  opponent.

A briefing is dated the day it is issued. If the situation changes after it
goes out (anything the page shows other than its date), writing issues a new
one and keeps the old one beside it, as what he saw, named for its date
(Game_Week_Briefing_October_5.md). Stone settling the week's own items on his
Game Plan is not such a change (``overtaken``); a briefing issued later shows
them "Set on your Game Plan". Writing opens the week's two decision items
first (scripts/open_game_week.py), so the briefing lists them. Opening or
building a page never moves time or creates an event; the week index carries
the event line of the applied Game Plan from its record.

``--check`` writes nothing. It reports a missing or out-of-date index, a
missing Game Plan beside a briefing, a malformed staff read, and a briefing
the situation has overtaken (a new one is due). Repository validation runs the
narrower ``validation_errors``: the open week's index current, its Game Plan
present beside its briefing and its staff read well formed (a dated briefing
that has been overtaken is the weekly workflow's to re-issue, not a defect).
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
CLEAR = "No communicated restriction"
MOVE_WORDS = {"ps_signing": "Signed to the practice squad", "waived": "Waived", "fa_signing": "Signed as a free agent",
              "ps_promotion": "Promoted from the practice squad", "ps_release": "Released from the practice squad",
              "released": "Released", "released_unspecified": "Released", "re_signing": "Re-signed",
              "ps_poach": "Signed from another club's practice squad", "waiver_claim": "Claimed off waivers",
              "retirement": "Retired", "trade_in": "Acquired in a trade", "trade_out": "Traded away",
              "reserve_injured": "Placed on reserve/injured", "suspension": "Suspended"}
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
TEAM_ROWS = (("Points", lambda t, s: s), ("First downs", lambda t, s: t.get("first_downs", 0)),
             ("Passing yards", lambda t, s: t.get("passing_yards", 0)),
             ("Rushing yards", lambda t, s: t.get("rushing_yards", 0)),
             ("Turnovers", lambda t, s: t.get("turnovers", 0)),
             ("Sacks allowed", lambda t, s: t.get("sacks_allowed", 0)),
             ("Third downs converted", lambda t, s: (t.get("third_down_conversions", 0), t.get("third_down_attempts", 0))),
             ("Penalties", lambda t, s: (t.get("penalties", 0), t.get("penalty_yards", 0))))


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
        from scripts import render_career_views as views
        self.root = Path(root).resolve()
        self.views = views
        self.cv = views.context(self.root)
        self.season, self.paths, self.master = self.cv.season, self.cv.paths, self.cv.master
        self.job = self.cv.job
        self.receipts = self._receipts()
        closed = {int(r["week"]) for r in self.receipts if JAX in (r["home"], r["away"])}
        games = self.cv.games
        if week is None:
            open_games = [g for g in games if g["week"] not in closed]
            self.game = open_games[0] if open_games else None
        else:
            self.game = next((g for g in games if g["week"] == week), None)
            if self.game is None:
                raise ValueError("Jacksonville has no game in Week %d of %d" % (week, self.season))
        self.closed = self.game is not None and self.game["week"] in closed
        if self.game is not None:
            self.pages = decisions.week_pages(self.season, self.game["week"], self.root)
            self.opponent = self.game["home"] if self.game["away"] == JAX else self.game["away"]

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


# ---------------------------------------------------------------- the briefing
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


def game_section(wk):
    g = wk.game
    site = "%s (%s)" % (g.get("stadium"), "away" if g["away"] == JAX else "home")
    rows = [[club_short(c), wk.record(c)] for c in (JAX, wk.opponent)]
    return (["## The game", ""] + table(["Opponent", "Date", "Kickoff", "Site"],
                                        [[wk.opponent, "%s, %s" % (g.get("weekday"), day(g["date"])),
                                          wk.views.kickoff(g["kickoff_et"]), site]]) + [""]
            + table(["Club", "Record"], rows) + [""])


def availability_rows(wk, page_rel):
    data = roster_record.load(wk.paths.roster)
    roster_page = wk.rel(wk.paths.roster_page)
    rows = []
    for p in roster_record.players(data):
        text = p.get("availability") or ""
        if not text or text.startswith(CLEAR):
            continue
        status, _, rest = text.partition(":")
        injury = rest.split(",")[0].strip() if rest else ""
        back = re.search(r"projected return ((?:%s) \d{1,2}, \d{4})" % MONTHS, text)
        exams = [m for m in re.finditer(r"\breassessment ((?:%s) \d{1,2})\b" % MONTHS, text)]
        upcoming = []
        for m in exams:
            when = date.fromisoformat("%d-%02d-%02d" % (wk.master.year, MONTHS.split("|").index(m[1].split()[0]) + 1,
                                                        int(m[1].split()[1])))
            if when >= wk.master:
                upcoming.append(day(when, False))
        limits = re.findall(r"\bno (?:practice|return) before (?:%s) \d{1,2}" % MONTHS, text)
        record = re.search(r"\[(medical record|medical history)\]\(([^)]+)\)", text)
        target = ""
        if record:
            dest, _, anchor = record[2].partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(roster_page), dest)).replace(os.sep, "/")
            target = link(page_rel, resolved, record[1][:1].upper() + record[1][1:], anchor)
        listed = {"active": "Active roster", "reserve": "Reserve list", "practice_squad": "Practice squad"}[p["list"]]
        rows.append([p["name"], p["position"], listed, status.strip(), injury,
                     back[1] if back else "Not set", "; ".join(upcoming) or "None communicated",
                     "; ".join(l[:1].upper() + l[1:] for l in limits), target])
    return rows


def medical_section(wk, page_rel):
    rows = availability_rows(wk, page_rel)
    out = ["## Medical update", "", "From the medical staff: every player under a medical instruction, as the club "
           "has communicated it.", ""]
    if not rows:
        return out + ["No player is under a medical instruction.", ""]
    head = ["Player", "Pos", "List", "Status", "Injury", "Projected return", "Next exam", "Limits", "Record"]
    return out + table(head, rows) + [""]


def team_stat_rows(games, club):
    totals = {}
    other_totals = {}
    for r in games:
        other = r["away"] if r["home"] == club else r["home"]
        for side, store in ((club, totals), (other, other_totals)):
            stats = r["team_stats"].get(side, {})
            for label, value in TEAM_ROWS:
                v = value(stats, r["final_score"][side])
                if isinstance(v, tuple):
                    old = store.get(label, (0, 0))
                    store[label] = (old[0] + v[0], old[1] + v[1])
                else:
                    store[label] = store.get(label, 0) + v
    return totals, other_totals


def shown(label, value):
    if isinstance(value, tuple):
        return "%d of %d" % value if label.startswith("Third") else "%d for %d yards" % value
    return yards(value)


def leaders(games, club):
    lines = {}
    for r in games:
        for name, line in (r["team_stats"].get(club, {}).get("players") or {}).items():
            total = lines.setdefault(name, {})
            for key, value in line.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    total[key] = total.get(key, 0) + value
            total["position"] = line.get("position", total.get("position", ""))
    rows = []
    for label, field, fmt in LEADERS:
        ranked = sorted(((n, l) for n, l in lines.items() if l.get(field, 0) > 0), key=lambda x: (-x[1][field], x[0]))
        if ranked:
            name, line = ranked[0]
            rows.append([label, name, line.get("position", ""), fmt(line)])
    return rows


def last_game_section(wk):
    games = wk.club_games(JAX)
    out = ["## How we played", ""]
    if not games:
        return out + ["No regular-season game has been played.", ""]
    last = games[-1]
    other = last["away"] if last["home"] == JAX else last["home"]
    mine, theirs = last["final_score"][JAX], last["final_score"][other]
    verb = "beat" if mine > theirs else "lost to" if mine < theirs else "tied"
    out += ["Last game: Week %d, %s %s %d-%d %s." % (int(last["week"]), verb, wk.place(other), max(mine, theirs),
                                                     min(mine, theirs), "at home" if last["home"] == JAX else "away"), ""]
    ours, theirs_ = team_stat_rows([last], JAX)
    out += table(["", club_short(JAX), club_short(other)],
                 [[label, shown(label, ours[label]), shown(label, theirs_[label])] for label, _ in TEAM_ROWS]) + [""]
    out += ["Season leaders through Week %d:" % int(last["week"]), ""]
    out += table(["Category", "Player", "Pos", "Season"], leaders(games, JAX)) + [""]
    return out


def opponent_section(wk):
    club = wk.opponent
    games = wk.club_games(club)
    out = ["## Pro scouting report: %s" % club_short(club), "",
           "From the pro scouting staff: %s's games this season and its roster as the league's transactions "
           "have made it public by %s." % (club_short(club), day(wk.master)), ""]
    rows, w, l, t = [], 0, 0, 0
    for r in games:
        other = r["away"] if r["home"] == club else r["home"]
        mine, theirs = r["final_score"][club], r["final_score"][other]
        w, l, t = w + (mine > theirs), l + (mine < theirs), t + (mine == theirs)
        result = "W" if mine > theirs else "L" if mine < theirs else "T"
        rows.append([int(r["week"]), ("vs. %s" if r["home"] == club else "at %s") % wk.place(other),
                     "%s %d-%d" % (result, mine, theirs), "%d-%d" % (w, l) + ("-%d" % t if t else "")])
    if not rows:
        out += ["%s has not played a regular-season game." % club_short(club), ""]
    else:
        out += ["### Results", ""] + table(["Week", "Opponent", "Result", "Record"], rows) + [""]
        ours, theirs = team_stat_rows(games, club)
        out += ["### Season statistics", "", "Totals over %d games." % len(games), ""]
        out += table(["", club_short(club), "Its opponents"],
                     [[label, shown(label, ours[label]), shown(label, theirs[label])] for label, _ in TEAM_ROWS]) + [""]
        out += ["### Leaders", ""] + table(["Category", "Player", "Pos", "Season"], leaders(games, club)) + [""]
    out += roster_lines(wk, club)
    return out


def roster_lines(wk, club):
    """The opponent's opening-week chart (first at each spot) and its moves made public by today."""
    chart_path = wk.paths.background_depth
    out = []
    try:
        library = json.loads(chart_path.read_text(encoding="utf-8"))
        players = library["clubs"][club]["players"]
    except (OSError, ValueError, KeyError):
        return ["### Roster", "", "No opening-week roster for %s is on file." % club_short(club), ""]
    first = []
    for p in players:
        spots = [s for s in str(p.get("slots", "")).split(",") if re.search(r"(?<!\d)1$", s)
                 and not re.match(r"^(KR|PR|KO|H)\d", s)]
        if spots:
            first.append([spots[0][:-1], p["player_id"], p.get("jersey") or ""])
    out += ["### Roster", "", "First on the opening-week depth chart at each spot:", ""]
    out += table(["Spot", "Player", "#"], first) + [""]
    from runtime import rails
    data = rails.load(wk.season, wk.root)
    code = (library["clubs"][club] or {}).get("code")
    moves = []
    if data is not None:
        for row in data.rows:
            if row.get("club") != code or row.get("outcome") != "APPLY" or not row.get("gate_date"):
                continue
            if date.fromisoformat(row["gate_date"]) > wk.master:
                continue
            moves.append((row["gate_date"], row.get("player", ""), [
                day(row["gate_date"], False), MOVE_WORDS.get(row.get("kind"), str(row.get("kind")).replace("_", " ").capitalize()),
                row.get("player", ""), row.get("position", "")]))
    moves = [m[2] for m in sorted(moves, key=lambda m: (m[0], m[1]))]
    out += ["Moves made public since the opening week:", ""]
    out += (table(["Date", "Move", "Player", "Pos"], moves) if moves else ["None on file."]) + [""]
    return out


def plan_settled(wk):
    """The week's items Stone settled on his own Game Plan (resolved by the user with the page as
    their record): the briefing keeps them in its asks, marked set."""
    holder, week, page = wk.job.get("holder"), wk.game["week"], wk.rel(wk.pages.plan)
    return [i for i in wk.cv.queue["items"] if i.get("status") == "RESOLVED" and i.get("owner") == holder
            and wk.views._week_of(i) == week and (i.get("resolution") or {}).get("by") == "user"
            and ((i.get("resolution") or {}).get("record") or {}).get("path") == page]


def asks_section(wk, page_rel, plan_open=False):
    """What is asked of Stone for the week. The items he settled on his Game Plan stay in the table,
    marked set on it (``plan_open`` shows them as they were before he set it, which is how a briefing
    is compared: settling his own items does not overtake it)."""
    holder = wk.job.get("holder")
    week = wk.game["week"]
    items = [i for i in wk.views.ordered_items(wk.cv) if i.get("owner") == holder
             and wk.views._week_of(i) == week]
    settled = {i["id"]: i for i in plan_settled(wk)}
    items = sorted(items + list(settled.values()), key=lambda i: (
        (i.get("deadline") or {}).get("date") is None, (i.get("deadline") or {}).get("date") or "", i.get("id") or ""))
    out = ["## What we need from you", ""]
    if not items:
        out += ["Nothing is waiting on you for this game.", ""]
    else:
        rows = []
        kickoff = "Before kickoff, %s, %s, %s" % (wk.game.get("weekday"), day(wk.game["date"], False),
                                                   wk.views.kickoff(wk.game["kickoff_et"]))
        for item in items:
            question = item.get("question") or ""
            settle = wk.views.football(question.split(":", 1)[1]) if ":" in question else ""
            deadline = item.get("deadline") or {}
            before = deadline.get("before") or {}
            due = kickoff if before.get("week") == week else ("By %s" % day(deadline["date"], False)
                                                             if deadline.get("date") else "Not set")
            if item["id"] in settled and not plan_open:
                due = "Set on your Game Plan, %s" % day(item["resolution"]["date"], False)
            waits = [wk.views.football(w["what"].split(";")[0]) + (" (%s)" % day(w["date"], False) if w.get("date") else "")
                     for w in item.get("waits_on") or ()]
            settle = settle or SETTLE.get(item.get("class"), "")
            rows.append([item["title"].rstrip("."), settle[:1].upper() + settle[1:] if settle else "",
                         due, "; ".join(w for w in waits if w) or "Nothing"])
        out += table(["Decision", "To settle", "Due", "Still to come"], rows) + [""]
        out += ["Write your decisions on the %s; the staff checks it and tells you what is missing before "
                "anything is set for the game." % link(page_rel, wk.rel(wk.pages.plan), "Game Plan"), ""]
    return out


def standing_section(wk, page_rel):
    lines = wk.views._instructions(wk.cv)
    return ["## Your standing instructions", ""] + [wk.views.localize(l, page_rel) for l in lines] + [""]


def others_section(wk, page_rel):
    out = ["## Who else decides", ""]
    out += [wk.views.localize(l, page_rel) for l in wk.views._callers(wk.cv)]
    from scripts.render_club_pages import DECISIONS
    current = current_job.appointment(wk.job) or {}
    holder = wk.job.get("holder")
    for d in (current.get("authority") or {}).get("domains", ()):
        if d.get("domain") not in GAME_WEEK_DOMAINS or not d.get("final") or holder in d["final"]:
            continue
        names = []
        for i, pid in enumerate(d["final"]):
            name = current_job.party_name(wk.job, pid)
            group = ((wk.job.get("parties") or {}).get(pid) or {}).get("kind") == "group"
            names.append(name[:1].lower() + name[1:] if i and group else name)
        part = YOUR_PART.get(d.get("stone_action"), "your part is not recorded")
        out.append("- **%s.** %s; %s." % (DECISIONS[d["domain"]], " and ".join(names), part))
    return out + [""]


def staff_read(wk):
    """(author, date, text) of the week's stored staff read, or None; ValueError when malformed."""
    path = wk.pages.staff_read
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"author", "date", "text"} or not all(
            isinstance(data[k], str) and data[k].strip() for k in data):
        raise ValueError("%s must hold exactly an author, a date and a text" % wk.rel(path))
    when = date.fromisoformat(data["date"])
    if when > wk.master:
        raise ValueError("%s is dated %s, after today (%s)" % (wk.rel(path), data["date"], wk.master))
    return data["author"], when, data["text"]


def read_section(wk):
    found = staff_read(wk)
    if found is None:
        return ["## Staff read", "", "Staff read to come.", ""]
    author, when, text = found
    return ["## Staff read", "", "**%s, %s.** %s" % (author, day(when), text), ""]


def briefing(wk, issued=None, plan_open=False):
    page_rel = wk.rel(wk.pages.briefing)
    issued = issued or wk.master
    names = coordinators(wk)
    staff = ", ".join("%s (%s)" % n for n in names[:-1]) + (" and " if len(names) > 1 else "") + (
        "%s (%s)" % names[-1] if names else "")
    out = ["# Week %d Game Week Briefing: %s" % (wk.game["week"], wk.title_where()), "",
           "From the coaching staff, %s: %s, with the medical staff's update and the pro scouting report on %s."
           % (day(issued), staff or "the coordinators", club_short(wk.opponent)), ""]
    out += game_section(wk)
    out += medical_section(wk, page_rel)
    out += last_game_section(wk)
    out += opponent_section(wk)
    out += asks_section(wk, page_rel, plan_open)
    out += standing_section(wk, page_rel)
    out += others_section(wk, page_rel)
    out += read_section(wk)
    out += [" · ".join([link(page_rel, wk.rel(wk.pages.plan), "Game Plan"), link(page_rel, wk.rel(wk.pages.readme), "Week %d" % wk.game["week"]),
                        link(page_rel, wk.rel(wk.paths.record("depth_chart.md")), "Depth chart"),
                        link(page_rel, wk.rel(wk.paths.roster_page), "Roster"),
                        link(page_rel, wk.rel(wk.paths.record("medical/medical_history.md")), "Medical history")]), ""]
    return "\n".join(out).rstrip("\n") + "\n"


ISSUED = re.compile(r"^(From the coaching staff, )((?:%s) \d{1,2}, \d{4})(: )" % MONTHS, re.M)


def issued_on(text):
    m = ISSUED.search(text or "")
    if not m:
        return None
    from datetime import datetime
    return datetime.strptime(m[2], "%B %d, %Y").date()


def undated(text):
    return ISSUED.sub(r"\1\3", text)


def overtaken(wk, old):
    """Whether the situation has changed since the briefing ``old`` went out: anything it shows other
    than its date. Stone settling the week's own items on his Game Plan is his answer to the
    briefing, not a change of situation, so it is compared as it was before he set them."""
    then = undated(old)
    return then != undated(briefing(wk)) and then != undated(briefing(wk, plan_open=True))


def read_errors(wk, text):
    """The staff read against its rules: present form, and only figures the page shows."""
    try:
        found = staff_read(wk)
    except (OSError, ValueError) as exc:
        return ["Staff read: %s" % exc]
    if found is None:
        return []
    errors = ["Staff read: %s" % e for e in page_errors(wk.rel(wk.pages.staff_read), found[2], root=wk.root)]
    rest = text.replace(found[2], "")
    shown_numbers = set(re.findall(r"\d[\d,.]*", rest))
    for figure in re.findall(r"\d[\d,.]*", found[2]):
        figure = figure.rstrip(".,")
        if figure and figure not in shown_numbers and figure not in {n.rstrip(".,") for n in shown_numbers}:
            errors.append("Staff read: %s is not a figure the briefing shows" % figure)
    return errors


# ---------------------------------------------------------------- the plan and the index
def plan_page(wk):
    week = wk.game["week"]
    previous = [g["week"] for g in wk.cv.games if g["week"] < week]
    roster = roster_record.load(wk.paths.roster)
    from runtime.rules import RULES
    inactive = len(roster_record.players(roster, ("active",))) - RULES.active_limit
    interval = current_job.interval_on(wk.job, "special_teams", wk.master) or {}
    caller = current_job.party_name(wk.job, interval["caller"]) if interval.get("caller") else None
    standing = {i.get("subject"): i.get("summary") for i in current_job.instructions(wk.job)
                if i.get("subject") in ("fourth_down", "two_point", "kickoff", "inactives")}
    legal = game_plan.legal_lines(inactive, caller, previous[-1] if previous else None, standing)
    page_rel = wk.rel(wk.pages.plan)
    intro = ("%s. Your decisions for the game: write under each heading, or upload a .md or .txt file with the "
             "same headings. The first line under each heading names the choices open to you. The staff checks "
             "the page and tells you what is missing or invalid before anything is set for the game; the page "
             "stays as the record of your decisions. %s" % (wk.when(), link(page_rel, wk.rel(wk.pages.briefing),
                                                                         "Game Week Briefing")))
    return game_plan.blank("Week %d Game Plan: %s" % (week, wk.title_where()), intro, legal)


def earlier_briefings(wk):
    found = sorted(wk.pages.folder.glob(wk.pages.briefing.stem + "_*.md"))
    return sorted(found, key=lambda p: (issued_on(p.read_text(encoding="utf-8")) or date.min, p.name))


def index_page(wk):
    page_rel = wk.rel(wk.pages.readme)
    week = wk.game["week"]
    rows = []
    if wk.pages.briefing.is_file():
        when = issued_on(wk.pages.briefing.read_text(encoding="utf-8"))
        rows.append([link(page_rel, wk.rel(wk.pages.briefing), "Game Week Briefing"),
                     "The coaching staff's brief: availability, how both clubs have played, what we need from you "
                     "and by when", "Issued %s" % day(when) if when else "Issued"])
    else:
        rows.append(["Game Week Briefing", "The coaching staff's brief for the week", "To come"])
    plan_status = ("Set for the game" if wk.pages.call_sheet.is_file()
                   else "Waiting on you" if wk.pages.plan.is_file() else "To come")
    rows.append([link(page_rel, wk.rel(wk.pages.plan), "Game Plan") if wk.pages.plan.is_file() else "Game Plan",
                 "Your decisions for the game: inactives, depth, practice, the offense, fourth downs, two-point "
                 "tries, kickoffs, the defense and the kicking game", plan_status])
    report = wk.pages.report
    rows.append([link(page_rel, wk.rel(report), "Game Report") if report.is_file() else "Game Report",
                 "What happened and what changed", "Written" if report.is_file() else "After the game"])
    out = ["# Week %d: %s" % (week, wk.title_where()), "", "%s." % wk.when(), ""]
    out += table(["Page", "What it holds", "Status"], rows) + [""]
    earlier = earlier_briefings(wk)
    if earlier:
        out += ["Earlier briefings, as they went out: " + ", ".join(
            link(page_rel, wk.rel(p), day(issued_on(p.read_text(encoding="utf-8")))) for p in earlier) + ".", ""]
    applied = game_plan.applied_record(wk.pages.applied)
    if applied is not None and applied.get("event"):
        out += [game_plan.event_line(applied), ""]
    out += [" · ".join([link(page_rel, wk.rel(wk.pages.folder.parent / "README.md"), "All weeks"),
                        link(page_rel, wk.rel(wk.paths.record("statbook.md")), "Regular-season statistics"),
                        link(page_rel, wk.rel(wk.paths.awards / ("week_%02d" % week) / "README.md"),
                             "Week %d awards" % week)]), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- write and check
def write(root=ROOT, week=None):
    """Issue the week's pages; returns the paths written. A briefing the situation has overtaken is
    kept beside the new one, named for its date."""
    wk = Week(root, week)
    if wk.game is None:
        return []
    if wk.closed:
        raise ValueError("Week %d has closed; its briefing stays as it went out" % wk.game["week"])
    written = []
    # The week's decision items, opened before its first briefing (scripts/open_game_week.py).
    from scripts import open_game_week
    if open_game_week.open_items(root, wk.game["week"]):
        written.append(Path(root).resolve() / open_game_week.QUEUE)
        wk = Week(root, week)
    wk.pages.folder.mkdir(parents=True, exist_ok=True)
    new = briefing(wk)
    old = wk.pages.briefing.read_text(encoding="utf-8") if wk.pages.briefing.is_file() else None
    if old is None or overtaken(wk, old):
        if old is not None:
            when = issued_on(old)
            label = day(when, False) if when else "earlier"
            target, n = wk.pages.earlier_briefing(label), 2
            while target.exists():
                target, n = wk.pages.earlier_briefing("%s %d" % (label, n)), n + 1
            target.write_text(old, encoding="utf-8")
            written.append(target)
        wk.pages.briefing.write_text(new, encoding="utf-8")
        written.append(wk.pages.briefing)
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


def validation_errors(root=ROOT):
    """The open week's pages: its index current, its Game Plan beside its briefing, its staff read
    well formed. Nothing to check before a week's briefing is issued."""
    wk = Week(root)
    if wk.game is None or not wk.pages.briefing.is_file():
        return []
    errors = []
    label = "Week %d" % wk.game["week"]
    if not wk.pages.plan.is_file():
        errors.append("%s: the Game Week Briefing is issued without a Game Plan (%s)" % (label, wk.rel(wk.pages.plan)))
    index = index_page(wk)
    if not wk.pages.readme.is_file() or wk.pages.readme.read_text(encoding="utf-8") != index:
        errors.append("%s: the week index is missing or stale (%s); run python scripts/render_game_week.py"
                      % (label, wk.rel(wk.pages.readme)))
    errors += ["%s: %s" % (label, e) for e in read_errors(wk, wk.pages.briefing.read_text(encoding="utf-8"))]
    if issued_on(wk.pages.briefing.read_text(encoding="utf-8")) is None:
        errors.append("%s: the Game Week Briefing carries no issue date" % label)
    return errors


def check(root=ROOT, week=None):
    wk = Week(root, week)
    if wk.game is None:
        return []
    errors = validation_errors(root) if week is None else []
    label = "Week %d" % wk.game["week"]
    if wk.closed:
        return errors
    if not wk.pages.briefing.is_file():
        return errors + ["%s: no Game Week Briefing has been issued; run python scripts/render_game_week.py" % label]
    new = briefing(wk)
    old = wk.pages.briefing.read_text(encoding="utf-8")
    if overtaken(wk, old):
        errors.append("%s: the situation has changed since the briefing of %s; a new briefing is due (run python "
                      "scripts/render_game_week.py, which keeps the old one as he saw it)"
                      % (label, day(issued_on(old)) if issued_on(old) else "its issue"))
    errors += page_errors(wk.rel(wk.pages.briefing), new, root=wk.root)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--week", type=int)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    wk = Week(args.root, args.week)
    note = None
    if wk.game is not None and not wk.closed and not wk.pages.staff_read.is_file():
        note = "note: Week %d's staff read is still to come (%s); the briefing says so" % (
            wk.game["week"], wk.rel(wk.pages.staff_read))
    if args.check:
        errors = check(args.root, args.week)
        print("\n".join(errors) if errors else "GAME WEEK PAGES CURRENT")
        if note:
            print(note)
        return 1 if errors else 0
    if wk.game is not None and wk.closed:
        written = write_index(args.root, args.week)
    else:
        written = write(args.root, args.week)
    for path in written:
        print("wrote %s" % Path(path).relative_to(Path(args.root).resolve()).as_posix())
    if not written:
        print("game week pages: nothing to write")
    if note:
        print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
