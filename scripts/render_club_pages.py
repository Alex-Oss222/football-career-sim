#!/usr/bin/env python3
"""Build the club pages (rebuild step 3b): the team page, the roster and the depth chart.

  python scripts/render_club_pages.py [--check] [--root PATH]

Each page is built from its stored owners and never edited by hand:

- the roster page (``SeasonPaths.roster_page``) from the roster record
  (runtime/roster.py): an as-of line with the last game, the counts, then one
  table per position group (Player, linked to his page | # | Pos | Age |
  Status | Availability). The number is the one his player page shows
  (runtime/player_pages), the age is worked out from his birth date at the
  roster's date (runtime/player_bios), the status is named as the player
  pages name it. The depth chart owns order and roles, the player records own
  transactions, so neither appears here.
- the depth chart page from the game depth chart (the order, positions,
  game roles, captains and inactives the weekly build reads, rendered in its
  exact order), the working chart (Stone's dated role decisions), the roster
  record (availability) and the dated update log in the data area.
- the team page from the closed games (results, and the division through
  runtime/standings.py), the fixtures (the next game), the roster record, and
  the current-job record (runtime/current_job.py: who calls and prepares each
  phase, who decides what at the club, and what the owner and general manager
  have asked of the head coach).

Every page is dated by the master date (runtime/player_bios.master_date), as
the desk and the coach pages are: the results, the standings, the next game,
the staff on game day and the ages all come from the closed games up to that
date. A closed game is matched to its fixture by week and clubs, never by its
event id. The roster record carries the date of the event it was last brought
up to; ``check`` fails when that date is earlier than Jacksonville's last
closed game, so a game's close must refresh the record (docs/update_workflow.md).
The check also holds the depth chart's update log to its form (``log_errors``).

Every page passes the clean-page rule (runtime/clean_pages.py). ``check``
(--check) rebuilds each page in memory, writes nothing and reports one that is
missing, differs or breaks the rule; ``write`` writes them. Run after any
change to a stored owner they read, and after every closed game
(docs/update_workflow.md). The builder is a script, not a runtime module,
because it reads the current-job record, which no runtime module may import
(tests/test_career_layer_isolation.py).
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

from runtime import current_job, people, player_bios, roster as roster_record  # noqa: E402
from runtime.assignments import ROLE_NAMES, SEATS, role_labels as chart_role_labels  # noqa: E402,F401
from runtime.league import DIVISION_OF  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths, active_season  # noqa: E402
JAX = "Jacksonville Jaguars"
UNITS = (("Offense", ("QB", "RB", "FB", "WR", "TE", "OL")), ("Defense", ("DL", "LB", "DB")))
GROUP_NAMES = {"QB": "Quarterbacks", "RB": "Running backs", "FB": "Fullback", "WR": "Wide receivers",
               "TE": "Tight ends", "OL": "Offensive line", "DL": "Defensive line", "LB": "Linebackers",
               "DB": "Defensive backs"}
# The game chart's role names in football words, the seats and the role labels are
# runtime/assignments.py's, shared with the player pages' Current assignment line.
ACTIONS = {"decides": "Decides", "decides_part": "Decides part", "recommends": "Recommends",
           "consulted": "Consulted", "responds": "Responds", "informs": "Supplies information", "none": "No part",
           "unset": "Not recorded"}
# The club's decisions as an NFL front office names them (the current-job record holds the
# rulebook's general wording, written for any club or level). Every domain the club's appointment
# holds needs a label here; a new one fails the build until it is named.
DECISIONS = {
    "Hire, retain, suspend, or fire the head coach": "Hiring and firing the head coach",
    "Permission for another club to contact or interview the head coach while he is under contract, including "
    "any compensation asked for it": "Letting another club talk to the head coach",
    "Hire, retain, assign, suspend, or fire assistant coaches": "Hiring, assigning and firing assistant coaches",
    "Final player-acquisition and target-selection decisions": "Which players to acquire",
    "Franchise-level quarterback decisions specifically: using the first-round pick on a QB, trading premium "
    "draft capital for one, a major multiyear financial commitment to one as the intended starter, or a major "
    "disposition of the starting QB": "Franchise quarterback moves: a first-round quarterback, premium picks traded "
    "for one, a major long-term contract for an intended starter, or moving on from the starter",
    "Draft selections or recruiting offers": "Draft selections",
    "Player contract negotiation and execution": "Player contracts",
    "Salary-cap management or team and program budget": "The salary cap and the football budget",
    "Final roster cuts and roster-limit compliance": "Final roster cuts and roster limits",
    "Game-day active status, elevations, and inactives": "Game-day actives and inactives",
    "Depth chart and package roles": "Depth chart and package roles",
    "Starting lineups": "Starting lineups",
    "Practice schedule, workload, and repetition allocation": "Practice schedule, workload and reps",
    "Offensive game-day operation": "The offense on game day",
    "Defensive game-day operation": "The defense on game day",
    "Special-teams decisions and calls": "Special teams decisions and calls",
    "Medical diagnosis": "Medical diagnosis",
    "Medical clearance and return-to-participation status": "Medical clearance and return to practice and play",
    "Injury reporting and official availability designation": "The injury report and game-status designations",
    "Player discipline": "Player discipline",
    "Media policy, access, and official communications": "Media policy, access and club statements",
    "Professional trades, waivers, claims, releases, reserve mechanisms, and practice-squad transactions":
        "Trades, waivers, claims, releases, the reserve lists and the practice squad",
    "Facilities, staffing levels, equipment, technology, travel resources, and other material allocation":
        "Facilities, staffing, equipment, technology and travel",
}
# The club titles of the people the team page names beside the head coach.
TITLES = {"Shad Khan": "owner", "David Caldwell": "general manager"}
PHASE_NAMES = {"offense": "Offense", "defense": "Defense", "special_teams": "Special teams"}


# ------------------------------------------------------------------ small formats
def long_date(value):
    d = date.fromisoformat(value) if isinstance(value, str) else value
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def month_day(value):
    d = date.fromisoformat(value) if isinstance(value, str) else value
    return "%s %d" % (d.strftime("%B"), d.day)


def city(team):
    from runtime.player_pages import club_short
    return club_short(team)


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def table(head, rows, right=()):
    lines = ["| " + " | ".join(head) + " |",
             "|" + "|".join("---:" if i in right else "---" for i in range(len(head))) + "|"]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def link(page_rel, target_rel, label, anchor=""):
    """A Markdown link from the page at ``page_rel`` to ``target_rel`` (both repository paths)."""
    path = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, path.replace(" ", "%20"), "#" + anchor if anchor else "")


# ------------------------------------------------------------------ inputs
class Context:
    """Everything the club pages read, loaded once."""

    def __init__(self, root=ROOT, year=None):
        from scripts.render_season_stats import load_receipts
        root = Path(root).resolve()
        self.root = root
        self.year = active_season(root) if year is None else year
        self.paths = SeasonPaths(self.year, root)
        self.roster = roster_record.load(self.paths.roster)
        self.as_of = master_date(root)
        self.chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        working = self.paths.record("offseason/depth_chart_working.json")
        self.working = json.loads(working.read_text(encoding="utf-8")) if working.is_file() else {}
        log = self.paths.record("team/depth_chart/update_log.json")
        self.log = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else {"entries": []}
        self.job = current_job.load(root)
        self.fixtures = {game_key(g): g for g in self.paths.regular_games()}
        receipts = load_receipts(self.paths.receipts) if self.paths.receipts.is_dir() else []
        # Every closed game, matched to its fixture by week and clubs (an event id may be regenerated).
        self.unmatched = [r for r in receipts if game_key(r) not in self.fixtures]
        self.closed = [r for r in receipts if game_key(r) in self.fixtures]
        self.receipts = [r for r in self.closed if date.fromisoformat(self.fixture(r)["date"]) <= self.as_of]
        self.games = sorted((r for r in self.receipts if JAX in (r["home"], r["away"])), key=lambda r: int(r["week"]))
        self.bios = player_bios.load(root)
        self.pages = self._player_pages()

    def _player_pages(self):
        """{name: (page repository path, number)} for every player on the roster record."""
        from runtime import player_pages
        ctx = player_pages.Context(self.root)
        folder = player_pages.jaguars_folder(ctx).relative_to(self.root).as_posix()
        out = {}
        for record in ctx.records.values():
            if record["name"] in out or not player_pages.controlled_name(ctx, record):
                continue
            p = ctx.league_player(record)
            out[record["name"]] = ("%s/%s.md" % (folder, people.slugify(record["name"])),
                                   p["number"] if p and p["number"] is not None else None)
        return out

    def fixture(self, receipt):
        return self.fixtures[game_key(receipt)]

    def next_game(self):
        """Jacksonville's next game not yet closed: on game day, before the close, that day's game."""
        closed = {game_key(r) for r in self.closed}
        ours = sorted((g for g in self.fixtures.values() if JAX in (g["away"], g["home"])
                       and date.fromisoformat(g["date"]) >= self.as_of and game_key(g) not in closed),
                      key=lambda g: g["date"])
        return ours[0] if ours else None


def game_key(game):
    """(week, away club, home club): how a closed game finds its fixture."""
    return int(game["week"]), game["away"], game["home"]


def game_line(receipt):
    """("against Pittsburgh" or "at San Diego", "Pittsburgh 27, Jacksonville 10")."""
    home = receipt["home"] == JAX
    opponent = receipt["away"] if home else receipt["home"]
    score = receipt["final_score"]
    first, second = sorted((JAX, opponent), key=lambda t: -score[t])
    if score[JAX] == score[opponent]:
        first, second = JAX, opponent
    return (("vs. %s" if home else "at %s") % city(opponent),
            "%s %d, %s %d" % (city(first), score[first], city(second), score[second]))


def as_of_line(ctx):
    line = "As of %s" % long_date(ctx.as_of)
    if ctx.games:
        last = ctx.games[-1]
        where, score = game_line(last)
        line += ", after the Week %d game %s (%s)" % (int(last["week"]), where.replace("vs.", "against"), score)
    return line + "."


def fixture_line(game):
    home = game["home"] == JAX
    return "Week %d %s %s, %s" % (game["week"], "against" if home else "at",
                                 city(game["away"] if home else game["home"]), long_date(game["date"]))


def player_link(ctx, rel, name):
    page = ctx.pages.get(name, (None, None))[0]
    return link(rel, page, name) if page else name


def join_names(names):
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def availability(ctx, name):
    row = next((p for p in ctx.roster["players"] if p["name"] == name), None)
    return (row or {}).get("availability") or ""


# ------------------------------------------------------------------ roster page
STATUS_NAMES = {"Active 53": "Active roster", "Offseason roster": "Offseason roster",
                "Reserve/Injured": "Reserve/injured",
                "Reserve/Injured, designated for return": "Reserve/injured, designated for return",
                "Practice squad": "Practice squad"}


def status_text(status):
    name = roster_record.status_name(status)
    return STATUS_NAMES.get(name, name)


def roster_page(ctx):
    rel = ctx.paths.roster_page.relative_to(ctx.root).as_posix()
    n = roster_record.counts(ctx.roster)
    ages = player_bios.biographies([p["name"] for p in ctx.roster["players"]], ctx.as_of, ctx.bios)
    open_places = []
    if n["open_active"]:
        open_places.append("%d on the active roster" % n["open_active"])
    if n["open_practice_squad"]:
        open_places.append("%d on the practice squad" % n["open_practice_squad"])
    lines = ["# Jacksonville Jaguars roster", "", as_of_line(ctx), "",
             table(["Active roster", "Reserve lists", "Practice squad", "Open places"],
                   [["%d of %d" % (n["active"], ctx.roster["active_limit"]), n["reserve"],
                     "%d of %d" % (n["practice_squad"], ctx.roster["practice_squad_places"]),
                     ", ".join(open_places) or "None"]], right=(1,)), "",
             " · ".join([link(rel, ctx.paths.record("depth_chart.md").relative_to(ctx.root).as_posix(), "Depth chart"),
                         link(rel, ctx.paths.record("medical/medical_history.md").relative_to(ctx.root).as_posix(),
                              "Medical history"),
                         link(rel, ctx.paths.record("player_ages.md").relative_to(ctx.root).as_posix(), "Player ages"),
                         link(rel, ctx.paths.record("team/README.md").relative_to(ctx.root).as_posix(), "The team")]),
             ""]

    def rows(players, with_availability=True):
        out = []
        for p in players:
            number = ctx.pages.get(p["name"], (None, None))[1]
            row = [player_link(ctx, rel, p["name"]), "" if number is None else number, p["position"], ages[p["name"]]["age"],
                   status_text(p["status"])]
            if with_availability:
                row.append(p["availability"])
            out.append(row)
        return out

    head = ["Player", "#", "Pos", "Age", "Status", "Availability"]
    groups = []
    for p in roster_record.players(ctx.roster, ("active",)):
        if p["group"] not in groups:
            groups.append(p["group"])
    for group in groups:
        members = [p for p in roster_record.players(ctx.roster, ("active",)) if p["group"] == group]
        lines += ["## %s" % group, "", table(head, rows(members), right=(1, 3)), ""]
    reserve = roster_record.players(ctx.roster, ("reserve",))
    if reserve:
        lines += ["## Reserve lists", "", table(head, rows(reserve), right=(1, 3)), ""]
    squad = roster_record.players(ctx.roster, ("practice_squad",))
    if squad:
        lines += ["## Practice squad", "", table(head[:-1], rows(squad, False), right=(1, 3)), ""]
    lines += ["Availability is the club's current medical communication on each player; no restriction "
              "communicated means none has been. Ages count completed birthdays at the roster's date.", ""]
    return rel, "\n".join(lines)


# ------------------------------------------------------------------ depth chart page
def role_labels(ctx):
    """{player: label}: Stone's latest dated role decision on the working chart, else his game role
    (runtime/assignments.role_labels)."""
    return chart_role_labels(ctx.chart, ctx.working)


def depth_chart_page(ctx):
    """Current assignments first; a shorter full depth order follows. Every name and note comes
    from the game depth chart and the roster record."""
    from runtime import season_summary as summary

    rel = ctx.paths.record("depth_chart.md").relative_to(ctx.root).as_posix()
    labels = role_labels(ctx)
    depth, positions = ctx.chart.get("depth") or {}, ctx.chart.get("positions") or {}
    roster = {p["name"]: p for p in ctx.roster.get("players", ())}
    lines = ["# Jacksonville Jaguars depth chart", "", as_of_line(ctx), "",
             "This is Stone's current depth order, not a confirmed game-day lineup. Injuries do not "
             "change a starter or reserve assignment until Stone changes the chart.", "",
             " · ".join([
                 link(rel, ctx.paths.roster_page.relative_to(ctx.root).as_posix(), "Roster"),
                 link(rel, ctx.paths.record("medical/current_injury_report.md").relative_to(ctx.root).as_posix(),
                      "Medical and availability"),
                 link(rel, ctx.paths.desk.relative_to(ctx.root).as_posix(), "Head coach's desk")]), "",
             "## First-unit offense", "",
             "Player use varies with the personnel package. The starting line and the X, H and Z "
             "receiver assignments are shown separately.", ""]
    offense = []

    def note(group, names, name):
        if group == "QB":
            return "%s is QB2" % names[1] if len(names) > 1 else ""
        if group == "RB":
            return ("%s %s" % (join_names(names[1:]), "follows" if len(names) == 2 else "follow")
                    if len(names) > 1 else "")
        if group == "FB":
            return "For fullback packages"
        if group == "WR":
            return labels.get(name, "")
        if group == "TE":
            return "Additional tight ends follow in the group order"
        return ""
    for group, index, label, _words in SEATS["offense"]:
        names = depth.get(group) or []
        if index < len(names) and names[index]:
            offense.append([label, player_link(ctx, rel, names[index]), note(group, names, names[index])])
    lines += [table(["Position", "Player", "Assignment"], offense), "",
              "## Base defense", "",
              "The first defensive-line and linebacker groups, and the first four defensive backs, "
              "are shown here. Individual front and package calls still control the snap.", ""]
    defense = []
    for group, unit, count in SEATS["defense"]:
        names = (depth.get(group) or [])[:count]
        defense.append([unit, ", ".join(player_link(ctx, rel, name) for name in names)])
    lines += [table(["Unit", "First group"], defense), "",
              "## Situational defensive roles", ""]
    jobs = (("nickel", "Nickel corner"), ("outside_reserve", "Outside corner reserve"))
    special_defense = []
    for code, label in jobs:
        names = [name for name, roles in ctx.chart.get("roles", {}).items() if code in roles]
        if names:
            special_defense.append([label, ", ".join(player_link(ctx, rel, name) for name in names)])
    dime_group, dime = SEATS["dime"]
    dbs = depth.get(dime_group) or []
    if len(dbs) > dime:
        special_defense.append(["Dime, sixth defensive back", player_link(ctx, rel, dbs[dime])])
    lines += [table(["Role", "Player"], special_defense) if special_defense else "No separate package seats recorded.", "",
              "## Current medical limitations", ""]
    active = summary.held(ctx.roster)
    if active:
        lines += [table(["Player", "Status", "Next medical date"],
                        [[player_link(ctx, rel, p["name"]), summary.medical_status(p),
                          summary.next_dates(p, ctx.as_of)] for p in active]), ""]
    else:
        lines += ["No medical instructions on the 53-man roster.", ""]
    lines += ["Medical clearance remains with the medical staff. " +
              link(rel, ctx.paths.record("medical/current_injury_report.md").relative_to(ctx.root).as_posix(),
                   "Full medical report"), "",
              "## Full depth order", "",
              "The order in each group remains Stone's current order. Reserve assignments that have "
              "not been named are not inferred from the table.", ""]
    for unit, groups in UNITS:
        lines += ["### " + unit, ""]
        for group in groups:
            players = depth.get(group) or []
            lines += ["#### " + GROUP_NAMES[group], "",
                      table(["Order", "Player", "Pos", "Role"],
                            [[i, player_link(ctx, rel, p), positions.get(p, ""), labels.get(p, "")]
                             for i, p in enumerate(players, 1)], right=(0,)), ""]
    special = [[job, ", ".join(player_link(ctx, rel, p) for p in depth.get(group) or [])]
               for group, job in SEATS["specialists"]]
    for code, label in (("kick_return", "Kick returner"), ("punt_return", "Punt returner")):
        names = [p for p, roles in ctx.chart.get("roles", {}).items() if code in roles]
        special.append([label, ", ".join(player_link(ctx, rel, p) for p in names)])
    lines += ["## Special teams", "", table(["Job", "Player"], special), ""]
    inactive = ctx.chart.get("game_day_inactives") or {}
    upcoming = ctx.next_game()
    lines += ["## Inactives", ""]
    listed = inactive.get("week")
    if upcoming and listed != upcoming["week"]:
        lines += ["%s: not yet set. Stone selects the eligible inactives before the game." %
                  fixture_line(upcoming), ""]
    if inactive.get("players"):
        game = next((g for g in ctx.fixtures.values()
                     if g["week"] == listed and JAX in (g["away"], g["home"])), None)
        lines += ["The prior game's inactives, for reference:", "",
                  table(["Player", "Position"],
                        [[player_link(ctx, rel, p), positions.get(p, "")]
                         for p in inactive["players"]]), ""]
    captains = ctx.chart.get("captains") or ctx.working.get("captains") or {}
    if captains:
        reserve = {p["name"] for p in roster_record.players(ctx.roster, ("reserve",))}
        def names(group):
            return ", ".join(p + (" (reserve/injured)" if p in reserve else "") for p in captains.get(group, ()))
        lines += ["## Captains, %s" % captains["date"], "",
                  table(["Offense", "Defense"], [[names("offense"), names("defense")]]), ""]
    history = ctx.paths.record("team/depth_chart/Changes.md")
    lines += ["## Update log", "",
              link(rel, history.relative_to(ctx.root).as_posix(), "Read all dated changes"), ""]
    return rel, "\n".join(lines)


def depth_history_page(ctx):
    """The complete dated change history stays readable off the main chart."""
    rel = (ctx.paths.record("team/depth_chart/Changes.md")).relative_to(ctx.root).as_posix()
    chart = ctx.paths.record("depth_chart.md").relative_to(ctx.root).as_posix()
    rows = []
    for e in ctx.log.get("entries", ()):
        sources = "; ".join(link(rel, s["page"].split("#")[0], s["label"],
                                 s["page"].split("#", 1)[1] if "#" in s["page"] else "")
                            for s in e["sources"])
        rows.append([e["date"], e["event"], e["change"], sources])
    lines = ["# Depth chart changes", "", as_of_line(ctx), "",
             link(rel, chart, "Current depth chart"), "",
             "## Update log", "", "Every dated assignment change, oldest first.", "",
             table(["Date", "Event", "Change", "Source"], rows), ""]
    return rel, "\n".join(lines)


# ------------------------------------------------------------------ team page
def results_rows(ctx):
    rows, wins, losses, ties = [], 0, 0, 0
    for r in ctx.games:
        where, _ = game_line(r)
        score = r["final_score"]
        opponent = r["away"] if r["home"] == JAX else r["home"]
        mine, theirs = score[JAX], score[opponent]
        result = "W" if mine > theirs else "L" if mine < theirs else "T"
        wins, losses, ties = wins + (result == "W"), losses + (result == "L"), ties + (result == "T")
        record = "%d-%d" % (wins, losses) + ("-%d" % ties if ties else "")
        rows.append([int(r["week"]), month_day(ctx.fixture(r)["date"]), where,
                     "%s %d-%d" % (result, mine, theirs), record])
    return rows


def division_rows(ctx):
    from runtime.standings import compute, pct_text
    result = compute(ctx.receipts)
    division = DIVISION_OF[JAX]
    out = []
    for team in result["division_ranks"][division]:
        line = result["lines"][team]
        o = line.overall
        out.append([team, o.wins, o.losses, o.ties, pct_text(o.pct), line.points_for, line.points_against])
    return division, out


def staff_lines(ctx):
    out = []
    for phase in current_job.PHASES:
        interval = current_job.interval_on(ctx.job, phase, ctx.as_of)
        if not interval:
            continue
        caller = current_job.party_name(ctx.job, interval["caller"])
        prepares = current_job.party_name(ctx.job, interval.get("prepares") or interval["caller"])
        text = "%s calls the plays" % caller
        if prepares != caller:
            text += "; %s prepares the plan" % prepares
        out.append([PHASE_NAMES[phase], text])
    return out


def party_names(ctx, pids):
    """The parties joined in one phrase: a group's name takes a small letter after the first
    ("Team medical staff and team communications staff"); a person's name is as recorded."""
    parties = ctx.job.get("parties") or {}
    names = []
    for i, pid in enumerate(pids):
        name = current_job.party_name(ctx.job, pid)
        if i and (parties.get(pid) or {}).get("kind") == "group":
            name = name[:1].lower() + name[1:]
        names.append(name)
    return " and ".join(names)


def authority_rows(ctx):
    current = current_job.appointment(ctx.job) or {}
    rows = []
    for d in (current.get("authority") or {}).get("domains", ()):
        if d.get("stone_action") == "not_applicable" or not d.get("final"):
            continue
        who = party_names(ctx, d["final"])
        part = ACTIONS[d["stone_action"]]
        scope = d.get("scope")
        if scope and not re.search(r"\brow\b", scope, re.I):
            part += ": " + scope
        if d["domain"] not in DECISIONS:
            raise ValueError("No football label for the club decision %r (render_club_pages.DECISIONS)" % d["domain"])
        rows.append([DECISIONS[d["domain"]], who, part])
    return rows


def requests_lines(ctx, rel):
    current = current_job.appointment(ctx.job) or {}
    out = []
    for e in current.get("evaluation") or ():
        if e.get("by") == "contract" or e.get("season") != ctx.year:
            continue
        text = e.get("text") or "%s: %s" % (e.get("label", "measures"), "; ".join(e.get("measures", ())))
        out.append((e, text))
    for e in current.get("employer_requests") or ():
        if e.get("season") == ctx.year:
            out.append((e, e["text"]))
    lines = []
    for e, text in out:
        record = e.get("record") or {}
        source = link(rel, record["path"], "season review", record.get("anchor", "")) if record.get("path") else ""
        lines.append("- **%s**: %s%s." % (titled(current_job.party_name(ctx.job, e["by"])), text[0].upper() + text[1:],
                                          " (%s)" % source if source else ""))
    return lines


def titled(name):
    """"Shad Khan, owner": a name with his club title, where the team page names one."""
    return "%s, %s" % (name, TITLES[name]) if name in TITLES else name


def team_page(ctx):
    rel = ctx.paths.record("team/README.md").relative_to(ctx.root).as_posix()
    current = current_job.appointment(ctx.job) or {}
    find = lambda pid: current_job.party_name(ctx.job, pid)
    to = lambda logical, label, anchor="": link(rel, ctx.paths.record(logical).relative_to(ctx.root).as_posix(),
                                                label, anchor)
    owners = [titled(find(p)) for p in (current.get("reporting") or {}).get("employment_decided_by") or ()]
    deciders = ", and ".join([", ".join(owners[:-1]), owners[-1]]) if len(owners) > 1 else "".join(owners)
    lines = ["# Jacksonville Jaguars", "", as_of_line(ctx), "",
             "Head coach %s. Employed by the %s%s." % (
                 find(ctx.job.get("holder")), (current.get("employer") or {}).get("club") or JAX,
                 "; employment decided by %s" % deciders if deciders else ""), ""]
    lines += ["## Results, %d" % ctx.year, ""]
    rows = results_rows(ctx)
    lines += [table(["Week", "Date", "Opponent", "Result", "Record"], rows, right=(0,)) if rows
              else "No game played yet.", ""]
    upcoming = ctx.next_game()
    if upcoming:
        lines += ["Next: %s." % fixture_line(upcoming), ""]
    division, standing = division_rows(ctx)
    lines += ["## %s" % division, "",
              table(["Team", "W", "L", "T", "Pct", "PF", "PA"], standing, right=(1, 2, 3, 4, 5, 6)), "",
              to("standings.md", "League standings"), ""]
    n = roster_record.counts(ctx.roster)
    groups = []
    for p in roster_record.players(ctx.roster, ("active",)):
        if p["group"] not in [g for g, _ in groups]:
            groups.append((p["group"], sum(1 for q in roster_record.players(ctx.roster, ("active",))
                                           if q["group"] == p["group"])))
    lines += ["## Roster", "",
              "%d on the active roster, %d on the reserve lists and %d of %d on the practice squad." % (
                  n["active"], n["reserve"], n["practice_squad"], ctx.roster["practice_squad_places"]), "",
              table(["Group", "Players"], [[g, c] for g, c in groups], right=(1,)), "",
              " · ".join([to("roster.md", "Roster"), to("depth_chart.md", "Depth chart"),
                          to("player_profiles/README.md", "Player pages")]), ""]
    lines += ["## Staff", "", table(["Phase", "Game day"], staff_lines(ctx)), "",
              to("team/coaching_staff/README.md", "The staff"), ""]
    lines += ["## Who decides what", "", table(["Decision", "Decided by", "Head coach"], authority_rows(ctx)), ""]
    asked = requests_lines(ctx, rel)
    lines += ["## What the owner and general manager have asked", ""] + (asked or ["Nothing recorded."]) + [""]
    lines += ["## More", "",
              " · ".join([to("player_profiles/README.md", "Player pages"), to("medical/README.md", "Medical"),
                          to("medical/current_injury_report.md", "Injury report"), to("team/film/README.md", "Film"),
                          to("team/player_development/README.md", "Player development"),
                          to("finances/README.md", "Finances")]), ""]
    return rel, "\n".join(lines)


# ------------------------------------------------------------------ build, check, write
def build(root=ROOT, ctx=None):
    ctx = Context(root) if ctx is None else ctx
    return dict(builder(ctx) for builder in (roster_page, depth_chart_page, depth_history_page, team_page))


LOG_KEYS = ("team", "season", "about", "entries")
ENTRY_KEYS = ("date", "recorded", "event", "change", "sources")
# "events": the closed events an entry belongs to; "as_written": the entry's original row, kept
# exactly when it was reworded for the page and never rendered.
ENTRY_OPTIONAL = ("events", "as_written")
AS_WRITTEN_KEYS = ("date", "event", "source", "change")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
# How an entry's date is shown: the long form of the day it was recorded ("October 5, 2014"), or
# built from it: a window ending on it ("April 4 to 7, 2014", "September 29 to October 4, 2014"),
# a note on the same day ("February 28, 2014 review"), or the day it happened with the day it was
# recorded ("May 12, 2014 (recorded May 23)").
SHOWN_DATE = re.compile(r"^(?P<month>%(m)s) (?P<day>\d{1,2})(?: to (?:(?P<end_month>%(m)s) )?(?P<end_day>\d{1,2}))?, "
                        r"(?P<year>\d{4})(?: (?:review|correction))?"
                        r"(?: \(recorded (?P<rec_month>%(m)s) (?P<rec_day>\d{1,2})\))?$" % {"m": MONTHS})


def shown_recorded(text):
    """The day an entry's shown date says it was recorded, or None when it is not built from one:
    the "(recorded ...)" day if it names one, else the window's last day, else the day itself. The
    first day it names may not come after that day (a window that crosses the new year starts in
    the year before)."""
    m = SHOWN_DATE.match(text) if isinstance(text, str) else None
    if not m:
        return None
    month = lambda name: MONTHS.split("|").index(name) + 1
    year = int(m["year"])
    try:
        first = date(year, month(m["month"]), int(m["day"]))
        if m["rec_month"]:
            last = date(year, month(m["rec_month"]), int(m["rec_day"]))
        elif m["end_day"]:
            last = date(year, month(m["end_month"] or m["month"]), int(m["end_day"]))
            if m["end_month"] and first > last:
                first = first.replace(year=year - 1)
        else:
            last = first
    except ValueError:
        return None
    return last if first <= last else None


def career_page(root, page):
    """Whether ``page`` (a repository path, with any anchor) names, after normalizing, an existing
    Markdown page under career/: career/../AGENTS.md does not."""
    path = page.split("#")[0] if isinstance(page, str) else ""
    normal = os.path.normpath(path).replace(os.sep, "/") if path else ""
    if not normal.startswith("career/") or not normal.endswith(".md"):
        return False
    target = (Path(root) / normal).resolve()
    return target.is_file() and target.is_relative_to((Path(root) / "career").resolve())


def log_errors(log, root=ROOT):
    """The depth chart's update log against its form: the record's keys, each entry's required and
    allowed keys, a recorded ISO date no later than the master date, a shown date that is the long
    form of the recorded date or built from it (``shown_recorded``), entries oldest first, and
    sources that are existing pages under career/ (``career_page``)."""
    root = Path(root)
    if not isinstance(log, dict) or set(log) != set(LOG_KEYS) or not isinstance(log["entries"], list):
        return ["Depth chart update log must hold exactly %s" % ", ".join(LOG_KEYS)]
    master = master_date(root)
    errors, previous = [], None
    for i, e in enumerate(log["entries"], 1):
        where = "Depth chart update log entry %d" % i
        if not isinstance(e, dict) or not set(ENTRY_KEYS) <= set(e) or not set(e) <= set(ENTRY_KEYS + ENTRY_OPTIONAL):
            errors.append("%s: keys must be %s (optionally %s)" % (where, ", ".join(ENTRY_KEYS), ", ".join(ENTRY_OPTIONAL)))
            continue
        if not all(isinstance(e[k], str) and e[k].strip() for k in ("date", "event", "change")):
            errors.append("%s: the date, event and change need text" % where)
        try:
            recorded = date.fromisoformat(e["recorded"])
        except (TypeError, ValueError):
            errors.append("%s: recorded needs an ISO date" % where)
            recorded = None
        if recorded and previous and recorded < previous:
            errors.append("%s: recorded %s is earlier than the entry before it" % (where, e["recorded"]))
        if recorded and recorded > master:
            errors.append("%s: recorded %s is after the master date %s" % (where, e["recorded"], master.isoformat()))
        if recorded and shown_recorded(e["date"]) != recorded:
            errors.append("%s: the date %r must be the long form of recorded %s (%s) or built from it"
                          % (where, e["date"], e["recorded"], long_date(recorded)))
        previous = recorded or previous
        if not isinstance(e["sources"], list) or not e["sources"]:
            errors.append("%s: needs at least one source" % where)
        for s in e["sources"] if isinstance(e["sources"], list) else ():
            page = s.get("page", "") if isinstance(s, dict) else ""
            if (not isinstance(s, dict) or set(s) != {"label", "page"} or not s.get("label")
                    or not career_page(root, page)):
                errors.append("%s: a source must be a labelled page under career/ that exists: %r" % (where, s))
        if "events" in e and (not isinstance(e["events"], list) or not all(isinstance(x, str) and x for x in e["events"])):
            errors.append("%s: events must be a list of event ids" % where)
        if "as_written" in e and (not isinstance(e["as_written"], dict) or set(e["as_written"]) != set(AS_WRITTEN_KEYS)
                                  or not all(isinstance(v, str) for v in e["as_written"].values())):
            errors.append("%s: as_written must hold the original %s" % (where, ", ".join(AS_WRITTEN_KEYS)))
    return errors


def record_errors(ctx):
    """The roster record and the closed games against each other: every closed game matches a
    fixture, and the record is not dated before Jacksonville's last closed game."""
    errors = ["Closed game with no fixture (week %s, %s at %s)" % (r["week"], r["away"], r["home"])
              for r in ctx.unmatched]
    ours = [r for r in ctx.closed if JAX in (r["home"], r["away"])]
    if ours:
        last = max(ours, key=lambda r: ctx.fixture(r)["date"])
        played = date.fromisoformat(ctx.fixture(last)["date"])
        recorded = date.fromisoformat(ctx.roster["as_of"]["date"])
        if recorded < played:
            errors.append("Roster record dated %s, before Jacksonville's last closed game (Week %d, %s): bring the "
                          "record's as_of up to the game's close" % (recorded, int(last["week"]), played))
    return errors


def check(root=ROOT):
    """Every club page that is missing, differs from its rebuild or breaks the clean-page rule, a
    roster record behind the last closed game, and an update log out of form."""
    from runtime.clean_pages import page_errors
    root = Path(root).resolve()
    ctx = Context(root)
    errors = record_errors(ctx) + log_errors(ctx.log, root)
    for rel, text in build(root, ctx).items():
        path = root / rel
        if not path.is_file():
            errors.append("Club page missing: %s" % rel)
        elif path.read_bytes() != text.encode("utf-8"):
            errors.append("Club page stale or hand-edited: %s" % rel)
        errors += page_errors(rel, text, root=root)
    return errors


def write(root=ROOT):
    root = Path(root).resolve()
    written = 0
    for rel, text in build(root).items():
        path = root / rel
        data = text.encode("utf-8")
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written += 1
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        print("\n".join(errors) if errors else "CLUB PAGES CURRENT")
        return 1 if errors else 0
    print("club pages: %d written" % write(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
